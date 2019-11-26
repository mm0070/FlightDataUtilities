##############################################################################

'''
Provides utilities for handling conversions between units of flight data.

The following links are useful resources:

 - http://en.wikipedia.org/wiki/Conversion_of_units

'''

##############################################################################
# Imports


import decimal

import six
import numpy as np

##############################################################################
# Constants


# Names of localisation profiles:
US_PROFILE = 'US'


# NOTE: There are limitations for units because of technical issues.
#
# We cannot use certain symbols, e.g. degree, middot, mu, ohm; this is due to
# problems with unicode support on Microsoft Windows. Instead we use an
# alternative that best suits our needs.
#
# [0] Not strictly speaking a unit.  Mach is a number.
# [1] Cannot use a correct symbol due to unicode problems.
# [2] Conflicts with an SI unit we're unlikely to use.
# [3] We standardise on US fluid pints and quarts, etc.

# Acceleration:
G = 'g'  # [2]
FPS2 = 'ft/s/s'
MPS2 = 'm/s/s'
DEGREE_S2 = 'deg/s/s'
KT_S = 'kt/s'

# Angles:
DEGREE = 'deg'  # [1]
RADIAN = 'rad'
DEGREE_S = 'deg/s'  # [1]
RADIAN_S = 'rad/s'

# Density:
KG_LITER = 'kg/l'
LB_GALLON = 'lb/gal'

# Electricity:
AMP = 'A'
VOLT = 'V'
KVA = 'kVA'
OHM = 'ohm'  # [1]
MILLIVOLT = 'mV'
MILLIAMP = 'mA'
MICROAMP = 'uA'  # [1]

# Energy
JOULE = 'J'
KJ = 'kJ'
MJ = 'MJ'

# Flow (Mass):
LB_H = 'lb/h'
LB_MIN = 'lb/min'
KG_H = 'kg/h'
TONNE_H = 't/h'

# Flow (Volume):
PINT_H = 'pt/h'  # [3]
QUART_H = 'qt/h'  # [3]
GALLON_H = 'gal/h'  # [3]
LITER_H = 'l/h'

# Force:
LBF = 'lbf'
KGF = 'kgf'
DECANEWTON = 'daN'
NEWTON = 'N'

# Frequency:
HZ = 'Hz'
KHZ = 'KHz'
MHZ = 'MHz'
GHZ = 'GHz'

# Length:
FT = 'ft'
METER = 'm'
KM = 'km'
MILE = 'mi'
NM = 'NM'  # Nautical Miles
INCH = 'in'
MILLIMETER = 'mm'
MIL = 'mil'

# Mass:
LB = 'lb'
KG = 'kg'
TONNE = 't'
SLUG = 'slug'

# Pressure:
INHG = 'inHg'
MILLIBAR = 'mb'
BAR = 'bar'
PASCAL = 'Pa'
HECTOPASCAL = 'hPa'
PSI = 'psi'
PSIA = 'psia'
PSID = 'psid'
PSIG = 'psig'
PSI_MINUTE = 'psi/min'
LB_FT2 = 'lb/ft/ft'

# Speed:
KT = 'kt'
MPH = 'mph'
FPM = 'fpm'
FPS = 'fps'
IPS = 'ips'
METER_S = 'm/s'
MACH = 'Mach'  # [0]
RPM = 'rpm'

# Temperature:
CELSIUS = 'C'  # [1][2]
FAHRENHEIT = 'F'  # [1][2]
KELVIN = 'K'  # [1]
RANKINE = 'R'

# Time:
HOUR = 'h'
MINUTE = 'min'
SECOND = 's'
DAY = 'd'
WEEK = 'wk'
MONTH = 'mo'
YEAR = 'yr'

# Torque:
FT_LB = 'ft.lb'  # [1]
IN_LB = 'in.lb'  # [1]
IN_OZ = 'in.oz'  # [1]

# Volume:
PINT = 'pt'  # [3]
QUART = 'qt'  # [3]
GALLON = 'gal'  # [3]
LITER = 'l'

# Other:
DDM = 'ddm'
GS_DDM = 'gs-ddm'
LOC_DDM = 'loc-ddm'
DOTS = 'dots'
TRIM = 'trim'
CYCLES = 'cycles'
PERCENT = '%'
NM_KG = 'NM/kg'
#COUNTS = 'counts'#Readout
DU = 'du'
DI = 'di'
# UNITS = 'units'#Readout
# CU = 'cu'#Readout
# SCALAR = 'scalar'#Readout
# EPR = 'epr'#Readout


CONVERSION_MULTIPLIERS = {
    # Acceleration:
    MPS2: {
        G: 0.101971621,
    },
    # Density:
    KG_LITER: {
        LB_GALLON: 8.3454063545262,
    },
    LB_GALLON: {
        KG_LITER: 0.1198264,
    },
    # Energy:
    JOULE: {
        KJ: 0.001,
        MJ: 0.000001,
    },
    KJ: {
        JOULE: 1000,
        MJ: 0.001,
    },
    MJ: {
        JOULE: 1000000,
        KJ: 1000,
    },
    # Flow (Mass):
    LB_H: {
        LB_MIN: 0.0166666667,
        KG_H: 0.45359237,
        TONNE_H: 0.00045359237,
    },
    LB_MIN: {
        LB_H: 60,
        KG_H: 27.2155422,
        TONNE_H: 0.0272155422,
    },
    KG_H: {
        LB_H: 2.204622622,
        LB_MIN: 0.0367437104,
        TONNE_H: 0.001,
    },
    TONNE_H: {
        LB_H: 2204.622621849,
        LB_MIN: 36.7437104,
        KG_H: 1000.0,
    },
    # Flow (Volume):
    PINT_H: {
        QUART_H: 0.5,
        GALLON_H: 0.125,
        LITER_H: 0.473176,
    },
    QUART_H: {
        PINT_H: 2,
        GALLON_H: 0.25,
        LITER_H: 0.946353,
    },
    GALLON_H: {
        PINT_H: 8,
        QUART_H: 4,
        LITER_H: 3.78541,
    },
    LITER_H: {
        PINT_H: 2.11338,
        QUART_H: 1.05669,
        GALLON_H: 0.264172,
    },
    # Force:
    LBF: {
        KGF: 0.45359237,
        DECANEWTON: 0.444822162,
        NEWTON: 4.44822162,
    },
    KGF: {
        LBF: 2.20462262,
        DECANEWTON: 0.980665,
        NEWTON: 9.80665,
    },
    DECANEWTON: {
        LBF: 2.24808943,
        KGF: 1.01971621,
        NEWTON: 10,
    },
    NEWTON: {
        LBF: 0.224808943,
        KGF: 0.101971621,
        DECANEWTON: 0.1,
    },
    # Frequency:
    HZ: {
        KHZ: 0.001,
        MHZ: 0.000001,
        GHZ: 0.000000001,
    },
    KHZ: {
        HZ: 1000.0,
        MHZ: 0.001,
        GHZ: 0.000001,
    },
    MHZ: {
        HZ: 1000000.0,
        KHZ: 1000.0,
        GHZ: 0.001,
    },
    GHZ: {
        HZ: 1000000000.0,
        KHZ: 1000000.0,
        MHZ: 1000.0,
    },
    # Length:
    FT: {
        METER: 0.3048,
        KM: 0.0003048,
        MILE: 0.00018939,
        NM: 0.000164579,
        MILLIMETER: 304.8,
    },
    METER: {
        FT: 3.280839895,
        KM: 0.001,
        MILE: 0.000621371,
        NM: 0.000539957,
        MILLIMETER: 1000,
    },
    KM: {
        FT: 3280.839895013,
        METER: 1000,
        MILE: 0.621371192,
        NM: 0.539956803,
        MILLIMETER: 1000000,
    },
    MILE: {
        FT: 5280,
        METER: 1609.344,
        KM: 1.609344,
        NM: 0.868976242,
        MILLIMETER: 1609344,
    },
    NM: {
        FT: 6076.11548554,
        METER: 1852,
        KM: 1.852,
        MILE: 1.150779448,
        MILLIMETER: 1852000,
    },
    MILLIMETER: {
        FT: 0.003280839895,
        METER: 0.001,
        KM: 0.000001,
        MILE: 0.000000621371,
        NM: 0.000000539957,
    },
    # Mass:
    LB: {
        KG: 0.45359237,
        SLUG: 0.0310809502,
        TONNE: 0.00045359237,
    },
    KG: {
        LB: 2.204622622,
        SLUG: 0.0685217659,
        TONNE: 0.001,
    },
    SLUG: {
        LB: 32.1740486,
        KG: 14.5939029,
        TONNE: 0.0145939029,
    },
    TONNE: {
        LB: 2204.622621849,
        KG: 1000.0,
        SLUG: 68.5217659,
    },
    # Pressure:
    INHG: {
        MILLIBAR: 33.86389,
        PASCAL: 3386.389,
        HECTOPASCAL: 33.86389,
        PSI: 0.491154221,
    },
    BAR: {
        INHG: 29.529983071415973,
        PASCAL: 100000,
        HECTOPASCAL: 1000,
        PSI: 14.5037738,
    },
    MILLIBAR: {
        INHG: 0.02952998,
        PASCAL: 100,
        HECTOPASCAL: 1,
        PSI: 0.014503774,
    },
    PASCAL: {
        INHG: 0.0002952998,
        MILLIBAR: 0.01,
        HECTOPASCAL: 0.01,
        PSI: 0.00014503774,
    },
    HECTOPASCAL: {
        INHG: 0.02952998,
        MILLIBAR: 1,
        PASCAL: 100,
        PSI: 0.014503774,
    },
    PSI: {
        INHG: 2.036020375,
        MILLIBAR: 68.94757,
        PASCAL: 6894.757,
        HECTOPASCAL: 68.94757,
    },
    # Speed:
    KT: {
        MPH: 1.150778454,
        FPM: 101.268503937,
        FPS: 1.68781,
        METER_S: 0.514444,
    },
    MPH: {
        KT: 0.868976993,
        FPM: 88.0,
        FPS: 1.46667,
        METER_S: 0.44704,
    },
    FPM: {
        KT: 0.009874739,
        MPH: 0.011363636,
        FPS: 1 / 60.0,
        METER_S: 0.00508,
    },
    FPS: {
        KT: 0.592483801,
        MPH: 0.681818,
        FPM: 60.0,
        METER_S: 0.3048,
    },
    METER_S: {
        KT: 1.94384,
        MPH: 2.23694,
        FPM: 196.850394,
        FPS: 3.28084,
    },
    # Time:
    HOUR: {
        MINUTE: 60.0,
        SECOND: 3600.0,
    },
    MINUTE: {
        HOUR: 0.016666667,
        SECOND: 60.0,
    },
    SECOND: {
        HOUR: 0.000277778,
        MINUTE: 0.016666667,
    },
    # Torque:
    FT_LB: {
        IN_LB: 12,
        IN_OZ: 192,
    },
    IN_LB: {
        FT_LB: 0.0833,
        IN_OZ: 16,
    },
    IN_OZ: {
        FT_LB: 0.00520833,
        IN_LB: 0.0625,
    },
    # Volume:
    PINT: {
        QUART: 0.5,
        GALLON: 0.125,
        LITER: 0.473176,
    },
    QUART: {
        PINT: 2,
        GALLON: 0.25,
        LITER: 0.946353,
    },
    GALLON: {
        PINT: 8,
        QUART: 4,
        LITER: 3.78541,
    },
    LITER: {
        PINT: 2.11338,
        QUART: 1.05669,
        GALLON: 0.264172,
    },
    # Other:
    GS_DDM: {
        DOTS: 11.428571428571429,
    },
    LOC_DDM: {
        DOTS: 12.903225806451614,
    },
    MILLIVOLT: {
        DOTS: 0.01333333333333333,
    },
    MICROAMP: {
        DOTS: 0.01333333333333333,
    },
    DOTS: {
        GS_DDM: 0.0875,
        LOC_DDM: 0.0775,
        MILLIVOLT: 75,
        MICROAMP: 75,
    }
}


CONVERSION_FUNCTIONS = {
    # Angles:
    DEGREE: {
        RADIAN: np.radians,
    },
    RADIAN: {
        DEGREE: np.degrees,
    },
    # Temperature:
    CELSIUS: {
        FAHRENHEIT: lambda v: v * 9.0 / 5.0 + 32.0,
        KELVIN: lambda v: v + 273.15,
        RANKINE: lambda v: (v + 273.15) * 9.0 / 5.0,
    },
    FAHRENHEIT: {
        CELSIUS: lambda v: (v - 32.0) * 5.0 / 9.0,
        KELVIN: lambda v: (v + 459.67) * 5.0 / 9.0,
        RANKINE: lambda v: v + 459.67,
    },
    KELVIN: {
        CELSIUS: lambda v: v - 273.15,
        FAHRENHEIT: lambda v: v * 9.0 / 5.0 - 459.67,
        RANKINE: lambda v: v * 9.0 / 5.0,
    },
    RANKINE: {
        CELSIUS: lambda v: (v - 491.67) * 5.0 / 9.0,
        FAHRENHEIT: lambda v: v - 459.67,
        KELVIN: lambda v: v * 5.0 / 9.0,
    },
}


STANDARD_CONVERSIONS = {
    # Acceleration
    MPS2: G,
    # Angle:
    RADIAN: DEGREE,
    # Electricity:
    MICROAMP: DOTS,
    MILLIVOLT: DOTS,
    # Flow (Mass):
    LB_H: KG_H,
    TONNE_H: KG_H,
    # Flow (Volume):
    PINT_H: QUART_H,
    # Force:
    NEWTON: DECANEWTON,
    LBF: DECANEWTON,
    KGF: DECANEWTON,
    # Length:
    MILE: NM,
    # Mass:
    LB: KG,
    SLUG: KG,
    TONNE: KG,
    # Pressure:
    BAR: PSI,
    INHG: MILLIBAR,
    HECTOPASCAL: MILLIBAR,
    # Temperature:
    FAHRENHEIT: CELSIUS,
    KELVIN: CELSIUS,
    RANKINE: CELSIUS,
    # Volume:
    PINT: QUART,
    # Other:
    GS_DDM: DOTS,
    LOC_DDM: DOTS,
}


UNIT_DISPLAY = {
    CELSIUS: '°C',
    FAHRENHEIT: '°F',
    RANKINE: '°R',
    # DEGREE: '°',
    # DEGREE_S: '°/s',
    DEGREE_S2: 'deg/s²',  # '°/s²'
    FT_LB: 'ft·lb',
    IN_LB: 'in·lb',
    IN_OZ: 'in·oz',
    MICROAMP: 'μA',
    OHM: 'Ω',
    FPS2: 'ft/s²',
    LB_FT2: 'lb/ft²',
}


UNIT_CORRECTIONS = {
    # Acceleration:
    'G': G,
    'G\'s': G,
    'g\'s': G,
    'ft/sec^2': FPS2,
    'ft/sec/sec': FPS2,
    'm/s²': MPS2,
    b'm/s\xc2\xb2': MPS2,
    'kt/sec': KT_S,
    'kts/sec': KT_S,
    'kts/s': KT_S,
    'deg/s^2': DEGREE_S2,
    'deg/s2': DEGREE_S2,
    'deg/sec/sec': DEGREE_S2,
    'deg/sec2': DEGREE_S2,
    'deg/sec^2': DEGREE_S2,
    # Angles:
    '\xb0': DEGREE,  # degree symbol
    'DEG': DEGREE,
    'Deg': DEGREE,
    'degs.': DEGREE,
    'degree': DEGREE,
    'degrees': DEGREE,
    'radian': RADIAN,
    'radians': RADIAN,
    'DEG/S': DEGREE_S,
    'DEG/SEC': DEGREE_S,
    'DPS': DEGREE_S,
    'deg/se': DEGREE_S,
    'deg/sec': DEGREE_S,
    'degree/s': DEGREE_S,
    'degree/sec': DEGREE_S,
    'degrees/s': DEGREE_S,
    'degrees/sec': DEGREE_S,
    'RAD/S': RADIAN_S,
    'RAD/SEC': RADIAN_S,
    'RPS': RADIAN_S,
    'rad/se': RADIAN_S,
    'rad/sec': RADIAN_S,
    'radian/s': RADIAN_S,
    'radian/sec': RADIAN_S,
    'radians/s': RADIAN_S,
    'radians/sec': RADIAN_S,
    # Density:
    'kilogram/liter': KG_LITER,
    'kilogram/litre': KG_LITER,
    'kgs/liter': KG_LITER,
    'kgs/litre': KG_LITER,
    'kgs/l': KG_LITER,
    'kg/liter': KG_LITER,
    'kg/litre': KG_LITER,
    'pound/gallon': LB_GALLON,
    'lbs/gallon': LB_GALLON,
    'lbs/gal': LB_GALLON,
    'lb/gallon': LB_GALLON,
    # Electricity:
    'amp': AMP,
    'amps': AMP,
    'AMPS': AMP,
    'amperes': AMP,
    'kilovolt-amps': KVA,
    'KVA': KVA,
    'v': VOLT,
    'volt': VOLT,
    'volts': VOLT,
    'voltage': VOLT,
    'VAC': VOLT,
    'VDC': VOLT,
    'ohms': OHM,
    'mv': MILLIVOLT,
    'millivolts': MILLIVOLT,
    'ua': MICROAMP,
    'microamps': MICROAMP,
    'ma': MILLIAMP,
    'milliamps': MILLIAMP,
    # Energy:
    'joule': JOULE,
    'kilojoule': KJ,
    'megajoule': MJ,
    # Flow (Mass):
    'lb/hr': LB_H,
    'lbs/h': LB_H,
    'lbs/hr': LB_H,
    'pph': LB_H,
    'LB/HR': LB_H,
    'LBS/H': LB_H,
    'LBS/HR': LB_H,
    'PPH': LB_H,
    'lbs/min': LB_MIN,
    'LBS/MIN': LB_MIN,
    'ppm': LB_MIN,
    'PPM': LB_MIN,
    'kg/hr': KG_H,
    'kgs/h': KG_H,
    'kgs/hr': KG_H,
    'kph': KG_H,
    'KG/HR': KG_H,
    'KG/H': KG_H,
    'KGS/H': KG_H,
    'KGS/HR': KG_H,
    'KPH': KG_H,
    't/hr': TONNE_H,
    'ts/h': TONNE_H,
    'ts/hr': TONNE_H,
    'tonne/h': TONNE_H,
    'tonne/hr': TONNE_H,
    'tonnes/h': TONNE_H,
    'tonnes/hr': TONNE_H,
    # Force:
    'pound-force': LBF,
    'kilogram-force': KGF,
    'kilopond': KGF,
    'kp': KGF,
    'decanewton': DECANEWTON,
    'dan': DECANEWTON,
    'DAN': DECANEWTON,
    'Newton': NEWTON,
    'newton': NEWTON,
    'n': NEWTON,
    # Frequency:
    'hertz': HZ,
    'kilohertz': KHZ,
    'megahertz': MHZ,
    'gigahertz': GHZ,
    'hz': HZ,
    'khz': KHZ,
    'mhz': MHZ,
    'ghz': GHZ,
    'HZ': HZ,
    'KHZ': KHZ,
    'MHZ': MHZ,
    'GHZ': GHZ,
    'Khz': KHZ,
    'Mhz': MHZ,
    'Ghz': GHZ,
    # Length:
    'FT': FT,
    'Ft': FT,
    'fts': FT,
    'feet': FT,
    'FEET': FT,
    'foot': FT,
    'metre': METER,
    'metres': METER,
    'meter': METER,
    'meters': METER,
    'kilometre': KM,
    'kilometres': KM,
    'kilometer': KM,
    'kilometers': KM,
    'mile': MILE,
    'miles': MILE,
    'MILE': MILE,
    'MILES': MILE,
    'nm': NM,
    'inch': INCH,
    'inches': INCH,
    'IN': INCH,
    'MM': MILLIMETER,
    'Mm': MILLIMETER,
    'mils': MIL,
    'Mil': MIL,
    'MIL': MIL,
    'Mils': MIL,
    'MILS': MIL,
    # Mass:
    'KGS': KG,
    'Kgs': KG,
    'kgs': KG,
    'Kg': KG,
    'KG': KG,
    'LBS': LB,
    'Lbs': LB,
    'lbs': LB,
    'lbs.': LB,
    'Slugs': SLUG,
    'slugs': SLUG,
    'tonne': TONNE,
    'tonnes': TONNE,
    # Pressure:
    'IN-HG': INHG,
    'in-Hg': INHG,
    'in.Hg': INHG,
    'inhg': INHG,
    'in-hg': INHG,
    'in.hg': INHG,
    'InHg': INHG,
    'inHG': INHG,
    'In-Hg': INHG,
    'In.Hg': INHG,
    'IN HG': INHG,
    'pa': PASCAL,
    'hpa': HECTOPASCAL,
    'Hpa': HECTOPASCAL,
    'HPa': HECTOPASCAL,
    'HPA': HECTOPASCAL,
    'MB': MILLIBAR,
    'Mb': MILLIBAR,
    'mB': MILLIBAR,
    'mbar': MILLIBAR,
    'PSI': PSI,
    'Psi': PSI,
    'PSIA': PSIA,
    'PSID': PSID,
    'PSIG': PSIG,
    'lb/ft^2': LB_FT2,
    'lb/ft2': LB_FT2,
    # Speed:
    'KT': KT,
    'KTS': KT,
    'Kt': KT,
    'Kts': KT,
    'kts': KT,
    'kn': KT,
    'knot': KT,
    'knots': KT,
    'KNOT': KT,
    'KNOTS': KT,
    'mi/h': MPH,
    'mi/hr': MPH,
    'ft/m': FPM,
    'ft/mn': FPM,
    'ft/min': FPM,
    'FT/MIN': FPM,
    'Ft/Mn': FPM,
    'Ft/min': FPM,
    'FEET/MIN': FPM,
    'feet/min': FPM,
    'FPM': FPM,
    'ft/s': FPS,
    'ft/sec': FPS,
    'feet/sec': FPS,
    'FPS': FPS,
    'in/s': IPS,
    'in/sec': IPS,
    'inch/sec': IPS,
    'IPS': IPS,
    'meter/s': METER_S,
    'meters/s': METER_S,
    'meter/s': METER_S,
    'meters/sec': METER_S,
    'metre/s': METER_S,
    'metres/s': METER_S,
    'metre/s': METER_S,
    'metres/sec': METER_S,
    'M/s': METER_S,
    'm/sec': METER_S,
    'M': MACH,
    'MACH': MACH,
    'mach': MACH,
    'RPM': RPM,
    'Rpm': RPM,
    # Temperature:
    b'\xb0C': CELSIUS,
    '\xb0C': CELSIUS,
    b'\xf8C': CELSIUS,
    'DEGC': CELSIUS,
    'DEG C': CELSIUS,
    'degree C': CELSIUS,
    'degrees C': CELSIUS,
    'deg. C': CELSIUS,
    'degs. C': CELSIUS,
    'deg C': CELSIUS,
    'degC': CELSIUS,
    'degree F': FAHRENHEIT,
    'degrees F': FAHRENHEIT,
    'deg. F': FAHRENHEIT,
    'deg F': FAHRENHEIT,
    'degree K': KELVIN,
    'degrees K': KELVIN,
    'deg. K': KELVIN,
    'deg K': KELVIN,
    'deg R': RANKINE,
    'degRankine': RANKINE,
    # Time:
    'day': DAY,
    'days': DAY,
    'DAY': DAY,
    'DAYS': DAY,
    'DD': DAY,
    'hr': HOUR,
    'hrs': HOUR,
    'hour': HOUR,
    'hours': HOUR,
    'HH': HOUR,
    'HR': HOUR,
    'HRS': HOUR,
    'HOUR': HOUR,
    'HOURS': HOUR,
    'mn': MINUTE,
    'mins': MINUTE,
    'MIN': MINUTE,
    'MINS': MINUTE,
    'MINUTE': MINUTE,
    'MINUTES': MINUTE,
    'mon': MONTH,
    'mth': MONTH,
    'month': MONTH,
    'months': MONTH,
    'MM': MONTH,
    'MON': MONTH,
    'MONTH': MONTH,
    'MONTHS': MONTH,
    'sec': SECOND,
    'secs': SECOND,
    'second': SECOND,
    'seconds': SECOND,
    'SEC': SECOND,
    'SECS': SECOND,
    'SECOND': SECOND,
    'SECONDS': SECOND,
    'SS': SECOND,
    'wks': WEEK,
    'week': WEEK,
    'weeks': WEEK,
    'yrs': YEAR,
    'year': YEAR,
    'years': YEAR,
    'Years': YEAR,
    'YR': YEAR,
    'YY': YEAR,
    'YEAR': YEAR,
    'YEARS': YEAR,
    # Torque:
    'ft-lb': FT_LB,
    'ft-lbs': FT_LB,
    'ft.lbs': FT_LB,
    'in-lb': IN_LB,
    'in-lbs': IN_LB,
    'in.lbs': IN_LB,
    'in-oz': IN_OZ,
    'In-Oz': IN_OZ,
    'IN-OZ': IN_OZ,
    # Volume:
    'PT': PINT,
    'PTS': PINT,
    'pts': PINT,
    'pt (US)': PINT,
    'pint': PINT,
    'pints': PINT,
    'PINT': PINT,
    'PINTS': PINT,
    'qts': QUART,
    'Qts': QUART,
    'QT': QUART,
    'QTS': QUART,
    'QT US': QUART,
    'QT. US': QUART,
    'qt (US)': QUART,
    'Us/Qt': QUART,
    'quart': QUART,
    'quarts': QUART,
    'QUART': QUART,
    'QUARTS': QUART,
    'US QRT': QUART,
    'US Qt': QUART,
    'Gal': GALLON,
    'Gals': GALLON,
    'gals': GALLON,
    'gal (US)': GALLON,
    'gallon': GALLON,
    'gallons': GALLON,
    'lt': LITER,
    'Lt': LITER,
    'liter': LITER,
    'liters': LITER,
    'litre': LITER,
    'litres': LITER,
    # Other:
    'DDM': DDM,
    'GS-DDM': GS_DDM,
    'GSDDM': GS_DDM,
    'gsddm': GS_DDM,
    'LOC-DDM': LOC_DDM,
    'LOCDDM': LOC_DDM,
    'locddm': LOC_DDM,
    'dot': DOTS,
    'TRIM': TRIM,
    'Trim': TRIM,
    'cycle': CYCLES,
    'Cycle': CYCLES,
    'percent': PERCENT,
    '% N1': PERCENT,
    '% MAC': PERCENT,
    '% RPM': PERCENT,
    '% n1': PERCENT,
    '% mac': PERCENT,
    '% rpm': PERCENT,
    '% N1': PERCENT,
    '% Mac': PERCENT,
    '% Rpm': PERCENT,
    '%N1': PERCENT,
    '%MAC': PERCENT,
    '%RPM': PERCENT,
    '%n1': PERCENT,
    '%mac': PERCENT,
    '%rpm': PERCENT,
    '%N1': PERCENT,
    '%Mac': PERCENT,
    'MAC': PERCENT,
    '%Load': PERCENT,
    'LOAD': PERCENT,
    '%LOAD': PERCENT,
    '%Rpm': PERCENT,
    '%open': PERCENT,
    '%stroke': PERCENT,
    '% Open': PERCENT,
    '% OPEN': PERCENT,
    '%full': PERCENT,
    '% full': PERCENT,
    '%Full': PERCENT,
    '% FULL': PERCENT,
    'PCT': PERCENT,
    # 'Epr': EPR,#Readout
    # 'EPR': EPR,#Readout
    # 'UNIT': UNITS,#Readout
    # 'Unit': UNITS,#Readout
    # 'UNITS': UNITS,#Readout
    # 'Units': UNITS,#Readout
    # 'Unit': UNITS,#Readout
    # 'Cu': CU, #Readout
    # 'CU': CU, #Readout
    'Du': DU,
    'DU': DU,
    'Di': DI,
    'DI': DI,
}


UNIT_CATEGORIES = {
    'Acceleration': (G, FPS2, MPS2, DEGREE_S2, KT_S),
    'Angles': (DEGREE, RADIAN, DEGREE_S, RADIAN_S),
    'Density': (KG_LITER, LB_GALLON),
    'Electricity': (AMP, VOLT, KVA, OHM, MILLIVOLT, MICROAMP, MILLIAMP),
    'Energy': (JOULE, KJ, MJ),
    'Flow (Mass)': (LB_H, LB_MIN, KG_H, TONNE_H),
    'Flow (Volume)': (PINT_H, QUART_H, GALLON_H, LITER_H),
    'Force': (LBF, KGF, DECANEWTON, NEWTON),
    'Frequency': (HZ, KHZ, MHZ, GHZ),
    'Length': (FT, METER, KM, MILE, NM, INCH, MILLIMETER),
    'Mass': (LB, KG, SLUG, TONNE),
    'Pressure': (INHG, PASCAL, HECTOPASCAL, BAR, MILLIBAR, PSI, PSIA, PSID, PSIG, PSI_MINUTE, LB_FT2),
    'Speed': (KT, MPH, FPM, FPS, IPS, METER_S, MACH, RPM),
    'Temperature': (CELSIUS, FAHRENHEIT, KELVIN, RANKINE),
    'Time': (HOUR, MINUTE, SECOND, DAY, WEEK, MONTH, YEAR),
    'Torque': (FT_LB, IN_LB, IN_OZ),
    'Volume': (PINT, QUART, GALLON, LITER),
    'Other': (DDM, GS_DDM, LOC_DDM, DOTS, TRIM, CYCLES, PERCENT, NM_KG, DU, DI, MIL), #COUNTS, CU, SCALAR, UNITS, EPR #Readout,
}


UNIT_DESCRIPTIONS = {
    # Acceleration:
    G: 'acceleration',
    FPS2: 'feet per second squared',
    MPS2: 'meters per second squared',
    DEGREE_S2: 'degrees per second squared',
    KT_S: 'knots per second',
    # Angles:
    DEGREE: 'degrees',
    RADIAN: 'radians',
    DEGREE_S: 'degrees per second',
    RADIAN_S: 'radians per second',
    # Density:
    KG_LITER: 'kilograms per liter',
    LB_GALLON: 'pounds per gallon',
    # Electricity:
    AMP: 'amperes',
    VOLT: 'volts',
    KVA: 'kilovolt-amps',
    OHM: 'ohms',
    MILLIVOLT: 'millivolts',
    MILLIAMP: 'milliamperes',
    MICROAMP: 'microamperes',
    # Energy
    JOULE: 'joule',
    KJ: 'kilojoule',
    MJ: 'megajoule',
    # Flow (Mass):
    LB_H: 'pounds per hour',
    LB_MIN: 'pounds per minute',
    KG_H: 'pounds per kilogram',
    TONNE_H: 'tonnes per hour',
    # Flow (Volume):
    PINT_H: 'pints per hour',
    QUART_H: 'quarts per hour',
    GALLON_H: 'gallons per hour',
    LITER_H: 'liters per hour',
    # Force:
    LBF: 'pound-force',
    KGF: 'kilogram-force',
    DECANEWTON: 'decanewton',
    NEWTON: 'newton',
    # Frequency:
    HZ: 'hertz',
    KHZ: 'kilohertz',
    MHZ: 'megahertz',
    GHZ: 'gigahertz',
    # Length:
    FT: 'feet',
    METER: 'meters',
    KM: 'kilometers',
    MILE: 'miles',
    NM: 'nautical miles',
    INCH: 'inches',
    MILLIMETER: 'millimeters',
    MIL: 'mils',
    # Mass:
    LB: 'pounds',
    KG: 'kilograms',
    SLUG: 'slugs',
    TONNE: 'tonnes',
    # Pressure:
    INHG: 'inches of mercury',
    PASCAL: 'pascals',
    HECTOPASCAL: 'hectopascals',
    MILLIBAR: 'millibars',
    PSI: 'pounds per square inch',
    PSIA: 'pounds per square inch (absolute)',
    PSID: 'pounds per square inch (differential)',
    PSIG: 'pounds per square inch (gauge)',
    PSI_MINUTE: 'pounds per square inch per minute',
    BAR: 'bar',
    LB_FT2: 'pounds per square foot',
    # Speed:
    KT: 'knots',
    MPH: 'miles per hour',
    FPM: 'feet per minute',
    FPS: 'feet per second',
    IPS: 'inches per second',
    METER_S: 'meters per second',
    MACH: 'Mach',
    RPM: 'revolutions per minute',
    # Temperature:
    CELSIUS: 'degrees Celsius',
    FAHRENHEIT: 'degrees Fahrenheit',
    KELVIN: 'degrees Kelvin',
    RANKINE: 'degrees Rankine',
    # Time:
    HOUR: 'hours',
    MINUTE: 'minutes',
    SECOND: 'seconds',
    DAY: 'days',
    WEEK: 'weeks',
    MONTH: 'months',
    YEAR: 'years',
    # Torque:
    FT_LB: 'foot-pounds',
    IN_LB: 'inch-pounds',
    IN_OZ: 'inch-ounces',
    # Volume:
    PINT: 'pints',
    QUART: 'quarts',
    GALLON: 'gallons',
    LITER: 'liters',
    # Other:
    DDM: 'difference in depth of modulation',
    GS_DDM: 'glideslope difference in depth of modulation',
    LOC_DDM: 'localizer difference in depth of modulation',
    DOTS: 'dots',
    TRIM: 'trim',
    CYCLES: 'cycles',
    PERCENT: 'percent',
    NM_KG: 'nautical miles per kilogram',
    DU: 'display unit',
    DI: 'direction/deviation indicator',
    # COUNTS: 'counts',#Readout
    # CU: 'control units',#Readout
    # SCALAR: 'scalar',#Readout
    # UNITS: 'units',#Readout
    # EPR: 'engine pressure ratio',
}


UNIT_PROFILE_CONVERSIONS = {
    US_PROFILE: {
        # Flow (Mass):
        KG_H: LB_H,
        TONNE_H: LB_H,
        # Flow (Volume):
        LITER_H: GALLON_H,
        # Length:
        KM: NM,
        METER: FT,
        MILE: NM,
        # Mass:
        KG: LB,
        TONNE: LB,
        # Pressure:
        HECTOPASCAL: INHG,
        MILLIBAR: INHG,
        PASCAL: INHG,
        # Temperature:
        CELSIUS: FAHRENHEIT,
        KELVIN: FAHRENHEIT,
        RANKINE: FAHRENHEIT,
        # Speed:
        METER_S: FPS,
        MPH: KT,
        # Volume:
        PINT: QUART,
    },
}


##############################################################################
# Functions


def available(values=True):
    '''
    Returns a list of units available that are defined in this module.

    If the ``constants`` flag is set a tuple of the module paired with the
    constant names will be returned instead of the string values.

    :param values: whether to return values (default) or the constants.
    :type values: boolean
    :returns: a list of unit string values or a tuple of module to constants.
    :rtype: iterable
    '''
    import sys
    module = sys.modules[__name__]
    x = dir(module)
    x = list(filter(lambda v: v.isupper() and not v.startswith('_') and not v.endswith('_PROFILE'), x))
    x = list(filter(lambda v: isinstance(getattr(module, v), str), x))
    if values:
        return map(lambda c: getattr(module, c), x)
    else:
        return module, x


def normalise(unit, profile=None):
    '''
    Normalises the provided unit to a well known form.

    :param unit: the unit to normalise.
    :type unit: string
    :param profile: the profile to use for conversion.
    :type profile: string
    :returns: the normalised unit.
    :rtype: string
    '''
    unit = UNIT_CORRECTIONS.get(unit, unit)
    return UNIT_PROFILE_CONVERSIONS.get(profile, {}).get(unit, unit) if profile else unit


def function(unit, output):
    '''
    Looks up the conversion function for the units provided.

    :param unit: the unit to convert from.
    :type unit: string
    :param output: the unit to convert to.
    :type output: string
    :returns: the conversion function
    :rtype: function
    '''
    unit0, unit1 = normalise(unit), normalise(output)

    if unit0 == unit1:
        return lambda v: v

    try:
        return CONVERSION_FUNCTIONS[unit0][unit1]
    except KeyError:
        pass

    try:
        return lambda v: v * CONVERSION_MULTIPLIERS[unit0][unit1]
    except KeyError:
        pass

    return None


def multiplier(unit, output):
    '''
    Looks up the conversion multiplier for the units provided.

    :param unit: the unit to convert from.
    :type unit: string
    :param output: the unit to convert to.
    :type output: string
    :returns: the conversion multiplier
    :rtype: float
    '''
    unit0, unit1 = normalise(unit), normalise(output)
    return 1 if unit == output else CONVERSION_MULTIPLIERS[unit0][unit1]


def convert(value, unit, output):
    '''
    Converts a value from one unit to another.

    :param value: the value to convert.
    :type value: numeric
    :param unit: the unit to convert from.
    :type unit: string
    :param output: the unit to convert to.
    :type output: string
    :returns: the value altered to new units
    :rtype: numeric
    :raises: ValueError -- if any of the units are not known.
    '''
    unit0, unit1 = normalise(unit), normalise(output)

    if unit0 == unit1:
        return value

    # XXX: Probably ought to preserve decimal type for precision?
    if isinstance(value, decimal.Decimal):
        value = float(value)

    try:
        if unit0 in CONVERSION_FUNCTIONS:
            return function(unit0, unit1)(value)
        if unit0 in CONVERSION_MULTIPLIERS:
            return value * multiplier(unit0, unit1)
        raise ValueError('Unknown input unit: %s' % unit0)
    except KeyError:
        raise ValueError('Unknown output unit: %s' % unit1)


def localise(value, unit, profile, reverse=False):
    '''
    Converts a value from one unit to another based on a chosen localisation.

    :param value: the value to convert.
    :type value: numeric
    :param unit: the unit to convert from.
    :type unit: string
    :param profile: the profile to use for conversion.
    :type profile: string
    :param reverse: convert the value back from the localised value.
    :type reverse: boolean
    :returns: the value altered to new units
    :rtype: numeric
    '''
    output = normalise(unit, profile=profile)
    if reverse:
        unit, output = output, unit
    return (value, unit) if output == unit else (convert(value, unit, output), output)
