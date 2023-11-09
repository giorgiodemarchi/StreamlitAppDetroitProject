import streamlit as st

def check_credentials(username, password):
    # Get user credentials from Streamlit secrets
    user_credentials = st.secrets["users"]
    
    # Check if the username exists and the password matches
    return user_credentials.get(username) == password