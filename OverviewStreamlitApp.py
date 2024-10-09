import streamlit as st
import pandas as pd
import base64
import json
from io import BytesIO
import sys
sys.dont_write_bytecode = True  # Don't generate the __pycache__ folder locally
sys.tracebacklimit = 0  # Print exception without the built-in python warning

"""
This Streamlit app generates metadata reports for the ABA Project at MPI-NAT, Göttingen.
It connects to a Linkahead database, retrieves data, and presents it in a user-friendly format.
"""

# Database credentials and proxy settings
LINKAHEAD_URL = st.secrets.db_credentials.LINKAHEAD_URL
LINKAHEAD_USERNAME = st.secrets.db_credentials.LINKAHEAD_USERNAME
LINKAHEAD_PASSWORD = st.secrets.db_credentials.LINKAHEAD_PASSWORD
UMG_PROXY = st.secrets.db_credentials.UMG_PROXY

from GenerateLogs import *

def download_csv(df, filename):
    """
    Generate a download link for a DataFrame as a CSV file.
    
    Args:
    df (pandas.DataFrame): The DataFrame to be downloaded
    filename (str): The name of the file (without extension)
    
    Returns:
    str: HTML string containing the download link
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}.csv">Download report</a>'
    return href

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
