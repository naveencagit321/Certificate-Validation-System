import streamlit as st
from db.firebase_app import login
from dotenv import load_dotenv
import os
from utils.streamlit_utils import hide_icons, hide_sidebar, remove_whitespaces

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
hide_icons()
hide_sidebar()
remove_whitespaces()

load_dotenv()

# --- FIX 1: Initialize session state if it doesn't exist ---
if "profile" not in st.session_state:
    st.session_state.profile = "Verifier" # Fallback default

# --- FIX 2: Use a 'with' block for the form ---
with st.form("login_form"):
    email = st.text_input("Enter your email")
    password = st.text_input("Enter your password", type="password")
    submit = st.form_submit_button("Login")

# Place the register button OUTSIDE the form block
if st.session_state.profile != "Institute":
    clicked_register = st.button("New user? Click here to register!")
    if clicked_register:
        st.switch_page("pages/register.py")

# Handle the login logic after the form is submitted
if submit:
    if st.session_state.profile == "Institute":
        valid_email = os.getenv("institute_email")
        valid_pass = os.getenv("institute_password")
        if email == valid_email and password == valid_pass:
            st.switch_page("pages/institute.py")
        else:
            st.error("Invalid credentials!")
    else:
        result = login(email, password)
        if result == "success":
            st.success("Login successful!")
            st.switch_page("pages/verifier.py")
        else:
            st.error("Invalid credentials!")