import os
import gradio as gr
from PIL import Image
import io
import base64
import tempfile
import segno
from pyzxing import BarCodeReader
import asyncio

# Ensure the event loop is properly initialized
if asyncio.get_event_loop().is_closed():
    asyncio.set_event_loop(asyncio.new_event_loop())

def generate_qr(data):
    try:
        qr = segno.make(data)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        qr.save(temp_file.name, scale=6)
        temp_file.close()
        return temp_file.name
    except Exception as e:
        return f"QR code generation failed: {e}"

def decode_qr_with_zxing(image):
    try:
        reader = BarCodeReader()
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        image.save(temp_file.name)
        result = reader.decode(temp_file.name)
        os.unlink(temp_file.name)
        if result and "parsed" in result[0]:
            return result[0]["parsed"]
        return "No QR code detected"
    except Exception as e:
        return f"QR code decoding failed: {e}"

def handle_image_to_qr(image):
    try:
        image_path = generate_qr(image.filename)
        if "failed" in image_path:
            return image_path
        return Image.open(image_path)
    except Exception as e:
        return f"Error processing image to QR: {e}"

def handle_qr_to_data(qr_image):
    try:
        decoded_data = decode_qr_with_zxing(qr_image)
        return decoded_data
    except Exception as e:
        return f"Error processing QR to data: {e}"

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

gr.TabbedInterface(
    [image_to_qr_interface, qr_to_data_interface],
    ["Image to QR Code", "QR Code to Data"]
).launch(share=True, server_name="0.0.0.0")
