import os
import gradio as gr
from PIL import Image
import io
import base64
import tempfile
import segno  # For QR code generation
import numpy as np
import cv2  # OpenCV for QR code decoding

# Function to convert an image to base64 (for display purposes)
def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str

# Function to generate a QR code for the image's file path or URL
def generate_qr(data):
    try:
        # Generate the QR code with the file path or URL
        qr = segno.make(data)

        # Create a temporary file to save the QR code as PNG
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        qr.save(temp_file.name, scale=6)  # Save the QR code as a PNG file

        # Return the path to the saved QR code file
        return temp_file.name
    except Exception as e:
        return f"QR code generation failed: {e}"

# Function to decode a QR code from an uploaded image using OpenCV
def decode_qr(image):
    # Convert PIL image to NumPy array
    img_array = np.array(image)

    # Convert RGB to grayscale (for QR decoding)
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

    # Use OpenCV QR code detector
    detector = cv2.QRCodeDetector()
    data, _, _ = detector.detectAndDecode(gray)

    if data:
        return data
    else:
        return "No QR code detected"

# Function to handle image upload and generate QR code
def handle_image_to_qr(image):
    # Resize image to smaller size for better QR code generation
    img = image.resize((100, 100))  # Resize image to smaller size

    # Save image locally and get its path
    temp_dir = tempfile.mkdtemp()
    image_path = os.path.join(temp_dir, "image.png")
    img.save(image_path)

    # Generate QR code with image path
    qr_image_path = generate_qr(image_path)

    if "failed" in qr_image_path:
        return qr_image_path  # Error message

    # Open the generated QR code image and return it
    qr_image = Image.open(qr_image_path)
    return qr_image

# Function to handle QR code decoding and display original image
def handle_qr_to_image(qr_image):
    decoded_data = decode_qr(qr_image)

    if "No QR code detected" in decoded_data:
        return decoded_data  # Error message

    # If the QR code data is a valid file path, show the image
    if os.path.exists(decoded_data):
        img = Image.open(decoded_data)
        return img  # Return the original image

    # If QR contains a base64 encoded image, decode and display it
    try:
        # Check if the decoded data is a valid base64 image
        img_data = base64.b64decode(decoded_data)
        img = Image.open(io.BytesIO(img_data))
        return img
    except Exception as e:
        return f"Error decoding image from QR code: {e}"

# Create Gradio interfaces for the two functionalities

# Image to QR Code interface
image_to_qr_interface = gr.Interface(
    fn=handle_image_to_qr,
    inputs=gr.Image(type="pil", label="Upload Image",
                    image_mode="RGB"),  # RGB mode for images
    outputs=gr.Image(type="pil", label="Generated QR Code"),
    live=True
)

# QR Code to Image interface
qr_to_image_interface = gr.Interface(
    fn=handle_qr_to_image,
    inputs=gr.Image(type="pil", label="Upload QR Code Image",
                    image_mode="RGB"),  # RGB mode for images
    outputs=gr.Image(type="pil", label="Decoded Image"),
    live=True
)

# Launch the Gradio app with tabs for each function
gr.TabbedInterface([image_to_qr_interface, qr_to_image_interface],
                   ["Image to QR Code", "QR Code to Image"]).launch(share=True)
