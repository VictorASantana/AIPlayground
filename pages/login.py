#import os
#import streamlit as st
#from dotenv import load_dotenv
#import sys
#import os

#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#from services.auth import Authenticator

#load_dotenv()

# Initialize session state variables if they don't exist
#if "connected" not in st.session_state:
#    st.session_state["connected"] = False
#if "user_info" not in st.session_state:
#    st.session_state["user_info"] = None
#if "logout" not in st.session_state:
#    st.session_state["logout"] = False

# emails of users that are allowed to login
#allowed_users = os.getenv("ALLOWED_USERS").split(",")

#st.title("Streamlit Google Auth")

#authenticator = Authenticator(
#    allowed_users=allowed_users,
#    token_key=os.getenv("TOKEN_KEY"),
#    secret_path="client_secret.json",
#    redirect_uri="http://localhost:8501",
#)
#authenticator.check_auth()
#authenticator.login()
# show content that requires login
#if st.session_state["connected"]:
#    st.write(f"welcome! {st.session_state['user_info'].get('email')}")
#    home, logout = st.columns(2)
#    with home:
#        if st.button("Home"):
#            st.switch_page("pages/home.py")
#    with logout:
#        if st.button("Log out"):
#            authenticator.logout()

#if not st.session_state["connected"]:
#    st.write("you have to log in first ...")