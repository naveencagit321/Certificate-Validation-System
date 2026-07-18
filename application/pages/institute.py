import streamlit as st
import cv2
import os
import json
import requests
import hashlib
import time
import smtplib
import qrcode
import pandas as pd
from pathlib import Path
# 🌟 ADD THESE IMPORTS AT THE VERY TOP OF YOUR FILE
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.encoders import encode_base64
from connection import contract, w3  # Web3 and contract instance imports
from utils.streamlit_utils import hide_icons, hide_sidebar, remove_whitespaces

# ─── STREAMLIT PAGE CONFIGURATION ───
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
hide_icons()
hide_sidebar()
remove_whitespaces()

# ─── ELIMINATE SIDEBAR INFRASTRUCTURE ───
st.markdown(
    """
    <style>
        [data-testid="stSidebarCollapseButton"] {
            display: none !important;
            visibility: hidden !important;
        }
        section[data-testid="stSidebar"] {
            display: none !important;
            width: 0px !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ─── TOP-LEFT INLINE NAVIGATION HEADER ───
if st.button("Home", key="nav_home_verifier_btn"):
    st.switch_page("app.py")

# Dynamic Root Directory Path Tracking
ROOT_DIR = Path(__file__).resolve().parent.parent.parent

def upload_to_pinata(file_path, api_key, api_secret):
    """Uploads the local certificate PDF file safely to the Pinata IPFS network node."""
    pinata_api_url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    headers = {
        "pinata_api_key": api_key,
        "pinata_secret_api_key": api_secret,
    }

    try:
        with open(file_path, "rb") as file:
            files = {"file": (os.path.basename(file_path), file)}
            response = requests.post(pinata_api_url, headers=headers, files=files)
            result = json.loads(response.text)

            if "IpfsHash" in result:
                ipfs_hash = result["IpfsHash"]
                print(f"File uploaded to Pinata. IPFS Hash: {ipfs_hash}")
                return ipfs_hash
            else:
                print(f"Error uploading to Pinata: {result.get('error', 'Unknown error')}")
                return None
    except Exception as e:
        st.error(f"Pinata Core Connection Failure: {e}")
        return None

def send_email_with_attachment(recipient_emails, subject, body, file_path):
    """Dispatches verification data email alerts using standard secure network SMTP protocols."""
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")

    if not sender_email or not sender_password:
        st.warning("Email notification skipped: SMTP environment credentials absent.")
        return False

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = ", ".join(recipient_emails)
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    if not file_path or not os.path.exists(file_path):
        st.error(f"Attachment file execution path invalid: {file_path}")
        return False

    try:
        with open(file_path, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename={os.path.basename(file_path)}")
        msg.attach(part)
    except Exception as e:
        st.error(f"Failed to prepare secure file mapping payload attachment: {e}")
        return False

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_emails, msg.as_string())
        server.quit()
        st.success(f"Notification details successfully dispatched to: {', '.join(recipient_emails)}")
        return True
    except Exception as e:
        st.error(f"SMTP Secure Outbound Network Dispatch Failed: {e}")
        return False

# Placeholder structural stubs to prevent pipeline dependencies from raising runtime exceptions
def generate_certificate(pdf_path, uid, name, course, org, logo_path, cert_id):
    """Generates a geometrically valid binary PDF layout artifact with a built-in verification QR code."""
    try:
        c = canvas.Canvas(pdf_path, pagesize=letter)
        
        # Draw background border layout lines
        c.setLineWidth(5)
        c.setStrokeColorRGB(0.1, 0.2, 0.4)
        c.rect(20, 20, 572, 752)
        
        # Add institute logo image if provided
        if logo_path and os.path.exists(logo_path):
            try:
                c.drawImage(logo_path, 250, 650, width=100, height=50)
            except Exception:
                pass
        
        # Typography text elements layout
        c.setFont("Helvetica-Bold", 28)
        c.drawCentredString(306, 550, "CERTIFICATE OF COMPLETION")
        
        c.setFont("Helvetica", 16)
        c.drawCentredString(306, 480, "This is proudly presented to")
        
        c.setFont("Helvetica-Bold", 22)
        c.drawCentredString(306, 430, name)
        
        c.setFont("Helvetica", 14)
        c.drawCentredString(306, 380, "For successfully completing the course program:")
        c.setFont("Helvetica-Oblique", 16)
        c.drawCentredString(306, 350, course)
        
        c.setFont("Helvetica", 12)
        c.drawCentredString(306, 280, f"Authorized by: {org}")
        c.drawCentredString(306, 260, f"Student UID: {uid}")
        
        # 🌟 DYNAMICALLY GENERATE AND ATTACH THE QR CODE TARGET DIRECTLY INSIDE THE PDF
        # We encode the 'uid' string since that's what the contract reads!
        qr = qrcode.QRCode(version=1, box_size=3, border=1)
        qr.add_data(uid.strip())
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        temp_qr_pdf_path = "temp_pdf_qr.png"
        qr_img.save(temp_qr_pdf_path)
        
        # Draw the QR code target asset box image near the bottom right center
        c.drawImage(temp_qr_pdf_path, 256, 120, width=100, height=100)
        if os.path.exists(temp_qr_pdf_path):
            os.remove(temp_qr_pdf_path)
        
        # Embed the validation verification fingerprint footprint hash at the footer lines
        c.setFont("Courier", 8)
        c.setFillColorRGB(0.5, 0.5, 0.5)
        c.drawCentredString(306, 50, f"Verification Ledger ID: {cert_id}")
        
        c.save()
        print(f"Successfully compiled valid binary PDF layout artifact with attached verification QR code to {pdf_path}")
    except Exception as e:
        st.error(f"Failed to compile valid PDF artifact layer: {e}")

def view_certificate(cert_id):
    """Queries the smart contract ledger to retrieve data for a target certificate ID."""
    with st.spinner("Fetching certificate data from Ethereum Blockchain..."):
        try:
            # Check connection stability
            if not getattr(w3, 'is_connected', None) or not w3.is_connected():
                st.error("Connection Error: Web3 provider is offline.")
                return

            # Call the smart contract getter method natively
            # Based on the contract return structure: (studentName, courseName, organization, ipfsHash)
            cert_details = contract.functions.getCertificate(cert_id.strip()).call()

            if cert_details and cert_details[0]:
                st.success("### 🔐 Certificate Record Retrieved!")
                
                # Render information via a clean layout using the correct Solidity indices
                st.markdown("#### **Verified Records:**")
                st.markdown(f"* 🧑‍🎓 **Student Name:** {cert_details[0]}")
                st.markdown(f"* 📚 **Course Program:** {cert_details[1]}")
                st.markdown(f"* 🏢 **Issuing Authority:** {cert_details[2]}")
                
                # Provide a direct clickable button linking to the document hosted on IPFS
                if cert_details[3]:
                    ipfs_url = f"https://gateway.pinata.cloud/ipfs/{cert_details[3]}"
                    st.markdown(f"[📄 View Original Certificate Document on IPFS]({ipfs_url})")
            else:
                st.error("Certificate not found on-chain.")
        except Exception as e:
            st.error(f"Error accessing contract parameters: {str(e)}")

# Initialize cloud configurations
api_key = os.getenv("PINATA_API_KEY", "")
api_secret = os.getenv("PINATA_API_SECRET", "")

options = ("Generate Certificate", "View Certificates")
selected = st.selectbox("Choose an action", options)

if selected == options[0]:
    col1, col2 = st.columns(2)
    with col1:
        form = st.form("Generate-Certificate")
        form.subheader("Generate Certificate Portal")
        uid = form.text_input(label="UID")
        candidate_name = form.text_input(label="Name")
        course_name = form.text_input(label="Course Name")
        org_name = form.text_input(label="Org Name")

        # Your beautiful notification parameters
        student_email = form.text_input(label="Student's Email")
        verifier_email = form.text_input(label="Verifier's Email")
        uploaded_logo = form.file_uploader("Upload Institute Logo (Optional)", type=["png", "jpg", "jpeg"])

        submit = form.form_submit_button("Submit")

    if submit:
        default_logo_path = str(ROOT_DIR / "assets" / "logo.jpg")
        institute_logo_path = None
        temp_logo_path = None

        if uploaded_logo is not None:
            temp_dir = ROOT_DIR / "application"
            temp_dir.mkdir(exist_ok=True)
            temp_logo_path = str(temp_dir / f"temp_logo.{uploaded_logo.name.split('.')[-1]}")
            with open(temp_logo_path, "wb") as f:
                f.write(uploaded_logo.getbuffer())
            institute_logo_path = temp_logo_path
        elif os.path.exists(default_logo_path):
            institute_logo_path = default_logo_path

        data_to_hash = f"{uid}{candidate_name}{course_name}{org_name}".encode('utf-8')
        certificate_id = hashlib.sha256(data_to_hash).hexdigest()

        pdf_file_path = "certificate.pdf"
        generate_certificate(pdf_file_path, uid, candidate_name, course_name, org_name, institute_logo_path, certificate_id)

        if temp_logo_path and os.path.exists(temp_logo_path):
            os.remove(temp_logo_path)

        # Upload generated artifact asset array onto decentralized file system layout
        ipfs_hash = upload_to_pinata(pdf_file_path, api_key, api_secret)
        
        # State tracking pipeline parameters
        private_key = os.getenv("PRIVATE_KEY")
        blockchain_submitted = False
        receipt = None
        tx_hash = None
        start_time = None
        end_time = None

        # ─── BLOCKCHAIN TRANSACTION ARCHITECTURE MODULE ───
        if not private_key:
            st.warning("PRIVATE_KEY configuration empty. Execution terminated locally without ledger mutation submission.")
        else:
            if not private_key.startswith('0x'):
                private_key = '0x' + private_key

            if not ipfs_hash:
                st.error("IPFS token identification failure — execution aborted.")
            else:
                try:
                    account = w3.eth.account.from_key(private_key)
                    nonce = w3.eth.get_transaction_count(account.address, 'pending')

                    # 🌟 FIX 1: Calls 'issueCertificate' with precisely 5 parameters
                    try:
                        contract.functions.issueCertificate(
                            uid,
                            candidate_name,
                            course_name,
                            org_name,
                            ipfs_hash
                        ).call({'from': account.address})
                    except Exception as exc:
                        st.error(f"On-chain preflight simulation dry-run failed: {exc}")
                        raise

                    try:
                        estimated_gas = contract.functions.issueCertificate(
                            uid,
                            candidate_name,
                            course_name,
                            org_name,
                            ipfs_hash
                        ).estimate_gas({'from': account.address})
                        gas_limit = int(estimated_gas * 1.2)
                    except Exception as exc:
                        gas_limit = 400000  # Safe transaction gas wall baseline limit headroom fallback configuration

                    # 🌟 FIX 2: Fixed to match Web3.py snake_case build_transaction schema configuration
                    contract_txn = contract.functions.issueCertificate(
                        uid,
                        candidate_name,
                        course_name,
                        org_name,
                        ipfs_hash
                    ).build_transaction({
                        'chainId': 11155111,
                        'gas': gas_limit,
                        'gasPrice': w3.eth.gas_price,
                        'nonce': nonce,
                    })

                    # Secure local signing procedure via native bytes validation mapping logic
                    signed_txn = w3.eth.account.sign_transaction(contract_txn, private_key=private_key)
                    raw_tx = getattr(signed_txn, 'rawTransaction', None) or getattr(signed_txn, 'raw_transaction', None)
                    
                    if raw_tx is None and isinstance(signed_txn, dict):
                        raw_tx = signed_txn.get('rawTransaction') or signed_txn.get('raw_transaction')

                    if isinstance(raw_tx, str) and raw_tx.startswith('0x'):
                        raw_tx = bytes.fromhex(raw_tx[2:])
                    elif raw_tx is not None:
                        raw_tx = bytes(raw_tx)

                    if raw_tx is None:
                        st.error('Signed transaction buffer parsing initialization exception.')
                        raise RuntimeError('Signed object payload structure bytes mapping missing')

                    # Execute raw transaction payload over Sepolia public RPC node gateway
                    start_time = time.time()
                    tx_hash = w3.eth.send_raw_transaction(raw_tx)
                    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                    end_time = time.time()

                    status = receipt.get('status') if isinstance(receipt, dict) else getattr(receipt, 'status', None)
                    tx_hex = tx_hash.hex() if hasattr(tx_hash, 'hex') else str(tx_hash)
                    
                    if status is None:
                        st.info(f"Transaction broadcasting complete: {tx_hex}. Miner validation pending confirmation blocks.")
                    elif int(status) == 1:
                        st.success(f"Ledger mutation finalized successfully! Hash footprint signature: {tx_hex} (Block: {receipt.get('blockNumber', 'N/A')})")
                        blockchain_submitted = True
                    else:
                        st.error(f"Transaction processing failed: Execution reverted on-chain inside smart contract execution logic runtime environment context: {tx_hex}")
                        blockchain_submitted = False
                except Exception as exc:
                    st.error(f"Blockchain node execution processing failure exception raised: {exc}")

        # Dispatch off-chain communications to requested recipients using local file storage buffers
        if student_email or verifier_email:
            recipients = [email for email in [student_email, verifier_email] if email]
            email_subject = f"Cryptographic Verification Record Issued: {candidate_name}"
            email_body = (
                f"Dear {candidate_name},\n\n"
                f"Your official verification statement document file has been successfully issued for course program: {course_name}.\n\n"
                f"Unique Decentralized Ledger Lookup Certificate ID: {certificate_id}\n\n"
                f"Sincerely,\n{org_name}"
            )
            send_email_with_attachment(recipients, email_subject, email_body, pdf_file_path)

        # Clear temporary data storage layout caches dynamically to free execution server allocations
        try:
            if os.path.exists(pdf_file_path):
                os.remove(pdf_file_path)
        except Exception as e:
            st.warning(f"Could not clear runtime storage memory for asset path {pdf_file_path}: {e}")

        # Render analytical dashboard values out onto user layout panel grid column wrapper structures
        with col2:
            st.success("Verification Document Created Successfully!")
            st.write("Unique Lookup Index Token ID:")
            st.code(certificate_id, language=None)

            st.write("Dynamic Routing QR Verification Grid Target Allocation:")
            qr_img = qrcode.make(uid.strip())
            qr_img.save("certificate_qr.png")
            st.image("certificate_qr.png", width=200)
            with open("certificate_qr.png", "rb") as file:
                st.download_button(
                    label="Download QR Signature Asset",
                    data=file,
                    file_name="certificate_qr.png",
                    mime="image/png"
                )
            if os.path.exists("certificate_qr.png"):
                os.remove("certificate_qr.png")

            if blockchain_submitted and start_time is not None and end_time is not None and receipt is not None:
                execution_time = end_time - start_time
                gas_used = receipt.get('gasUsed', 'N/A')
                df = pd.DataFrame({
                    "Particulars": ["Execution Network Time (Seconds)", "On-Chain Gas Fee Consumption Units"],
                    "Value": [f"{execution_time:.4f}", gas_used]
                })
            else:
                df = pd.DataFrame({
                    "Particulars": ["Execution Network Time (Seconds)", "On-Chain Gas Fee Consumption Units"],
                    "Value": ["N/A", "N/A"]
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
            st.error("Invalid Certificate Identification Parameters Provided!")