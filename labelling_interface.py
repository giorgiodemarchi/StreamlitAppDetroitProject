import streamlit as st
import os
import pandas as pd
from images_handling import generate_images

def save_label(images, label, metadata):
    """
    Function to store the images
    """
    
    angle = metadata['angle']
    p = metadata['p']
    latitude = metadata['latitude']
    longitude = metadata['longitude']
    address = metadata['address']
    headings = metadata['headings']


    # Save the observation of first side (images + metadata)
    new_path = f"Data\DetroitImageDataset_v2\{p}_{angle}_{latitude}_{longitude}" 
    # For one image dataset
    one_path = f"Data\DetroitImageDataset_SingleImage_v2\{p}_{angle}_{latitude}_{longitude}" 

    if not os.path.exists(new_path) and not os.path.exists(one_path):
        os.makedirs(new_path)
        os.makedirs(one_path)

        # Save images
        for idx, img in enumerate(images):
            # Save the central one to the one image dataset
            if idx == 2:
                img.save(f"{one_path}\image_{idx}.png")

            # All of them to the 5 images dataset
            img.save(f"{new_path}\image_{idx}.png")
        
        # Save Metadata
        with open(f"{new_path}\metadata.txt", "w") as f:
            f.write(f"""Latitude: {latitude}\nLongitude: {longitude}
                    \nHeadings: {headings}
                    \nAddress: {address}\nLabel: {str(label)}""")
            
        # Save Metadata on one image dataset
        with open(f"{one_path}\metadata.txt", "w") as f:
            f.write(f"""Latitude: {latitude}\nLongitude: {longitude}
                    \nHeadings: {headings}
                    \nAddress: {address}\nLabel: {str(label)}""")

def label_page():
    # Get API key
    api_key_path = "api_key.txt"
    with open(api_key_path) as file:
        api_key = str(file.read())

    # Read Location Sampling
    points_df = pd.read_csv("Data/LocationSamplingDataset/DowntownDetroitPointsDataset_v2.csv", index_col=0)

    # Define parameters for Google Maps call
    image_size = "640x480"

    # STREAMLIT APP CORE
    st.set_page_config(layout="wide")
    st.title("Labeling Interface - EV Charging Stations Project")

    if 'data_points' not in st.session_state:
        st.session_state.data_points = []

    if 'labels' not in st.session_state:
        st.session_state.labels = []

    if 'metadata' not in st.session_state:
        st.session_state.metadata = []

    if st.markdown('<style>div.row-widget.stButton > button { width: 200px; height: 50px; font-size: 1.5em; }</style>', unsafe_allow_html=True):
        if st.button("Generate"):
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
        for images, label, metadata_image in zip(st.session_state.data_points, st.session_state.labels, st.session_state.metadata):
            if label:
                label_digit = ''.join(filter(str.isdigit, label))
                save_label(images, label_digit, metadata_image)
                st.success(f"Images and label saved successfully!")

        # Reset session state after submission
        st.session_state.data_points = []
        st.session_state.labels = []

