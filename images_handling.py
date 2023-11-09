import requests
from PIL import Image 
import io
import random
import math 
import os 

### Import from other modules of the app
from dataset import already_in_dataset

def get_street_view_images(api_key, location, size, headings, pitch=0, fov=90):
    """
    API Call to get Street View images
    
    Cost per 1000 requests: $7
    """
    images = []

    base_url = "https://maps.googleapis.com/maps/api/streetview"
    for heading in headings:
        params = {

            "key": api_key,
            "location": f"{location[0]},{location[1]}",
            "size": size,
            "heading": heading,
            "pitch": pitch,
            "fov": fov,
            "source": "outdoor"
        
        }

        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            image_data = io.BytesIO(response.content)
            images.append(Image.open(image_data))
 
        else:
            print(f"Error fetching image with heading {heading}: {response.status_code}")

    return images


def calculate_orientation(coord1, coord2):
    """
    Compute N-E-S-W Orientation of the street based on two points belonging in it.
    """

    lat1, lon1 = coord1
    lat2, lon2 = coord2
    
    Δλ = lon2 - lon1
    Δφ = lat2 - lat1
    
    # Calculate the angle in radians
    θ = math.atan2(Δλ, Δφ)
    
    # Convert angle to degrees
    θ_deg = θ * (180.0 / math.pi)
    
    # Normalize the angle to be between 0 and 360 degrees
    normalized_angle = (θ_deg + 360) % 360
    
    # Determine cardinal direction
    cardinal_directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    index = int((normalized_angle + 22.5) / 45) % 8
    direction = cardinal_directions[index]

    # Determine the angle at which the street is directed (using the API standards)
    angle_google_api = [0, 45, 90, 135, 180, 225, 270, 315]
    baseline_angle = angle_google_api[index]

    
    return direction, baseline_angle

# A few functions that are necessary to handle angles
def normalize_angle(angle):
    """
    Normalize the angle to be within [0, 360) degrees.
    """
    normalized_angle = angle % 360
    return normalized_angle

def add_angles(angle1, angle2):
    """
    Add two angles, considering the circular nature of angles.
    """
    result = normalize_angle(angle1 + angle2)
    return result

def subtract_angles(angle1, angle2):
    """
    Subtract one angle from another, considering the circular nature of angles.
    """
    result = normalize_angle(angle1 - angle2)
    return result

def generate_unique_random(exclude_numbers, min_value, max_value):
    while True:
        number = random.randint(min_value, max_value)
        if number not in exclude_numbers:
            return number

def generate_images(points_df, api_key, image_size):
    """ 
    Return 5 images
    """

    # Get list of indexes already in dataset
    items = os.listdir("Data\DetroitImageDataset_v2") 
    indexes = []
    for item in os.listdir("Data\DetroitImageDataset_v2") :
        idx = item.split("_")[0]
        indexes.append(idx)

    # Pick a point -- make it random 
    p = generate_unique_random(indexes, 0, len(points_df))
    print(p)

    coordinates = (points_df.iloc[p]['latitude'], points_df.iloc[p]['longitude'])
    # Check if point is already in dataset
    if not already_in_dataset(coordinates):
        # Get the address
        # address = reverse_geocode(coordinates[0], coordinates[1])

        ###  Set headings
        # Get a second point on the same line
        second_point = points_df[(points_df["street_id"] == points_df.iloc[p]["street_id"])
                                & (points_df["point_id"] != points_df.iloc[p]["point_id"])].iloc[0]
        
        second_point_coordinates = (second_point["latitude"], second_point["longitude"])
        # Compute the N-E-S-W direction where the street is pointing at
        direction, angle_baseline = calculate_orientation(coordinates, second_point_coordinates)
        
        ### Do it for one side of the street
        straight_one = angle_baseline + 90
        headings_one = [subtract_angles(straight_one, 60), subtract_angles(straight_one, 30), 
                        straight_one, 
                        add_angles(straight_one, 30), add_angles(straight_one, 60)] 

        street_view_images_first = get_street_view_images(api_key, coordinates, image_size, headings_one)

        metadata_one = {'p':p, 
                        'angle':straight_one,
                        'latitude': coordinates[0],
                        'longitude': coordinates[1],
                        'headings': headings_one,
                        'address': 'N/A'} # address}
        

        straight_two = angle_baseline - 90
        headings_two = [subtract_angles(straight_two, 60), subtract_angles(straight_two, 30), 
                        straight_two, 
                        add_angles(straight_two, 30), add_angles(straight_two, 60)] 
        
        street_view_images_second = get_street_view_images(api_key, coordinates, image_size, headings_two)

        metadata_two = {'p':p, 
                'angle':straight_two,
                'latitude': coordinates[0],
                'longitude': coordinates[1],
                'headings': headings_two,
                'address': 'N/A'} # address}

        return [street_view_images_first, street_view_images_second], [metadata_one, metadata_two]
