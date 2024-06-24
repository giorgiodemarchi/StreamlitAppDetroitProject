import pandas as pd
import boto3 
from io import StringIO, BytesIO
import io
import streamlit as st
from datetime import datetime
from PIL import Image 

def download_datapoint(folder):
    """
    Given a ID/folder name, returns images and metadat

    """

    s3_client = boto3.client('s3',
                        aws_access_key_id=st.secrets["aws_access_key_id"],
                        aws_secret_access_key=st.secrets["aws_secret_access_key"])

    path = f"GoogleDetroitDatabase/{folder}"

    # Metadata
    point_id, angle, lat, lon = folder.split("_")
    metadata = {
        'p': point_id,
        'angle': angle,
        'latitude': lat,
        'longitude': lon
    }

    # Read images and store them
    images = []
    for i in range(5):
        image_key = f"{path}/image_{i}.png"
        image_obj = s3_client.get_object(Bucket='detroit-project-data-bucket', Key=image_key)
        image = Image.open(io.BytesIO(image_obj['Body'].read()))
        images.append(image)

    return images, metadata

def extract_images():
    """
    - Reads active learning tracking dataset
    - Reads the next image to label
    - Downloads the image to label
    - Returns Images and metadata
    """

    al_tracking_path = 'LocationSamplingDataset/close_nhoods_prediction.csv'
    tracking = read_location_sampling(file_key=al_tracking_path)

    tracking = tracking[tracking['label']==5] ## Flag for unlabelled data
    # take the most uncertain datapoint as per model prediction (uncertainty based active learning)
    to_label = tracking.sort_values('certainty', ascending=True).iloc[0]

    folder_id = to_label['folder_id']

    images, metadata = download_datapoint(folder_id)

    return [images], [metadata]

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

def read_location_sampling(file_key = 'LocationSamplingDataset/DowntownDetroitPointsDataset_v2.csv'):
    """
    Input: None
    Output: Dataframe with location sampling dataset
    """

    s3_client = boto3.client('s3',
                         aws_access_key_id=st.secrets["aws_access_key_id"],
                         aws_secret_access_key=st.secrets["aws_secret_access_key"])


    bucket_name = 'detroit-project-data-bucket'
    #file_key = 'LocationSamplingDataset/DowntownDetroitPointsDataset_v2.csv'

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

def load_data(bucket_name, dataset_prefix):
    """
    Load data from S3 bucket
    """
    # Initialize boto3 client
    s3 = boto3.client('s3', aws_access_key_id=st.secrets["aws_access_key_id"], aws_secret_access_key=st.secrets["aws_secret_access_key"])

    # Initialize lists to store data
    ids = []
    angles = []
    latitudes = []
    longitudes = []
    labels = []
    image_numbers = []
    images = []
    addresses = []
    labellers = []

    # List objects within a given prefix
    folders = get_folder_names()

    for datapoint in folders:
        path = f"{dataset_prefix}{datapoint}"

        point_id, angle, lat, lon = datapoint.split("_")

        # Read metadata
        metadata_file = f"{path}/metadata.txt"
        metadata_obj = s3.get_object(Bucket=bucket_name, Key=metadata_file)
        metadata_content = metadata_obj['Body'].read().decode('latin-1')
        metadata = {}
        for content in metadata_content.splitlines():
            if ":" in content:
                data_name = content.split(":")[0]
                data_value = content.split(":")[1]
                metadata[data_name] = data_value
        

        # Read images and store them
        for i in range(5):
            image_key = f"{path}/image_{i}.png"
            image_obj = s3.get_object(Bucket='detroit-project-data-bucket', Key=image_key)
            image = Image.open(io.BytesIO(image_obj['Body'].read()))

            # Append data to lists
            ids.append(point_id)
            angles.append(angle)
            latitudes.append(lat)
            longitudes.append(lon)
            labels.append(metadata['Label'])
            image_numbers.append(i)
            images.append(image)
            addresses.append(metadata['Address'])
            if 'Labeller username' in metadata.keys():
                labellers.append(metadata['Labeller username'])
            else:
                labellers.append("Unknown")
                
            
    # Create a DataFrame
    data = {
        "id": ids,
        "angle": angles,
        "latitude": latitudes,
        "longitude": longitudes,
        "label": labels,
        "image_number": image_numbers,
        "image": images,
        "address": addresses,
        "labeller": labellers
    }

    df = pd.DataFrame(data)
    
    return df

def update_active_learning_csv(folder, label):
    """
    Update active learning tracking csv with the new label
    """
    s3_client = boto3.client('s3',
                         aws_access_key_id=st.secrets["aws_access_key_id"],
                         aws_secret_access_key=st.secrets["aws_secret_access_key"])

    al_tracking_path = 'LocationSamplingDataset/close_nhoods_prediction.csv'
    al_tracking = read_location_sampling(file_key=al_tracking_path)

    al_tracking.loc[al_tracking['folder_id']==folder, 'label'] = label

    csv_buffer = StringIO()
    al_tracking.to_csv(csv_buffer, index=False)
    s3_client.put_object(Bucket='detroit-project-data-bucket', Key=al_tracking_path, Body=csv_buffer.getvalue())

def save_label_activelearning(label, metadata):
    """
    
    """
    angle = metadata['angle']
    p = metadata['p']
    latitude = metadata['latitude']
    longitude = metadata['longitude']

    folder_name = f"{p}_{angle}_{latitude}_{longitude}"

    update_active_learning_csv(folder_name, label)

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



            