import os 

def already_in_dataset(coordinates):
    """
    Check if coordinate point is already in dataset
    """
    coords_stored = []
    items = os.listdir("Data\DetroitImageDataset_v2") 
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