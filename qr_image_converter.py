
import os
import gradio as gr
from PIL import Image
import io
import base64
import tempfile
import segno  # For QR code generation
import numpy as np
import pyzbar.pyzbar as pyzbar  # For QR code decoding with pyzbar

# Function to convert an image to base64 (for display purposes)
def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str

# Function to generate a QR code for the image's file path or URL
import cv2  # OpenCV for QR code decoding

def decode_qr(image):
    # Convert PIL image to OpenCV format (numpy array)
    img_array = np.array(image)

    # Initialize OpenCV QRCode detector
    detector = cv2.QRCodeDetector()

    # Detect and decode the QR code
    data, points, _ = detector.detectAndDecode(img_array)

    if points is not None and data:
        return data  # Return the decoded data
    else:
        return "No QR code detected"


# Function to decode a QR code from an uploaded image using pyzbar
def decode_qr(image):
    # Convert PIL image to NumPy array (for pyzbar)
    img_array = np.array(image)

    # Convert RGB to BGR (pyzbar uses BGR format)
    img_bgr = img_array[:, :, ::-1]

    # Use pyzbar to detect and decode QR code
    decoded_objects = pyzbar.decode(img_bgr)

    if decoded_objects:
        # Return the data from the first decoded QR code (if multiple QR codes are present)
        return decoded_objects[0].data.decode('utf-8')
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
