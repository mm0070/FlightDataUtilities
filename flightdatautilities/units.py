'''
Provides utilities for handling conversions between units of flight data.

The following links are useful resources:

 - http://en.wikipedia.org/wiki/Conversion_of_units

'''

import decimal

import numpy as np

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


# This is the list of the standard forms for each unit.
# See also a list of non-standard but accepted forms below.

# Acceleration:
G = 'g'  # [2]
FPS2 = 'ft/s/s'
MPS2 = 'm/s/s'
DEGREE_S2 = 'deg/s/s'
KT_S = 'kt/s'

# Angles:
DEGREE = 'deg'  # [1]
RADIAN = 'rad'

# Angular velocity
DEGREE_S = 'deg/s'  # [1]
RADIAN_S = 'rad/s'

# Angular acceleration:
RPM_S = 'rpm/s'
DEGREE_S2 = 'deg/s/s'

# Density:
KG_LITER = 'kg/l'
LB_GALLON = 'lb/gal'

# Electricity:
AMP = 'A'
VOLT = 'V'
KVA = 'kVA'
OHM = 'ohm'  # [1]
MICROVOLT = 'microV'
MILLIVOLT = 'mV'
MILLIAMP = 'mA'
MICROAMP = 'uA'  # [1]

# Energy
JOULE = 'J'
KJ = 'kJ'
MJ = 'MJ'

# Flow (Mass):
LB_S = 'lb/s'
LB_MIN = 'lb/min'
LB_H = 'lb/h'
KG_S = 'kg/s'
KG_H = 'kg/h'
TONNE_H = 't/h'

# Flow (Volume):
PINT_H = 'pt/h'  # [3]
QUART_H = 'qt/h'  # [3]
GALLON_S = 'gal/s'
GALLON_H = 'gal/h'  # [3]
CUFT_M = 'cu.ft/min'
LITER_H = 'l/h'

# Force:
LBF = 'lbf'
KGF = 'kgf'
DECANEWTON = 'daN'
NEWTON = 'N'

# Power:
KW = 'kW'

# Frequency:
HZ = 'Hz'
KHZ = 'kHz'
MHZ = 'MHz'
GHZ = 'GHz'

# Length:
FT = 'ft'
FL = 'fl'
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
KILOPASCAL = 'kPa'
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
MILLIMACH = 'milliMach'  # [0]
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

# Non-dimensional:
DDM = 'ddm'
GS_DDM = 'gs-ddm'
LOC_DDM = 'loc-ddm'
DOTS = 'dots'
TRIM = 'trim'
CYCLES = 'cycles'
PERCENT = '%'
NM_KG = 'NM/kg'
DU = 'du'
DI = 'di'
MODE = 'mode' # e.g. autopilot mode enumeration
NUM = 'number' # e.g. engine serial numbers
UNITS = 'units'
CU = 'cu'
SCALAR = 'scalar'
EPR = 'epr'


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
    LB_S: {
        LB_MIN: 60.0,
        LB_H: 3600.0,
        KG_S: 0.45359237,
        KG_H: 1632.932532,
        TONNE_H: 1.632932532,
    },
    LB_MIN: {
        LB_S: 0.0166666667,
        LB_H: 60,
        KG_S: 0.007559873,
        KG_H: 27.2155422,
        TONNE_H: 0.0272155422,
    },
    LB_H: {
        LB_S: 0.0002777777777777778,
        LB_MIN: 0.0166666667,
        KG_S: 0.00012599788055555556,
        KG_H: 0.45359237,
        TONNE_H: 0.00045359237,
    },
    KG_S: {
        LB_S: 2.204622622,
        LB_MIN: 132.2773573,
        LB_H: 7936.641439,
        KG_H: 3600.0,
        TONNE_H: 3.6,
    },
    KG_H: {
        LB_S: 0.000612395,
        LB_MIN: 0.0367437104,
        LB_H: 2.204622622,
        KG_H: 0.0002777777777777778,
        TONNE_H: 0.001,
    },
    TONNE_H: {
        LB_S: 0.612395173,
        LB_MIN: 36.7437104,
        LB_H: 2204.622621849,
        KG_S: 0.2777777777777778,
        KG_H: 1000.0,
    },
    # Flow (Volume):
    PINT_H: {
        QUART_H: 0.5,
        GALLON_S: 450.0,
        GALLON_H: 0.125,
        CUFT_M: 0.0002785,
        LITER_H: 0.473176,
    },
    QUART_H: {
        PINT_H: 2,
        GALLON_S: 900.0,
        GALLON_H: 0.25,
        CUFT_M: 0.000557,
        LITER_H: 0.946353,
    },
    GALLON_S: {
        PINT_H: 0.002222222,
        QUART_H: 0.001111111,
        GALLON_H: 0.000277778,
        CUFT_M: 6.18889E-07,
        LITER_H: 0.001051503,
    },
    GALLON_H: {
        PINT_H: 8,
        QUART_H: 4,
        GALLON_S: 3600.0,
        CUFT_M: 0.002228,
        LITER_H: 3.78541,
    },
    CUFT_M: {
        PINT_H: 3590.664273,
        QUART_H: 1795.332136,
        GALLON_S: 1615798.923,
        GALLON_H: 448.8330341,
        LITER_H: 1.699,
    },
    LITER_H: {
        PINT_H: 2.11338,
        QUART_H: 1.05669,
        GALLON_S: 951.0198367,
        GALLON_H: 0.264172,
        CUFT_M: 0.0005886,
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
        FL: 0.01,
        METER: 0.3048,
        KM: 0.0003048,
        MILE: 0.00018939,
        NM: 0.000164579,
        MILLIMETER: 304.8,
    },
    FL: {
        FT: 100.0,
        METER: 30.48,
        KM: 0.03048,
        MILE: 0.018939,
        NM: 0.0164579,
        MILLIMETER: 30480.0,
    },
    METER: {
        FT: 3.280839895,
        FL: 0.03280839895,
        KM: 0.001,
        MILE: 0.000621371,
        NM: 0.000539957,
        MILLIMETER: 1000,
    },
    KM: {
        FT: 3280.839895013,
        FL: 32.80839895013,
        METER: 1000,
        MILE: 0.621371192,
        NM: 0.539956803,
        MILLIMETER: 1000000,
    },
    MILE: {
        FT: 5280,
        FL: 52.8,
        METER: 1609.344,
        KM: 1.609344,
        NM: 0.868976242,
        MILLIMETER: 1609344,
    },
    NM: {
        FT: 6076.11548554,
        FL: 60.7611548554,
        METER: 1852,
        KM: 1.852,
        MILE: 1.150779448,
        MILLIMETER: 1852000,
    },
    MILLIMETER: {
        FT: 0.003280839895,
        FL: 0.00003280839895,
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
        KILOPASCAL: 0.001,
        PSI: 0.00014503774,
    },
    HECTOPASCAL: {
        INHG: 0.02952998,
        MILLIBAR: 1,
        PASCAL: 100,
        PSI: 0.014503774,
    },
    KILOPASCAL: {
        INHG: 0.2952998,
        MILLIBAR: 10,
        PASCAL: 1000,
        PSI: 0.14503774,
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
    MACH: {
        MILLIMACH: 1000.0,
    },
    MILLIMACH: {
        MACH: 0.001,
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
    MICROVOLT: {
        DOTS: 0.00001333333333333,
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
    # Angular velocity
    DEGREE_S: {
        RADIAN_S: np.radians,
    },
    RADIAN_S: {
        DEGREE_S: np.degrees,
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
    # Angular velocity
    RADIAN_S: DEGREE_S,
    # Electricity:
    MICROAMP: DOTS,
    MICROVOLT: DOTS,
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
    KILOPASCAL: MILLIBAR,
    # Speed:
    MILLIMACH: MACH,
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


# This is the list of alternative forms of the units,
# mapped against the identifier for the standard form.
UNIT_CORRECTIONS = {
    # Acceleration:
    'G': G,
    'G\'S': G,
    'G\'s': G,
    'g\'s': G,
    'Std G': G,
    'ft/sec^2': FPS2,
    'ft/sec/sec': FPS2,
    'm/s²': MPS2,
    'm/s2': MPS2,
    b'm/s\xc2\xb2': MPS2,
    'kt/sec': KT_S,
    'kts/sec': KT_S,
    'kts/s': KT_S,
    '°/s2': DEGREE_S2,
    'Degree/Sec2': DEGREE_S2,
    'deg/s^2': DEGREE_S2,
    'Deg/S2': DEGREE_S2,
    'deg/s2': DEGREE_S2,
    'deg/sec/sec': DEGREE_S2,
    'deg/sec2': DEGREE_S2,
    'deg/sec^2': DEGREE_S2,
    # Angles:
    '\xb0': DEGREE,  # degree symbol
    '°': DEGREE,
    '0': DEGREE,
    '°surface': DEGREE,
    '0surface': DEGREE,
    '0 surface': DEGREE,
    'DEG': DEGREE,
    'Deg': DEGREE,
    'Deg Angle': DEGREE,
    'deg sync': DEGREE,
    'DegSuf': DEGREE,
    'Degree': DEGREE,
    'Degrees': DEGREE,
    'Degrees E of N': DEGREE,
    'Degrees R': DEGREE,
    'Degrees Right': DEGREE,
    'Degrees RVDT': DEGREE,
    'Degrees upward': DEGREE,
    'degs.': DEGREE,
    'Degree': DEGREE,
    'degree': DEGREE,
    'Degrees': DEGREE,
    'degrees': DEGREE,
    'radian': RADIAN,
    'radians': RADIAN,
    '°/s': DEGREE_S,
    'DEG/S': DEGREE_S,
    'DEG/SEC': DEGREE_S,
    'DPS': DEGREE_S,
    'Degrees/sec': DEGREE_S,
    'Deg/S': DEGREE_S,
    'Deg P/S': DEGREE_S,
    'Deg\s': DEGREE_S,
    'deg\'s': DEGREE_S,
    'Deg/s': DEGREE_S,
    'deg/se': DEGREE_S,
    'Deg/Sec': DEGREE_S,
    'deg/sec': DEGREE_S,
    'degree/s': DEGREE_S,
    'Degree/Sec': DEGREE_S,
    'degree/sec': DEGREE_S,
    'degrees/s': DEGREE_S,
    'degrees/sec': DEGREE_S,
    'Degrees P/S': DEGREE_S,
    'RAD/S': RADIAN_S,
    'RAD/SEC': RADIAN_S,
    'RPS': RADIAN_S,
    'rad/se': RADIAN_S,
    'rad/sec': RADIAN_S,
    'radian/s': RADIAN_S,
    'radian/sec': RADIAN_S,
    'radians/s': RADIAN_S,
    'radians/sec': RADIAN_S,
    # Angular acceleration:
    'rpm/sec': RPM_S,
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
    'LBS Per Gal': LB_GALLON,
    # Electricity:
    'Amp': AMP,
    'amp': AMP,
    'amps': AMP,
    'Amps': AMP,
    'AMPS': AMP,
    'amperes': AMP,
    'kilovolt-amps': KVA,
    'KVA': KVA,
    'v': VOLT,
    'Volt': VOLT,
    'volt': VOLT,
    'Volts': VOLT,
    'volts': VOLT,
    'voltage': VOLT,
    'Volts RMS': VOLT,
    'Volts AC': VOLT,
    'VAC': VOLT,
    'Volts DC': VOLT,
    'VDC': VOLT,
    'ohms': OHM,
    'mv': MILLIVOLT,
    'millivolts': MILLIVOLT,
    'ua': MICROAMP,
    'microamps': MICROAMP,
    'mA': MILLIAMP,
    'ma': MILLIAMP,
    'milliamps': MILLIAMP,
    # Energy:
    'joule': JOULE,
    'kilojoule': KJ,
    'megajoule': MJ,
    # Flow (Mass):
    'PPS': LB_S,
    'pps': LB_S,
    'lb/hr': LB_H,
    'lbs/h': LB_H,
    'lbs/hr': LB_H,
    'pph': LB_H,
    'LB/HR': LB_H,
    'LBS/H': LB_H,
    'LBS/HR': LB_H,
    'PPH': LB_H,
    'Pounds Per Hour': LB_H,
    'Lbs/Min': LB_MIN,
    'lbs/min': LB_MIN,
    'LBS/MIN': LB_MIN,
    'ppm': LB_MIN,
    'PPM': LB_MIN,
    'KG/S' : KG_S,
    'Kg/Hour': KG_H,
    'Kg/h': KG_H,
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
    'LBF': LBF,
    'Pounds Force': LBF,
    'Pounds-Force': LBF,
    'pound-force': LBF,
    'kilogram-force': KGF,
    'kilopond': KGF,
    'kp': KGF,
    'decanewton': DECANEWTON,
    'dan': DECANEWTON,
    'DAN': DECANEWTON,
    'Newton': NEWTON,
    'Newtons': NEWTON,
    'newton': NEWTON,
    'n': NEWTON,
    # Frequency:
    'hertz': HZ,
    'KHz': KHZ,
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
    'Feet': FT,
    'Feet AGL': FT,
    'Feet MSL': FT,
    'Feets': FT,
    'foot': FT,
    'metre': METER,
    'Meters': METER,
    'Metres': METER,
    'metres': METER,
    'meter': METER,
    'meters': METER,
    'kilometre': KM,
    'kilometres': KM,
    'kilometer': KM,
    'kilometers': KM,
    'mile': MILE,
    'Miles': MILE,
    'miles': MILE,
    'MILE': MILE,
    'MILES': MILE,
    'Nautical Miles': NM,
    'N Miles': NM,
    'Nm': NM,
    'nm': NM,
    'Inch LVDT': INCH,
    'Inches LVDT': INCH,
    'Inches LVDT Disp': INCH,
    'inch': INCH,
    'Inches': INCH,
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
    'Pounds': LB,
    'Slugs': SLUG,
    'slugs': SLUG,
    'tonne': TONNE,
    'tonnes': TONNE,
    # Pressure:
    'Inches HG': INHG,
    'Inches Hg': INHG,
    'in Hg': INHG,
    'IN-HG': INHG,
    'in Hg': INHG,
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
    'hPA': HECTOPASCAL,
    'hpa': HECTOPASCAL,
    'Hpa': HECTOPASCAL,
    'HPa': HECTOPASCAL,
    'HPA': HECTOPASCAL,
    'MB': MILLIBAR,
    'Mb': MILLIBAR,
    'mB': MILLIBAR,
    'mBar': MILLIBAR,
    'mbar': MILLIBAR,
    'Millibars': MILLIBAR,
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
    'Knots': KT,
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
    'Ft/Min': FPM,
    'Ft/min': FPM,
    'Ft/minute': FPM,
    'FEET/MIN': FPM,
    'Feet/Min': FPM,
    'feet/min': FPM,
    'FPM': FPM,
    'Feet P/M': FPM,
    'ft/s': FPS,
    'ft/sec': FPS,
    'feet/sec': FPS,
    'Feet Per Second': FPS,
    'FPS': FPS,
    'in/s': IPS,
    'In/Sec': IPS,
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
    'Millimach': MILLIMACH,
    'millimach': MILLIMACH,
    'RPM': RPM,
    'Rpm': RPM,
    # Temperature:
    b'\xb0C': CELSIUS,
    '\xb0C': CELSIUS,
    '°C': CELSIUS,
    '° C': CELSIUS,
    '0C': CELSIUS,
    '\ufffdC': CELSIUS,  # �C is probably °C (see AE-2886)
    b'\xf8C': CELSIUS,
    'C Degrees': CELSIUS,
    'C° deg': CELSIUS,
    'DEGC': CELSIUS,
    'DEG.C': CELSIUS,
    'DEG C': CELSIUS,
    'Deg C': CELSIUS,
    'Deg \'C': CELSIUS,
    'Deg  \'C': CELSIUS,
    'Degress Celsius': CELSIUS,
    'Degrees Celcius': CELSIUS,
    'Degrees Celsius': CELSIUS,
    'degree C': CELSIUS,
    'Degrees C': CELSIUS,
    'degrees C': CELSIUS,
    'deg. C': CELSIUS,
    'degs. C': CELSIUS,
    'deg C': CELSIUS,
    'degC': CELSIUS,
    'degree F': FAHRENHEIT,
    'degrees F': FAHRENHEIT,
    'deg. F': FAHRENHEIT,
    'Deg F': FAHRENHEIT,
    'deg F': FAHRENHEIT,
    'Fahrenheit': FAHRENHEIT,
    'Deg K': KELVIN,
    'degree K': KELVIN,
    'degrees K': KELVIN,
    'deg. K': KELVIN,
    'deg K': KELVIN,
    'deg R': RANKINE,
    'degRankine': RANKINE,
    # Time:
    'Day': DAY,
    'day': DAY,
    'days': DAY,
    'DAY': DAY,
    'DAYS': DAY,
    'DD': DAY,
    'hr': HOUR,
    'hrs': HOUR,
    'Hour': HOUR,
    'hour': HOUR,
    'Hours': HOUR,
    'hours': HOUR,
    'HH': HOUR,
    'HR': HOUR,
    'HRS': HOUR,
    'Hrs': HOUR,
    'HOUR': HOUR,
    'HOURS': HOUR,
    'mn': MINUTE,
    'mins': MINUTE,
    'MIN': MINUTE,
    'MINS': MINUTE,
    'MINUTE': MINUTE,
    'MINUTES': MINUTE,
    'Minutes': MINUTE,
    'Mon': MONTH,
    'mon': MONTH,
    'mth': MONTH,
    'Month': MONTH,
    'month': MONTH,
    'months': MONTH,
    'MM': MONTH,
    'MON': MONTH,
    'MONTH': MONTH,
    'MONTHS': MONTH,
    'Sec': SECOND,
    'sec': SECOND,
    'secs': SECOND,
    'second': SECOND,
    'Seconds': SECOND,
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
    'Year': YEAR,
    'year': YEAR,
    'years': YEAR,
    'Years': YEAR,
    'YR': YEAR,
    'YY': YEAR,
    'YEAR': YEAR,
    'YEARS': YEAR,
    # Torque:
    'FT-LBS': FT_LB,
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
    'Qt': QUART,
    'QTS': QUART,
    'QT US': QUART,
    'QT. US': QUART,
    'qt (US)': QUART,
    'Us/Qt': QUART,
    'Quart': QUART,
    'quart': QUART,
    'quarts': QUART,
    'QUART': QUART,
    'QUARTS': QUART,
    'US QUARTS': QUART,
    'US Quarts': QUART,
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
    'Liter': LITER,
    'liter': LITER,
    'liters': LITER,
    'litre': LITER,
    'litres': LITER,
    # Flow (Volume)
    'Pints/Hr': PINT_H,
    # Other:
    'DDM': DDM,
    'ddm R': DDM,
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
    'Percent': PERCENT,
    'Percent Open': PERCENT,
    'percent': PERCENT,
    '% Full': PERCENT,
    '% N1': PERCENT,
    '% N1 RPM': PERCENT,
    '% N2 RPM': PERCENT,
    '% N3 RPM': PERCENT,
    '% Load': PERCENT,
    '% Open': PERCENT,
    '% MAC': PERCENT,
    '% Mean': PERCENT,
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
    'MAC %': PERCENT,
    '%Load': PERCENT,
    'LOAD': PERCENT,
    '%LOAD': PERCENT,
    '%Rpm': PERCENT,
    '%open': PERCENT,
    '%stroke': PERCENT,
    '% Open': PERCENT,
    '% Open/Degrees': PERCENT,
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
    'Cu': CU,
    'CU': CU,
    'Du': DU,
    'DU': DU,
    'Di': DI,
    'DI': DI,
}


UNIT_CATEGORIES = {
    'Acceleration': (G, FPS2, MPS2, DEGREE_S2, KT_S),
    'Angles': (DEGREE, RADIAN, DEGREE_S, RADIAN_S),
    'Angular acceleration': (RPM_S,),
    'Density': (KG_LITER, LB_GALLON),
    'Electricity': (AMP, VOLT, KVA, OHM, MICROVOLT, MILLIVOLT, MICROAMP, MILLIAMP),
    'Energy': (JOULE, KJ, MJ),
    'Flow (Mass)': (LB_S, LB_MIN, LB_H, KG_S, KG_H, TONNE_H),
    'Flow (Volume)': (PINT_H, QUART_H, GALLON_S, GALLON_H, CUFT_M, LITER_H),
    'Force': (LBF, KGF, DECANEWTON, NEWTON),
    'Frequency': (HZ, KHZ, MHZ, GHZ),
    'Length': (FT, FL, METER, KM, MILE, NM, INCH, MILLIMETER),
    'Mass': (LB, KG, SLUG, TONNE),
    'Power': (KW,),
    'Pressure': (INHG, PASCAL, HECTOPASCAL, KILOPASCAL, BAR, MILLIBAR, PSI, PSIA, PSID, PSIG, PSI_MINUTE, LB_FT2),
    'Speed': (KT, MPH, FPM, FPS, IPS, METER_S, MACH, MILLIMACH, RPM),
    'Temperature': (CELSIUS, FAHRENHEIT, KELVIN, RANKINE),
    'Time': (HOUR, MINUTE, SECOND, DAY, WEEK, MONTH, YEAR),
    'Torque': (FT_LB, IN_LB, IN_OZ),
    'Volume': (PINT, QUART, GALLON, LITER),
    'Other': (DDM, GS_DDM, LOC_DDM, DOTS, TRIM, CYCLES, PERCENT, NM_KG, DU, DI, MIL, CU, SCALAR, MODE, NUM, UNITS, EPR),
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
    # Angular acceleration:
    RPM_S: 'rpm per second',
    # Density:
    KG_LITER: 'kilograms per liter',
    LB_GALLON: 'pounds per gallon',
    # Electricity:
    AMP: 'amperes',
    VOLT: 'volts',
    KVA: 'kilovolt-amps',
    OHM: 'ohms',
    MICROVOLT: 'microvolts',
    MILLIVOLT: 'millivolts',
    MILLIAMP: 'milliamperes',
    MICROAMP: 'microamperes',
    # Energy
    JOULE: 'joule',
    KJ: 'kilojoule',
    MJ: 'megajoule',
    # Flow (Mass):
    LB_S: 'pounds per second',
    LB_MIN: 'pounds per minute',
    LB_H: 'pounds per hour',
    KG_S: 'kilograms per second',
    KG_H: 'kilograms per hour',
    TONNE_H: 'tonnes per hour',
    # Flow (Volume):
    PINT_H: 'pints per hour',
    QUART_H: 'quarts per hour',
    GALLON_S: 'gallons per second',
    GALLON_H: 'gallons per hour',
    CUFT_M: 'cubic feet per minute',
    LITER_H: 'liters per hour',
    # Force:
    LBF: 'pound-force',
    KGF: 'kilogram-force',
    DECANEWTON: 'decanewton',
    NEWTON: 'newton',
    # Power:
    KW: 'kW',
    # Frequency:
    HZ: 'hertz',
    KHZ: 'kilohertz',
    MHZ: 'megahertz',
    GHZ: 'gigahertz',
    # Length:
    FT: 'feet',
    FL: 'flight level',
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
    KILOPASCAL: 'kilopascals',
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
    MILLIMACH: 'milliMach',
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
    CU: 'control units',
    SCALAR: 'scalar',
    MODE: 'mode',
    NUM: 'number',
    UNITS: 'units',
    EPR: 'engine pressure ratio',
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
