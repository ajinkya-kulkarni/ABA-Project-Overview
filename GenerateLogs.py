import numpy as np
import os
import json
import csv
import boto3
import sys
# Don't generate the __pycache__ folder locally
sys.dont_write_bytecode = True 
# Print exception without the buit-in python warning
sys.tracebacklimit = 0 
import caosdb as db
import urllib3
#Disable the HTTPS warnings for CaosDB authentication
urllib3.disable_warnings() 
import random
import string

############################################################################################################

def make_LSM_overview_json_file():

	# Find all LSM scan entries in the database

	which_type_of_scan = 'LSM_SCAN'

	LSM_entries = db.execute_query('FIND RECORD ' + which_type_of_scan)

	##############################################

	global_entries = []

	current_index = 1

	for single_entry in LSM_entries:
		
		SampleID = list(single_entry.get_property_values('Sample'))[0]

		SampleID = str(int(SampleID))

		##############################################

		SampleName = list(db.execute_query(f"FIND SAMPLE WITH id = '{SampleID}'", unique=True).get_property_values('name'))[0]
		
		if SampleName is None:
			SampleName = 'None'

		SampleName = str(SampleName)

		##############################################

		UploaderID = list(single_entry.get_property_values('operator'))[0]

		UploaderID = str(int(UploaderID))

		##############################################

		GivenName = list(db.execute_query(f"FIND PERSON WITH id = '{UploaderID}'", unique=True).get_property_values('given_name'))[0]

		GivenName = str(GivenName)

		##############################################

		FamilyName = list(db.execute_query(f"FIND PERSON WITH id = '{UploaderID}'", unique=True).get_property_values('family_name'))[0]

		FamilyName = str(FamilyName)

		##############################################

		EmailAddress = list(db.execute_query(f"FIND PERSON WITH id = '{UploaderID}'", unique=True).get_property_values('email_address'))[0]

		EmailAddress = str(EmailAddress)

		##############################################

		Date = list(single_entry.get_property_values('date'))[0]

		Date = str(Date)

		##############################################

		DeltaPixelXY = list(single_entry.get_property_values('delta_pixel_xy'))[0]

		DeltaPixelXY = str(round(DeltaPixelXY, 2))

		##############################################

		DeltaPixelZ = list(single_entry.get_property_values('delta_pixel_z'))[0]

		DeltaPixelZ = str(round(DeltaPixelZ, 2))

		##############################################

		NumberOfChannels_raw = list(single_entry.get_property_values('number_of_channels'))[0]

		NumberOfChannels = str(int(NumberOfChannels_raw))

		##############################################

		wavelengths_only = []

		for single_filter in list(single_entry.get_property_values('filters')[0]):
			wavelengths_only.append((list(db.execute_query(f"FIND Wavelengths WITH id = '{single_filter}'", unique=True).get_property_values('name'))[0]))

		str_wavelengths = ", ".join(wavelengths_only)

		##############################################

		if len(wavelengths_only) != int(NumberOfChannels_raw):

			raise Exception('Number of channels is not equal to number of wavelengths isolated')

		##############################################

		IlluminationLeft = list(single_entry.get_property_values('illumination_left'))[0]

		IlluminationLeft = str(IlluminationLeft)

		##############################################

		IlluminationRight = list(single_entry.get_property_values('illumination_right'))[0]

		IlluminationRight = str(IlluminationRight)

		##############################################

		Apertures = list(single_entry.get_property_values('apertures')[0])

		Apertures = np.int_(Apertures)

		Apertures = ", ".join(str(x) for x in Apertures)

		##############################################

		ExposureTimes = list(single_entry.get_property_values('exposure_times')[0])

		ExposureTimes = np.int_(ExposureTimes)

		ExposureTimes = ", ".join(str(x) for x in ExposureTimes)

		##############################################

		Objective = list(single_entry.get_property_values('objective'))[0]

		##############################################

		Zoom = list(single_entry.get_property_values('zoom'))[0]

		##############################################

		SheetWidth = list(single_entry.get_property_values('sheet_width'))[0]

		SheetWidth = str(SheetWidth)

		##############################################

		AdditionalComments = list(single_entry.get_property_values('additional_comments'))[0]

		if len(AdditionalComments) == 0:
			AdditionalComments = 'None'

		AdditionalComments = str(AdditionalComments)

		##############################################

		# create a dictionary to store the properties
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

		##############################################

		global_entries.append(single_entry_data)

		current_index = current_index + 1

	return global_entries

############################################################################################################

def create_random_json(num_rows = 50, num_cols = 30, string_length = 10):
	column_names = ['column{}'.format(i) for i in range(1, num_cols + 1)]

	# create a list to hold the data
	data = []

	# create random data for each row and column
	for i in range(num_rows):
		row = {}

		for col_name in column_names:
			row[col_name] = ''.join(random.choices(string.ascii_lowercase + string.digits, k = string_length))

		# append the row to the data list
		data.append(row)

	# return JSON data
	return data

############################################################################################################
