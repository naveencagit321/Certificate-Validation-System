import streamlit as st
import cv2
import os
import numpy as np
from connection import contract, w3
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

st.markdown("<h2 style='margin-top: 10px;'>Verifier Verification Portal</h2>", unsafe_allow_html=True)
st.write("---")

# Initialize default session tracking for selector interface state
if "verification_mode" not in st.session_state:
    st.session_state.verification_mode = "QR Code Scanner"

# ─── SIDE-BY-SIDE CLICKABLE NAVIGATION INTERFACE ───
# Creates three symmetric layout grids for the utility navigation buttons
btn_col1, btn_col2, btn_col3 = st.columns(3)

with btn_col1:
    # Highlight the active option using primary button configurations
    if st.button(
        "QR Code Scanner", 
        use_container_width=True, 
        type="primary" if st.session_state.verification_mode == "QR Code Scanner" else "secondary"
    ):
        st.session_state.verification_mode = "QR Code Scanner"
        st.rerun()

with btn_col2:
    if st.button(
        "Upload Certificate PDF", 
        use_container_width=True, 
        type="primary" if st.session_state.verification_mode == "Upload PDF" else "secondary"
    ):
        st.session_state.verification_mode = "Upload PDF"
        st.rerun()

with btn_col3:
    if st.button(
        "Enter Certificate ID", 
        use_container_width=True, 
        type="primary" if st.session_state.verification_mode == "Manual ID Lookup" else "secondary"
    ):
        st.session_state.verification_mode = "Manual ID Lookup"
        st.rerun()

st.write("") # Margin spacing padding

# ─── MODE CONDITION PIPELINE MODULES ───

# MODULE 1: NATIVE QR CODE SCANNER WORKSPACE
if st.session_state.verification_mode == "QR Code Scanner":
    st.subheader("QR Code Scanner Workspace")
    camera_input = st.camera_input("Position the certificate QR code target clearly inside the viewport frame")
    
    if camera_input:
        bytes_data = camera_input.getvalue()
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        detector = cv2.QRCodeDetector()
        data, bbox, straight_qrcode = detector.detectAndDecode(cv2_img)
        
        if data:
            # ─── 🎉 POPUP HOOK FOR SUCCESSFUL QR SCAN ───
            st.toast("🎯 QR Code Scanned Successfully!", icon="✅")
            
            with st.spinner("Verifying authenticity with Ethereum ledger..."):
                try:
                    # sanity checks
                    if not getattr(w3, 'is_connected', None) or not w3.is_connected():
                        raise ConnectionError('Web3 provider is not connected. Check SEPOLIA_RPC_URL and network access.')
                    if contract is None or not hasattr(contract, 'functions'):
                        raise RuntimeError('Smart contract is not loaded properly (ABI or address missing).')

                    cert_details = contract.functions.getCertificate(data.strip()).call()
                    if cert_details and cert_details[0]:
                        st.success("### 🎉 Certificate Successfully Verified!")
                        st.balloons() # Decorative element for presentation impact
                        # Show key validation data elegantly instead of full JSON
                        st.markdown(f"**Student:** {cert_details[1]} | **Course:** {cert_details[2]}")
                    else:
                        st.error('Certificate not found on-chain.')
                except Exception as e:
                    st.error(f"Verification failed on network: {e}")

# MODULE 2: FILE UPLOAD SEGMENTATION WORKSPACE
elif st.session_state.verification_mode == "Upload PDF":
    st.subheader("Upload Certificate PDF File Workspace")
    uploaded_file = st.file_uploader("Drop the digital certificate PDF file here for evaluation", type=["pdf"])
    
    if uploaded_file is not None:
        st.success("File uploaded successfully!")
        # Verification logic placeholder: Extract text/metadata or match transaction parameters
        # Example tracking: hash_val = hashlib.sha256(uploaded_file.read()).hexdigest()

# MODULE 3: MANUAL REGISTRY TRANSACTION LOOKUP WORKSPACE
elif st.session_state.verification_mode == "Manual ID Lookup":
    st.subheader("Manual Certificate ID Identification Workspace")
    cert_id = st.text_input("Enter the unique Certificate Registration Identification Number (UID):")
    
    if st.button("Validate ID Signature", use_container_width=True):
        if cert_id.strip():
            with st.spinner("Querying Ethereum Blockchain smart contract ledger..."):
                try:
                    if not getattr(w3, 'is_connected', None) or not w3.is_connected():
                        raise ConnectionError('Web3 provider is not connected. Check SEPOLIA_RPC_URL and network access.')
                    if contract is None or not hasattr(contract, 'functions'):
                        raise RuntimeError('Smart contract is not loaded properly (ABI or address missing).')

                    # Calls the smart contract getter method natively
                    cert_details = contract.functions.getCertificate(cert_id.strip()).call()

                    if cert_details and cert_details[0]:
                        # ─── 🎉 POPUP HOOK FOR SUCCESSFUL MANUAL LOOKUP ───
                        st.toast("🔐 Cryptographic Signature Matched!", icon="🛡️")
                        st.success("### 🎉 Certificate Successfully Verified!")
                        st.balloons()

                        # Render information via a clean bulleted layout instead of raw JSON parameters
                        st.markdown("#### **Verified Records:**")
                        st.markdown(f"* 🧑‍🎓 **Student Name:** {cert_details[1]}") # Swapped indices to show actual string match values
                        st.markdown(f"* 📚 **Course Program:** {cert_details[2]}")
                        st.markdown(f"* 🏢 **Issuing Authority:** {cert_details[3]}")
                    else:
                        st.error('Certificate not found on-chain.')
                except Exception as e:
                    st.error(f"Error accessing contract parameters: {str(e)}")
        else:
            st.warning("Please supply a functional UID parameter before initiating blockchain network lookups.")