import streamlit as st
from utils.streamlit_utils import hide_icons, hide_sidebar, remove_whitespaces

# ─── STREAMLIT PAGE CONFIGURATION ───
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
hide_icons()
hide_sidebar()
remove_whitespaces()

# ─── MAIN LANDING HEADER ───
st.markdown("<h1 style='text-align: center; margin-bottom: 10px;'>🎓 Certificate Validation System</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #a1a1a1; margin-bottom: 40px;'>Select a portal role to experience the DApp live</h4>", unsafe_allow_html=True)
st.write("---")

# ─── INTERACTIVE ROLE SELECTION GRID ───
# Creates balanced padding columns to align the interface beautifully on all screen resolutions
pad_l, col1, spacer, col2, pad_r = st.columns([1, 4, 1, 4, 1])

with col1:
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    # Renders the institution graphic interface component
    st.image("assets/institute_logo.png", width=220)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.write("") # Spacing margin
    if st.button("Institute Dashboard", use_container_width=True, key="go_to_inst"):
        # Switches context directly to the public certificate generation workspace
        st.switch_page("pages/institute.py")

with col2:
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    # Renders the verification company graphic interface component
    st.image("assets/company_logo.jpg", width=220)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.write("") # Spacing margin
    if st.button("Verifier Portal", use_container_width=True, key="go_to_ver"):
        # Switches context directly to the public camera scanner workspace
        st.switch_page("pages/verifier.py")