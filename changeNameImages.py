import os

# Define the path to the directory containing the images
folder_path = './data/confused'  # Update this to your actual folder path

# List all files in the directory
files = os.listdir(folder_path)

# Sort files to maintain order if needed
files.sort()  # This is optional and can be adjusted based on specific requirements

# Initialize the starting number
number = 1

# Iterate over each file in the folder
for file in files:
    # Construct the new filename using three-digit numbering
    # The new filename will be something like '001.jpg', '002.jpg', etc.
    new_filename = f"{str(number).zfill(3)}.png"

    # Construct the full old and new file paths
    old_file_path = os.path.join(folder_path, file)
    new_file_path = os.path.join(folder_path, new_filename)

    # Rename the file
    os.rename(old_file_path, new_file_path)

    # Increment the number for the next file
    number += 1

print("Renaming completed.")
