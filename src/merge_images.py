import os
import shutil
import uuid

# List of directories containing images
folders = [
    '../Assets/CarImagesAmbulance',
    '../Assets/CarImagesBlue',
    '../Assets/CarImagesBrownTruck',
    '../Assets/CarImagesGreenTruck',
    '../Assets/CarImagesGrey',
    '../Assets/CarImagesGreyTruck',
    '../Assets/CarImagesPolice',
    '../Assets/CarImagesPurple',
    '../Assets/CarImagesRedTruck',
    '../Assets/CarImagesTaxi',
    '../Assets/CarImagesWhite',
]

# Destination folder to merge all images into
destination_folder = '../Assets/VehicleImages'

# Create destination folder if it doesn't exist
if not os.path.exists(destination_folder):
    os.makedirs(destination_folder)

# Function to generate a new unique filename
def get_unique_filename(filename):
    name, ext = os.path.splitext(filename)
    unique_name = f"{name}_{uuid.uuid4().hex}{ext}"
    return unique_name

# Merge images from all folders into the destination folder
for folder in folders:
    for filename in os.listdir(folder):
        source_path = os.path.join(folder, filename)
        if os.path.isfile(source_path):  # Ensure it's a file
            unique_filename = get_unique_filename(filename)
            destination_path = os.path.join(destination_folder, unique_filename)
            shutil.copy2(source_path, destination_path)

print("All images have been successfully merged into the destination folder.")
