import streamlit as st
import psycopg2
import easyocr
import cv2
import numpy as np

# Connect to PostgreSQL database
try:
    connection = psycopg2.connect(
        host="localhost",
        user="postgres",
        password="1204",
        database="bizcardx"
    )
    cursor = connection.cursor()
except psycopg2.Error as e:
    st.error(f"Error connecting to the database: {e}")
    st.stop()

# Create a table to store the business card information
create_table_query = """
    CREATE TABLE IF NOT EXISTS bizcardx (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255),
        job_title VARCHAR(255),
        address VARCHAR(255),
        postcode VARCHAR(255),
        phone VARCHAR(255),
        email VARCHAR(255),
        website VARCHAR(255),
        company_name VARCHAR(225)
    )
"""
cursor.execute(create_table_query)
connection.commit()

# Create an OCR object to read text from the image
reader = easyocr.Reader(['en'])

# Streamlit app
st.title("Business Card Extraction")

# File upload
uploaded_file = st.file_uploader("Upload a business card image", type=["jpg", "jpeg", "png"])

# Handle user actions
if uploaded_file is not None:
    if st.button("Extract Information"):
        # Read the image data
        image = cv2.imdecode(np.fromstring(uploaded_file.read(), np.uint8), 1)

        # Extract information from the image using OCR
        bounds = reader.readtext(image, detail=0)
        name = bounds[0] if len(bounds) > 0 else ""
        job_title = bounds[1] if len(bounds) > 1 else ""
        address = bounds[2] if len(bounds) > 2 else ""
        postcode = bounds[3] if len(bounds) > 3 else ""
        phone = bounds[4] if len(bounds) > 4 else ""
        email = bounds[5] if len(bounds) > 5 else ""
        website = bounds[6] if len(bounds) > 6 else ""
        company_name = bounds[7] if len(bounds) > 7 else ""

        # Insert the extracted information into the database
        insert_query = """
            INSERT INTO bizcardx (name, job_title, address, postcode, phone, email, website, company_name)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (name, job_title, address, postcode, phone, email, website, company_name)
        cursor.execute(insert_query, values)
        connection.commit()

        st.success("Business card information added to the database.")

# Display the stored business card information
display_cards = st.button("View Business Cards")
if display_cards:
    select_query = "SELECT * FROM bizcardx"
    cursor.execute(select_query)
    records = cursor.fetchall()
    if len(records) > 0:
        st.table(records)
    else:
        st.info("No business card records found.")

# Close the database connection
cursor.close()
connection.close()
