import streamlit as st
import random
import time
import requests
import os
import math
import pandas as pd
from random import randrange

# Import from other modules of the app
from labelling_interface import label_page 
from auth import check_credentials

def main():
    st.title("Login Page")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if check_credentials(username, password):
            # Authentication successful
            st.session_state['authenticated'] = True
            st.session_state['user'] = username
            st.success(f"Welcome {username}!")
            # Force a rerun to go to the label page
            st.experimental_rerun()  # This line will cause the script to rerun
        else:
            st.error("Incorrect username or password")

# Check if the user is already authenticated
if 'authenticated' not in st.session_state or not st.session_state['authenticated']:
    main()
else:
    label_page()