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

import datetime

############################################################################################################

def make_log_file():
	"""
	Creates a log file with a list of files in an Amazon S3 bucket and deletes all files containing 'TestSample_0' in their key name. This function retrieves a list of all objects in the specified Amazon S3 bucket and writes their names and upload dates to a text file named 'S3_files.txt' in the current working directory. It then loops over all objects in the bucket that contain the word 'TestSample_0' in their key name and deletes them.

	Parameters:
		None

	Returns:
		None

	Raises:
		Exception: If an error occurs during the deletion process.
	"""

	# Create an S3 resource object using endpoint URL and access keys
	s3 = boto3.resource('s3',endpoint_url=AMAZON_S3_ENDPOINT_URL, aws_access_key_id=AMAZON_S3_ACCESS_KEY, aws_secret_access_key=AMAZON_S3_SECRET_KEY)

	##################

	# Create a Bucket object representing the specified Amazon S3 bucket
	bucket = s3.Bucket(AMAZON_S3_BUCKET)

	# Get list of objects in the bucket
	objects = list(bucket.objects.all())

	# Get total number of files in the bucket
	total_files = len(objects)

	##################

	filename = 'S3_files.txt'

	if os.path.exists(filename):
		os.remove(filename)

	##################

	with open(filename, 'w') as file:
		# Write the first line with timestamp
		timestamp = datetime.datetime.now().strftime('%d %B %Y at %H:%M hrs')
		file.write('Log generated on ' + timestamp + '\n')
		file.write('\n')
		
		# Loop over each object in the bucket and write its name and upload date to the text file
		for i in range(total_files):

			obj = objects[i]

			# Write object name and upload date to text file
			file.write(obj.key + ' ' + obj.last_modified.strftime('(Created on : ' + '%d %B %Y at %H:%M hrs)') + '\n')

	##################

	# Loop over all objects in the bucket that contain the word 'TestSample_0' in their key name

	for i in range(total_files):
		obj = objects[i]

		if ('TestSample_0' in obj.key):
			try:
				print(str(obj.key) + ' found')

				## Delete the object
				#obj.delete()

				# # Print message indicating that the object was deleted successfully
				# print(str(obj.key) + ' deleted')

				print()
			except:
				# If an error occurs, raise an exception
				raise Exception('Something went wrong')

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

	##############################################

	# # create the JSON file
	# with open(json_file, 'w') as outfile:
	# 	json.dump(global_entries, outfile)

	return global_entries

############################################################################################################

import random
import string

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