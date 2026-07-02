import streamlit as st
from db.firebase_app import register
from utils.streamlit_utils import hide_icons, hide_sidebar, remove_whitespaces

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
hide_icons()
hide_sidebar()
remove_whitespaces()

# --- Initialize session state if it doesn't exist ---
if "profile" not in st.session_state:
    st.session_state.profile = "Verifier" # Fallback default

# --- Use a 'with' block for the form ---
with st.form("register_form"):
    email = st.text_input("Enter your email")
    password = st.text_input("Enter your password", type="password")
    submit = st.form_submit_button("Register")

# Place the login redirect button OUTSIDE the form block
clicked_login = st.button("Already registered? Click here to login!")

if clicked_login:
    # UPDATED PATH
    st.switch_page("pages/login.py")
    
if submit:
    result = register(email, password)
    if result == "success":
        st.success("Registration successful!")
        if st.session_state.profile == "Institute":
            # UPDATED PATH
            st.switch_page("pages/institute.py")
        else:
            # UPDATED PATH
            st.switch_page("pages/verifier.py")
    else:
        st.error("Registration unsuccessful!")