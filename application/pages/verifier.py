import streamlit as st
import os
import hashlib
from utils.cert_utils import extract_certificate
from utils.streamlit_utils import view_certificate
from connection import contract
from utils.streamlit_utils import displayPDF, hide_icons, hide_sidebar, remove_whitespaces
import cv2
from streamlit_webrtc import webrtc_streamer, RTCConfiguration
import threading

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
hide_icons()
hide_sidebar()
remove_whitespaces()

# --- Thread-safe storage for the result ---
lock = threading.Lock()
qr_decoder = cv2.QRCodeDetector()

# Use Streamlit Session State to hold the scanned ID securely across thread renders
if "scanned_qr_id" not in st.session_state:
    st.session_state.scanned_qr_id = None

# Free public Google STUN server configuration to resolve connection timeouts over the internet
RTC_CONFIGURATION = RTCConfiguration(
    {
        "iceServers": [
            {"urls": ["stun:stun.l.google.com:19302"]},
            {"urls": ["stun:stun1.l.google.com:19302"]},
            {"urls": ["stun:stun2.l.google.com:19302"]},
            # Free reliable TURN servers from Open Relay Project as a fallback tunnel
            {
                "urls": ["turn:openrelay.metered.ca:80", "turn:openrelay.metered.ca:443"],
                "username": "openrelayproject",
                "credential": "openrelayproject"
            }
        ]
    }
)


def video_frame_callback(frame):
    """
    Decodes QR codes from each video frame.
    """
    img = frame.to_ndarray(format="bgr24")
    data, bbox, straight_qrcode = qr_decoder.detectAndDecode(img)

    if data:
        with lock:
            st.session_state.scanned_qr_id = data

    return frame


options = ("Verify using QR Code Scanner","Verify Certificate using PDF","View/Verify Certificate using Certificate ID")
selected = st.selectbox("", options, label_visibility="hidden")

if selected == options[0]: # Verify using QR Code Scanner
    st.subheader("Instant QR Code Scanner")
    st.write("Take a quick photo of the QR code using your device camera.")

    # 🌟 INSTANT FIX: Uses native camera API instead of firewall-blocked WebRTC streams
    img_file = st.camera_input("Scan Certificate QR", label_visibility="collapsed")

    if img_file is not None:
        import numpy as np
        
        # Read the image bytes directly into OpenCV
        file_bytes = np.frombuffer(img_file.getvalue(), np.uint8)
        img_np = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        # Decode the image instantly
        data, bbox, straight_qrcode = qr_decoder.detectAndDecode(img_np)

        if data:
            st.session_state.scanned_qr_id = data
            st.success("🎯 QR Code captured successfully!")
        else:
            st.error("Could not read a valid QR code from this picture.")
            st.info("Suggestion: Hold the camera steady, ensure the QR code is centered, and take another photo.")

    # Smart Contract Validation Logic
    if st.session_state.scanned_qr_id:
        st.write("Extracted Certificate ID:")
        st.code(st.session_state.scanned_qr_id, language=None)

        try:
            # Smart Contract Call
            result = contract.functions.isVerified(st.session_state.scanned_qr_id).call()
            if result:
                st.success("✅ Certificate validated successfully against the Blockchain record!")
            else:
                st.error("Verification Failed: This record on the blockchain is marked as invalid.")
                
        except Exception as e:
            st.error("Error: The data from this QR code does not correspond to a valid entry on the blockchain.")

        if st.button("Scan Another Certificate"):
            st.session_state.scanned_qr_id = None
            st.rerun()

elif selected == options[1]:
    uploaded_file = st.file_uploader("Upload the PDF version of the certificate")
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        with open("certificate.pdf", "wb") as file:
            file.write(bytes_data)
        try:
            (uid, candidate_name, course_name, org_name) = extract_certificate("certificate.pdf")
            displayPDF("certificate.pdf")
            os.remove("certificate.pdf")

            # Calculating hash
            data_to_hash = f"{uid}{candidate_name}{course_name}{org_name}".encode('utf-8')
            certificate_id = hashlib.sha256(data_to_hash).hexdigest()

            try:
                result = contract.functions.isVerified(certificate_id).call()
                if result:
                    st.success("Certificate validated successfully!")
                else:
                    st.error("Verification Failed: The data in this PDF does not match the blockchain record. The document may have been tampered with or is outdated.")
                    st.info("Suggestion: Please ensure you are using the official, unmodified PDF provided by the institute.")
            except Exception as e:
                st.error("Error: This certificate could not be found on the blockchain.")
                st.info("Suggestion: Please check if you have uploaded the correct document.")

        except Exception as e:
            st.error("File Error: Could not read the required information from this PDF.")
            st.info("Suggestion: The uploaded file does not appear to be a valid certificate. Please upload the official certificate PDF, which should contain a UID, Name, Course Name, and Organization Name.")
            

elif selected == options[2]:
    form = st.form("Validate-Certificate")
    certificate_id = form.text_input("Enter the Certificate ID")
    submit = form.form_submit_button("Validate")
    if submit:
        try:
            certificate_details = contract.functions.getCertificate(certificate_id).call()
    
            if certificate_details and certificate_details[0]:
                view_certificate(certificate_id)
                st.success("Certificate details found and displayed.")
        
                is_valid = contract.functions.isVerified(certificate_id).call()
                if is_valid:
                    st.success("Certificate is verified and valid.")
                else:
                    st.error("Verification Failed: The certificate exists but is currently marked as invalid.")
                    st.info("Suggestion: Please contact the issuing organization for more information regarding the status of this certificate.")
            else:
                st.error("Error: No certificate found with the provided ID.")

        except Exception as e:
            st.error("Error: No certificate found with the provided ID.")
            st.info("Suggestion: Please double-check the Certificate ID for typos. The ID is a long alphanumeric string.")