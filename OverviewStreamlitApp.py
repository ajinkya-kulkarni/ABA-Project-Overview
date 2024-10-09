import numpy as np
import os
import json
import csv
import sys
import caosdb as db
import urllib3
import random
import string
import streamlit as st
import pandas as pd
import base64
from io import BytesIO

sys.dont_write_bytecode = True  # Don't generate the __pycache__ folder locally
sys.tracebacklimit = 0  # Print exception without the built-in python warning
urllib3.disable_warnings()  # Disable the HTTPS warnings for CaosDB authentication

"""
This script combines database operations, data generation, and a Streamlit app
for the ABA Project at MPI-NAT, Göttingen. It retrieves data from a Linkahead database,
generates metadata reports, and presents them in a user-friendly format.
"""

# Database credentials and proxy settings
LINKAHEAD_URL = st.secrets.db_credentials.LINKAHEAD_URL
LINKAHEAD_USERNAME = st.secrets.db_credentials.LINKAHEAD_USERNAME
LINKAHEAD_PASSWORD = st.secrets.db_credentials.LINKAHEAD_PASSWORD
UMG_PROXY = st.secrets.db_credentials.UMG_PROXY

def make_LSM_overview_json_file():
    """
    Generate an overview of Light Sheet Microscopy (LSM) scan entries from the database.
    
    Returns:
    list: A list of dictionaries, each containing metadata for a single LSM scan entry.
    """
    which_type_of_scan = 'LSM_SCAN'
    LSM_entries = db.execute_query('FIND RECORD ' + which_type_of_scan)

    global_entries = []
    current_index = 1

    for single_entry in LSM_entries:
        # Extract and process various metadata fields
        SampleID = str(int(list(single_entry.get_property_values('Sample'))[0]))
        
        SampleName = list(db.execute_query(f"FIND SAMPLE WITH id = '{SampleID}'", unique=True).get_property_values('name'))[0]
        SampleName = 'None' if SampleName is None else str(SampleName)
        
        UploaderID = str(int(list(single_entry.get_property_values('operator'))[0]))
        
        GivenName = str(list(db.execute_query(f"FIND PERSON WITH id = '{UploaderID}'", unique=True).get_property_values('given_name'))[0])
        
        FamilyName = str(list(db.execute_query(f"FIND PERSON WITH id = '{UploaderID}'", unique=True).get_property_values('family_name'))[0])
        
        EmailAddress = str(list(db.execute_query(f"FIND PERSON WITH id = '{UploaderID}'", unique=True).get_property_values('email_address'))[0])
        
        Date = str(list(single_entry.get_property_values('date'))[0])
        
        DeltaPixelXY = str(round(list(single_entry.get_property_values('delta_pixel_xy'))[0], 2))
        
        DeltaPixelZ = str(round(list(single_entry.get_property_values('delta_pixel_z'))[0], 2))
        
        NumberOfChannels_raw = list(single_entry.get_property_values('number_of_channels'))[0]
        NumberOfChannels = str(int(NumberOfChannels_raw))
        
        # Process wavelength information
        wavelengths_only = [list(db.execute_query(f"FIND Wavelengths WITH id = '{single_filter}'", unique=True).get_property_values('name'))[0] 
                            for single_filter in list(single_entry.get_property_values('filters')[0])]
        str_wavelengths = ", ".join(wavelengths_only)
        
        if len(wavelengths_only) != int(NumberOfChannels_raw):
            raise Exception('Number of channels is not equal to number of wavelengths isolated')
        
        IlluminationLeft = str(list(single_entry.get_property_values('illumination_left'))[0])
        
        IlluminationRight = str(list(single_entry.get_property_values('illumination_right'))[0])
        
        Apertures = ", ".join(str(x) for x in np.int_(list(single_entry.get_property_values('apertures')[0])))
        
        ExposureTimes = ", ".join(str(x) for x in np.int_(list(single_entry.get_property_values('exposure_times')[0])))
        
        Objective = list(single_entry.get_property_values('objective'))[0]
        
        Zoom = list(single_entry.get_property_values('zoom'))[0]
        
        SheetWidth = str(list(single_entry.get_property_values('sheet_width'))[0])
        
        AdditionalComments = list(single_entry.get_property_values('additional_comments'))[0]
        AdditionalComments = 'None' if len(AdditionalComments) == 0 else str(AdditionalComments)

        # Create a dictionary to store the properties
        single_entry_data = {
            "Entry #": current_index,
            "Scan Type": which_type_of_scan,
            "Sample ID": SampleID,
            "Sample Name / Barcode": SampleName,
            "Uploader ID": UploaderID,
            "Uploader First Name": GivenName,
            "Uploader Family Name": FamilyName,
            "Uploader Email Address": EmailAddress,
            "Upload Date [YYYY-MM-DD]": Date,
            "Resolution in XY Plane [mu m]": DeltaPixelXY,
            "Resolution in Z direction [mu m]": DeltaPixelZ,
            "Number of Channels": NumberOfChannels,
            "Wavelengths": str_wavelengths,
            "Illumination Right": IlluminationRight,
            "Illumination Left": IlluminationLeft,
            "Aperture [%]": Apertures,
            "Exposure Times [mu s]": ExposureTimes,
            "Objective": Objective,
            "Zoom": Zoom,
            "Sheet Width [%]": SheetWidth,
            "Additional Comments": AdditionalComments
        }

        global_entries.append(single_entry_data)
        current_index += 1

    return global_entries

def create_random_json(num_rows=50, num_cols=30, string_length=10):
    """
    Create a random JSON-like data structure for testing purposes.
    
    Args:
    num_rows (int): Number of rows in the dataset
    num_cols (int): Number of columns in the dataset
    string_length (int): Length of random strings to generate
    
    Returns:
    list: A list of dictionaries containing random data
    """
    column_names = ['column{}'.format(i) for i in range(1, num_cols + 1)]
    data = []

    # Create random data for each row and column
    for i in range(num_rows):
        row = {col_name: ''.join(random.choices(string.ascii_lowercase + string.digits, k=string_length))
               for col_name in column_names}
        data.append(row)

    return data

def download_excel(df, filename):
    """
    Generate a download link for a DataFrame as an Excel file.
    
    Args:
    df (pandas.DataFrame): The DataFrame to be downloaded
    filename (str): The name of the file (without extension)
    
    Returns:
    str: HTML string containing the download link
    """
    excel_io = BytesIO()
    writer = pd.ExcelWriter(excel_io, engine='openpyxl')
    df.to_excel(writer, sheet_name='Sheet1', index=False)
    writer.close()
    excel_io.seek(0)
    b64 = base64.b64encode(excel_io.getvalue()).decode()
    href = f'<a href="data:application/vnd.ms-excel;base64,{b64}" download="{filename}.xlsx">Download report</a>'
    return href

# Set up the Streamlit page configuration
with open("logo.jpg", "rb") as f:
    image_data = f.read()
image_bytes = BytesIO(image_data)

st.set_page_config(
    page_title='ABA Project Overview',
    page_icon=image_bytes,
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get help': 'mailto:ajinkya.kulkarni@mpinat.mpg.de',
        'Report a bug': 'mailto:ajinkya.kulkarni@mpinat.mpg.de',
        'About': 'This is a webpage for generating an overview of the metadata uploaded in the ABA project at the MPI-NAT, Göttingen. Developed, tested and maintained by Ajinkya Kulkarni: https://github.com/ajinkya-kulkarni and reachable at mailto:ajinkya.kulkarni@mpinat.mpg.de'
    }
)

# Title of the web app
st.title(':blue[Metadata report generation for the ABA Project]')
st.markdown("")

# Create a button to generate the DataFrame
generate_df = st.button("Click here to generate the latest reports")

if generate_df:
    st.markdown("""---""")

    with st.spinner(text="Generating latest reports..."):
        # Attempt to connect to the Linkahead database
        try:
            db.configure_connection(
                url=LINKAHEAD_URL,
                password_method="plain",
                ssl_insecure=True,  # remove after naming server
                username=LINKAHEAD_USERNAME,
                password=LINKAHEAD_PASSWORD,
                timeout=1000
            )
        except:
            try:
                # If connection fails, try again using a proxy server
                db.configure_connection(
                    url=LINKAHEAD_URL,
                    password_method="plain",
                    ssl_insecure=True,  # remove after naming server
                    username=LINKAHEAD_USERNAME,
                    password=LINKAHEAD_PASSWORD,
                    https_proxy=UMG_PROXY,
                    timeout=1000
                )
            except:
                raise Exception('Unsuccessful connection with the Linkahead DB. Contact the admin(s) for help.')
                st.stop()

        # Generate overview data
        LSM_overview = make_LSM_overview_json_file()
        TwoPhoton_overview = create_random_json()
        CT_overview = create_random_json()

        # Create tabs for different types of microscopy data
        tab1, tab2, tab3 = st.tabs(["Light sheet Microscopy Data", "Two Photon Microscopy Data", "CT Scan Data"])

        # Display data in each tab
        with tab1:
            df = pd.DataFrame(LSM_overview)
            st.dataframe(data=df, use_container_width=True)
            st.markdown(download_excel(df, 'LSM_overview'), unsafe_allow_html=True)

        with tab2:
            df = pd.DataFrame(TwoPhoton_overview)
            st.dataframe(data=df, use_container_width=True)
            st.markdown(download_excel(df, 'TwoPhoton_overview'), unsafe_allow_html=True)

        with tab3:
            df = pd.DataFrame(CT_overview)
            st.dataframe(data=df, use_container_width=True)
            st.markdown(download_excel(df, 'CT_overview'), unsafe_allow_html=True)

else:
    st.stop()
