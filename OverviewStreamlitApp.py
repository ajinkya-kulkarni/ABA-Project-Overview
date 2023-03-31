import streamlit as st
import pandas as pd
import json
from io import BytesIO

import sys
sys.dont_write_bytecode = True # Don't generate the __pycache__ folder locally
sys.tracebacklimit = 0 # Print exception without the buit-in python warning

import datetime

#######################################################################

## Uncomment to activate streamlit version

LINKAHEAD_URL = st.secrets.db_credentials.LINKAHEAD_URL
LINKAHEAD_USERNAME = st.secrets.db_credentials.LINKAHEAD_USERNAME
LINKAHEAD_PASSWORD = st.secrets.db_credentials.LINKAHEAD_PASSWORD
UMG_PROXY = st.secrets.db_credentials.UMG_PROXY

## Uncomment to activate the local version

# from PASSWORDS import *

from GenerateLogs import *

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

# # Create a button to generate the DataFrame

generate_df = st.button("Click here to generate the latest reports")

# with st.form(key = 'form1', clear_on_submit = True):

# 	submitted = st.form_submit_button('Click here to generate the latest reports')

#######################################################################

if generate_df:

# if submitted:

	st.markdown("""---""")

	#######################################################################

	with st.spinner(text = "Generating latest reports..."):

		#######################################################################

		# Attempt to connect to the Linkahead database without using a proxy server
		try:
			db.configure_connection(
				url = LINKAHEAD_URL,
				password_method = "plain",
				ssl_insecure = True, # remove after naming server
				username = LINKAHEAD_USERNAME,
				password = LINKAHEAD_PASSWORD,
				timeout = 1000
			)

			print()

		# If connection fails, try again using a proxy server

		except:
			try:
				db.configure_connection(
					url = LINKAHEAD_URL,
					password_method = "plain",
					ssl_insecure = True, # remove after naming server
					username = LINKAHEAD_USERNAME,
					password = LINKAHEAD_PASSWORD,
					https_proxy = UMG_PROXY,
					timeout = 1000
				)

				print()

			# If connection still fails, raise an exception
			except:
				raise Exception('Unsuccessful connection with the Linkahead DB. Contact the admin(s) for help.')

				st.stop()

		#######################################################################

		LSM_overview = make_json_file()

		#######################################################################

		tab1, tab2, tab3 = st.tabs(["Light sheet Microscopy Data", "Two Photon Microscopy Data", "CT Scan Data"])

		#######################################################################

		# Create dataframes for each tab

		with tab1:

			df = pd.DataFrame(LSM_overview)

			st.dataframe(data=df, height = 500, use_container_width = True)
			
			# st.markdown(download_csv(df, 'LSM_overview'), unsafe_allow_html = True)

			st.markdown(download_excel(df, 'LSM_overview'), unsafe_allow_html = True)

		with tab2:
			st.empty()

		with tab3:
			st.empty()

	#######################################################################

	# Show timestamp of data creation

	st.markdown("")

	timestamp = datetime.datetime.now().strftime('%d %B %Y at %H:%M hrs')
	created_on = f"Report generated on {timestamp}"
	st.caption(created_on)

else:

	st.stop()

#######################################################################