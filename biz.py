import streamlit as st
import psycopg2
import easyocr

# Load database credentials from st.secrets
db_credentials = st.secrets["db_credentials"]

# Connect to the database
conn = psycopg2.connect(**db_credentials)

# Create a cursor object
cur = conn.cursor()

# Create a table to store the extracted information
cur.execute('''CREATE TABLE IF NOT EXISTS business_cards
               (id SERIAL PRIMARY KEY,
                image BYTEA,
                company_name TEXT,
                card_holder_name TEXT,
                designation TEXT,
                mobile_number TEXT,
                email TEXT,
                website TEXT,
                area TEXT,
                city TEXT,
                state TEXT,
                pin_code TEXT);''')

# Function to extract information from the image
def extract_info(image):
    reader = easyocr.Reader(['en'])
    results = reader.readtext(image)
    company_name = ''
    card_holder_name = ''
    designation = ''
    mobile_number = ''
    email = ''
    website = ''
    area = ''
    city = ''
    state = ''
    pin_code = ''
    for result in results:
        text = result[1]
        if 'company' in text.lower():
            company_name = text
        elif 'name' in text.lower():
            card_holder_name = text
        elif 'designation' in text.lower():
            designation = text
        elif 'mobile' in text.lower():
            mobile_number = text
        elif 'email' in text.lower():
            email = text
        elif 'website' in text.lower():
            website = text
        elif 'area' in text.lower():
            area = text
        elif 'city' in text.lower():
            city = text
        elif 'state' in text.lower():
            state = text
        elif 'pin' in text.lower():
            pin_code = text
    return company_name, card_holder_name, designation, mobile_number, email, website, area, city, state, pin_code

# Streamlit app code
def app():
    st.title('Business Card Reader')
    uploaded_file = st.file_uploader('Upload a business card image')
    if uploaded_file is not None:
        image = uploaded_file.read()
        st.image(uploaded_file, caption='Uploaded business card', use_column_width=True)
        company_name, card_holder_name, designation, mobile_number, email, website, area, city, state, pin_code = extract_info(image)
        # Insert the extracted information into the database
        cur.execute("INSERT INTO business_cards (image, company_name, card_holder_name, designation, mobile_number, email, website, area, city, state, pin_code) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (psycopg2.Binary(image), company_name, card_holder_name, designation, mobile_number, email, website, area, city, state, pin_code))
        conn.commit()
        st.success('Information extracted and stored in the database.')

# Run the Streamlit app
if __name__ == '__main__':
    app()

   
                 

