import streamlit as st
import time

# Hide the sidebar menu and set wide layout
st.set_page_config(initial_sidebar_state="collapsed",layout="wide")

# Redirect to home page
time.sleep(0.1)  # Small delay to ensure page config is applied
st.switch_page("pages/home.py")
