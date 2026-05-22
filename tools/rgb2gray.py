from PIL import Image

# Open the image
image = Image.open("images/i_COL_72_09_17_1705_LHZ.jpeg")

# Convert the image to grayscale. The `"L"` argument in Pillow represents grayscale mode.
grayscale_image = image.convert("L")

# Save the grayscale image
grayscale_image.save("grayscale_image.jpg")