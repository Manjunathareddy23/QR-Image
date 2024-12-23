import os
import gradio as gr
from PIL import Image
import io
import base64
import tempfile
import segno  # For QR code generation
from pyzxing import BarCodeReader  # Python wrapper for ZXing


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


# Function to decode a QR code from an uploaded image using ZXing
def decode_qr_with_zxing(image):
    try:
        reader = BarCodeReader()
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        image.save(temp_file.name)  # Save the uploaded image temporarily
        result = reader.decode(temp_file.name)  # Decode using ZXing
        if result and "parsed" in result[0]:
            return result[0]["parsed"]  # Extract decoded data
        return "No QR code detected"
    except Exception as e:
        return f"QR code decoding failed: {e}"


# Function to handle image upload and generate QR code
def handle_image_to_qr(image):
    try:
        image_path = generate_qr(image.filename)  # Use the file's path for QR code generation
        if "failed" in image_path:
            return image_path
        return Image.open(image_path)
    except Exception as e:
        return f"Error processing image to QR: {e}"


# Function to handle QR code decoding and display original data
def handle_qr_to_data(qr_image):
    try:
        decoded_data = decode_qr_with_zxing(qr_image)
        return decoded_data
    except Exception as e:
        return f"Error processing QR to data: {e}"


# Create Gradio interfaces
image_to_qr_interface = gr.Interface(
    fn=handle_image_to_qr,
    inputs=gr.Image(type="pil", label="Upload Image", image_mode="RGB"),
    outputs=gr.Image(type="pil", label="Generated QR Code"),
)

qr_to_data_interface = gr.Interface(
    fn=handle_qr_to_data,
    inputs=gr.Image(type="pil", label="Upload QR Code Image", image_mode="RGB"),
    outputs=gr.Textbox(label="Decoded Data"),
)

# Launch Gradio app
gr.TabbedInterface(
    [image_to_qr_interface, qr_to_data_interface],
    ["Image to QR Code", "QR Code to Data"]
).launch(share=True)
