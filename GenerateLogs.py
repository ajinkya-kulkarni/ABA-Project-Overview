import numpy as np
import os
import json
import csv
import boto3
import sys
sys.dont_write_bytecode = True  # Don't generate the __pycache__ folder locally
sys.tracebacklimit = 0  # Print exception without the built-in python warning
import caosdb as db
import urllib3
urllib3.disable_warnings()  # Disable the HTTPS warnings for CaosDB authentication
import random
import string

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
