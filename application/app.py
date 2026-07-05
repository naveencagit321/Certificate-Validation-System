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
# Balanced layout grid structure
pad_l, col1, spacer, col2, pad_r = st.columns([1.5, 3.5, 1, 3.5, 1.5])

with col1:
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    
    # 🌟 RESPONSIVE IMAGE: width: 80% dynamically scales down on mobile, max-width keeps it perfect on PC
    st.markdown(
        r'<a href="/institute" target="_self">'
        r'<img src="app/static/assets/institute_logo.png" style="width: 80%; max-width: 200px; border-radius: 10px; cursor: pointer;">'
        r'</a>', 
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.write("") 
    st.markdown(
        r'<div style="text-align: center; margin-top: 10px;">'
        r'<a href="/institute" target="_self" style="text-decoration: none; display: inline-block; background-color: #262730; color: white; padding: 8px 16px; border-radius: 8px; border: 1px solid #464855; font-size: 14px;">🏫 Institute Dashboard</a>'
        r'</div>',
        unsafe_allow_html=True
    )

with col2:
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    
    # 🌟 RESPONSIVE IMAGE: Dynamic scale configuration
    st.markdown(
        r'<a href="/verifier" target="_self">'
        r'<img src="app/static/assets/company_logo.jpg" style="width: 80%; max-width: 200px; border-radius: 10px; cursor: pointer;">'
        r'</a>', 
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.write("") 
    st.markdown(
        r'<div style="text-align: center; margin-top: 10px;">'
        r'<a href="/verifier" target="_self" style="text-decoration: none; display: inline-block; background-color: #262730; color: white; padding: 8px 16px; border-radius: 8px; border: 1px solid #464855; font-size: 14px;">🔍 Verifier Portal</a>'
        r'</div>',
        unsafe_allow_html=True
    )