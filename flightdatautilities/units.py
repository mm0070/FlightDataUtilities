# -*- coding: utf-8 -*-
##############################################################################

'''
Provides utilities for handling conversions between units of flight data.

The following links are useful resources:

 - http://en.wikipedia.org/wiki/Conversion_of_units

'''

##############################################################################
# Imports


import math


##############################################################################
# Constants

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
RMS_G = 'RMS g'

# Angles:
DEGREE = 'deg'  # [1]
RADIAN = 'rad'
DEGREE_S = 'deg/s'  # [1]

# Electricity:
AMP = 'A'
VOLT = 'V'
KVA = 'kVA'
OHM = 'ohm'  # [1]
MILLIVOLT = 'mV'
MILLIAMP = 'mA'
MICROAMP = 'uA'  # [1]

# Flow (Volume):
LB_H = 'lb/h'
KG_H = 'kg/h'
TONNE_H = 't/h'

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

# Mass:
LB = 'lb'
KG = 'kg'
TONNE = 't'

# Pressure:
INHG = 'inHg'
MILLIBAR = 'mb'
PASCAL = 'Pa'
HECTOPASCAL = 'hPa'
PSI = 'psi'
PSIA = 'psia'
PSID = 'psid'
PSIG = 'psig'

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


CONVERSION_MULTIPLIERS = {
    # Flow (Volume):
    LB_H: {
        KG_H: 0.45359237,
        TONNE_H: 0.00045359237,
    },
    KG_H: {
        LB_H: 2.204622622,
        TONNE_H: 0.001,
    },
    TONNE_H: {
        LB_H: 2204.622621849,
        KG_H: 1000.0,
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
    },
    METER: {
        FT: 3.280839895,
        KM: 0.001,
        MILE: 0.000621371,
        NM: 0.000539957,
    },
    KM: {
        FT: 3280.839895013,
        METER: 1000.0,
        MILE: 0.621371192,
        NM: 0.539956803,
    },
    MILE: {
        FT: 5280.0,
        METER: 1609.344,
        KM: 1.609344,
        NM: 0.868976242,
    },
    NM: {
        FT: 6076.11548554,
        METER: 1852.0,
        KM: 1.852,
        MILE: 1.150779448,
    },
    # Mass:
    LB: {
        KG: 0.45359237,
        TONNE: 0.00045359237,
    },
    KG: {
        LB: 2.204622622,
        TONNE: 0.001,
    },
    TONNE: {
        LB: 2204.622621849,
        KG: 1000.0,
    },
    # Pressure:
    INHG: {
        HECTOPASCAL: 33.86389,
        MILLIBAR: 33.86389,
        PSI: 0.491154221,
    },
    HECTOPASCAL: {
        INHG: 0.02952998,
        MILLIBAR: 1.0,
        PSI: 0.014503774,
    },
    MILLIBAR: {
        INHG: 0.02952998,
        HECTOPASCAL: 1.0,
        PSI: 0.014503774,
    },
    PSI: {
        INHG: 2.036020375,
        HECTOPASCAL: 68.94757,
        MILLIBAR: 68.94757,
    },
    # Speed:
    KT: {
        MPH: 1.150778454,
        FPM: 101.268503937,
    },
    MPH: {
        KT: 0.868976993,
        FPM: 88.0,
    },
    FPM: {
        KT: 0.009874739,
        MPH: 0.011363636,
        FPS: 60.0,
    },
    FPS: {
        FPM: 1 / 60.0,
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
    # Volume:
    PINT: {
        QUART: 0.5,
        GALLON: 0.125,
    },
    QUART: {
        PINT: 2,
        GALLON: 0.25
    },
    GALLON: {
        PINT: 8,
        QUART: 4,
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
        RADIAN: math.radians,
    },
    RADIAN: {
        DEGREE: math.degrees,
    },
    # Temperature:
    CELSIUS: {
        FAHRENHEIT: lambda v: v * 9.0 / 5.0 + 32.0,
        KELVIN: lambda v: v + 273.15,
    },
    FAHRENHEIT: {
        CELSIUS: lambda v: (v - 32.0) * 5.0 / 9.0,
        KELVIN: lambda v: (v + 459.67) * 5.0 / 9.0,
    },
    KELVIN: {
        CELSIUS: lambda v: v - 273.15,
        FAHRENHEIT: lambda v: v * 9.0 / 5.0 - 459.67,
    },
}


STANDARD_CONVERSIONS = {
    # Angle:
    RADIAN: DEGREE,
    # Electricity:
    MICROAMP: DOTS,
    MILLIVOLT: DOTS,
    # Flow (Volume):
    LB_H: KG_H,
    TONNE_H: KG_H,
    # Force:
    LBF: DECANEWTON,
    KGF: DECANEWTON,
    # Length:
    MILE: NM,
    # Mass:
    LB: KG,
    TONNE: KG,
    # Pressure:
    INHG: MILLIBAR,
    HECTOPASCAL: MILLIBAR,
    # Temperature:
    FAHRENHEIT: CELSIUS,
    KELVIN: CELSIUS,
    # Volume:
    PINT: QUART,
    # Other:
    GS_DDM: DOTS,
    LOC_DDM: DOTS,
}


UNIT_CORRECTIONS = {
    # Acceleration:
    'G': G,
    'G\'s': G,
    'g\'s': G,
    # Angles:
    'DEG': DEGREE,
    'Deg': DEGREE,
    'degree': DEGREE,
    'degrees': DEGREE,
    'radian': RADIAN,
    'radians': RADIAN,
    'DEG/S': DEGREE_S,
    'DEG/SEC': DEGREE_S,
    'deg/se': DEGREE_S,
    'deg/sec': DEGREE_S,
    'degree/s': DEGREE_S,
    'degree/sec': DEGREE_S,
    'degrees/s': DEGREE_S,
    'degrees/sec': DEGREE_S,
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
    # Flow (Volume):
    'lb/hr': LB_H,
    'lbs/h': LB_H,
    'lbs/hr': LB_H,
    'pph': LB_H,
    'LB/HR': LB_H,
    'LBS/H': LB_H,
    'LBS/HR': LB_H,
    'PPH': LB_H,
    'kg/hr': KG_H,
    'kgs/h': KG_H,
    'kgs/hr': KG_H,
    'kph': KG_H,
    'KG/HR': KG_H,
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
    # Mass:
    'KGS': KG,
    'Kgs': KG,
    'kgs': KG,
    'LBS': LB,
    'Lbs': LB,
    'lbs': LB,
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
    'In-Hg': INHG,
    'In.Hg': INHG,
    'IN HG': INHG,
    'pa': PASCAL,
    'hpa': HECTOPASCAL,
    'Hpa': HECTOPASCAL,
    'HPa': HECTOPASCAL,
    'MB': MILLIBAR,
    'Mb': MILLIBAR,
    'mB': MILLIBAR,
    'mbar': MILLIBAR,
    'PSI': PSI,
    'PSIA': PSIA,
    'PSID': PSID,
    'PSIG': PSIG,
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
    'DEGC': CELSIUS,
    'DEG C': CELSIUS,
    'degree C': CELSIUS,
    'degrees C': CELSIUS,
    'deg. C': CELSIUS,
    'deg C': CELSIUS,
    'degree F': FAHRENHEIT,
    'degrees F': FAHRENHEIT,
    'deg. F': FAHRENHEIT,
    'deg F': FAHRENHEIT,
    'degree K': KELVIN,
    'degrees K': KELVIN,
    'deg. K': KELVIN,
    'deg K': KELVIN,
    # Time:
    'day': DAY,
    'days': DAY,
    'DAY': DAY,
    'DAYS': DAY,
    'hr': HOUR,
    'hrs': HOUR,
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
    'wks': WEEK,
    'week': WEEK,
    'weeks': WEEK,
    'yrs': YEAR,
    'year': YEAR,
    'years': YEAR,
    'Years': YEAR,
    'YR': YEAR,
    'YEAR': YEAR,
    'YEARS': YEAR,
    # Torque:
    'ft-lb': FT_LB,
    'ft-lbs': FT_LB,
    'ft.lbs': FT_LB,
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
    'QT. US': QUART,
    'qt (US)': QUART,
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
    'cycle': CYCLES,
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
    '%Rpm': PERCENT,
    '%open': PERCENT,
    '%stroke': PERCENT,
    '% Open': PERCENT,
    '% OPEN': PERCENT,
    '%full': PERCENT,
    '% full': PERCENT,
    '%Full': PERCENT,
    '% FULL': PERCENT,
}


UNIT_CATEGORIES = {
    'Acceleration': (G, RMS_G),
    'Angles': (DEGREE, RADIAN, DEGREE_S),
    'Electricity': (AMP, VOLT, KVA, OHM, MILLIVOLT, MICROAMP, MILLIAMP),
    'Flow (Volume)': (LB_H, KG_H, TONNE_H),
    'Force': (LBF, KGF, DECANEWTON, NEWTON),
    'Frequency': (HZ, KHZ, MHZ, GHZ),
    'Length': (FT, METER, KM, MILE, NM, INCH),
    'Mass': (LB, KG, TONNE),
    'Pressure': (INHG, PASCAL, HECTOPASCAL, MILLIBAR, PSI, PSIA, PSID, PSIG),
    'Speed': (KT, MPH, FPM, FPS, IPS, METER_S, MACH, RPM),
    'Temperature': (CELSIUS, FAHRENHEIT, KELVIN),
    'Time': (HOUR, MINUTE, SECOND, DAY, WEEK, MONTH, YEAR),
    'Torque': (FT_LB, IN_OZ),
    'Volume': (PINT, QUART, GALLON, LITER),
    'Other': (DDM, GS_DDM, LOC_DDM, DOTS, TRIM, CYCLES, PERCENT),
}


UNIT_DESCRIPTIONS = {
    # Acceleration:
    G: 'acceleration',
    RMS_G: 'root-mean-squared acceleration',
    # Angles:
    DEGREE: 'degrees',
    RADIAN: 'radians',
    DEGREE_S: 'degrees per second',
    # Electricity:
    AMP: 'amperes',
    VOLT: 'volts',
    KVA: 'kilovolt-amps',
    OHM: 'ohms',
    MILLIVOLT: 'millivolts',
    MILLIAMP: 'milliamperes',
    MICROAMP: 'microamperes',
    # Flow (Volume):
    LB_H: 'pounds per hour',
    KG_H: 'pounds per kilogram',
    TONNE_H: 'tonnes per hour',
    # Force:
    LBF: 'pound-force',
    KGF: 'kilogram-force',
    DECANEWTON: 'decanewton',
    NEWTON: 'Newton',
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
    # Mass:
    LB: 'pounds',
    KG: 'kilograms',
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
    x = filter(lambda v: v.isupper() and not v.startswith('_'), x)
    x = filter(lambda v: isinstance(getattr(module, v), basestring), x)
    if values:
        return map(lambda c: getattr(module, c), x)
    else:
        return module, x


def normalise(unit):
    '''
    Normalises the provided unit to a well known form.

    :param unit: the unit to normalise.
    :type unit: string
    :returns: the normalised unit.
    :rtype: string
    '''
    return UNIT_CORRECTIONS.get(unit, unit)


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
    return CONVERSION_MULTIPLIERS[normalise(unit)][normalise(output)]


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
    unit = normalise(unit)
    output = normalise(output)
    if unit == output:
        return value
    try:
        if unit in CONVERSION_FUNCTIONS:
            return function(unit, output)(value)
        if unit in CONVERSION_MULTIPLIERS:
            return value * multiplier(unit, output)
        raise ValueError('Unknown unit: %s' % unit)
    except KeyError:
        raise ValueError('Unknown output unit: %s' % output)


##############################################################################
# vim:et:ft=python:nowrap:sts=4:sw=4:ts=4
