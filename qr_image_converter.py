import gradio as gr
from PIL import Image
import segno
import tempfile
import os
import uuid

# Folder to store uploaded images
UPLOAD_FOLDER = "uploaded_images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Function to generate QR code
def image_to_qr(image):

    # Generate unique filename
    filename = f"{uuid.uuid4()}.png"

    # Save uploaded image
    image_path = os.path.join(UPLOAD_FOLDER, filename)
    image.save(image_path)

    # IMPORTANT:
    # Replace this with your deployed HuggingFace URL
    
    public_url = f"https://mistermanju01-qr-image.hf.space/gradio_api/file={image_path}"

    # Generate QR code
    qr = segno.make(public_url)

    # Save QR image
    temp_qr = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    qr.save(temp_qr.name, scale=8)

    return temp_qr.name, public_url


# Gradio UI
interface = gr.Interface(
    fn=image_to_qr,
    inputs=gr.Image(type="pil", label="Upload Image"),
    outputs=[
        gr.Image(label="Generated QR Code"),
        gr.Textbox(label="Image URL")
    ],
    title="Image to QR Code Converter",
    description="Upload any image and generate a QR code that opens the image when scanned."
)

interface.launch()
