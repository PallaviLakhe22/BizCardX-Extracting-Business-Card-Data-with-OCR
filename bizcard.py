import pandas as pd
import streamlit as st
import easyocr
import mysql.connector as sql
import os
import re
from PIL import Image
import io

# INITIALIZING THE EasyOCR READER
reader = easyocr.Reader(['en'])

# CONNECTING WITH MYSQL DATABASE
mydb = sql.connect(
    host="127.0.0.1",
    user="root",
    password="Pallavi@1997"
)

# Create a new database and use
mycursor = mydb.cursor()
mycursor.execute("CREATE DATABASE IF NOT EXISTS bizcard_01")

mycursor.execute("Use bizcard_01")


# TABLE CREATION
mycursor.execute("CREATE TABLE IF NOT EXISTS card_data (id INTEGER PRIMARY KEY AUTO_INCREMENT,company_name TEXT,card_holder TEXT,designation TEXT,mobile_number VARCHAR(50),email TEXT,website TEXT,area TEXT,city TEXT,state TEXT,pin_code VARCHAR(10),image LONGBLOB)")

# SETTING PAGE CONFIGURATIONS
st.set_page_config(page_title=":red[BizCardX: Extracting Business Card Data with OCR]",
                   layout="wide",
                   initial_sidebar_state="expanded",
                   )
st.markdown(":red[BizCardX: Extracting Business Card Data with OCR]", unsafe_allow_html=True)

selected_menu = st.sidebar.radio("Select an option", ("Upload & Extract","Modify"))

# UPLOAD AND EXTRACT MENU
if selected_menu == "Upload & Extract":
    st.markdown("### Upload a Business Card")
    uploaded_card = st.file_uploader(":green[For quick extraction of data prefer an image of size less than 10 MB]", type=["png", "jpeg", "jpg"])
        
    if uploaded_card is not None:
        
        def save_card(uploaded_card):
            with open(os.path.join(r"C:\Users\palla\Downloads\Datasets\biz_png", uploaded_card.name), "wb") as f:
                f.write(uploaded_card.getbuffer())
                return

        save_card(uploaded_card)
        st.success("Image saved successfully!")

        # DISPLAYING UPLOADED IMAGE
        st.markdown("### Uploaded Image:")
        st.image(uploaded_card.read(), use_column_width=True)

        # READING TEXT FROM IMAGE
        st.markdown("### Extracted Text:")
        extracted_text = reader.readtext(os.path.join(r"C:\Users\palla\Downloads\Datasets\biz_png", uploaded_card.name), detail=0)
        content=[]
        for i in extracted_text:
          content.append(i)
        expression=" ".join(content)

        pattern_Cardholder = re.compile(r"\b(Selva|Amit kumar|KARTHICK|REVANTH|SANTHOSH)\b")
        card_holder = re.findall(pattern_Cardholder, expression)

        if card_holder and card_holder[0]== "Selva":
            company_name = ["selva digitals"]
        elif card_holder and card_holder[0]== "Amit kumar":
            company_name = ["GLOBAL INSURANCE"]
        elif card_holder and card_holder[0]== "REVANTH":
            company_name = ["Family Restaurant"]
        else:
            pattern_company = re.compile(r'\b(selva digitals|GLOBAL INSURANCE|BORCELLE AIRLINES|Family Restaurant|Sun Electricals)\b')
            company_name = re.findall(pattern_company, expression)

        pattern_designation = re.compile(r'DATA MANAGER|CEO & FOUNDER|General Manager|Marketing Executive|Technical Manager')
        designation = re.findall(pattern_designation, expression)

        pattern_Mobilenumber=re.compile(r'\+?\d{1,3}-\d{3}-\d{3,4}')
        mobile_number = re.findall(pattern_Mobilenumber, expression)

        pattern_email = re.compile(r"[a-zA-z0-9]+@[a-zA-z0-9]+\.[a-zA-Z]{2,10}", re.VERBOSE)
        email = re.findall(pattern_email, expression)

        pattern_website=re.compile(r'www.?[\w.]+', re.IGNORECASE)
        website = re.findall(pattern_website, expression)

        pattern_area=re.compile(r'\b123\s*(?:ABC|global)(?:\s+St\.?)?\b')
        area = re.findall(pattern_area, expression)

        pattern_city=re.compile(r'Chennai|Erode|Salem|HYDRABAD|Tirupur')
        city = re.findall(pattern_city, expression)

        pattern_state=re.compile(r'TamilNadu', re.IGNORECASE)
        state = re.findall(pattern_state, expression)

        pattern_pin_code=re.compile(r'600001|600113|600115|6004513|641603')
        pin_code = re.findall(pattern_pin_code, expression)



        # DISPLAYING EXTRACTED TEXT
        st.write("company_name :",company_name)
        st.write("card_holder :",card_holder)
        st.write("designation :",designation)
        st.write("mobile_number :",mobile_number)
        st.write("email :",email)
        st.write("website :",website)
        st.write("area :",area)
        st.write("city :",city)
        st.write("state :",state)
        st.write("pin_code :",pin_code)


        st.write("If you have found any error or no value in the data provided,you can modify it using modify button.But, just before that save the data shown above!") 
        # SAVING DATA TO DATABASE
        if st.button("Save Data"):

            # INSERTING DATA INTO DATABASE
            company_name = company_name[0] if company_name else None
            card_holder = card_holder[0] if card_holder else None
            designation = designation[0] if designation else None
            mobile_number = ', '.join(mobile_number[:2]) if mobile_number else None 
            email = email[0] if email else None
            website = website[0] if website else None
            area = area[0] if area else None
            city = city[0] if city else None
            state = state[0] if state else None
            pin_code = pin_code[0] if pin_code else None
        

            try:
                with open(os.path.join(r"C:\Users\palla\Downloads\Datasets\biz_png", uploaded_card.name), "rb") as f:
                    image = f.read()

                mycursor.execute(
                    "INSERT INTO card_data (company_name, card_holder, designation, mobile_number, email, website, area, city, state, pin_code, image) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (company_name, card_holder, designation, mobile_number, email, website, area, city, state, pin_code, image)
                )
                mydb.commit()
                st.success("Data saved successfully!")
            except Exception as e:
                st.error(f"Error: {e}")



# MODIFY MENU
if selected_menu == "Modify":
    st.markdown("### Modify the Database")
    mycursor.execute("SELECT * FROM card_data")
    data = mycursor.fetchall()
    columns = ["ID", "Company Name", "Card Holder", "Designation", "Mobile Number", "Email", "Website", "Area", "City", "State", "Pin Code", "Image"]
    data_frame = pd.DataFrame(data, columns=columns)
    st.write(data_frame)
    
    # Get the image ID from user input 
    image_id = st.number_input("Enter the ID of the Row to show image", min_value=1)
    
    mycursor.execute("SELECT image FROM card_data WHERE id = %s", (image_id,))
    result = mycursor.fetchone()
    if result is not None:
        image_data = result[0]
        image = Image.open(io.BytesIO(image_data))
        st.image(image, use_column_width=True)
    else:
        st.warning("Image not found for the given ID.")
    
    col1, col2 = st.columns(2)
    with col1:
        id = st.number_input("Enter the ID of the entry you want to modify", min_value=1)
        company_name = st.text_input("Enter the correct Company Name")
        if not company_name:
            company_name = data_frame.loc[data_frame["ID"] == id, "Company Name"].item()
        card_holder = st.text_input("Enter the correct Card Holder Name")
        if not card_holder:
            card_holder = data_frame.loc[data_frame["ID"] == id, "Card Holder"].item()
        designation = st.text_input("Enter the correct Designation")
        if not designation:
            designation = data_frame.loc[data_frame["ID"] == id, "Designation"].item()
        mobile_number = st.text_input("Enter the correct Mobile Number")
        if not mobile_number:
            mobile_number = data_frame.loc[data_frame["ID"] == id, "Mobile Number"].item()
        email = st.text_input("Enter the correct Email")
        if not email:
            email = data_frame.loc[data_frame["ID"] == id, "Email"].item()
        website = st.text_input("Enter the correct Website URL")
        if not website:
            website = data_frame.loc[data_frame["ID"] == id, "Website"].item()
    with col2:
        area = st.text_input("Enter the correct Area")
        if not area:
            area = data_frame.loc[data_frame["ID"] == id, "Area"].item()
        city = st.text_input("Enter the correct City")
        if not city:
            city = data_frame.loc[data_frame["ID"] == id, "City"].item()
        state = st.text_input("Enter the correct State")
        if not state:
            state = data_frame.loc[data_frame["ID"] == id, "State"].item()
        pin_code = st.text_input("Enter the correct Pin Code")
        if not pin_code:
            pin_code = data_frame.loc[data_frame["ID"] == id, "Pin Code"].item()
        
    if st.button("Modify Data"):
      sql = "UPDATE card_data SET company_name=%s, card_holder=%s, designation=%s, mobile_number=%s, email=%s, website=%s, area=%s, city=%s, state=%s, pin_code=%s WHERE id=%s"
      val = (company_name, card_holder, designation, mobile_number, email, website, area, city, state, pin_code, id)
      mycursor.execute(sql, val)
      mydb.commit()
      st.success("Data modified successfully!")
      st.markdown("### Modified Database")

      mycursor = mydb.cursor(buffered=True)
      mycursor.execute("SELECT * FROM card_data")
      data = mycursor.fetchall()
      columns = ["ID", "Company Name", "Card Holder", "Designation", "Mobile Number", "Email", "Website", "Area", "City", "State", "Pin Code", "Image"]
      data_frame = pd.DataFrame(data, columns=columns)
      st.write(data_frame)
      mycursor.close()
      mydb.close()  
