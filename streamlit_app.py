import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import re
import gspread

# Display Title and Description
# st.image("./VOXlogo.jpeg",width=500,)
st.title("VOX Dealer Display")
st.markdown("Details to collect Credit Note")

# Establishing a Google Sheets connection
conn = st.connection("gsheets", type=GSheetsConnection)

# Fetch existing vendors data
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

# Onboarding New Vendor Form
with st.form(key="vendor_form"):
    Name = st.text_input(label="Indent Raised By*")
    Email = st.text_input(label="Email ID")
    Phone = st.text_input(label="Phone No*")
    Distributor = st.text_input(label="Distributor Name*")
    Dealer = st.text_input(label="Dealer Name*")
    City = st.text_input(label="City*")
    products = st.multiselect("Products*", options=PRODUCTS)
    colors = st.multiselect("Decor*", options=COLORS)
    Size = st.multiselect("Panel sizes*", options=SIZES)
    Quantity = st.text_input(label="Quantity of panels*")
    Dateofdisplay = st.date_input(label="Date of display executed*")
    InvoiceDoc = st.file_uploader(label="Upload Invoice copy*")
    DisplayImage = st.file_uploader(label="Upload Display images*")

    # Mark mandatory fields
    st.markdown("**required*")


    submit_button = st.form_submit_button(label="Submit Details")

    # If the submit button is pressed
    if submit_button:
        # Check if all mandatory fields are filled
        pattern = re.compile(r"^[6-9]\d{9}$")
        is_valid = bool(pattern.match(Phone))
        st.warning("Incorrect Phone Number.") 
        if not Name or not Phone or not Distributor or not Dealer or not City or not Dateofdisplay or not InvoiceDoc or not DisplayImage:
            st.warning("Ensure all mandatory fields are filled.")
            st.stop()
        elif Phone in existing_data["Phone"].astype(str).values:
              st.warning("Phone number already exists.")                
        #elif existing_data["Phone"] == Phone:
         #   st.warning("Phone number already exists.")
          #  st.stop()
        else:
            # Create a new row of vendor data
            vendor_data = pd.DataFrame(
                [
                    {
                        "Name": Name,
                        "Email": Email,
                        "Phone": Phone,
                        "Distributor": Distributor,
                        "Dealer": Dealer,
                        "City": City,
                        "Products": ", ".join(products),
                        "Colors": ", ".join(colors),
                        "Sizes": ", ".join(Size),
                        "Quantity": Quantity,
                        "Display date": Dateofdisplay.strftime("%Y-%m-%d"),
                        "Invoice": InvoiceDoc,
                        "Display Image": DisplayImage, 
                    }
                ]
            )

            # Add the new vendor data to the existing data
            updated_df = pd.concat([existing_data, vendor_data], ignore_index=True)

            # Update Google Sheets with the new vendor data
            conn.update(worksheet="dealer", data=updated_df)

            st.success("Details successfully submitted!")

