import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import re

# st.image("./VOXlogo.jpeg",width=500,)
st.title("VOX Dealer Display")
st.markdown("Details to collect Credit Note")


conn = st.connection("gsheets", type=GSheetsConnection)

existing_data = conn.read(worksheet="dealer", usecols=list(range(13)), ttl=5)
existing_data = existing_data.dropna(how="all")

# List of Business Types and Products
COLORS = [
    "Walnut",
    "White",
    "Black",
    "Golden Oak",
    "Basalt Oak",
    "Rosewood",
    "Dark Mahagany",
    "Oak",
    "Oak Winchester",
    "Brown",
    "Graphite",
]
PRODUCTS = [
    "Soffit",
    "Fronto",
    "MAX-3",
    "SPC",
    "Kerradeco",
    "Kerrafront",
    "Espumo",
    "J Trims",
    "T Trims",
]

SIZES = [
    "8.71",
    "12.43",
    "7.9",
    "10.3",
]

pattern = re.compile(r"^[6-9]\d{9}$")

# Onboarding New Vendor Form
with st.form(key="vendor_form"):
    Name = st.text_input(label="Indent Raised By*")
    Email = st.text_input(label="Email ID")
    Phone = st.text_input(label="Phone No*")
    Distributor = st.text_input(label="Distributor Name*")
    Dealer = st.text_input(label="Dealer Name*")
    City = st.text_input(label="City*")
    num_rows = st.slider('Number of rows', min_value=1, max_value=10)
    grid = st.columns(4)
    product_list, color_list, size_list, quantity_list = [], [], [], []
    for row in range(num_rows):
       with grid[0]:
           product_list.append(st.selectbox(label=f"Product{row}",index=None, options=PRODUCTS, key=f'input_product{row}'))
       with grid[1]:
           color_list.append(st.selectbox(label="Color",index=None, options=COLORS, key=f'input_color{row}'))
       with grid[2]:
           size_list.append(st.selectbox(label="Size",index=None, options=SIZES, key=f'input_size{row}'))
       with grid[3]:
           quantity_list.append(st.text_input(label="Quantity", key=f'input_quantity{row}'))
    
    Dateofdisplay = st.date_input(label="Date of display executed*")
    InvoiceDoc = st.file_uploader(label="Upload Invoice copy*")
    DisplayImage = st.file_uploader(label="Upload Display images*")
    

    # Mark mandatory fields
    st.markdown("**required*")


    submit_button = st.form_submit_button(label="Submit Details")
    


    # If the submit button is pressed
    if submit_button:
        # Check if all mandatory fields are filled
        is_valid = bool(pattern.match(Phone))
        if not Name or not Phone or not Distributor or not Dealer or not City or not Dateofdisplay or not InvoiceDoc or not DisplayImage:
            st.warning("Ensure all mandatory fields are filled.")
            st.stop()
        elif not is_valid:
            st.warning("Incorrect Phone Number")
        elif Phone in existing_data["Phone"].astype(str).values:
            st.warning("Phone number already exists.")             
        else:
            
            vendor_data = pd.DataFrame(
                [
                    {
                        "Name": Name,
                        "Email": Email,
                        "Phone": Phone,
                        "Distributor": Distributor,
                        "Dealer": Dealer,
                        "City": City,
                        "Products": ", ".join(product_list),
                        "Colors": ", ".join(color_list),
                        "Sizes": ", ".join(size_list),
                        "Quantity": ", ".join(quantity_list),
                        "Display date": Dateofdisplay.strftime("%Y-%m-%d"),
                        "Invoice": InvoiceDoc,
                        "Display Image": Dateofdisplay, 
                    }
                ]
            )

            # Add the new vendor data to the existing data
            updated_df = pd.concat([existing_data, vendor_data], ignore_index=True)

            # Update Google Sheets with the new vendor data
            conn.update(worksheet="dealer", data=updated_df)

            st.success("Details successfully submitted!")

