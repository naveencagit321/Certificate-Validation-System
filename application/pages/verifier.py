import streamlit as st
import cv2
import os
import numpy as np
from connection import contract
from utils.streamlit_utils import hide_icons, hide_sidebar, remove_whitespaces

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
hide_icons()
hide_sidebar()
remove_whitespaces()

# ─── FIXED LEFT-ALIGNED NAVIGATION HEADER ───
nav_col1, nav_col2, nav_col3 = st.columns([1.5, 6.5, 2])

with nav_col1:
    if st.button("Home", use_container_width=True):
        st.switch_page("app.py")

with nav_col2:
    st.markdown("<h2 style='margin-top: -10px;'>🔍 Verifier Verification Portal</h2>", unsafe_allow_html=True)

st.write("---")

if "scanned_qr_id" not in st.session_state:
    st.session_state.scanned_qr_id = None

qr_decoder = cv2.QRCodeDetector()

# ─── NO SELECTOR MENU ─── Jumps straight to the scanner layout:
cam_pad_l, cam_core, cam_pad_r = st.columns([1, 4, 1])

with cam_core:
    st.subheader("Instant QR Code Scanner")
    st.write("Take a quick photo of the QR code using your device camera.")
    img_file = st.camera_input("Scan Certificate QR", label_visibility="collapsed")

if img_file is not None:
    file_bytes = np.frombuffer(img_file.getvalue(), np.uint8)
    img_np = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    data, bbox, straight_qrcode = qr_decoder.detectAndDecode(img_np)

    if data:
        st.session_state.scanned_qr_id = data
        st.success("QR Code captured successfully!")
    else:
        st.error("Could not read a valid QR code from this picture.")

if st.session_state.scanned_qr_id:
    st.write("Extracted Certificate ID:")
    st.code(st.session_state.scanned_qr_id, language=None)

    try:
        result = contract.functions.isVerified(st.session_state.scanned_qr_id).call()
        if result:
            st.success("Certificate validated successfully against the Blockchain record!")
        else:
            st.error("Verification Failed: This record on the blockchain is marked as invalid.")
    except Exception as e:
        st.error("Error: The data from this QR code does not correspond to a valid entry on the blockchain.")

    if st.button("Scan Another Certificate"):
        st.session_state.scanned_qr_id = None
        st.rerun()