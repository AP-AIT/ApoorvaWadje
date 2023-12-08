import streamlit as st
import imaplib
import email
from datetime import datetime, timedelta
import io
from PIL import Image

def extract_text_from_email(msg):
    text_parts = []
    for part in msg.walk():
        if part.get_content_type() == 'text/plain':
            text_parts.append(part.get_payload(decode=True).decode(part.get_content_charset(), 'ignore'))
    return '\n'.join(text_parts)

def display_images_with_text(username, password, target_email, start_date):
    image_and_text_data = []

    try:
        # Convert start_date to datetime object
        start_date = datetime.strptime(start_date, '%Y-%m-%d')

        # Connect to the IMAP server (Gmail in this case)
        mail = imaplib.IMAP4_SSL('imap.gmail.com')

        # Login to your email account
        mail.login(username, password)

        # Select the mailbox (e.g., 'inbox')
        mail.select("inbox")

        # Construct the search criterion using the date range and target email address
        search_criterion = f'(FROM "{target_email}" SINCE "{start_date.strftime("%d-%b-%Y")}" BEFORE "{(start_date + timedelta(days=1)).strftime("%d-%b-%Y")}")'

        # Search for emails matching the criteria
        result, data = mail.uid('search', None, search_criterion)
        email_ids = data[0].split()

        # Iterate through the email IDs
        for email_id in email_ids:
            result, msg_data = mail.uid('fetch', email_id, "(RFC822)")
            raw_email = msg_data[0][1]

            # Parse the raw email content
            msg = email.message_from_bytes(raw_email)

            # Extract text from the email
            text_content = extract_text_from_email(msg)

            # Iterate through email parts
            for part in msg.walk():
                if part.get_content_maintype() == 'image':
                    # Extract image data
                    image_and_text_data.append({
                        'image': part.get_payload(decode=True),
                        'text': text_content
                    })
    except Exception as e:
        st.error(f"An error occurred: {e}")
    finally:
        # Logout from the IMAP server (even if an error occurs)
        mail.logout()

    return image_and_text_data

# Streamlit app
st.title("Image and Text Viewer")

# Get user input through Streamlit
email_address = st.text_input("Enter your email address:")
password = st.text_input("Enter your email account password:", type="password")
target_email = st.text_input("Enter the email address from which you want to view images:")
start_date = st.text_input("Enter the start date (YYYY-MM-DD):")

# Check if the user has provided all necessary inputs
if email_address and password and target_email and start_date:
    # Display images and text when the user clicks the button
    if st.button("View Images and Text"):
        # Display extracted images and text
        data = display_images_with_text(email_address, password, target_email, start_date)

        if not data:
            st.warning("No images found.")

        for idx, entry in enumerate(data, start=1):
            # Display text content
            st.text(f'Text {idx}: {entry["text"]}')

            # Display image using PIL
            image = Image.open(io.BytesIO(entry["image"]))
            st.image(image, caption=f'Image {idx}', use_column_width=True)
else:
    st.warning("Please fill in all the required fields.")
