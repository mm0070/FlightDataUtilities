# Restricted parameter patterns for de-identification.


RESTRICTED_AIRCRAFT_PARAMETERS = {
    'AC Fleet Ident',
    'AC Ident (*)',
    'AC Number',
    'AC Number Ident',
    'AC Type (*)',
    'AC Type Ident',
    'AC Tail',
    'AC Tail Number',
    'AC Serial Number',
    'ACMS Software PN Code',
    'ACMS Software Part Number Code',
    'AFDAU SW Ident',
    'Airline Ident',
    'APU Serial Number',
    'Bleed Monitoring Computer (*) Identification',
    'Bump Code (LH)',
    'Bump Code (RH)',
    'CDAM DFDRS Software Part Number',
    'CDAM Hardware Part Number',
    'CDAM Serial Number High',
    'CDAM Serial Number Low',
    'CDAU Hardware Part Number',
    'CDAU Serial Number High',
    'CDAU Serial Number Low',
    'DAR Frame SAS Version Number',
    'DFDAU Program Ident',
    'DFDR Database Software Part Number',
    'DFDR Database SW Part Number',
    'DMU Customer Setup Database Version',
    'EICAS OPC Part Number',
    'EICAS OPS Part Number',
    'Electronic Part Numbering',
    'Embedded Software Part Number',
    'Eng (*) Aircraft Type Code',
    'Eng (*) ESN (*)',
    'Eng (*) Family Serial Number',
    'Eng (*) Ident',
    'Eng (*) Sequence Serial Number',
    'Eng (*) Serial Number',
    'Eng (*) Prop Ident',
    'Eng (*) Type',
    'Fleet Ident',
    'Fleet Number',
    'Identification Data Code',
    'Image Number To FDIU',
    'Mandatory Software Part Number Code',
    'Manufacturer Code',
    'Manufacturer Software PN Code',
    'Mode S Transponder Aircraft Address',
    'Prog Ident',
    'SAS DAR Frame Version Number',
    'SD Selector Image Number',
    'Software Part Number',
    'Software Part Number Code',
    'System Identification',
    'TCAS Intruder Number',
    'TCAS RA Intruder Number',
    'TCAS Transponder Ident Code',
    'Tail Number',
    'Transponder Code',
    'Vendor Database Code',
}


RESTRICTED_AIRPORTS_PARAMETERS = {
    'Airport From',
    'Airport To',
    'Airport (*) Selected',
    'Approach Ident (*) Displayed',
    'Destination',
    'FDEP Depart',
    'FDEP Destination',
    'FDEP Flight Number',
    'FDEP Flight Number (Char 1)',
    'FDEP Flight Number (Char 2)',
    'FDEP Flight Number (Char 3)',
    'FDEP Flight Number (Char 4)',
    'FDEP Flight Number (Char 1-4)',
    'FDEP Leg Number',
    'Flight Number',
    'Flight Number (Char 1)',
    'Flight Number (Char 2)',
    'Flight Number (Char 3)',
    'Flight Number (Char 4)',
    'Flight Number (Char 1-4)',
    'Flight Number (DAR)',
    'Flight Number Character',
    'Flight Number Digit 1',
    'Flight Number Digit 2',
    'Flight Number Digit 3',
    'Flight Number Digit 4',
    'Flight Number Digit 5',
    'Flight Number Digit 6',
    'Flight Number Digit 7',
    'Flight Number Digit 8',
    'Flight Number Digit 1 MSB',
    'Flight Number Digit 8 LSB',
    'Flight Number Numeric',
    'FMC Latitude',
    'FMC Longitude',
    'FMF Latitude',
    'FMF Longitude',
    'FMS Latitude',
    'FMS Longitude',
    'GPS Latitude',
    'GPS Longitude',
    'IRS Latitude',
    'IRS Longitude',
    'IRU Latitude',
    'IRU Longitude',
    'Latitude (*)',
    'Latitude (*) FMC (*)',
    'Latitude (*) GPIRS (*)',
    'Latitude (*) GPS (*)',
    'Latitude (*) IRS (*)',
    'Latitude (*) IRU (*)',
    'Latitude (*) QAR (*)',
    'Latitude (Coarse)',
    'Latitude (DMC)',
    'Latitude (FMF)',
    'Latitude (Fine)',
    'Latitude (GPS)',
    'Latitude (IRS)',
    'Latitude Capture',
    'Latitude Coarse',
    'Latitude Combined',
    'Latitude Fine',
    'Latitude Hybrid',
    'Latitude Position IRS',
    'Latitude Prepared',
    'Latitude Recorded',
    'Latitude Smoothed',
    'Latitude Variable',
    'Leg Number',
    'Longitude (*)',
    'Longitude (*) FMC (*)',
    'Longitude (*) GPIRS (*)',
    'Longitude (*) GPS (*)',
    'Longitude (*) IRS (*)',
    'Longitude (*) IRU (*)',
    'Longitude (*) QAR (*)',
    'Longitude (Coarse)',
    'Longitude (DMC)',
    'Longitude (FMF)',
    'Longitude (Fine)',
    'Longitude (GPS)',
    'Longitude (IRS)',
    'Longitude Capture',
    'Longitude Coarse',
    'Longitude Combined',
    'Longitude Fine',
    'Longitude Hybrid',
    'Longitude Position IRS',
    'Longitude Prepared',
    'Longitude Recorded',
    'Longitude Smoothed',
    'Longitude Variable',
    'Origin',
    'Waypoint (*)',
    'Waypoint Ident (*)',
    'Zone (*) Identify Number',
}


RESTRICTED_DATETIME_PARAMETERS = {
    'Database Day',
    'Database Month',
    'Date',
    'Day (*)',
    'Day Digital',
    'Day FDAU',
    'Day QAR',
    'Day Recorded',
    'Day (ARINC 429)',
    'Day (DAC)',
    'FDEP Day',
    'Recorded Day',
}