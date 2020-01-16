# vim:et:ft=python:nowrap:sts=4:sw=4:ts=4
##############################################################################

'''
Flight Data Utilities: Date Extensions: Unit Tests
'''

##############################################################################
# Imports


import logging
import unittest

from datetime import date, datetime

from flightdatautilities import dateext


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


class TestIsDay(unittest.TestCase):
    # Solstice times for 2012 at Stonehenge.
    # Sunset on Wednesday 20th June 2012 is at 2126 hrs (9.26pm BST)
    # Sunrise on Thursday 21st June 2012 is at 0452 hrs (4.52am BST)
    def test_sunset(self):
        self.assertTrue(dateext.is_day(datetime(2012, 6, 20, 20, 25), 51.1789, -1.8264, twilight=None))
        self.assertFalse(dateext.is_day(datetime(2012, 6, 20, 20, 27), 51.1789, -1.8264, twilight=None))

    def test_sunrise(self):
        self.assertFalse(dateext.is_day(datetime(2012, 6, 21, 3, 51), 51.1789, -1.8264, twilight=None))
        self.assertTrue(dateext.is_day(datetime(2012, 6, 21, 3, 53), 51.1789, -1.8264, twilight=None))

    def test_location_west(self):
        # Sunrise over the Goodyear, Az, office on New Year is 07:33 + 7 hours from UTC
        self.assertFalse(dateext.is_day(datetime(2013, 1, 1, 14, 32), 33.449291, -112.359015, twilight=None))
        self.assertTrue(dateext.is_day(datetime(2013, 1, 1, 14, 34), 33.449291, -112.359015, twilight=None))

    def test_location_east(self):
        # Sunrise over Sydney Harbour Bridge is 3 Jan 2013 05:49 -11 hours from UTC
        self.assertFalse(dateext.is_day(datetime(2013, 1, 2, 18, 48), -33.85, 151.21, twilight=None))
        self.assertTrue(dateext.is_day(datetime(2013, 1, 2, 18, 50), -33.85, 151.21, twilight=None))

    def test_midnight_sun(self):
        # July in Bodo is light all night
        self.assertTrue(dateext.is_day(datetime(2013, 6, 21, 0, 0),  67.280356,  14.404916, twilight=None))

    def test_midday_gloom(self):
        # July in Ross Island can be miserable :o(
        self.assertFalse(dateext.is_day(datetime(2013, 6, 21, 0, 0), -77.52474, 166.960313, twilight=None))

    def test_twilight_libreville(self):
        # Sunrise on 4 Jun 2012 at Libreville is 06:16. There will be a
        # partial eclipse on that day visible from Libreville, if you're
        # interested. Twilight is almost directly proportional to rotation as
        # this is right on the equator, hence 6 deg = 24 mins.
        self.assertTrue(dateext.is_day(datetime(2013, 6, 4, 5, 17), 0.454927, 9.411872, twilight=None))
        self.assertFalse(dateext.is_day(datetime(2013, 6, 4, 5, 15), 0.454927, 9.411872, twilight=None))
        self.assertTrue(dateext.is_day(datetime(2013, 6, 4, 4, 54), 0.454927, 9.411872, twilight='civil'))
        self.assertFalse(dateext.is_day(datetime(2013, 6, 4, 4, 52), 0.454927, 9.411872))
        self.assertTrue(dateext.is_day(datetime(2013, 6, 4, 4, 29), 0.454927, 9.411872, twilight='nautical'))
        self.assertTrue(dateext.is_day(datetime(2013, 6, 4, 4, 5), 0.454927, 9.411872, twilight='astronomical'))

    def test_uk_aip(self):
        # These cases are taken from the United Kingdom AIP, page GEN 2.7.1 dated 13 Dec 2012.
        #Carlisle winter morning
        lat = 54.0 + 56.0 / 60.0 + 15.0 / 3600.0
        lon = (2.0 + 48.0 / 60.0 + 33.0 / 3600.0) * -1.0
        self.assertFalse(dateext.is_day(datetime(2012, 1, 15, 7, 43), lat, lon))
        self.assertTrue(dateext.is_day(datetime(2012, 1, 15, 7, 45), lat, lon))

        # Lands End summer evening
        lat = 50.0 + 6.0 / 60.0 + 5.0 / 3600.0
        lon = (5.0 + 40.0 / 60.0 + 14.0 / 3600.0) * -1.0
        self.assertFalse(dateext.is_day(datetime(2012, 6, 18, 21, 21), lat, lon))
        self.assertTrue(dateext.is_day(datetime(2012, 6, 18, 21, 19), lat, lon))

        # Scatsta summer morning
        lat = 60.0 + 25.0 / 60.0 + 58.0 / 3600.0
        lon = (1.0 + 17.0 / 60.0 + 46.0 / 3600.0) * -1.0
        self.assertFalse(dateext.is_day(datetime(2012, 6, 4, 1, 10), lat, lon))
        self.assertTrue(dateext.is_day(datetime(2012, 6, 4, 1, 12), lat, lon))


class TestRange(unittest.TestCase):

    expected = [
        [datetime(2000, 1, x) for x in range(1, 32, 1)],
        [datetime(2000, 1, x) for x in range(31, 0, -1)],
        [datetime(2000, 1, x) for x in range(1, 32, 2)],
        [datetime(2000, 1, x) for x in range(31, 0, -2)],
        [date(2000, 1, x) for x in range(1, 5, 1)],
    ]

    def test_range__step_float(self):
        args = (datetime(2000, 1, 1), datetime(2000, 1, 1), 1.5)
        self.assertRaises(TypeError, dateext.range, *args)

    def test_range__step_none(self):
        args = (datetime(2000, 1, 1), datetime(2000, 1, 1), None)
        self.assertRaises(TypeError, dateext.range, *args)

    def test_range__step_zero(self):
        args = (datetime(2000, 1, 1), datetime(2000, 1, 1), 0)
        self.assertRaises(ValueError, dateext.range, *args)

    def test_range__step_normal(self):
        args = (datetime(2000, 1, 1), datetime(2000, 2, 1), 1)
        self.assertEquals(dateext.range(*args), self.expected[0])
        args = (datetime(2000, 1, 31), datetime(1999, 12, 31), -1)
        self.assertEquals(dateext.range(*args), self.expected[1])
        args = (datetime(2000, 1, 1), datetime(2000, 2, 1), 2)
        self.assertEquals(dateext.range(*args), self.expected[2])
        args = (datetime(2000, 1, 31), datetime(1999, 12, 31), -2)
        self.assertEquals(dateext.range(*args), self.expected[3])

    def test_range__step_reversed(self):
        args = (datetime(2000, 1, 1), datetime(2000, 2, 1), -1)
        self.assertEquals(dateext.range(*args), [])
        args = (datetime(2000, 1, 31), datetime(1999, 12, 31), 1)
        self.assertEquals(dateext.range(*args), [])

    def test_range__valid_field(self):
        for field in ('seconds', 'minutes', 'hours', 'days', 'weeks'):
            try:
                args = (datetime(2000, 1, 1), datetime(2000, 2, 1), 1, field)
                dateext.range(*args)
            except:
                self.fail('Unexpected exception raised for field %s' % field)

    def test_range__invalid_field(self):
        for field in ('months', 'years', 'centuries', 'millenia'):
            args = (datetime(2000, 1, 1), datetime(2000, 2, 1), 1, field)
            self.assertRaises(ValueError, dateext.range, *args)

    def test_range__date_convert(self):
        args = (date(2000, 1, 1), date(2000, 1, 5), 12)
        kwargs = {'field': 'hours'}
        self.assertEquals(dateext.range(*args, **kwargs), self.expected[4])
