import streamlit as st
from PIL import Image
from utils.streamlit_utils import hide_icons, hide_sidebar, remove_whitespaces
from pathlib import Path


st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
hide_icons()
hide_sidebar()
remove_whitespaces()


st.title("Certificate Validation System")
st.write("")
st.subheader("Select Your Role")

from pathlib import Path

# 1. Dynamically locate the directory where app.py lives
current_dir = Path(__file__).parent.resolve()
root_dir = current_dir.parent

col1, col2 = st.columns(2)

# Fix paths using the robust pathlib setup
institute_logo_path = root_dir / "assets" / "institute_logo.png"
institite_logo = Image.open(institute_logo_path)

with col1:
    st.image(institite_logo, output_format="jpg", width=230)
    clicked_institute = st.button("Institute")

company_logo_path = root_dir / "assets" / "company_logo.jpg"
company_logo = Image.open(company_logo_path)

with col2:
    st.image(company_logo, output_format="jpg", width=230)
    clicked_verifier = st.button("Verifier")

if clicked_institute:
    st.session_state.profile = "Institute"
    # Streamlit multi-page apps look inside the "pages" folder automatically 
    st.switch_page("pages/login.py")
elif clicked_verifier:
    st.session_state.profile = "Verifier"
    st.switch_page("pages/login.py")