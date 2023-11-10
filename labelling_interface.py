import streamlit as st
import pandas as pd


from images_handling import generate_images
from dataset import read_location_sampling, save_label

def label_page():
    # Get API key
    api_key = st.secrets["google_api_key"]

    # Read Location Sampling
    points_df = read_location_sampling()
    # Define parameters for Google Maps call
    image_size = "640x480"

    # STREAMLIT APP CORE
    st.set_page_config(layout="wide")

    st.title("Labeling Interface - EV Charging Stations Project")
    st.markdown(""" ## Labeling Guidelines
Please follow the guidelines below to ensure accurate labeling:

- **Feasibility**: Assess if each image depicts a feasible location for an EV charging station.
- **Uncertainty**: If unsure, use the 'unsure' codes to reflect this.
- **Consistency**: Apply the labeling codes consistently across similar images.
- **Quality Check**: Report any images that are unclear or not visible as 'Bad Data'.

Remember, accurate labels help improve the quality of our project data.""")
    
    st.markdown('---')

    if 'data_points' not in st.session_state:
        st.session_state.data_points = []

    if 'labels' not in st.session_state:
        st.session_state.labels = []

    if 'metadata' not in st.session_state:
        st.session_state.metadata = []

    if st.markdown('<style>div.row-widget.stButton > button { width: 200px; height: 50px; font-size: 1.5em; }</style>', unsafe_allow_html=True):
        if st.button("Generate New Datapoints"):
            st.session_state.data_points, st.session_state.metadata = generate_images(points_df, api_key, image_size)

    if st.session_state.data_points:
        for idx, images in enumerate(st.session_state.data_points):
            if idx > 0:
                st.markdown("---")

            st.subheader(f"Side {idx + 1}")

            label_options = ["Infeasible (code: 0)",
                             "Feasible (code: 1)",
                             "Infeasible but unsure (code: 2)",
                             "Feasible but unsure (code: 3)",
                             "Bad Data (code: 4)"]

            image_columns = st.columns(5)
            for col, image in zip(image_columns, images):
                col.image(image, use_column_width=True)

            label = st.radio(f"Please select the most appropriate label for the above images.", label_options, key=f"label{idx}")

            if idx >= len(st.session_state.labels):
                st.session_state.labels.append(label)
            else:
                st.session_state.labels[idx] = label

    if st.session_state.data_points and st.button("Save Labels and Continue"):
        username = st.session_state.get('user', 'Unknown')
        for images, label, metadata_image in zip(st.session_state.data_points, st.session_state.labels, st.session_state.metadata):
            if label:
                label_digit = ''.join(filter(str.isdigit, label))
                save_label(images, label_digit, metadata_image, username)
                st.success(f"Images and label saved successfully!")

        # Reset session state after submission
        st.session_state.data_points = []
        st.session_state.labels = []