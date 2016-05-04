# -*- coding: utf-8 -*-
##############################################################################

'''
Multi-state Parameter State Value Mappings
'''

##############################################################################
# Import


import re

from flightdatautilities.patterns import wildcard_match


##############################################################################
# Constants


PARAMETER_CORRECTIONS = {
    '115 VAC Standby Bus': {1: 'On'},
    '115 VAC XFR Bus': {1: 'On'},
    '28 VDC Battery Bus': {1: 'On'},
    '28 VDC Battery Bus Hot': {1: 'On'},
    '28 VDC Battery Bus Switch Hot': {1: 'On'},
    '28 VDC Bus (*)': {1: 'On'},
    '28 VDC Standby Bus': {1: 'On'},
    'AC Bus (*) (*) On': {1: 'On'},
    'AC Bus (*) Status': {1: 'Powered'},
    'AC ESS Bus': {1: 'On'},
    'AC Emergency Bus Fail': {1: 'Failed'},
    'AC Essential Bus Fail': {1: 'Failed'},
    'ADF (*) Selected (*)': {0: 'Not Selected', 1: 'Selected'},
    'AFCAS Active Lateral Mode Capture ': {0: 'Not Captured', 1: 'Captured'},
    'AFCAS Active Lateral Mode FMS ': {0: 'Not FMS', 1: 'FMS'},
    'AFCAS Active Lateral Mode Failure ': {0: 'Not Failed', 1: 'Failed'},
    'AFCAS Active Lateral Mode Valid ': {0: 'Not Valid', 1: 'Valid'},
    'AFCAS Active Path Mode Capture ': {0: 'Not Captured', 1: 'Captured'},
    'AFCAS Active Path Mode FMS ': {0: 'Not FMS', 1: 'FMS'},
    'AFCAS Active Path Mode Failure ': {0: 'Not Failed', 1: 'Failed'},
    'AFCAS Active Path Mode Valid ': {0: 'Not Valid', 1: 'Valid'},
    'AFCAS Active Path Parameter Controlled ': {0: 'Not Controlled',
                                                1: 'Controlled'},
    'AFCAS Active Speed Mode AT Limit ': {0: 'Not Captured', 1: 'Captured'},
    'AFCAS Active Speed Mode Capture ': {0: 'Not Captured', 1: 'Captured'},
    'AFCAS Active Speed Mode FMS ': {0: 'Not FMS', 1: 'FMS'},
    'AFCAS Active Speed Mode Failure ': {0: 'Not Failed', 1: 'Failed'},
    'AFCAS Active Speed Mode Valid ': {0: 'Not Valid', 1: 'Valid'},
    'AFCAS Active Speed Parameter Controlled ': {0: 'Not Controlled',
                                                 1: 'Controlled'},
    'AFCAS Active Thrust Mode AT Limit ': {0: 'No', 1: 'Yes'},
    'AFCAS Active Thrust Mode Capture ': {0: 'Not Captured', 1: 'Captured'},
    'AFCAS Active Thrust Mode FMS ': {0: 'Not FMS', 1: 'FMS'},
    'AFCAS Active Thrust Mode Failure ': {0: 'Not Failed', 1: 'Failed'},
    'AFCAS Active Thrust Mode Valid ': {0: 'Not Valid', 1: 'Valid'},
    'AP (*) Disconnect ': {0: '-', 1: 'Disconnect'},
    'AP (1) Engaged': {0: '-', 1: 'Engaged'},
    'AP (2) Engaged': {0: '-', 1: 'Engaged'},
    'AP (3) Engaged': {0: '-', 1: 'Engaged'},
    'AP (4) Engaged': {0: '-', 1: 'Engaged'},
    'AP Backcourse': {0: '-', 1: 'Engaged'},
    'AP Collective ALTA': {1: 'Armed'},
    'AP Collective GS (*)': {1: 'Armed'},
    'AP Collective Glideslope': {1: 'Armed'},
    'AP Collective Mode (*)': {1: 'Att'},
    'AP Engaged': {0: '-', 1: 'Engaged'},
    'AP Engaged ': {0: '-', 1: 'Engaged'},
    'AP F-TDN Button': {1: 'Pressed'},
    'AP ILS (*)': {1: 'Armed'},
    'AP ILS Localizer': {1: 'Armed'},
    'AP Manual Disconnect ': {0: '-', 1: 'Disconnect'},
    'AP Pitch ALTA': {1: 'Armed'},
    'AP Pitch GS (*)': {1: 'Armed'},
    'AP Pitch Glideslope': {1: 'Armed'},
    'AP Pitch Mode (*)': {1: 'Att'},
    'AP Roll-Yaw Mode (*)': {1: 'Att'},
    'AP VNAV': {0: '-', 1: 'Engaged'},
    'AP VOR (*)': {1: 'Armed'},
    'AP Warning': {1: 'Warning'},
    'APU Bleed Air Switch': {1: 'On'},
    'APU Bleed Valve (*) Open': {1: 'Closed'},
    'APU Bleed Valve Open': {1: 'Closed'},
    'APU Fire': {0: '-', 1: 'Fire'},
    'APU Oil Press Low': {1: 'Low Press'},
    'APU Oil Temp High': {1: 'High Temp'},
    'AT Engaged': {0: '-', 1: 'Engaged'},
    'AT FMC Speed': {0: '-', 1: 'Engaged'},
    'AT Go Around': {0: '-', 1: 'Engaged'},
    'AT Limit': {0: '-', 1: 'Engaged'},
    'AT MCP Speed': {0: '-', 1: 'Engaged'},
    'AT Manual Disconnect': {0: '-', 1: 'Disconnect'},
    'AT Min Speed': {0: '-', 1: 'Engaged'},
    'AT N1': {0: '-', 1: 'Engaged'},
    'AT Retard': {0: '-', 1: 'Engaged'},
    'AT Warning': {1: 'Warning'},
    'Air Conditioning Mode ': {1: 'Economy'},
    'Airports Selected (*)': {0: 'Not Selected', 1: 'Selected'},
    'Altitude Acq': {0: '-', 1: 'Engaged'},
    'Altitude Acquire': {0: '-', 1: 'Engaged'},
    'Altitude Acquire Mode Armed': {0: '-', 1: 'Armed'},
    'Altitude Alert': {0: '-', 1: 'Alert'},
    'Altitude Hold': {0: '-', 1: 'Selected'},
    'Altitude Hold Push Button Light': {0: '-', 1: 'On'},
    'Altitude Reference Active': {1: 'MCP'},
    'Approach Mode Selected (*)': {0: '-', 1: 'Selected'},
    'Auto Speed Fault': {0: '-', 1: 'Fault'},
    'Auto Speedbrake Extend': {0: '-', 1: 'Extend'},
    'Autobrake (*) Selected': {0: '-', 1: 'Selected'},
    'Autobrake Applied': {0: '-', 1: 'Autobrake'},
    'Autobrake HIGH Mode ': {0: '-', 1: 'Selected'},
    'Autobrake LO Mode ': {0: '-', 1: 'Selected'},
    'Autobrake MED Mode ': {0: '-', 1: 'Selected'},
    'Autobrake Mode ': {0: '-', 1: 'On'},
    'Autobrake RTO Mode ': {0: '-', 1: 'Selected'},
    'Autobrake Selected RTO': {0: '-', 1: 'Selected'},
    'Autoland Enabled': {0: '-', 1: 'Enabled'},
    'Backcourse Engaged': {0: '-', 1: 'Engaged'},
    'Battery (*) Overheat ': {0: '-', 1: 'Overheat'},
    'Brake Main Selected': {0: '-', 1: 'Main'},
    'Brake Temperature Sensor ': {0: 'Not Installed', 1: 'Installed'},
    'Cabin Air Conditioning ': {0: '-', 1: 'On'},
    'Cabin Altitude Warning': {0: '-', 1: 'Warning'},
    'Control Wheel Steering (*) Engaged': {0: '-', 1: 'Engaged'},
    'Control Wheel Steering Pitch Engaged': {0: '-', 1: 'Engaged'},
    'Control Wheel Steering Roll Engaged': {0: '-', 1: 'Engaged'},
    'DC Bus (*) (*) Status': {1: 'Powered'},
    'DC ESS Bus Status': {1: 'Powered'},
    'DEU Centre Display Format (*)': {0: '-', 1: 'Selected'},
    'DEU Check List': {0: '-', 1: 'Selected'},
    'DME Source': {0: '-', 1: 'DME'},
    'Display Control Panel (*) MAP Airports ': {0: 'Not Selected', 1: 'Selected'},
    'Display Control Panel (*) MAP Constraints ': {0: 'Not Selected',
                                                   1: 'Selected'},
    'Display Control Panel (*) MAP NDB ': {0: 'Not Selected', 1: 'Selected'},
    'Display Control Panel (*) MAP NavAids ': {0: 'Not Selected', 1: 'Selected'},
    'Display Control Panel (*) MAP Waypoints ': {0: 'Not Selected',
                                                 1: 'Selected'},
    'Display Control Panel (*) Status ': {1: 'Invalid'},
    'Display Control Panel (*) Traffic ': {0: 'Not Selected', 1: 'Selected'},
    'ECS Pack (*)': {0: '-', 1: 'On'},
    'ECS Pack (*) High Flow': {1: 'Low'},
    'ECS Pack (*) On': {0: '-', 1: 'On'},
    'EFIS (*) ADC Sensor Source ': {1: 'Normal'},
    'EFIS (*) ADF 1 Bearing ': {0: 'Not Selected', 1: 'Selected'},
    'EFIS (*) ADF 2 Bearing ': {0: 'Not Selected', 1: 'Selected'},
    'EFIS (*) ADF Bearing ': {1: 'In View'},
    'EFIS (*) ATT HDG Sensor Source ': {1: 'Normal'},
    'EFIS (*) DME Sensor Source ': {1: 'Normal'},
    'EFIS (*) Display Unit 1 Mode ': {1: 'PFD'},
    'EFIS (*) FCC Sensor Source ': {1: 'Normal'},
    'EFIS (*) FMS Sensor Source ': {1: 'Normal'},
    'EFIS (*) ILS MLS Sensor Source ': {1: 'Normal'},
    'EFIS (*) LRRA Sensor Source ': {1: 'Normal'},
    'EFIS (*) Navigation APP Mode ': {0: '-', 1: 'Selected'},
    'EFIS (*) Navigation ARC Mode ': {0: '-', 1: 'Selected'},
    'EFIS (*) Navigation ILS MLS Select Mode ': {1: 'MLS Selected'},
    'EFIS (*) Navigation MAP Mode ': {0: '-', 1: 'Selected'},
    'EFIS (*) Navigation PLAN Mode ': {0: '-', 1: 'Selected'},
    'EFIS (*) Navigation ROSE Mode ': {0: '-', 1: 'Selected'},
    'EFIS (*) Navigation VOR APP Set Mode ': {1: 'VOR set'},
    'EFIS (*) Navigation VOR Mode ': {0: '-', 1: 'Selected'},
    'EFIS (*) VOR Bearing ': {1: 'In View'},
    'EFIS (*) VOR Sensor Source ': {1: 'Normal'},
    'EFIS Frame': {0: '-', 1: 'EFIS'},
    'EID (*) Submodes Page': {1: 'Status'},
    'EMUX 1 Single Channel Fault ': {0: 'No Fault', 1: 'Fault'},
    'EMUX 2 Single Channel Fault ': {0: 'No Fault', 1: 'Fault'},
    'Eng (*) Airborne Vibration Monitoring': {0: '-', 1: 'Alert'},
    'Eng (*) Anti Ice': {0: '-', 1: 'On'},
    'Eng (*) Anti Ice Valve Command': {0: '-', 1: 'Command'},
    'Eng (*) Bleed ': {1: 'Closed'},
    'Eng (*) Chip Detector': {1: 'Chip Detected'},
    'Eng (*) Cowl Anti Ice Button': {1: 'Off'},
    'Eng (*) Cutoff': {1: 'Run'},
    'Eng (*) Fault Dispatch Level (A)': {0: '-', 1: 'MMEL Displayed'},
    'Eng (*) Fire': {0: '-', 1: 'Fire'},
    'Eng (*) Fire (*)': {0: '-', 1: 'Fire'},
    'Eng (*) Fire Extinguish Switch': {0: '-', 1: 'Pulled'},
    'Eng (*) Hyd (*)': {0: '-', 1: 'Low Press'},
    'Eng (*) Oil Press Low': {0: '-', 1: 'Low Press'},
    'Eng (*) Oil Press Low Red Warning': {0: '-', 1: 'Warning'},
    'Eng (*) Overheat ': {0: '-', 1: 'Overheat'},
    'Eng (*) Pylon Overheat': {0: '-', 1: 'Overheat'},
    'Eng (*) Start Valve ': {0: '-', 1: 'Open'},
    'Eng (*) Thrust Reverser': {0: '-', 1: 'Deployed'},
    'Eng (*) Thrust Reverser (*) Deployed': {0: '-', 1: 'Deployed'},
    'Eng (*) Thrust Reverser (*) In Transit': {0: '-', 1: 'In Transit'},
    'Eng (*) Thrust Reverser (*) Unlocked': {0: '-', 1: 'Unlocked'},
    'Eng (*) Thrust Reverser In Transit': {1: 'In Transit'},
    'Eng (*) Wing Anti Ice Button': {1: 'Off'},
    'Event Marker (*)': {0: '-', 1: 'Event'},
    'FCC Local Limited Master': {1: 'FCC (L)'},
    'FD (*) Engaged ': {0: '-', 1: 'Engaged'},
    'FD Engaged ': {0: '-', 1: 'Engaged'},
    'FMC Data Source Selected': {0: '-', 1: 'Selected'},
    'FMC Selected Switch (Capt)': {0: '-', 1: 'Selected'},
    'FMS (*) Navigation Status ': {1: 'Normal'},
    'FMS Installed ': {0: '-', 1: 'Installed'},
    'Final Approach Course Engaged': {0: '-', 1: 'Engaged'},
    'Fire APU Dual Bottle System': {0: '-', 1: 'Fire'},
    'Fire APU Single Bottle System': {0: '-', 1: 'Fire'},
    'Flap Alternate Armed': {0: '-', 1: 'Armed'},
    'Flap Leading Edge (*) Extended': {0: '-', 1: 'Extended'},
    'Flap Leading Edge (*) In Transit': {0: '-', 1: 'In Transit'},
    'Flap Load Relief': {0: '-', 1: 'Load Relief'},
    'Flap Skew (*)': {0: '-'},
    'Flare Engaged': {0: '-', 1: 'Engaged'},
    'Flight Deck Air Conditioning ': {0: '-', 1: 'On'},
    'Flight Dir (*) Engaged': {0: '-', 1: 'Engaged'},
    'Flight Path Vector Selected (*)': {0: '-', 1: 'Selected'},
    'Fuel Qty (*) Low': {0: '-', 1: 'Warning'},
    'GNSS Output Correction': {1: 'Corrected'},
    'GPS Approach': {0: '-', 1: 'GPS'},
    'GPS Selected': {0: '-', 1: 'GPS Active'},
    'Gear (*) Down': {1: 'Up'},
    'Gear (*) Down (*)': {1: 'Up'},
    'Gear (*) Locked Down (*)': {0: '-', 1: 'Locked'},
    'Gear (*) On Ground': {1: 'Air'},
    'Gear (*) Red Warning': {0: '-', 1: 'Warning'},
    'Gear (*) Up': {1: 'Up'},
    'Gear (*) WOW (*) ': {1: 'Air'},
    'Gear Down Selected (*)': {1: 'Up'},
    'Gear Selected Up': {1: 'Up'},
    'Gear Up Selected (*)': {1: 'Up'},
    'Glidepath Engaged': {0: '-', 1: 'Engaged'},
    'Go Around Mode': {0: '-', 1: 'Engaged'},
    'Ground Station Data Selected (*)': {0: '-', 1: 'Selected'},
    'HUD Approach Warning': {0: '-', 1: 'Set'},
    'HUD Combiner Position': {0: '-', 1: 'Stowed'},
    'HUD Touchdown': {0: '-', 1: 'Set'},
    'Heading Engaged': {0: '-', 1: 'Engaged'},
    'Heading Hold': {0: '-', 1: 'Engaged'},
    'Heading Mag-True (*)': {1: 'TRUE'},
    'Heading Mag-True (Capt)': {1: 'TRUE'},
    'Heading Selected Engaged': {0: '-', 1: 'Engaged'},
    'Heading Up MAP Format (*)': {0: '-', 1: 'Selected'},
    'Hectopascals Selected (*)': {0: '-', 1: 'Selected'},
    'Hyd (*) Electrical': {0: '-', 1: 'Low Press'},
    'Hyd (*) Low Press (*)': {1: 'Low Press'},
    'Hyd (*) Low Press Flight Controls': {0: '-', 1: 'Low Press'},
    'Hyd (*) Press Low (*)': {1: 'Low Press'},
    'Hyd Standby Low Press': {0: '-', 1: 'Low Press'},
    'ICAO FAA Selected (*)': {1: 'FAA Selected'},
    'ILS (*) Selected': {0: '-', 1: 'Selected'},
    'ILS (*) Standby': {0: '-', 1: 'Present'},
    'ILS Glideslope Engaged': {0: '-', 1: 'Engaged'},
    'ILS Inner Marker': {0: '-', 1: 'Present'},
    'ILS Inner Marker (*)': {0: '-', 1: 'Present'},
    'ILS Localizer Engaged': {0: '-', 1: 'Engaged'},
    'ILS Middle Marker': {0: '-', 1: 'Present'},
    'ILS Middle Marker (*)': {0: '-', 1: 'Present'},
    'ILS Outer Marker': {0: '-', 1: 'Present'},
    'ILS Outer Marker (*)': {0: '-', 1: 'Present'},
    'ILS Selected': {1: 'VOR'},
    'ILS XLS Selection ': {1: 'XLS Selected'},
    'IRU Navigation Capable': {0: '-', 1: 'Selected'},
    'Isolation Valve Open': {1: 'Closed'},
    'JAA Selected (*)': {0: '-', 1: 'Capable'},
    'Key HF (*)': {0: '-', 1: 'Keyed'},
    'Key Satcom (*)': {0: '-', 1: 'Keyed'},
    'Key VHF (*)': {0: '-', 1: 'Keyed'},
    'Land (*) (*)': {0: '-', 1: 'Land'},
    'Landing Configuration Gear Warning': {0: '-', 1: 'Warning'},
    'Landing Configuration Speedbrake Caution': {0: '-', 1: 'Caution'},
    'Leading Edge Master Extended': {0: '-', 1: 'Extended'},
    'Leading Edge Master In Transit': {0: '-', 1: 'In Transit'},
    'MAP Mode Selected (*)': {0: '-', 1: 'Selected'},
    'MDA Selected (*)': {0: '-', 1: 'Selected'},
    'MFCP ACARS Page Selected ': {0: 'Not Selected', 1: 'Selected'},
    'MFCP APU Page Selected ': {0: 'Not Selected', 1: 'Selected'},
    'MFCP Collision Page Selected ': {0: 'Not Selected', 1: 'Selected'},
    'MFCP STS Page Selected ': {0: 'Not Selected', 1: 'Selected'},
    'MFCP Secondary Engine Page Selected ': {0: 'Not Selected', 1: 'Selected'},
    'MFCP WXR Page (*) Selected ': {0: 'Not Selected', 1: 'Selected'},
    'MFCP XFR Selected ': {0: 'Not Selected', 1: 'Selected'},
    'MFDU 1 Display Mode ': {1: 'Secondary'},
    'MFDU 1 Procedure Page ': {0: 'Not Displayed', 1: 'Displayed'},
    'MLS XLS Selected Azimuth Angle 1 Status ': {1: 'Manual'},
    'MLS XLS Selected Glide Path Angle 1 Status ': {1: 'Manual'},
    'Master Caution (*) (*)': {0: '-', 1: 'Caution'},
    'Master Warning': {0: '-', 1: 'Warning'},
    'Master Warning (*) (*)': {0: '-', 1: 'Warning'},
    'Meters (*) Selected': {0: '-', 1: 'Selected'},
    'Mode Control Panel Speed (*)': {0: '-', 1: 'Engaged'},
    'Multi Function Control Panel Failure ': {0: 'Not Failed', 1: 'Failed'},
    'NAV Mode Operational (*)': {0: '-', 1: 'Engaged'},
    'Overspeed Warning': {0: '-', 1: 'Overspeed'},
    'PFD Navigation Display Format (*)': {0: '-', 1: 'Selected'},
    'Para-Visual Display (*) Enabled': {0: '-', 1: 'Enabled'},
    'Para-Visual Display (*) On': {0: '-', 1: 'On'},
    'Para-Visual Display Enabled': {0: '-', 1: 'Enabled'},
    'Passenger Oxygen Masks Deployed': {1: 'Deployed'},
    'Pitch Alternate Law': {1: 'Engaged'},
    'Pitch Direct Law': {1: 'Engaged'},
    'Pitch Normal Law': {1: 'Engaged'},
    'Plan Mode Selected (*)': {0: '-', 1: 'Selected'},
    'Position Data Selected (*)': {0: '-', 1: 'Selected'},
    'Pressure Control Switch ': {1: 'Manual Selected'},
    'Primary Flight Display No Autoland': {0: 'No Autoland'},
    'Report Auto Download ': {0: '-', 1: 'Enabled'},
    'Roll Trim Command Wing (*) Down': {0: '-', 1: 'Trim'},
    'Roll Trim Command Wing (L) Down': {0: '-', 1: 'Trim'},
    'Roll Trim Command Wing (R) Down': {0: '-', 1: 'Trim'},
    'Rollout Armed': {0: '-', 1: 'Armed'},
    'Rollout Engaged': {0: '-', 1: 'Engaged'},
    'Rotor Brake Engaged': {1: 'Engaged'},
    'Route Data Selected (*)': {0: '-', 1: 'Selected'},
    'Single Channel Engaged': {0: '-', 1: 'Engaged'},
    'Slat (*) Extended': {0: '-', 1: 'Extended'},
    'Slat (*) In Transit': {0: '-', 1: 'In Transit'},
    'Slat Alternate Armed': {0: '-', 1: 'Armed'},
    'Slat Master In Transit': {0: '-', 1: 'In Transit'},
    'Smoke (*) (*) Warning ': {0: '-', 1: 'Smoke'},
    'Smoke Autonomous VCC Warning ': {0: '-', 1: 'Smoke'},
    'Smoke Aux Area (*) Warning ': {0: '-', 1: 'Smoke'},
    'Smoke Avionic Bulk Warning ': {0: '-', 1: 'Smoke'},
    'Smoke Avionic Warning ': {0: '-', 1: 'Smoke'},
    'Smoke Avionics (*) Warning ': {0: '-', 1: 'Smoke'},
    'Smoke BCRC Warning ': {0: '-', 1: 'Smoke'},
    'Smoke Baggage Warning ': {0: '-', 1: 'Smoke'},
    'Smoke Cabin Rest (*) Warning ': {0: '-', 1: 'Smoke'},
    'Smoke Cargo (*) Warning ': {0: '-', 1: 'Smoke'},
    'Smoke Cargo Aft (*) Warning ': {0: '-', 1: 'Smoke'},
    'Smoke Cargo Aft Warning ': {0: '-', 1: 'Smoke'},
    'Smoke Cargo Forward Warning ': {0: '-', 1: 'Smoke'},
    'Smoke Cargo Lower Aft Warning (*) ': {0: '-', 1: 'Smoke'},
    'Smoke Cargo Lower Fwd Warning (*) ': {0: '-', 1: 'Smoke'},
    'Smoke Cargo Rest (*) Warning ': {0: '-', 1: 'Smoke'},
    'Smoke Cargo Upper Aft Warning (*) ': {0: '-', 1: 'Smoke'},
    'Smoke Cargo Upper Fwd Warning (*) ': {0: '-', 1: 'Smoke'},
    'Smoke Cargo Warning ': {0: '-', 1: 'Smoke'},
    'Smoke IFEC Warning ': {0: '-', 1: 'Smoke'},
    'Smoke Lavatory (*) Warning ': {0: '-', 1: 'Smoke'},
    'Smoke Lower Deck Stowage Warning ': {0: '-', 1: 'Smoke'},
    'Smoke Pax Broadband (*) Warning ': {0: '-', 1: 'Smoke'},
    'Speedbrake Armed': {0: '-', 1: 'Armed'},
    'Speedbrake Deployed': {0: '-', 1: 'Deployed'},
    'Speedbrake Do Not Arm': {0: '-', 1: 'Light On'},
    'Speedbrake Position ': {0: '-', 1: 'Deployed'},
    'Spoiler (*) (*) Deployed': {0: '-', 1: 'Deployed'},
    'Spoiler Armed (*)': {0: '-', 1: 'Armed'},
    'Stabilizer Manual Trim Down': {0: '-', 1: 'Trim'},
    'Stabilizer Manual Trim Up': {0: '-', 1: 'Trim'},
    'Stall Warning ': {0: '-', 1: 'Warning'},
    'Status Message New ': {0: 'Not Displayed', 1: 'Displayed'},
    'Steep Approach Mode ': {0: '-', 1: 'Selected'},
    'Stick Pusher': {0: '-', 1: 'Push'},
    'Stick Shaker (*)': {0: '-', 1: 'Shake'},
    'Sync Mode Engaged': {0: '-', 1: 'Engaged'},
    'TAWS (*) Dont Sink': {0: '-', 1: 'Warning'},
    'TAWS (*) Glideslope Cancel': {0: '-', 1: 'Cancel'},
    'TAWS (*) Too Low Gear': {0: '-', 1: 'Warning'},
    'TAWS Alert': {0: '-', 1: 'Alert'},
    'TAWS Alert Recorded': {0: '-', 1: 'Alert'},
    'TAWS Caution': {0: '-', 1: 'Caution'},
    'TAWS Caution Terrain': {0: '-', 1: 'Caution'},
    'TAWS Failure': {0: '-', 1: 'Failed'},
    'TAWS General': {0: '-', 1: 'Warning'},
    'TAWS Glideslope': {0: '-', 1: 'Warning'},
    'TAWS Glideslope Cancel': {0: '-', 1: 'Cancel'},
    'TAWS Inoperative': {0: '-', 1: 'Warning'},
    'TAWS Minimums': {0: '-', 1: 'Minimums'},
    'TAWS Mode 5 ': {0: '-', 1: 'Warning'},
    'TAWS Obstacle': {0: '-', 1: 'Warning'},
    'TAWS Obstacle Caution': {0: '-', 1: 'Caution'},
    'TAWS Obstacle Warning': {0: '-', 1: 'Warning'},
    'TAWS Predictive Windshear': {0: '-', 1: 'Warning'},
    'TAWS Pull Up': {0: '-', 1: 'Warning'},
    'TAWS Sink Rate': {0: '-', 1: 'Warning'},
    'TAWS Terrain': {0: '-', 1: 'Warning'},
    'TAWS Terrain Ahead': {0: '-', 1: 'Warning'},
    'TAWS Terrain Ahead Pull Up': {0: '-', 1: 'Warning'},
    'TAWS Terrain Awareness Inoperative': {0: '-', 1: 'Warning'},
    'TAWS Terrain Awareness Not Available': {0: '-', 1: 'Warning'},
    'TAWS Terrain Caution': {0: '-', 1: 'Caution'},
    'TAWS Terrain Display Selected (Capt)': {0: '-', 1: 'Selected'},
    'TAWS Terrain Display Selected (FO)': {0: '-', 1: 'Selected'},
    'TAWS Terrain Override': {0: '-', 1: 'Warning'},
    'TAWS Terrain Pull Up': {0: '-', 1: 'Warning'},
    'TAWS Terrain Pull Up Ahead': {0: '-', 1: 'Warning'},
    'TAWS Terrain Warning': {0: '-', 1: 'Warning'},
    'TAWS Test ': {0: '-', 1: 'On'},
    'TAWS Too Low Flap': {0: '-', 1: 'Warning'},
    'TAWS Too Low Gear': {0: '-', 1: 'Warning'},
    'TAWS Too Low Terrain': {0: '-', 1: 'Warning'},
    'TAWS Unspecified ': {0: '-', 1: 'Warning'},
    'TAWS V1 Callout Enabled (*)': {0: '-', 1: 'Enabled'},
    'TAWS Warning': {0: '-', 1: 'Warning'},
    'TAWS Windshear': {0: '-', 1: 'Warning'},
    'TAWS Windshear Caution ': {0: '-', 1: 'Caution'},
    'TAWS Windshear Caution 2 ': {0: '-', 1: 'Caution'},
    'TAWS Windshear Inoperative': {0: '-', 1: 'Warning'},
    'TAWS Windshear Siren': {0: '-', 1: 'Siren'},
    'TAWS Windshear Warning': {0: '-', 1: 'Warning'},
    'TAWS Windshear Warning (*)': {0: '-', 1: 'Warning'},
    'TAWS Windshear Warning 2 ': {0: '-', 1: 'Warning'},
    'TCAS (*) Failure': {0: '-', 1: 'Failed'},
    'TCAS Altitude Reporting': {0: '-', 1: 'On'},
    'TCAS Combined Control': {0: 'No Advisory'},
    'TCAS Down Advisory': {0: 'No Down Advisory'},
    'TCAS Installed ': {0: '-', 1: 'Installed'},
    'TCAS Resolution Advisory 2 ': {1: 'Warning'},
    'TCAS System Status': {0: '-', 1: 'Failed'},
    'TCAS Traffic Advisory 1 ': {0: '-', 1: 'Warning'},
    'TCAS Traffic Advisory 2 ': {0: '-', 1: 'Warning'},
    'TCAS Up Advisory': {0: 'No Up Advisory'},
    'TFC Selected (*)': {0: '-', 1: 'Selected'},
    'TRP CLB Mode Selected ': {0: 'Not Selected', 1: 'Selected'},
    'TRP CRZ Mode Selected ': {0: 'Not Selected', 1: 'Selected'},
    'TRP FLX Mode Selected ': {0: 'Not Selected', 1: 'Selected'},
    'TRP MCT Mode Selected ': {0: 'Not Selected', 1: 'Selected'},
    'TRP TOGA Mode Selected ': {0: 'Not Selected', 1: 'Selected'},
    'TRP Temp Manual EPR Override Switch ': {1: 'Normal'},
    'Takeoff And Go Around': {0: '-', 1: 'TOGA'},
    'Takeoff Config Warning': {0: '-', 1: 'Warning'},
    'Takeoff Configuration Flap Warning': {0: '-', 1: 'Warning'},
    'Takeoff Configuration Gear Warning': {0: '-', 1: 'Warning'},
    'Takeoff Configuration Parking Brake Warning': {0: '-', 1: 'Warning'},
    'Takeoff Configuration Rudder Warning': {0: '-', 1: 'Warning'},
    'Takeoff Configuration Spoiler Warning': {0: '-', 1: 'Warning'},
    'Takeoff Configuration Stabilizer Warning': {0: '-', 1: 'Warning'},
    'VHF (*) ': {1: 'Should be Key VHF'},
    'VOR (*) Selected (*)': {0: '-', 1: 'Selected'},
    'VOR Mode Selected (*)': {0: '-', 1: 'Selected'},
    'VORLOC Engaged': {0: '-', 1: 'Engaged'},
    'Vertical Speed Engaged': {0: '-', 1: 'Engaged'},
    'WPT Selected (*)': {0: '-', 1: 'Selected'},
    'WXR Selected (*)': {0: '-', 1: 'Selected'},
    'Weather Radar (*) Operational Status ': {1: 'Off'},
    'Weather Radar (*) Selection ': {0: '-', 1: 'On'},
    'Wheel Well Fire': {0: '-', 1: 'Fire'},
    'Windshear Caution': {1: 'Caution'},
    'Windshear Warning': {1: 'Warning'},
    'Wing (*) Anti Ice': {1: 'On'},
    'Wing (*) Anti Ice Inboard Valve': {1: 'Open'},
    'Wing (*) Anti Ice Outboard Valve': {1: 'Open'},
    'Wing (*) Anti Ice Valve': {1: 'Open'},
    'Wing Anti Ice': {1: 'Off'},
    'Yaw Damper (*) Engaged': {0: '-', 1: 'Engaged'},
    'Yaw Damper Engaged': {0: '-', 1: 'Engaged'},
    'Yaw Trim (*) Command': {0: '-', 1: 'Trim'},
    'inHg Selected (*)': {0: '-', 1: 'Selected'},

#old list
    #'AP (*) Engaged': {1: 'Engaged'},
    #'APU (*) On': {1: 'On'},
    #'APU Bleed Valve Open': {1: 'Open'},
    #'APU Fire': {1: 'Fire'},
    #'AT Active': {1: 'Activated'},
    #'Alpha Floor': {1: 'Engaged'},
    #'Alternate Law': {1: 'Engaged'},
    #'Altitude Capture Mode': {1: 'Activated'},
    #'Altitude Mode': {1: 'Activated'},
    #'Autobrake Selected RTO': {1: 'Selected'},
    #'Cabin Altitude Warning': {1: 'Warning'},
    #'Climb Mode Active': {1: 'Activated'},
    #'Direct Law': {1: 'Engaged'},
    #'ECS Pack (*) High Flow': {1: 'High', 0: 'Low'},
    #'ECS Pack (*) On': {1: 'On'},
    #'Eng (*) Anti Ice': {1: 'On'},
    #'Eng (*) Bleed': {0: 'Closed', 1: 'Open'},
    #'Eng (*) Fire (1L)': {1: 'Fire'},
    #'Eng (*) Fire (1R)': {1: 'Fire'},
    #'Eng (*) Fire (2L)': {1: 'Fire'},
    #'Eng (*) Fire (2R)': {1: 'Fire'},
    #'Eng (*) Fire': {1: 'Fire'},
    #'Eng (*) Oil Press Low': {1: 'Low Press'},
    #'Eng (*) Thrust Reverser (*) Deployed': {1: 'Deployed'},
    #'Eng (*) Thrust Reverser (*) In Transit': {1: 'In Transit'},
    #'Eng (*) Thrust Reverser (*) Unlocked': {1: 'Unlocked'},
    #'Event Marker (*)': {1: 'Event'},
    #'Event Marker (Capt)': {1: 'Event'},
    #'Event Marker (FO)': {1: 'Event'},
    #'Event Marker': {1: 'Event'},
    #'Expedite Climb Mode': {1: 'Activated'},
    #'Expedite Descent Mode': {1: 'Activated'},
    #'Fire APU Dual Bottle System': {1: 'Fire'},
    #'Fire APU Single Bottle System': {1: 'Fire'},
    #'Flap Alternate Armed': {1: 'Armed'},
    #'Flap Load Relief': {0: 'Normal', 1: 'Load Relief'},
    #'Flare Mode': {1: 'Engaged'},
    #'Fuel Jettison Nozzle': {1: 'Disagree'},
    #'Fuel Qty (L) Low': {1: 'Warning'},
    #'Fuel Qty (R) Low': {1: 'Warning'},
    #'Fuel Qty Low': {1: 'Warning'},
    #'Gear (*) Down': {0: 'Up', 1: 'Down'},
    #'Gear (*) In Air': {0: 'Ground', 1: 'Air'},
    #'Gear (*) In Transit': {1: 'In Transit'},
    #'Gear (*) On Ground': {0: 'Air', 1: 'Ground'},
    #'Gear (*) Red Warning': {1: 'Warning'},
    #'Gear (*) Up': {0: 'Down', 1: 'Up'},
    #'Gear Down Selected': {0: 'Up', 1: 'Down'},
    #'Gear Up Selected': {0: 'Down', 1: 'Up'},
    #'Heading Mode Active': {1: 'Activated'},
    #'ILS Glideslope Capture Active': {1: 'Activated'},
    #'ILS Inner Marker (*)': {1: 'Present'},
    #'ILS Localizer Capture Active': {1: 'Activated'},
    #'ILS Localizer Track Active': {1: 'Activated'},
    #'ILS Middle Marker (*)': {1: 'Present'},
    #'ILS Outer Marker (*)': {1: 'Present'},
    #'Jettison Nozzle': {1: 'Jettison'},
    #'Key HF (*)': {1: 'Keyed'},
    #'Key Satcom (*)': {1: 'Keyed'},
    #'Key VHF (*) (*)': {1: 'Keyed'},
    #'Land Track Activated': {1: 'Activated'},
    #'Landing Configuration Gear Warning': {1: 'Warning'},
    #'Landing Configuration Speedbrake Caution': {1: 'Caution'},
    #'Master Caution (*)': {1: 'Caution'},
    #'Master Warning (*)': {1: 'Warning'},
    #'NAV Mode Active': {1: 'Activated'},
    #'Normal Law': {1: 'Engaged'},
    #'Open Climb Mode': {1: 'Activated'},
    #'Open Descent Mode': {1: 'Activated'},
    #'Overspeed Warning': {1: 'Overspeed'},
    #'Pitch Alternate Law (*)': {1: 'Engaged'},
    #'Pitch Direct Law': {1: 'Engaged'},
    #'Pitch Normal Law': {1: 'Engaged'},
    #'Roll Alternate Law': {1: 'Engaged'},
    #'Roll Direct Law': {1: 'Engaged'},
    #'Roll Go Around Mode Active': {1: 'Activated'},
    #'Roll Normal Law': {1: 'Engaged'},
    #'Runway Mode Active': {1: 'Activated'},
    #'Slat Alternate Armed': {1: 'Armed'},
    #'Speed Control (*) Auto': {1: 'Auto'},
    #'Speed Control (*) Manual': {0: 'Auto'},
    #'Speedbrake Armed': {1: 'Armed'},
    #'Speedbrake Deployed': {1: 'Deployed'},
    #'Spoiler (*) Deployed': {1: 'Deployed'},
    #'Spoiler (*) Outboard Deployed': {1: 'Deployed'},
    #'Stick Pusher (*)': {1: 'Push'},
    #'Stick Shaker (*)': {1: 'Shake'},
    #'TAWS (*) Dont Sink': {1: 'Warning'},
    #'TAWS (*) Glideslope Cancel': {1: 'Cancel'},
    #'TAWS (*) Too Low Gear': {1: 'Warning'},
    #'TAWS Alert': {1: 'Alert'},
    #'TAWS Caution Obstacle': {1: 'Caution'},
    #'TAWS Caution Terrain': {1: 'Caution'},
    #'TAWS Caution': {1: 'Caution'},
    #'TAWS Failure': {1: 'Failed'},
    #'TAWS Glideslope': {1: 'Warning'},
    #'TAWS Minimums': {1: 'Minimums'},
    #'TAWS Obstacle Warning': {1: 'Warning'},
    #'TAWS Predictive Windshear': {1: 'Warning'},
    #'TAWS Pull Up': {1: 'Warning'},
    #'TAWS Sink Rate': {1: 'Warning'},
    #'TAWS Terrain Ahead Pull Up': {1: 'Warning'},
    #'TAWS Terrain Ahead': {1: 'Warning'},
    #'TAWS Terrain Caution': {1: 'Caution'},
    #'TAWS Terrain Override': {1: 'Override'},
    #'TAWS Terrain Pull Up': {1: 'Warning'},
    #'TAWS Terrain Warning Amber': {1: 'Warning'},
    #'TAWS Terrain Warning Red': {1: 'Warning'},
    #'TAWS Terrain': {1: 'Warning'},
    #'TAWS Too Low Flap': {1: 'Warning'},
    #'TAWS Too Low Terrain': {1: 'Warning'},
    #'TAWS Warning': {1: 'Warning'},
    #'TAWS Windshear Caution': {1: 'Caution'},
    #'TAWS Windshear Siren': {1: 'Siren'},
    #'TAWS Windshear Warning': {1: 'Warning'},
    #'TCAS (*) Failure': {1: 'Failed'},
    #'TCAS RA': {1: 'RA'},
    #'TCAS TA': {1: 'TA'},
    #'Takeoff And Go Around': {1: 'TOGA'},
    #'Takeoff Configuration AP Warning': {1: 'Warning'},
    #'Takeoff Configuration Aileron Warning': {1: 'Warning'},
    #'Takeoff Configuration Flap Warning': {1: 'Warning'},
    #'Takeoff Configuration Gear Warning': {1: 'Warning'},
    #'Takeoff Configuration Parking Brake Warning': {1: 'Warning'},
    #'Takeoff Configuration Rudder Warning': {1: 'Warning'},
    #'Takeoff Configuration Spoiler Warning': {1: 'Warning'},
    #'Takeoff Configuration Stabilizer Warning': {1: 'Warning'},
    #'Takeoff Configuration Warning': {1: 'Warning'},
    #'Thrust Mode Selected (*)': {1: 'Selected'},
    #'Wing Anti Ice': {1: 'On'},

}


STATE_CORRECTIONS = {
    'APU Bleed Valve Fully Open': 'Open',
    'APU Bleed Valve not Fully Open': 'Closed',
    'DOWN': 'Down',
    'Down Lock': 'Down',
    'Not Closed': 'Open',
    'Not Open': 'Closed',
    'Not armed': 'Not Armed',
    'Not engaged': 'Not Engaged',
    'Openned': 'Open',
    'UP': 'Up',
    'down': 'Down',
    'false': 'False',
    'no Fault': None,
    'not valid': 'Invalid',
    'off': 'Off',
    'on': 'On',
    'true': 'True',
    'up': 'Up',
    'valid': 'Valid',
}


TRUE_STATES = [
    'APU Bleed Valve not Fully Open',
    'APU Fire',
    'Aft CG',
    'Air',
    'Asymmetrical',
    'CMD Mode',
    'CWS Mode',
    'Deployed',
    'Down',
    'Engaged',
    'Event',
    'FMA Displayed',
    'Fault',
    'Good',
    'Ground',
    'Keyed',
    'Not Armed',
    'On',
    'Open',
    'Selected',
    'Track Phase',
    'Unlocked',
    'Valid',
    'Warning',
]


FALSE_STATES = [
    'APU Bleed Valve Fully Open',
    'Air',
    'Armed',
    'Closed',
    'FMA Not Displayed',
    'Ground',
    'Invalid',
    'No APU Fire',
    'No Aft CG',
    'No Event',
    'No Fault',
    'No Warning',
    'Normal',
    'Not Deployed',
    'Not Engaged',
    'Not Keyed',
    'Not in CMD Mode',
    'Not in CWS Mode',
    'Off',
    'Up',
]


# Examples where states conflict:
# * VMO/MMO Selected


##############################################################################
# Functions


def get_parameter_correction(parameter_name):

    if parameter_name in PARAMETER_CORRECTIONS:
        return PARAMETER_CORRECTIONS[parameter_name]

    for pattern, mapping in PARAMETER_CORRECTIONS.items():
        if wildcard_match(pattern, [parameter_name]):
            return mapping


def normalise_discrete_mapping(original_mapping, parameter_name=None):

    true_state = original_mapping[1]
    false_state = original_mapping[0]

    true_state = STATE_CORRECTIONS.get(true_state, true_state)
    false_state = STATE_CORRECTIONS.get(false_state, false_state)

    inverted = true_state in FALSE_STATES or false_state in TRUE_STATES

    normalised_mapping = \
        get_parameter_correction(parameter_name) if parameter_name else None

    if not normalised_mapping:
        normalised_mapping = {0: false_state, 1: true_state}

    return normalised_mapping, inverted


def normalise_multistate_mapping(original_mapping, parameter_name=None):

    normalised_mapping = \
        get_parameter_correction(parameter_name) if parameter_name else None

    if not normalised_mapping:
        normalised_mapping = {}

        for value, state in original_mapping.items():
            normalised_mapping[value] = STATE_CORRECTIONS.get(state, state)

    return normalised_mapping
