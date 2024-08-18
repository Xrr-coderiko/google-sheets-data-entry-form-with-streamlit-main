import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Display Title and Description
st.title("VOX Dealership form")

# Constants
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

# Establishing a Google Sheets connection
conn = st.connection("gsheets", type=GSheetsConnection)

# Fetch existing vendors data
existing_data = conn.read(worksheet="dealer", usecols=list(range(6)), ttl=5)
existing_data = existing_data.dropna(how="all")

action = st.selectbox(
    "Choose an Action",
    [
        "Onboard New Vendor",
        "Update Existing Vendor",
        "View All Vendors",
        "Delete Vendor",
    ],
)

if action == "Onboard New Vendor":
    st.markdown("Enter the details of the new vendor below.")
    with st.form(key="vendor_form"):
        Name = st.text_input(label="Indent Raised By")
        Email = st.text_input(lable="Email ID")
        Phone = st.time_input(label="Phone No.")
        Distributor = st.text_input(label="Distributor Name")
        Dealer = st.text_input(label="Dealer Name")
        City = st.text_input(label="City")
        products = st.multiselect("Products", options=PRODUCTS)
        colors = st.multiselect("Decor", options=COLORS)
        Size = st.multiselect("Panel sizes", options=SIZES)
        Quantity = st.text_input(label="Quantity of panels")
        Dateofdisplay = st.date_input(label="Date of display executed")
        InvoiceDoc = st.file_uploader(label="Upload Invoice copy")
        DisplayImage = st.file_uploader(label="Upload Display images")

        st.markdown("**required*")
        submit_button = st.form_submit_button(label="Submit Details")

        if submit_button:
            if not company_name or not business_type:
                st.warning("Ensure all mandatory fields are filled.")
            elif existing_data["Name"].str.contains(company_name).any():
                st.warning("A vendor with this company name already exists.")
            else:
                vendor_data = pd.DataFrame(
                    [
                        {
                            "Name": company_name,
                            "BusinessType": business_type,
                            "Products": ", ".join(products),
                            "YearsInBusiness": years_in_business,
                            "OnboardingDate": onboarding_date.strftime("%Y-%m-%d"),
                            "AdditionalInfo": additional_info,
                        }
                    ]
                )
                updated_df = pd.concat([existing_data, vendor_data], ignore_index=True)
                conn.update(worksheet="dealer", data=updated_df)
                st.success("Vendor details successfully submitted!")

elif action == "Update Existing Vendor":
    st.markdown("Select a vendor and update their details.")

    vendor_to_update = st.selectbox(
        "Select a Vendor to Update", options=existing_data["Name"].tolist()
    )
    vendor_data = existing_data[existing_data["Name"] == vendor_to_update].iloc[
        0
    ]

    with st.form(key="update_form"):
        company_name = st.text_input(
            label="Company Name*", value=vendor_data["Name"]
        )
        business_type = st.selectbox(
            "Business Type*",
            options=BUSINESS_TYPES,
            index=BUSINESS_TYPES.index(vendor_data["BusinessType"]),
        )
        products = st.multiselect(
            "Products Offered",
            options=PRODUCTS,
            default=vendor_data["Products"].split(", "),
        )
        years_in_business = st.slider(
            "Years in Business", 0, 50, int(vendor_data["YearsInBusiness"])
        )
        onboarding_date = st.date_input(
            label="Onboarding Date", value=pd.to_datetime(vendor_data["OnboardingDate"])
        )
        additional_info = st.text_area(
            label="Additional Notes", value=vendor_data["AdditionalInfo"]
        )

        st.markdown("**required*")
        update_button = st.form_submit_button(label="Update Vendor Details")

        if update_button:
            if not company_name or not business_type:
                st.warning("Ensure all mandatory fields are filled.")
            else:
                # Removing old entry
                existing_data.drop(
                    existing_data[
                        existing_data["Name"] == vendor_to_update
                    ].index,
                    inplace=True,
                )
                # Creating updated data entry
                updated_vendor_data = pd.DataFrame(
                    [
                        {
                            "Name": company_name,
                            "BusinessType": business_type,
                            "Products": ", ".join(products),
                            "YearsInBusiness": years_in_business,
                            "OnboardingDate": onboarding_date.strftime("%Y-%m-%d"),
                            "AdditionalInfo": additional_info,
                        }
                    ]
                )
                # Adding updated data to the dataframe
                updated_df = pd.concat(
                    [existing_data, updated_vendor_data], ignore_index=True
                )
                conn.update(worksheet="dealer", data=updated_df)
                st.success("Vendor details successfully updated!")

# View All Vendors
elif action == "View All Vendors":
    st.dataframe(existing_data)

# Delete Vendor
elif action == "Delete Vendor":
    vendor_to_delete = st.selectbox(
        "Select a Vendor to Delete", options=existing_data["Name"].tolist()
    )

    if st.button("Delete"):
        existing_data.drop(
            existing_data[existing_data["Name"] == vendor_to_delete].index,
            inplace=True,
        )
        conn.update(worksheet="dealer", data=existing_data)
        st.success("Vendor successfully deleted!")
