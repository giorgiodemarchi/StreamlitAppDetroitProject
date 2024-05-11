import streamlit as st
import pandas as pd


from images_handling import generate_images
from dataset import read_location_sampling, save_label, save_label_activelearning, extract_images

def label_page():
    # Get API key
    api_key = st.secrets["google_api_key"]

    # Define parameters for Google Maps call
    image_size = "640x480"

    # STREAMLIT APP CORE
    st.set_page_config(layout="wide", page_title="MIT ORC - Detroit Project")

    st.title("Labeling Interface - EV Charging Stations Project")
    
    st.markdown('---')
    st.markdown(""" ### Guidelines
The goal of this interface is to label the images as either feasible or infeasible for the installation of an EV charging station. This interface provides, at each request, two datapoints (images) of a location in Detroit. The images are taken from Google Street View and represent the two sides of the street. 


                
We define a location as feasible if it has the following characteristics:
- The location has a sidewalk that is at least 5 feet wide
- The location has a car parking on the side of the street
- There is no fire hydrant or bus stop in the location
- There is no other types of impediment (e.g. tree, bench, etc.) in the location.
                
Given the relatively high complexity of the labelling task, we offer the following labels:

- **Infeasible**: The images provide good visibility and there is no space for an EV charging station.
- **Feasible**: The images provide good visibility and there is clearly space on the sidewalk for an EV charging station.
- **Infeasible but unsure**: The images do not provide good visibility and you are unsure if there is space for an EV charging station, but you believe it is infeasible.
- **Feasible but unsure**: The images do not provide good visibility and you are unsure if there is space for an EV charging station, but you believe it is feasible.
- **Bad Data**: The image is not pointed at a side of a street (e.g. cross of sreets, parking lot, etc.)


Please make sure the images are correctly saved (two green success messages at the bottom of the page) before refreshing new datapoints.""")

    st.markdown('---')

    if 'data_points' not in st.session_state:
        st.session_state.data_points = []

    if 'labels' not in st.session_state:
        st.session_state.labels = []

    if 'metadata' not in st.session_state:
        st.session_state.metadata = []


    if st.markdown('<style>div.row-widget.stButton > button { width: 350px; height: 70px; font-size: 50px; }</style>', unsafe_allow_html=True):
        active_learning = st.toggle('Active Learning', value=True)
        if not active_learning:
            # Read Location Sampling
            points_df = read_location_sampling()

        if st.button("Save and Generate New Datapoints"):
            if st.session_state.data_points: # and st.button("Save Labels and Continue"):
                username = st.session_state.get('user', 'Unknown')
                for images, label, metadata_image in zip(st.session_state.data_points, st.session_state.labels, st.session_state.metadata):
                    if label:
                        label_digit = ''.join(filter(str.isdigit, label))
                        if active_learning:
                            save_label_activelearning(label_digit, metadata_image)
                        else:
                            save_label(images, label_digit, metadata_image, username)
                        #st.success(f"Images and label saved successfully!")

                # Reset session state after submission
                st.session_state.data_points = []
                st.session_state.labels = []

            if active_learning:
                st.session_state.data_points, st.session_state.metadata = extract_images()
            else:
                st.session_state.data_points, st.session_state.metadata = generate_images(points_df, api_key, image_size)


        if st.session_state.data_points:
            for idx, images in enumerate(st.session_state.data_points):
                if idx > 0:
                    st.markdown("---")

                st.subheader(f"Side {idx + 1}")

                label_options = ["Infeasible",
                                "Feasible",
                                "Infeasible but unsure",
                                "Feasible but unsure",
                                "Bad Data"]

                image_columns = st.columns(5)
                for col, image in zip(image_columns, images):
                    col.image(image, use_column_width=True)

                label = st.radio(f"Please select the most appropriate label for the above images.", label_options, key=f"label{idx}")

                if idx >= len(st.session_state.labels):
                    st.session_state.labels.append(label)
                else:
                    st.session_state.labels[idx] = label