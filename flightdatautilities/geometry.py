'''
Flight Data Utilities: Geometry Functions
'''

import numpy as np

from . import units as ut


# https://nssdc.gsfc.nasa.gov/planetary/factsheet/earthfact.html
EARTH_RADIUS = 6371008  # volumetric mean radius (meters)


##############################################################################
# Functions


def midpoint(p1_lat, p1_lon, p2_lat, p2_lon):
    '''
    Determine the midpoint along a great circle path between two points.

    http://www.movable-type.co.uk/scripts/latlong.html#midpoint

    :param p1_lat: The start latitude of the great-circle path.
    :type p1_lat: float or int
    :param p1_lon: The start longitude of the great-circle path.
    :type p1_lon: float or int
    :param p2_lat: The end latitude of the great-circle path.
    :type p2_lat: float or int
    :returns: The midpoint of the great-circle path as (lat, lon).
    :rtype: tuple
    '''
    dlon = np.radians(p2_lon - p1_lon)
    lat1 = np.radians(p1_lat)
    lat2 = np.radians(p2_lat)
    lon1 = np.radians(p1_lon)

    Bx = np.cos(lat2) * np.cos(dlon)
    By = np.cos(lat2) * np.sin(dlon)
    lat3 = np.arctan2(np.sin(lat1) + np.sin(lat2), np.sqrt((np.cos(lat1) + Bx) ** 2 + By ** 2))
    lon3 = lon1 + np.arctan2(By, np.cos(lat1) + Bx)
    lon3 = (lon3 + 3 * np.pi) % (2 * np.pi) - np.pi  # Normalise to -180°..+180°

    return np.degrees(lat3), np.degrees(lon3)


def cross_track_distance(p1_lat, p1_lon, p2_lat, p2_lon, p3_lat, p3_lon, units=ut.METER):
    '''
    Determine the cross track distance (the distance of a point from a
    great-circle path).

    See: http://www.movable-type.co.uk/scripts/latlong.html#crossTrack

    d13 is distance from start point to third point
    b13 is (initial) bearing from start point to third point
    b12 is (initial) bearing from start point to end point

    :param p1_lat: The start latitude of the great-circle path.
    :type p1_lat: float or int
    :param p1_lon: The start longitude of the great-circle path.
    :type p1_lon: float or int
    :param p2_lat: The end latitude of the great-circle path.
    :type p2_lat: float or int
    :param p2_lon: The end longitude of the great-circle path.
    :type p2_lon: float or int
    :param p3_lat: The latitude to calculate cross-track error from.
    :type p3_lat: float or int
    :param p3_lon: The longitude to calculate cross-track error from.
    :type p3_lon: float or int
    :param units: The units in which to represent the distance. (default: meters)
    :type units: string
    :returns: The cross-track distance.
    :rtype: float
    '''
    d13 = great_circle_distance__haversine(p1_lat, p1_lon, p3_lat, p3_lon)
    b12 = np.radians(initial_bearing(p1_lat, p1_lon, p2_lat, p2_lon))
    b13 = np.radians(initial_bearing(p1_lat, p1_lon, p3_lat, p3_lon))
    value = np.arcsin(np.sin(d13 / EARTH_RADIUS) * np.sin(b13 - b12)) * EARTH_RADIUS
    return ut.convert(value, ut.METER, units)


def along_track_distance(p1_lat, p1_lon, p2_lat, p2_lon, p3_lat, p3_lon, units=ut.METER):
    '''
    Determine the along track distance (the distance of a point along a
    great-circle path).

    See: http://www.movable-type.co.uk/scripts/latlong.html#crossTrack

    d13 is distance from start point to third point
    dxt is cross track distance

    :param p1_lat: The start latitude of the great-circle path.
    :type p1_lat: float or int
    :param p1_lon: The start longitude of the great-circle path.
    :type p1_lon: float or int
    :param p2_lat: The end latitude of the great-circle path.
    :type p2_lat: float or int
    :param p2_lon: The end longitude of the great-circle path.
    :type p2_lon: float or int
    :param p3_lat: The latitude to calculate cross-track error from.
    :type p3_lat: float or int
    :param p3_lon: The longitude to calculate cross-track error from.
    :type p3_lon: float or int
    :param units: The units in which to represent the distance. (default: meters)
    :type units: string
    :returns: The along-track distance.
    :rtype: float
    '''
    d13 = great_circle_distance__haversine(p1_lat, p1_lon, p3_lat, p3_lon)
    dxt = cross_track_distance(p1_lat, p1_lon, p2_lat, p2_lon, p3_lat, p3_lon)
    value = np.arccos(np.cos(d13 / EARTH_RADIUS) / np.cos(dxt / EARTH_RADIUS)) * EARTH_RADIUS
    return ut.convert(value, ut.METER, units)


def great_circle_distance__haversine(p1_lat, p1_lon, p2_lat, p2_lon, units=ut.METER):
    '''
    Determine the great-circle distance between two points using the
    Haversine formula.

    See: http://www.movable-type.co.uk/scripts/latlong.html

    :param p1_lat: The start latitude of the great-circle path.
    :type p1_lat: float or int
    :param p1_lon: The start longitude of the great-circle path.
    :type p1_lon: float or int
    :param p2_lat: The end latitude of the great-circle path.
    :type p2_lat: float_or_int
    :param p2_lon: The end longitude of the great-circle path.
    :type p2_lon: float_or_int
    :param units: The units in which to represent the distance. (default: meters)
    :type units: string
    :returns: The great-circle distance.
    :rtype: float
    '''
    sdlat2 = np.sin(np.radians(p1_lat - p2_lat) / 2.) ** 2
    sdlon2 = np.sin(np.radians(p1_lon - p2_lon) / 2.) ** 2
    a = sdlat2 + sdlon2 * np.cos(np.radians(p1_lat)) * np.cos(np.radians(p2_lat))
    value = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a)) * EARTH_RADIUS
    return ut.convert(value, ut.METER, units)


def initial_bearing(p1_lat, p1_lon, p2_lat, p2_lon):
    '''
    :param p1_lat: The start latitude of the great-circle path.
    :type p1_lat: float or int
    :param p1_lon: The start longitude of the great-circle path.
    :type p1_lon: float or int
    :param p2_lat: The end point latitude of the great-circle path.
    :type p2_lat: float or int
    :param p2_lon: The end point longitude of the great-circle path.
    :type p2_lon: float or int
    :returns: The initial bearing.
    :rtype: float
    '''
    dlon = np.radians(p2_lon - p1_lon)
    lat1 = np.radians(p1_lat)
    lat2 = np.radians(p2_lat)
    y = np.sin(dlon) * np.cos(lat2)
    x = np.cos(lat1) * np.sin(lat2) - np.sin(lat1) * np.cos(lat2) * np.cos(dlon)
    return np.degrees(np.arctan2(y, x)) % 360
