#!/usr/bin/env python
# coding: utf-8

# In[7]:


import streamlit as st
import easyocr
from PIL import Image
import sqlite3

# Create an instance of the EasyOCR reader
reader = easyocr.Reader(['en'])

# Create a file uploader widget in Streamlit
file = st.file_uploader("Upload a business card image", type=["jpg", "jpeg", "png"])

# Check if a file has been uploaded
if file is not None:
    # Load the image using PIL
    image = Image.open(file)

    # Display the uploaded image in Streamlit
    st.image(image, caption="Uploaded image", use_column_width=True)

    # Extract text from the image using EasyOCR
    results = reader.readtext(image)

    # Initialize variables for storing the extracted information
    company_name = ''
    card_holder_name = ''
    designation = ''
    mobile_number = ''
    email_address = ''
    website_url = ''
    area = ''
    city = ''
    state = ''
    pin_code = ''

    # Extract information from the results
    for result in results:
        text = result[1].lower().strip()
        if 'company' in text:
            company_name = text.replace('company', '').strip()
        elif 'name' in text:
            card_holder_name = text.replace('name', '').strip()
        elif 'designation' in text or 'title' in text:
            designation = text.replace('designation', '').replace('title', '').strip()
        elif 'mobile' in text or 'phone' in text:
            mobile_number = ''.join([c for c in text if c.isdigit()]) # Extract digits only
        elif 'email' in text:
            email_address = text.replace('email', '').strip()
        elif 'website' in text:
            website_url = text.replace('website', '').strip()
        elif 'address' in text:
            address_parts = text.replace('address', '').split(',')
            if len(address_parts) >= 1:
                area = address_parts[0].strip()
            if len(address_parts) >= 2:
                city = address_parts[1].strip()
            if len(address_parts) >= 3:
                state = address_parts[2].strip()
            if len(address_parts) >= 4:
                pin_code = address_parts[3].strip()

    # Store the extracted information in a SQLite database
    conn = sqlite3.connect('business_cards.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS business_cards
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  company_name TEXT,
                  card_holder_name TEXT,
                  designation TEXT,
                  mobile_number TEXT,
                  email_address TEXT,
                  website_url TEXT,
                  area TEXT,
                  city TEXT,
                  state TEXT,
                  pin_code TEXT)''')
    c.execute("INSERT INTO business_cards (company_name, card_holder_name, designation, mobile_number, email_address, website_url, area, city, state, pin_code) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (company_name, card_holder_name, designation, mobile_number, email_address, website_url, area, city, state, pin_code))
    conn.commit()
    conn.close()

    # Display the extracted information in the Streamlit GUI
    st.write("**Company name:**", company_name)
    st.write("**Card holder name:**", card_holder_name)
    st.write("**Designation:**", designation)
    st.write("**Mobile number:**", mobile_number)
    st.write("**Email address:**", email_address)
    st.write("**Website URL:**", website_url)
    st.write("**Address:**", f"{area}, {city}, {state} {pin_code}")

