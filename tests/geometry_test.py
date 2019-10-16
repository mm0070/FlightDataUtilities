##############################################################################

'''
'''

##############################################################################
# Imports


import logging
import unittest

from flightdatautilities import geometry


##############################################################################
# Module Setup


def setUpModule():
    '''
    Prepare the environment for all tests in this module.
    '''
    # Disable all logging but most critical:
    logging.disable(logging.CRITICAL)


##############################################################################
# Test Cases


class TestMidpoint(unittest.TestCase):
    '''
    '''

    arguments = [
        ((0, 0), (0, 0)),
        ((45, 45), (45, 45)),
        ((-45, -45), (-45, -45)),
        ((51.47, -0.4613), (55.95, -3.3725)),
        ((55.95, -3.3725), (51.47, -0.4613)),
        ((33.9425, -118.408056), (35.7653,  140.385556)),
        ((35.7653,  140.385556), (33.9425, -118.408056)),
    ]

    expected = [
        (0, 0),
        (45, 45),
        (-45, -45),
        (53.71879636048774, -1.8393457044657056),
        (53.71879636048774, -1.8393457044657056),
        (47.65246135994274, -168.23843296873065),
        (47.65246135994274, -168.23843296873065),
    ]

    def test_midpoint(self):
        '''
        '''
        for (a, b), expected in zip(self.arguments, self.expected):
            midpoint = geometry.midpoint(*(a + b))
            self.assertAlmostEqual(midpoint[0], expected[0])
            self.assertAlmostEqual(midpoint[1], expected[1])


class TestCrossTrackDistance(unittest.TestCase):
    '''
    '''

    arguments = [
        ((0, 0), (0, 0), (0, 0)),
        ((45, 45), (45, 45), (45, 45)),
        ((-45, -45), (-45, -45), (-45, -45)),
        ((51.47, -0.4613), (55.95, -3.3725),
            (53.71879636048774, -1.8393457044657056)),
        ((55.95, -3.3725), (51.47, -0.4613),
            (53.71879636048774, -1.8393457044657056)),
        ((33.9425, -118.408056), (35.7653,  140.385556),
            (47.65246135994274, -168.23843296873065)),
        ((35.7653,  140.385556), (33.9425, -118.408056),
            (47.65246135994274, -168.23843296873065)),
        ((51.47, -0.4613), (55.95, -3.3725),
            (52.71879636048774, -0.8393457044657056)),
        ((51.47, -0.4613), (55.95, -3.3725),
            (54.71879636048774, -2.8393457044657056)),
        ((33.9425, -118.408056), (35.7653,  140.385556),
            (46.65246135994274, -169.23843296873065)),
        ((33.9425, -118.408056), (35.7653,  140.385556),
            (48.65246135994274, -167.23843296873065)),
    ]

    expected = [
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        23273.687779678614,
        -20021.017313086195,
        -112983.24227480617,
        113861.32693247873,
    ]

    def test_cross_track_distance(self):
        '''
        '''
        for (a, b, c), expected in zip(self.arguments, self.expected):
            dxt = geometry.cross_track_distance(*(a + b + c))
            self.assertAlmostEqual(dxt, expected)


class TestAlongTrackDistance(unittest.TestCase):
    '''
    '''

    arguments = [
        ((0, 0), (0, 0), (0, 0)),
        ((45, 45), (45, 45), (45, 45)),
        ((-45, -45), (-45, -45), (-45, -45)),
        ((51.47, -0.4613), (55.95, -3.3725),
            (53.71879636048774, -1.8393457044657056)),
        ((55.95, -3.3725), (51.47, -0.4613),
            (53.71879636048774, -1.8393457044657056)),
        ((33.9425, -118.408056), (35.7653,  140.385556),
            (47.65246135994274, -168.23843296873065)),
        ((35.7653,  140.385556), (33.9425, -118.408056),
            (47.65246135994274, -168.23843296873065)),
        ((51.47, -0.4613), (55.95, -3.3725),
            (52.71879636048774, -0.8393457044657056)),
        ((51.47, -0.4613), (55.95, -3.3725),
            (54.71879636048774, -2.8393457044657056)),
        ((33.9425, -118.408056), (35.7653,  140.385556),
            (46.65246135994274, -169.23843296873065)),
        ((33.9425, -118.408056), (35.7653,  140.385556),
            (48.65246135994274, -167.23843296873065)),
    ]

    expected = [
        0,
        0,
        0,
        266804.36472106207,
        266804.36472106207,
        4376909.0022099856,
        4376909.0022099856,
        139310.21161785477,
        394043.05301903997,
        4449827.2317000441,
        4306887.7883137288,
    ]

    def test_along_track_distance(self):
        '''
        '''
        for (a, b, c), expected in zip(self.arguments, self.expected):
            dat = geometry.along_track_distance(*(a + b + c))
            self.assertAlmostEqual(dat, expected)


class TestGreatCircleDistanceHaversine(unittest.TestCase):
    '''
    '''

    arguments = [
        ((0, 0), (0, 0)),
        ((45, 45), (45, 45)),
        ((-45, -45), (-45, -45)),
        ((51.47, -0.4613), (55.95, -3.3725)),
        ((55.95, -3.3725), (51.47, -0.4613)),
        ((33.9425, -118.408056), (35.7653,  140.385556)),
        ((35.7653,  140.385556), (33.9425, -118.408056)),
    ]

    expected = [
        0,
        0,
        0,
        533608.72944213205,  # Moveable Type JS Output: 533.60805939591057
        533608.72944213205,  # Moveable Type JS Output: 533.60805939591057
        8753818.0044199713,  # Moveable Type JS Output: 8753.8070123534108
        8753818.0044199713,  # Moveable Type JS Output: 8753.8070123534108
    ]

    def test_great_circle_distance__haversine(self):
        '''
        '''
        for (a, b), expected in zip(self.arguments, self.expected):
            distance = geometry.great_circle_distance__haversine(*(a + b))
            self.assertAlmostEqual(distance, expected)


class TestInitialBearing(unittest.TestCase):
    '''
    '''

    arguments = [
        ((0, 0), (0, 0)),
        ((45, 45), (45, 45)),
        ((-45, -45), (-45, -45)),
        ((51.47, -0.4613), (55.95, -3.3725)),
        ((55.95, -3.3725), (51.47, -0.4613)),
        ((33.9425, -118.408056), (35.7653,  140.385556)),
        ((35.7653,  140.385556), (33.9425, -118.408056)),
    ]

    expected = [
        0,
        0,
        0,
        340.1279082634598,
        157.77941819114176,
        305.74632835325264,
        56.07780427801367,
    ]

    def test_initial_bearing(self):
        '''
        '''
        for (a, b), expected in zip(self.arguments, self.expected):
            bearing = geometry.initial_bearing(*(a + b))
            self.assertAlmostEqual(bearing, expected)
