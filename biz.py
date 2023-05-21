import streamlit as st
import psycopg2
import easyocr

# Load database credentials from st.secrets
db_credentials = st.secrets["db_credentials"]

# Connect to the database
try:
    conn = psycopg2.connect(**db_credentials)
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

except (psycopg2.Error, KeyError) as e:
    st.error("Error connecting to the database. Please check your credentials.")
    st.stop()

# Function to extract information from the image
def extract_info(image):
    reader = easyocr.Reader(['en'])
    results = reader.readtext(image)
    extracted_info = {
        'company_name': '',
        'card_holder_name': '',
        'designation': '',
        'mobile_number': '',
        'email': '',
        'website': '',
        'area': '',
        'city': '',
        'state': '',
        'pin_code': ''
    }
    for result in results:
        text = result[1].lower()
        if 'company' in text:
            extracted_info['company_name'] = result[1]
        elif 'name' in text:
            extracted_info['card_holder_name'] = result[1]
        elif 'designation' in text:
            extracted_info['designation'] = result[1]
        elif 'mobile' in text:
            extracted_info['mobile_number'] = result[1]
        elif 'email' in text:
            extracted_info['email'] = result[1]
        elif 'website' in text:
            extracted_info['website'] = result[1]
        elif 'area' in text:
            extracted_info['area'] = result[1]
        elif 'city' in text:
            extracted_info['city'] = result[1]
        elif 'state' in text:
            extracted_info['state'] = result[1]
        elif 'pin' in text:
            extracted_info['pin_code'] = result[1]
    return extracted_info

# Streamlit app code
def app():
    st.title('Business Card Reader')
    uploaded_file = st.file_uploader('Upload a business card image')
    if uploaded_file is not None:
        image = uploaded_file.read()
        st.image(uploaded_file, caption='Uploaded business card', use_column_width=True)
        extracted_info = extract_info(image)

        # Insert the extracted information into the database
        insert_query = '''INSERT INTO business_cards (image, company_name, card_holder_name, designation, mobile_number, email, website, area, city, state, pin_code)
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);'''
        try:
            cur.execute(insert_query, (
                psycopg2.Binary(image),
                extracted_info['company_name'],
                extracted_info['card_holder_name'],
                extracted_info['designation'],
                extracted_info['mobile_number'],
                extracted_info['email'],
                extracted_info['website'],
                extracted_info['area'],
                extracted_info['city'],
                extracted_info['state'],
                extracted_info['pin_code']
            ))
            conn.commit()
            st.success('Information extracted and stored in the database.')
        except psycopg2.Error as e:
            st.error("Error inserting data into the database.")
           
if name == 'main':
   app()
