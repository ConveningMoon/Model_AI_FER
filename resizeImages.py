from PIL import Image, ImageOps
import os

def resize_and_crop_image(input_path, output_path, size):
    """Resize and center-crop the input image to the specified size."""
    with Image.open(input_path) as img:
        # Resize image, maintaining aspect ratio
        img = ImageOps.contain(img, size)
        # Calculate coordinates to crop image from center
        width, height = img.size
        new_width, new_height = size
        left = (width - new_width)/2
        top = (height - new_height)/2
        right = (width + new_width)/2
        bottom = (height + new_height)/2
        img = img.crop((left, top, right, bottom))
        img.save(output_path)

def process_images(folder_path, output_folder, target_size):
    """Process all images in the specified folder."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    for filename in os.listdir(folder_path):
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            input_path = os.path.join(folder_path, filename)
            output_path = os.path.join(output_folder, filename)
            resize_and_crop_image(input_path, output_path, target_size)
            print(f"Processed {filename}")

# Set the folder path and the target size (width, height)
folder_path = './data/confused/new'
output_folder = './data/confused/resized'
target_size = (512, 512)  # example target size

process_images(folder_path, output_folder, target_size)
