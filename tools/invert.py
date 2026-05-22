import numpy as np
import cv2
from matplotlib import pyplot as plt
from PIL import Image
from pathlib import Path

def read_this(image_file):
    # Read image metadata to determine color space and format
    pil_image = Image.open(image_file)
    color_space = pil_image.mode
    image_format = pil_image.format
    
    # Read image with OpenCV
    image_src = cv2.imread(image_file)
    
    # Use metadata color space to determine conversion
    if color_space == 'L':
        # Grayscale image
        image_src = cv2.cvtColor(image_src, cv2.COLOR_BGR2GRAY)
    elif color_space in ['RGB', 'RGBA']:
        # RGB or RGBA image
        image_src = cv2.cvtColor(image_src, cv2.COLOR_BGR2RGB)
    else:
        # For other color spaces, default to RGB conversion
        image_src = cv2.cvtColor(image_src, cv2.COLOR_BGR2RGB)
    
    return image_src, image_format

if __name__ == "__main__":
    print("Executing directly")
    image_file = "images/COL_72_09_17_1705_LHZ.png"
    
    # Read the image using metadata color space and format detection
    processed_image, image_format = read_this(image_file)

    # Invert pixel intensities
    processed_image = cv2.bitwise_not(processed_image)
    
    # Convert numpy array to PIL Image and save with original format
    image_path = Path(image_file)
    output_file = image_path.with_name(f"i_{image_path.name}")
    pil_image = Image.fromarray(processed_image)
    with output_file.open("xb") as output_stream:
        pil_image.save(output_stream, format=image_format)
    print(f"Image saved to {output_file} in {image_format} format")
    
