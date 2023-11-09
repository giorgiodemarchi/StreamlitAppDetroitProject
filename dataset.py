import pandas as pd
import boto3 
from io import StringIO, BytesIO
import streamlit as st
from datetime import datetime

def get_folder_names():
    """
    Connect to S3 and read all folder (datapoints) names in the images dataset
    """
    s3_client = boto3.client('s3',
                         aws_access_key_id=st.secrets["aws_access_key_id"],
                         aws_secret_access_key=st.secrets["aws_secret_access_key"])


    bucket_name = 'detroit-project-data-bucket'
    directory_name = 'DetroitImageDataset_v2/'

    paginator = s3_client.get_paginator('list_objects_v2')
    response_iterator = paginator.paginate(
        Bucket=bucket_name,
        Prefix=directory_name,
        Delimiter='/'
    )

    folder_names = []
    for response in response_iterator:
        if response.get('CommonPrefixes') is not None:
            for prefix in response.get('CommonPrefixes'):
                # Extract the folder name from the prefix key
                folder_name = prefix.get('Prefix')
                # Removing the base directory and the trailing slash to get the folder name
                folder_name = folder_name[len(directory_name):].strip('/')
                folder_names.append(folder_name)

    return folder_names


def already_in_dataset(coordinates):
    """
    Check if coordinate point is already in dataset

    Input: Coordinates (lat, lon) --Tuple
    Output: Boolean TRUE/FALSE
    
    """
    coords_stored = []
    items = get_folder_names() 
    if len(items)>0:
        for item in items:
            lat = item.split("_")[2]
            lon = item.split("_")[3]
            coords_stored.append((lat, lon))
    else:
        return 0

    if coordinates in coords_stored:
        return 1
    else:
        return 0
    
def get_indexes_in_dataset():
    """ 
    Input: None
    Output: List of indexes already in dataset
    """
    items = get_folder_names()
    indexes = []
    for item in items:
        idx = item.split("_")[0]
        indexes.append(idx)

    return indexes


def read_location_sampling():
    """
    Input: None
    Output: Dataframe with location sampling dataset
    """

    s3_client = boto3.client('s3',
                         aws_access_key_id=st.secrets["aws_access_key_id"],
                         aws_secret_access_key=st.secrets["aws_secret_access_key"])


    bucket_name = 'detroit-project-data-bucket'
    file_key = 'LocationSamplingDataset/DowntownDetroitPointsDataset_v2.csv'

    obj = s3_client.get_object(Bucket=bucket_name, Key=file_key)

    data = obj['Body'].read().decode('utf-8')

    df = pd.read_csv(StringIO(data))

    return df

def read_tracking_data():
    """
    Input: None
    Output: Dataframe with tracking data from S3
    """

    s3_client = boto3.client('s3',
                         aws_access_key_id=st.secrets["aws_access_key_id"],
                         aws_secret_access_key=st.secrets["aws_secret_access_key"])


    bucket_name = 'detroit-project-data-bucket'
    file_key = 'tracking_df.csv'

    obj = s3_client.get_object(Bucket=bucket_name, Key=file_key)

    data = obj['Body'].read().decode('utf-8')

    df = pd.read_csv(StringIO(data))

    return df

def save_tracking_dataset(df):

    pass
    
def save_label(images, label, metadata, username):
    """
    Function to store the images
    """
    s3_client = boto3.client('s3',
                         aws_access_key_id=st.secrets["aws_access_key_id"],
                         aws_secret_access_key=st.secrets["aws_secret_access_key"])

    bucket_name = 'detroit-project-data-bucket'


    angle = metadata['angle']
    p = metadata['p']
    latitude = metadata['latitude']
    longitude = metadata['longitude']
    address = metadata['address']
    headings = metadata['headings']

    # Save the observation of first side (images + metadata)

    datapoint_id = f"{p}_{angle}_{latitude}_{longitude}"
    base_s3_path = f"DetroitImageDataset_v2/{datapoint_id}"

    for idx, img in enumerate(images):
        # Convert the image to bytes
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()

        # Create a full path for the image
        img_path = f"{base_s3_path}/image_{idx}.png"

        # Upload the image to S3
        s3_client.put_object(Bucket=bucket_name, Key=img_path, Body=img_byte_arr)

    # Prepare metadata text
    metadata_content = f"""Latitude: {latitude}
Longitude: {longitude}
Headings: {headings}
Address: {address}
Label: {label}
Labeller username: {username}"""

    # Save Metadata to a .txt file
    metadata_path = f"{base_s3_path}/metadata.txt"
    s3_client.put_object(Bucket=bucket_name, Key=metadata_path, Body=metadata_content)

    # Update tracking file
    tracking_df = read_tracking_data()
    current_time = datetime.now()
    current_label_df = pd.DataFrame({'username': [username], 'time': [current_time], 'datapoint_id': [datapoint_id], 'label': [label]})

    tracking_df = pd.concat([tracking_df, current_label_df], ignore_index=True)

    tracking_file_key = 'tracking_df.csv'

    csv_buffer = StringIO()
    tracking_df.to_csv(csv_buffer, index=False)
    s3_client.put_object(Bucket=bucket_name, Key=tracking_file_key, Body=csv_buffer.getvalue())



            