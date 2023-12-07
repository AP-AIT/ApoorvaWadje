import streamlit as st
import imaplib
import email
from datetime import datetime, timedelta
import io
from PIL import Image
import pytesseract
from pytesseract import Output

# Set the path to the Tesseract executable (change this to your Tesseract installation path)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR'

def extract_text_from_image(image_bytes):
    try:
        image = Image.open(io.BytesIO(image_bytes))
        extracted_text = pytesseract.image_to_string(image, output_type=Output.STRING)
        return extracted_text
    except Exception as e:
        return f"Text extraction error: {e}"

def display_images(username, password, target_email, start_date):
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(username, password)
        mail.select("inbox")
        search_criterion = f'(FROM "{target_email}" SINCE "{start_date.strftime("%d-%b-%Y")}" BEFORE "{(start_date + timedelta(days=1)).strftime("%d-%b-%Y")}")'
        result, data = mail.uid('search', None, search_criterion)
        email_ids = data[0].split()

        for idx, email_id in enumerate(email_ids, start=1):
            result, msg_data = mail.uid('fetch', email_id, "(RFC822)")
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            for part in msg.walk():
                if part.get_content_maintype() == 'image':
                    image_bytes = part.get_payload(decode=True)
                    image = Image.open(io.BytesIO(image_bytes))
                    st.image(image, caption=f'Image {idx}', use_column_width=True)

                    extracted_text = extract_text_from_image(image_bytes)
                    st.text(f'Text from Image {idx}: {extracted_text}')

    except Exception as e:
        st.error(f"An error occurred: {e}")
    finally:
        mail.logout()

# Streamlit app
st.title("Image Viewer")

# Get user input through Streamlit
email_address = st.text_input("Enter your email address:")
password = st.text_input("Enter your email account password:", type="password")
target_email = st.text_input("Enter the email address from which you want to view images:")
start_date = st.text_input("Enter the start date (YYYY-MM-DD):")

# Check if the user has provided all necessary inputs
if email_address and password and target_email and start_date:
    # Display images when the user clicks the button
    if st.button("View Images"):
        # Display extracted images
        display_images(email_address, password, target_email, start_date)
else:
    st.warning("Please fill in all the required fields.")
