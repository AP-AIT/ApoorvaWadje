# main.py
import streamlit as st
import io
from PIL import Image
import pytesseract
from pytesseract import Output

st.title("Image Viewer")

def extract_text_from_image(image_bytes):
    try:
        image = Image.open(io.BytesIO(image_bytes))
        extracted_text = pytesseract.image_to_string(image, output_type=Output.STRING)
        return extracted_text
    except Exception as e:
        return f"Text extraction error: {e}"

uploaded_file = st.file_uploader("Choose an image...", type="jpg")

if uploaded_file is not None:
    image_bytes = uploaded_file.read()
    image = Image.open(io.BytesIO(image_bytes))
    st.image(image, caption='Uploaded Image', use_column_width=True)

    extracted_text = extract_text_from_image(image_bytes)
    st.text(f'Text from Image: {extracted_text}')
