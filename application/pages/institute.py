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
from utils.streamlit_utils import hide_icons, hide_sidebar, remove_whitespaces, displayPDF
import qrcode
from PIL import Image
from pathlib import Path

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

    # Filter out empty string fields if any
    recipients = [email.strip() for email in recipient_emails if email and email.strip()]
    if not recipients:
        st.warning("No valid email addresses provided for notification.")
        return

    # Create the email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = ", ".join(recipients)
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
        server.sendmail(sender_email, recipients, msg.as_string())
        server.quit()
        st.success(f"📨 Certificate successfully emailed to {', '.join(recipients)}")
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

        # <--- ADD THIS: File uploader for the logo --->
        uploaded_logo = form.file_uploader("Upload Institute Logo (Optional)", type=["png", "jpg", "jpeg"])

        submit = form.form_submit_button("Submit")

    if submit:
        # 1. Base directory setups for dynamic absolute path evaluation
        current_dir = Path(__file__).parent.resolve()
        root_dir = current_dir.parent.parent
        
        default_logo_path = str(root_dir / "assets" / "logo.jpg")
        temp_logo_path = None

        # Handle image file upload check
        if uploaded_logo is not None:
            extension = uploaded_logo.name.split('.')[-1]
            temp_filename = f"temp_logo.{extension}"
            temp_logo_path = str(root_dir / temp_filename)
            
            with open(temp_logo_path, "wb") as f:
                f.write(uploaded_logo.getbuffer())
            institute_logo_path = temp_logo_path
        else:
            institute_logo_path = default_logo_path

        # 2. Cryptographic computation (Guaranteed to build certificate_id variable)
        data_to_hash = f"{uid}{candidate_name}{course_name}{org_name}".encode('utf-8')
        certificate_id = hashlib.sha256(data_to_hash).hexdigest()
        
        pdf_file_path = "certificate.pdf"
        
        # 3. Document PDF compilation layer
        generate_certificate(
            pdf_file_path, 
            uid, 
            candidate_name, 
            course_name, 
            org_name, 
            institute_logo_path, 
            certificate_id
        )

        # 4. Storage distribution
        ipfs_hash = upload_to_pinata(pdf_file_path, api_key, api_secret)

        # 5. Smart Contract Execution Pipeline
        try:
            # Build transaction sequence using uniform variable bounds
            contract_txn = contract.functions.generateCertificate(
                certificate_id,
                uid,
                candidate_name,
                course_name,
                org_name,
                ipfs_hash
            ).build_transaction({
                'chainId': 11155111,
                'gas': 400000,
                'gasPrice': int(w3.eth.gas_price * 1.15),
                'nonce': w3.eth.get_transaction_count(w3.eth.account.from_key(os.getenv("PRIVATE_KEY")).address, 'pending'),
            })

            # Cryptographic payload verification and broadcasting
            signed_txn = w3.eth.account.sign_transaction(contract_txn, private_key=os.getenv("PRIVATE_KEY"))
            tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            
            # Await testnet node settlement confirmation
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300, poll_latency=2)
            
            if receipt.status == 1:
                st.success("🎉 Certificate successfully anchored to the Ethereum Blockchain!")
                st.write(f"**Transaction Hash:** `{tx_hash.hex()}`")
                st.write(f"**IPFS CID Reference:** `{ipfs_hash}`")
                
                # ─── RESTORED VISUAL DASHBOARD & EMAIL COMPONENTS ───
                st.write("---")
                st.subheader("Generated Certificate Preview")
                
                # 1. Display PDF preview on dashboard if it exists
                if os.path.exists(pdf_file_path):
                    displayPDF(pdf_file_path)
                
                # 2. Dispatch email to Student and Verifier
                email_list = []
                if student_email:
                    email_list.append(student_email)
                if verifier_email:
                    email_list.append(verifier_email)
                
                if email_list and os.path.exists(pdf_file_path):
                    email_subject = f"Digital Certificate Issued: {course_name}"
                    email_body = f"Hello,\n\nA new digital certificate has been verified and securely anchored to the blockchain for {candidate_name}.\n\nCertificate ID: {certificate_id}\nIPFS Hash: {ipfs_hash}\n\nPlease find the official signed PDF document attached to this email."
                    send_email_with_attachment(email_list, email_subject, email_body, pdf_file_path)
                # ───────────────────────────────────────────────────
            else:
                st.error("Transaction failed during execution on Sepolia.")

        except Exception as e:
            st.error(f"Blockchain Verification Error: {str(e)}")

        # Cleanup temporary local instances safely
        if temp_logo_path and os.path.exists(temp_logo_path):
            os.remove(temp_logo_path)
        if os.path.exists(pdf_file_path):
            os.remove(pdf_file_path)