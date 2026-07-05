import streamlit as st
from utils.streamlit_utils import hide_icons, hide_sidebar, remove_whitespaces

# ─── STREAMLIT PAGE CONFIGURATION ───
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
hide_icons()
hide_sidebar()
remove_whitespaces()

# ─── MAIN LANDING HEADER ───
st.markdown("<h1 style='text-align: center; margin-top: 50px; margin-bottom: 10px;'>🎓 Certificate Validation System</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #a1a1a1; margin-bottom: 50px;'>Select a portal role to experience the DApp live</h4>", unsafe_allow_html=True)
st.write("---")

# ─── CLEAN INTERACTIVE SELECTION GRID ───
# Creates balanced padding columns to center our buttons nicely on the screen
pad_l, col1, spacer, col2, pad_r = st.columns([2, 3, 1, 3, 2])

with col1:
    # A sleek card-like description box for the Institute
    st.markdown(
        """
        <div style='text-align: center; padding: 20px; border: 1px solid #464855; border-radius: 10px; background-color: #1e2029; margin-bottom: 15px;'>
            <h3 style='margin: 0; color: #ffffff;'>Institute Portal</h3>
            <p style='color: #a1a1a1; font-size: 14px; margin-top: 8px;'>Issue secure certificates and anchor their footprints to the blockchain.</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    if st.button("Enter Institute Dashboard", use_container_width=True, key="btn_goto_institute"):
        st.switch_page("pages/institute.py")

with col2:
    # A sleek card-like description box for the Verifier
    st.markdown(
        """
        <div style='text-align: center; padding: 20px; border: 1px solid #464855; border-radius: 10px; background-color: #1e2029; margin-bottom: 15px;'>
            <h3 style='margin: 0; color: #ffffff;'>Verifier Portal</h3>
            <p style='color: #a1a1a1; font-size: 14px; margin-top: 8px;'>Scan certificate QR codes to instantly verify their authenticity live.</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    if st.button("Enter Verifier Portal", use_container_width=True, key="btn_goto_verifier"):
        st.switch_page("pages/verifier.py")