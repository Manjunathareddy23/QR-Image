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
        qr = segno.make(data)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        qr.save(temp_file.name, scale=6)  # Save the QR code as a PNG file
        return temp_file.name
    except Exception as e:
        return f"QR code generation failed: {e}"


# Function to decode a QR code from an uploaded image using OpenCV
def decode_qr(image):
    img_array = np.array(image)
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    detector = cv2.QRCodeDetector()
    data, _, _ = detector.detectAndDecode(gray)
    return data if data else "No QR code detected"


# Function to handle image upload and generate QR code
def handle_image_to_qr(image):
    img = image.resize((100, 100))
    temp_dir = tempfile.mkdtemp()
    image_path = os.path.join(temp_dir, "image.png")
    img.save(image_path)
    qr_image_path = generate_qr(image_path)
    if "failed" in qr_image_path:
        return qr_image_path
    return Image.open(qr_image_path)


# Function to handle QR code decoding and display original image
def handle_qr_to_image(qr_image):
    decoded_data = decode_qr(qr_image)
    if "No QR code detected" in decoded_data:
        return decoded_data
    if os.path.exists(decoded_data):
        return Image.open(decoded_data)
    try:
        img_data = base64.b64decode(decoded_data)
        return Image.open(io.BytesIO(img_data))
    except Exception as e:
        return f"Error decoding image from QR code: {e}"


# Create Gradio interfaces
image_to_qr_interface = gr.Interface(
    fn=handle_image_to_qr,
    inputs=gr.Image(type="pil", label="Upload Image", image_mode="RGB"),
    outputs=gr.Image(type="pil", label="Generated QR Code"),
    live=True,
)

qr_to_image_interface = gr.Interface(
    fn=handle_qr_to_image,
    inputs=gr.Image(type="pil", label="Upload QR Code Image", image_mode="RGB"),
    outputs=gr.Image(type="pil", label="Decoded Image"),
    live=True,
)

# Launch Gradio app
gr.TabbedInterface(
    [image_to_qr_interface, qr_to_image_interface],
    ["Image to QR Code", "QR Code to Image"]
).launch(share=True)
