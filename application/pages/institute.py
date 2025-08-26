import streamlit as st
import requests
import json
import os
import time
import pandas as pd
from dotenv import load_dotenv
import hashlib
from utils.cert_utils import generate_certificate
from utils.streamlit_utils import view_certificate
from connection import contract, w3
from utils.streamlit_utils import hide_icons, hide_sidebar, remove_whitespaces
import qrcode
from PIL import Image

# --- Add these imports for sending email ---
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
# -----------------------------------------

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
hide_icons()
hide_sidebar()
remove_whitespaces()

load_dotenv()

api_key = os.getenv("PINATA_API_KEY")
api_secret = os.getenv("PINATA_API_SECRET")


def upload_to_pinata(file_path, api_key, api_secret):
    # Set up the Pinata API endpoint and headers
    pinata_api_url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    headers = {
        "pinata_api_key": api_key,
        "pinata_secret_api_key": api_secret,
    }

    # Prepare the file for upload
    with open(file_path, "rb") as file:
        files = {"file": (file.name, file)}

        # Make the request to Pinata
        response = requests.post(pinata_api_url, headers=headers, files=files)

        # Parse the response
        result = json.loads(response.text)

        if "IpfsHash" in result:
            ipfs_hash = result["IpfsHash"]
            print(f"File uploaded to Pinata. IPFS Hash: {ipfs_hash}")
            return ipfs_hash
        else:
            print(f"Error uploading to Pinata: {result.get('error', 'Unknown error')}")
            return None
        
# --- New function to send email with attachment ---
def send_email_with_attachment(recipient_emails, subject, body, file_path):
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")

    # Create the email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = ", ".join(recipient_emails)
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Attach the file
    with open(file_path, "rb") as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(file_path)}")
    msg.attach(part)

    try:
        # Connect to the SMTP server (example for Gmail)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_emails, msg.as_string())
        server.quit()
        st.success(f"Certificate successfully emailed to {', '.join(recipient_emails)}")
    except Exception as e:
        st.error(f"Failed to send email. Error: {e}")
# ----------------------------------------------------

options = ("Generate Certificate", "View Certificates")
selected = st.selectbox("", options, label_visibility="hidden")

if selected == options[0]:
    col1, col2 = st.columns(2)
    with col1:

        form = st.form("Generate-Certificate")
        form.subheader("Generate Certificate")
        uid = form.text_input(label="UID")
        candidate_name = form.text_input(label="Name")
        course_name = form.text_input(label="Course Name")
        org_name = form.text_input(label="Org Name")

        # --- Add new fields for emails ---
        student_email = form.text_input(label="Student's Email")
        verifier_email = form.text_input(label="Verifier's Email")

        submit = form.form_submit_button("Submit")

    
    if submit:

        # --- KEY CHANGE: Generate certificate_id FIRST ---
        data_to_hash = f"{uid}{candidate_name}{course_name}{org_name}".encode('utf-8')
        certificate_id = hashlib.sha256(data_to_hash).hexdigest()

        pdf_file_path = "certificate.pdf"
        institute_logo_path = "../assets/logo.jpg"
        generate_certificate(pdf_file_path, uid, candidate_name, course_name, org_name, institute_logo_path, certificate_id)

        # Upload the PDF to Pinata
        ipfs_hash = upload_to_pinata(pdf_file_path, api_key, api_secret)
        
        

        # Smart Contract Call
        start_time = time.time()
        tx_hash = contract.functions.generateCertificate(certificate_id, uid, candidate_name, course_name, org_name, ipfs_hash).transact({'from': w3.eth.accounts[0]})
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        end_time = time.time()

        # --- Send the email after generating the PDF ---
        if student_email or verifier_email:
            recipients = [email for email in [student_email, verifier_email] if email]
            email_subject = f"Certificate of Completion for {candidate_name}"
            email_body = (
                f"Dear {candidate_name},\n\n"
                f"Please find attached your certificate for completing the course: {course_name}.\n\n"
                f"Your unique Certificate ID is: {certificate_id}\n\n"
                "This can be verified on our portal.\n\n"
                "Best Regards,\n"
                f"{org_name}"
            )
            send_email_with_attachment(recipients, email_subject, email_body, pdf_file_path)

        
        # -----------------------------------------------

        # Clean up the generated PDF file after sending
        os.remove(pdf_file_path)
        with col2:

            st.success("Certificate successfully generated!")
            st.write("Certificate ID:")
            st.code(certificate_id, language=None)

            # ... (rest of the results display code remains the same)
            st.write("Certificate QR Code:")
            qr_img = qrcode.make(certificate_id)
            qr_img.save("certificate_qr.png")
            st.image("certificate_qr.png", width=200)
            with open("certificate_qr.png", "rb") as file:
                st.download_button(
                    label="Download QR Code",
                    data=file,
                    file_name="certificate_qr.png",
                    mime="image/png"
                )
            os.remove("certificate_qr.png")

            # Display gas and execution time
            execution_time = end_time - start_time
            gas_used = receipt['gasUsed']

            df = pd.DataFrame({
                "Particulars": ["Execution Time (seconds)", "Gas Used"],
                "Value": [f"{execution_time:.4f}", gas_used]
            })

            st.dataframe(df, hide_index=True)

else:
    form = st.form("View-Certificate")
    certificate_id = form.text_input("Enter the Certificate ID")
    submit = form.form_submit_button("Submit")
    if submit:
        try:
            view_certificate(certificate_id)
        except Exception as e:
            st.error("Invalid Certificate ID!")
        
