# -*- coding: utf-8 -*-
# vim:et:ft=python:nowrap:sts=4:sw=4:ts=4
##############################################################################

'''
Flight Data Utilities: Date Extensions
'''

##############################################################################
# Imports


import __builtin__

import numpy as np
import operator

from datetime import date, datetime, time, timedelta


##############################################################################
# Exports


__all__ = ['is_day', 'range']


##############################################################################
# Functions


def is_day(when, latitude, longitude, twilight='civil'):
    '''
    This simple function takes the date, time and location of any point on
    the earth and return True for day and False for night.

    :param when: Date and time in datetime format
    :param longitude: Longitude in decimal degrees, east is positive
    :param latitude: Latitude in decimal degrees, north is positive
    :param twilight: optional twilight setting. Default='civil', None, 'nautical' or 'astronomical'.

    :raises ValueError if twilight not recognised.

    :returns boolean True = daytime (including twilight), False = nighttime.

    This function is drawn from Jean Meeus' Astronomial Algorithms as
    implemented by Michel J. Anders. In accordance with his Collective
    Commons license, the reworked function is being released under the OSL
    3.0 license by FDS as a part of the POLARIS project.

    For FDM purposes, the actual time of sunrise and sunset is of no
    interest, so function 12.6 is adapted to give just the day/night
    decision, with allowance for different, generally recognised, twilight
    tolerances.

    FAA Regulation FAR 1.1 defines night as: "Night means the time between
    the end of evening civil twilight and the beginning of morning civil
    twilight, as published in the American Air Almanac, converted to local
    time.

    EASA EU OPS 1 Annex 1 item (76) states: 'night' means the period between
    the end of evening civil twilight and the beginning of morning civil
    twilight or such other period between sunset and sunrise as may be
    prescribed by the appropriate authority, as defined by the Member State;

    CAA regulations confusingly define night as 30 minutes either side of
    sunset and sunrise, then include a civil twilight table in the AIP.

    With these references, it was decided to make civil twilight the default.

    Sources:

    - http://www.esrl.noaa.gov/gmd/grad/solcalc/main.js
    - http://www.esrl.noaa.gov/gmd/grad/solcalc/calcdetails.html
    - http://michelanders.blogspot.co.uk/2010/12/calulating-sunrise-and-sunset-in-python.html
    '''
    if latitude is np.ma.masked or longitude is np.ma.masked:
        return np.ma.masked

    day = when.toordinal() - 693594
    t = when.time()
    time = (t.hour + t.minute / 60.0 + t.second / 3600.0) / 24.0

    # calculate julian day and century:
    jd = day + 2415018.5 + time
    jc = (jd - 2451545.0) / 36525.0

    # siderial time at greenwich
    gstime = (280.46061837 + 360.98564736629 * (jd - 2451545.0) + (0.0003879331 - jc / 38710000) * jc ** 2) % 360.0

    # geometric mean longitude sun (deg)
    l0 = (280.46646 + jc * (36000.76983 + jc * 0.0003032)) % 360

    # geometric mean anomaly sun (radians)
    m = np.radians(357.52911 + jc * (35999.05029 - 0.0001537 * jc))

    # sun equation of center
    sin1m, sin2m, sin3m = (np.sin(i * m) for i in __builtin__.range(1, 4))
    c = sin1m * (1.914602 - jc * (0.004817 + 0.000014 * jc)) + sin2m * (0.019993 - 0.000101 * jc) + sin3m * 0.000289

    # calculate elements used in multiple places below:
    omega = np.radians(125.04 - 1934.136 * jc)
    latitude = np.radians(latitude)

    # mean obliquity of ecliptic, corrected (radians)
    seconds = 21.448 - jc * (46.815 + jc * (0.00059 - jc * 0.001813))
    e0 = 23.0 + (26.0 + seconds / 60.0) / 60.0
    e = np.radians(e0 + 0.00256 * np.cos(omega))

    # sun true longitude (deg)
    o = l0 + c

    # sun apparent longitude (radians)
    lambda_ = np.radians(o - 0.00569 - 0.00478 * np.sin(omega))

    # sun declination (radians)
    declination = np.arcsin(np.sin(e) * np.sin(lambda_))

    # sun right ascension (deg)
    rightasc = np.degrees(np.arctan2(np.cos(e) * np.sin(lambda_), np.cos(lambda_)))

    elevation = np.degrees(np.arcsin(
        np.sin(latitude) * np.sin(declination) +
        np.cos(latitude) * np.cos(declination) *
        np.cos(np.radians(gstime + longitude - rightasc))))

    # - Solar diameter gives 0.833 degrees - rim of sun appears before centre of disc.
    # - For civil twilight, allow 6 degrees.
    # - For nautical twilight, allow 12 degrees.
    # - For astronomical twilight, allow 18 degrees.
    if twilight is None:
        limit = -0.8333
    elif twilight == 'civil':
        limit = -6.0
    elif twilight == 'nautical':
        limit = -12.0
    elif twilight == 'astronomical':
        limit = -18.0
    else:
        raise ValueError('is_day() twilight argument must be one of: civil, nautical, astronomical or None.')

    return elevation > limit  # true = day, false = night


def range(start, stop, step=1, field='days'):
    '''
    Generates a list of date and times between the two provided dates.

    :param start: the date (and time) at the start of the range.
    :type start: datetime.date or datetime.datetime
    :param stop: the date (and time) at the end of the range.
    :type stop: datetime.date or datetime.datetime
    :param step: the step size
    :type step: integer
    :param field: the field to use when adding time with each step
    :type field: string
    :returns: a range of dates
    :rtype: list
    '''

    if not isinstance(step, int):
        raise TypeError('range() integer step argument expected, got %s.' % type(step).__name__)

    if step == 0:
        raise ValueError('range() step argument must not be zero')

    if field not in ['seconds', 'minutes', 'hours', 'days', 'weeks']:
        raise ValueError('range() field argument must be acceptable by timedelta().')

    if start > stop and step > 0 or start < stop and step < 0:
        return []

    if isinstance(start, datetime):
        current = start
        convert = False
    elif isinstance(start, date):
        current = datetime.combine(start, time())
        convert = True  # Convert back to datetime.date() at the end.
    else:
        raise ValueError('range() start argument must be date or datetime')

    if isinstance(stop, datetime):
        limit = stop
    elif isinstance(stop, date):
        limit = datetime.combine(stop, time())
    else:
        raise ValueError('range() stop argument must be date or datetime')

    increment = timedelta(**{field: step})
    compare = operator.lt if step > 0 else operator.gt

    dates = []

    while compare(current, limit):
        if not convert:
            dates.append(current)
        elif len(dates) == 0 or dates[-1] != current.date():
            dates.append(current.date())
        current += increment

    return dates
