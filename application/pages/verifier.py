import streamlit as st
import os
import hashlib
from utils.cert_utils import extract_certificate
from utils.streamlit_utils import view_certificate
from connection import contract
from utils.streamlit_utils import displayPDF, hide_icons, hide_sidebar, remove_whitespaces
import cv2
from streamlit_webrtc import webrtc_streamer
import threading
import time

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
hide_icons()
hide_sidebar()
remove_whitespaces()

# --- Thread-safe storage for the result ---
lock = threading.Lock()
qr_result_container = {"id": None}
qr_decoder = cv2.QRCodeDetector()

def video_frame_callback(frame):
    """
    Decodes QR codes from each video frame.
    """
    img = frame.to_ndarray(format="bgr24")
    data, bbox, straight_qrcode = qr_decoder.detectAndDecode(img)

    with lock:
        if data:
            # Get the first QR code found
            qr_result_container["id"] = data

    return frame


options = ("Verify using QR Code Scanner","Verify Certificate using PDF","View/Verify Certificate using Certificate ID")
selected = st.selectbox("", options, label_visibility="hidden")

if selected == options[0]: # Verify using QR Code Scanner
    st.subheader("Live QR Code Scanner")
    st.write("Place the QR code in front of your camera.")

    webrtc_ctx = webrtc_streamer(
        key="qr-scanner",
        video_frame_callback=video_frame_callback,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )

    # Wait for a result and display it
    if webrtc_ctx.state.playing:
        while True:
            with lock:
                if qr_result_container["id"]:
                    st.success("QR Code detected!")
                    st.write("Extracted Certificate ID:")
                    st.code(qr_result_container["id"], language=None)

                    try:
                        # Smart Contract Call
                        result = contract.functions.isVerified(qr_result_container["id"]).call()
                        if result:
                            st.success("Certificate validated successfully!")
                        else:
                            # This error means the ID was found, but the certificate is invalid.
                            st.error("Verification Failed: The certificate record on the blockchain is marked as invalid or has been tampered with.")
                            st.info("Suggestion: Please ensure you are using the latest version of the certificate. If the issue persists, contact the issuing organization.")

                    except Exception as e:
                        # This error means the ID from the QR code was not found on the blockchain.
                        st.error("Error: The data from this QR code does not correspond to a valid certificate on the blockchain.")
                        st.info("Suggestion: Please scan the official QR code located on the top-right corner of the certificate PDF.")

                    # Reset for next scan and stop the loop
                    qr_result_container["id"] = None
                    break
            time.sleep(0.5)

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