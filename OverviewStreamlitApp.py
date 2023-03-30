import streamlit as st
import pandas as pd
import base64
import json
from io import BytesIO

import sys
sys.dont_write_bytecode = True # Don't generate the __pycache__ folder locally
sys.tracebacklimit = 0 # Print exception without the buit-in python warning

import datetime

#######################################################################

from PASSWORDS import *
from GenerateLogs import *

#######################################################################

def create_dataframe(json_file):
	with open(json_file) as f:
		data = json.load(f)
	df = pd.DataFrame.from_dict(data)
	return df

#######################################################################

# Define function to download dataframe as CSV

def download_csv(df, filename):
	csv = df.to_csv(index=False)
	b64 = base64.b64encode(csv.encode()).decode()

	href = f'<a href="data:file/csv;base64,{b64}" download="{filename}.csv">Download report</a>'
	
	return href

#######################################################################

# Define app layout

with open("logo.jpg", "rb") as f:
	image_data = f.read()

image_bytes = BytesIO(image_data)

st.set_page_config(page_title = 'ABA Project Overview', page_icon = image_bytes, layout = "wide", initial_sidebar_state = "expanded", menu_items = {'Get help': 'mailto:ajinkya.kulkarni@mpinat.mpg.de', 'Report a bug': 'mailto:ajinkya.kulkarni@mpinat.mpg.de', 'About': 'This is a webpage for generating an overview of the metadata used in the ABA project at the MPI-NAT, Göttingen. Developed, tested and maintained by Ajinkya Kulkarni: https://github.com/ajinkya-kulkarni and reachable at mailto:ajinkya.kulkarni@mpinat.mpg.de'
})

# Title of the web app

st.title(':blue[Metadata report generation for the ABA Project]')

st.markdown("")

#######################################################################

# Create a button to generate the DataFrame

generate_df = st.button("Click here to generate the latest reports")

#######################################################################

if generate_df:

	st.markdown("""---""")

	#######################################################################

	with st.spinner(text = "Generating latest reports..."):
	
		make_json_file('LSM_overview.json')

	#######################################################################

	tab1, tab2, tab3 = st.tabs(["Light sheet Microscopy Data", "Two Photon Microscopy Data", "CT Scan Data"])

	#######################################################################

	df = create_dataframe("LSM_overview.json")

	# Create dataframes for each tab

	with tab1:
		st.dataframe(data=df, height = 500, use_container_width = True)
		st.markdown(download_csv(df, 'LSM_overview'), unsafe_allow_html = True)

	with tab2:
		st.empty()

	with tab3:
		st.empty()
	
	#######################################################################

	# Show timestamp of data creation

	timestamp = datetime.datetime.now().strftime('%d %B %Y at %H:%M hrs')
	created_on = f"Created on {timestamp}"
	st.markdown("""---""")
	st.write(created_on)

else:

	st.stop()

#######################################################################