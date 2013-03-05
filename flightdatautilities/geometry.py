# -*- coding: utf-8 -*-
##############################################################################

'''
'''

##############################################################################
# Imports


from math import acos, asin, atan2, cos, degrees, pi, radians, sin, sqrt


##############################################################################
# Constants


EARTH_RADIUS = 6378.1  # km


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
    dlon = radians(p2_lon - p1_lon)
    lat1 = radians(p1_lat)
    lat2 = radians(p2_lat)
    lon1 = radians(p1_lon)

    Bx = cos(lat2) * cos(dlon)
    By = cos(lat2) * sin(dlon)
    lat3 = atan2(sin(lat1) + sin(lat2), sqrt((cos(lat1) + Bx) ** 2 + By ** 2))
    lon3 = lon1 + atan2(By, cos(lat1) + Bx)
    lon3 = (lon3 + 3 * pi) % (2 * pi) - pi  # Normalise to -180°..+180°

    return degrees(lat3), degrees(lon3)


def cross_track_distance(p1_lat, p1_lon, p2_lat, p2_lon, p3_lat, p3_lon):
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
    :returns: The cross-track distance.
    :rtype: float
    '''
    d13 = great_circle_distance__haversine(p1_lat, p1_lon, p3_lat, p3_lon)
    b12 = radians(initial_bearing(p1_lat, p1_lon, p2_lat, p2_lon))
    b13 = radians(initial_bearing(p1_lat, p1_lon, p3_lat, p3_lon))
    R = EARTH_RADIUS
    return asin(sin(d13 / R) * sin(b13 - b12)) * R


def along_track_distance(p1_lat, p1_lon, p2_lat, p2_lon, p3_lat, p3_lon):
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
    :returns: The along-track distance.
    :rtype: float
    '''
    d13 = great_circle_distance__haversine(p1_lat, p1_lon, p3_lat, p3_lon)
    dxt = cross_track_distance(p1_lat, p1_lon, p2_lat, p2_lon, p3_lat, p3_lon)
    R = EARTH_RADIUS
    return acos(cos(d13 / R) / cos(dxt / R)) * R


def great_circle_distance__haversine(p1_lat, p1_lon, p2_lat, p2_lon):
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
    :returns: The great-circle distance.
    :rtype: float
    '''
    dlat = radians(p2_lat - p1_lat)
    dlon = radians(p2_lon - p1_lon)
    lat1 = radians(p1_lat)
    lat2 = radians(p2_lat)
    a = sin(dlat / 2) ** 2 + sin(dlon / 2) ** 2 * cos(lat1) * cos(lat2)
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    R = EARTH_RADIUS
    return R * c


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
    dlon = radians(p2_lon - p1_lon)
    lat1 = radians(p1_lat)
    lat2 = radians(p2_lat)
    y = sin(dlon) * cos(lat2)
    x = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dlon)
    return degrees(atan2(y, x)) % 360


##############################################################################
# vim:et:ft=python:nowrap:sts=4:sw=4:ts=4
