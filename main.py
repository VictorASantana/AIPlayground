import streamlit as st
import time

# Initialize session state
if "connected" not in st.session_state:
    st.session_state["connected"] = False
if "user_info" not in st.session_state:
    st.session_state["user_info"] = None
if "logout" not in st.session_state:
    st.session_state["logout"] = False

# Hide the sidebar menu and set wide layout
st.set_page_config(
    page_title="Streamlit Auth App",
    initial_sidebar_state="collapsed",
    layout="wide"
)

time.sleep(0.1)  # Small delay to ensure page config is applied
#st.switch_page("pages/login.py")

import os
import streamlit as st
from dotenv import load_dotenv
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.auth import Authenticator

load_dotenv()

# Initialize session state variables if they don't exist
if "connected" not in st.session_state:
    st.session_state["connected"] = False
if "user_info" not in st.session_state:
    st.session_state["user_info"] = None
if "logout" not in st.session_state:
    st.session_state["logout"] = False
if "autenticador" not in st.session_state:
    st.session_state["autenticador"] = None


# emails of users that are allowed to login
allowed_users = os.getenv("ALLOWED_USERS").split(",")

st.title("Instituto Minerva Playground")
if not st.session_state["connected"]:
    st.write("Acesse com o Google para continuar")

authenticator = Authenticator(
    allowed_users=allowed_users,
    token_key=os.getenv("TOKEN_KEY"),
    secret_path="client_secret.json",
    redirect_uri="http://localhost:8501",
)

authenticator.check_auth()
authenticator.login()
# show content that requires login
if st.session_state["connected"]:
    st.write(f"Bem vindo! {st.session_state['user_info'].get('email')}")
    home, logout = st.columns(2)
    with home:
        if st.button("Playground", use_container_width=True):
            st.switch_page("pages/home.py")
    with logout:
        if st.button("Log out", use_container_width=True):
            authenticator.logout()

if authenticator.valido == False:
    st.write(f"Escolha um email autenticado! Caso seu email seja válido, entre em contato com o administrador.")

# Add CSS for centering image and caption
st.markdown("""
    <style>
        [data-testid="stImage"] {
            text-align: center;
            display: block;
            margin-left: auto;
            margin-right: auto;
        }
        
        [data-testid="stImage"] img {
            max-width: 80%;
            margin: auto;
        }
        
        [data-testid="stImage"] div:nth-child(2) {
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# Display centered image
st.image("images/institutominerva_cover.jpg")