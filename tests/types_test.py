import re
import unittest
from datetime import date, datetime, timezone

from flightdatautilities.types import AIRAC, TACAN


class AIRACTest(unittest.TestCase):

    def _test_constructor_error(self, *values, exception=None):
        for value in values:
            with self.subTest(value):
                with self.assertRaisesRegex(exception, f'^Invalid AIRAC identifier: {re.escape(repr(value))}$'):
                    AIRAC(value)

    def test_invalid_type(self):
        self._test_constructor_error(None, True, False, set(), (), [], {}, b'', exception=TypeError)

    def test_invalid_value(self):
        self._test_constructor_error('', 'ABC', '001', exception=ValueError)

    def test_out_of_range(self):
        self._test_constructor_error('0000', '1900', '1914', '2000', '2015', exception=ValueError)

    def test_lower_limit(self):
        with self.assertRaisesRegex(ValueError, r'^AIRAC identifiers were not defined before 1964-01-16\.$'):
            AIRAC(AIRAC.BASE - 1)

    def test_immutable(self):
        with self.assertRaisesRegex(TypeError, r'^AIRAC objects are immutable\.$'):
            AIRAC('1913').timestamp = 0

    def test_str(self):
        obj = AIRAC('1913')
        self.assertEqual(str(obj), '1913')
        self.assertEqual(str(obj), obj.identifier)

    def test_repr(self):
        self.assertEqual(repr(AIRAC('1913')), "AIRAC('1913')")

    def test_ordering(self):
        self.assertEqual(AIRAC('1913'), AIRAC('1913'))
        self.assertNotEqual(AIRAC('1913'), AIRAC('2001'))
        self.assertLess(AIRAC('1913'), AIRAC('2001'))
        self.assertLessEqual(AIRAC('1913'), AIRAC('1913'))
        self.assertGreater(AIRAC('2002'), AIRAC('2001'))
        self.assertGreaterEqual(AIRAC('2002'), AIRAC('2002'))
        self.assertIs(AIRAC('1913').__eq__(None), NotImplemented)
        self.assertIs(AIRAC('1913').__ne__(None), NotImplemented)
        self.assertIs(AIRAC('1913').__lt__(None), NotImplemented)
        self.assertIs(AIRAC('1913').__le__(None), NotImplemented)
        self.assertIs(AIRAC('1913').__gt__(None), NotImplemented)
        self.assertIs(AIRAC('1913').__ge__(None), NotImplemented)

    def test_special_cases(self):
        # The years 1976, 1998, 2020, and 2043 have a 14th cycle in the year.
        for value in ('7614', '9814', '2014', '4314'):
            with self.subTest(value):
                try:
                    AIRAC(value)
                except Exception:
                    self.fail('Unexpected failure while parsing identifier.')

    def test_alternate_construction(self):
        identifier, year, ordinal, effective = '1906', 19, 6, datetime(2019, 5, 23, tzinfo=timezone.utc)
        values = ('1906', 1558569600, 1558569600.0, date(2019, 5, 23), datetime(2019, 5, 23, tzinfo=timezone.utc))
        for value in values:
            with self.subTest(value):
                a = AIRAC(value)
                self.assertEqual(a.year, year)
                self.assertEqual(a.ordinal, ordinal)
                self.assertEqual(a.effective, effective)
                self.assertEqual(a.identifier, identifier)

    def test_floored_to_effective(self):
        for day in range(23, 31):
            value = datetime(2019, 5, day, tzinfo=timezone.utc)
            with self.subTest(value):
                self.assertEqual(AIRAC(value).timestamp, 1558569600)


class TACANTest(unittest.TestCase):
    DATA = (
        ('17X', {'vor': 108.0, 'localizer': None, 'glideslope': None}),
        ('17Y', {'vor': 108.05, 'localizer': None, 'glideslope': None}),
        ('18X', {'vor': None, 'localizer': 108.1, 'glideslope': 334.7}),
        ('18Y', {'vor': None, 'localizer': 108.15, 'glideslope': 334.55}),
        ('19X', {'vor': 108.2, 'localizer': None, 'glideslope': None}),
        ('19Y', {'vor': 108.25, 'localizer': None, 'glideslope': None}),
        ('20X', {'vor': None, 'localizer': 108.3, 'glideslope': 334.1}),
        ('20Y', {'vor': None, 'localizer': 108.35, 'glideslope': 333.95}),
        ('21X', {'vor': 108.4, 'localizer': None, 'glideslope': None}),
        ('21Y', {'vor': 108.45, 'localizer': None, 'glideslope': None}),
        ('22X', {'vor': None, 'localizer': 108.5, 'glideslope': 329.9}),
        ('22Y', {'vor': None, 'localizer': 108.55, 'glideslope': 329.75}),
        ('23X', {'vor': 108.6, 'localizer': None, 'glideslope': None}),
        ('23Y', {'vor': 108.65, 'localizer': None, 'glideslope': None}),
        ('24X', {'vor': None, 'localizer': 108.7, 'glideslope': 330.5}),
        ('24Y', {'vor': None, 'localizer': 108.75, 'glideslope': 330.35}),
        ('25X', {'vor': 108.8, 'localizer': None, 'glideslope': None}),
        ('25Y', {'vor': 108.85, 'localizer': None, 'glideslope': None}),
        ('26X', {'vor': None, 'localizer': 108.9, 'glideslope': 329.3}),
        ('26Y', {'vor': None, 'localizer': 108.95, 'glideslope': 329.15}),
        ('27X', {'vor': 109.0, 'localizer': None, 'glideslope': None}),
        ('27Y', {'vor': 109.05, 'localizer': None, 'glideslope': None}),
        ('28X', {'vor': None, 'localizer': 109.1, 'glideslope': 331.4}),
        ('28Y', {'vor': None, 'localizer': 109.15, 'glideslope': 331.25}),
        ('29X', {'vor': 109.2, 'localizer': None, 'glideslope': None}),
        ('29Y', {'vor': 109.25, 'localizer': None, 'glideslope': None}),
        ('30X', {'vor': None, 'localizer': 109.3, 'glideslope': 332.0}),
        ('30Y', {'vor': None, 'localizer': 109.35, 'glideslope': 331.85}),
        ('31X', {'vor': 109.4, 'localizer': None, 'glideslope': None}),
        ('31Y', {'vor': 109.45, 'localizer': None, 'glideslope': None}),
        ('32X', {'vor': None, 'localizer': 109.5, 'glideslope': 332.6}),
        ('32Y', {'vor': None, 'localizer': 109.55, 'glideslope': 332.45}),
        ('33X', {'vor': 109.6, 'localizer': None, 'glideslope': None}),
        ('33Y', {'vor': 109.65, 'localizer': None, 'glideslope': None}),
        ('34X', {'vor': None, 'localizer': 109.7, 'glideslope': 333.2}),
        ('34Y', {'vor': None, 'localizer': 109.75, 'glideslope': 333.05}),
        ('35X', {'vor': 109.8, 'localizer': None, 'glideslope': None}),
        ('35Y', {'vor': 109.85, 'localizer': None, 'glideslope': None}),
        ('36X', {'vor': None, 'localizer': 109.9, 'glideslope': 333.8}),
        ('36Y', {'vor': None, 'localizer': 109.95, 'glideslope': 333.65}),
        ('37X', {'vor': 110.0, 'localizer': None, 'glideslope': None}),
        ('37Y', {'vor': 110.05, 'localizer': None, 'glideslope': None}),
        ('38X', {'vor': None, 'localizer': 110.1, 'glideslope': 334.4}),
        ('38Y', {'vor': None, 'localizer': 110.15, 'glideslope': 334.25}),
        ('39X', {'vor': 110.2, 'localizer': None, 'glideslope': None}),
        ('39Y', {'vor': 110.25, 'localizer': None, 'glideslope': None}),
        ('40X', {'vor': None, 'localizer': 110.3, 'glideslope': 335.0}),
        ('40Y', {'vor': None, 'localizer': 110.35, 'glideslope': 334.85}),
        ('41X', {'vor': 110.4, 'localizer': None, 'glideslope': None}),
        ('41Y', {'vor': 110.45, 'localizer': None, 'glideslope': None}),
        ('42X', {'vor': None, 'localizer': 110.5, 'glideslope': 329.6}),
        ('42Y', {'vor': None, 'localizer': 110.55, 'glideslope': 329.45}),
        ('43X', {'vor': 110.6, 'localizer': None, 'glideslope': None}),
        ('43Y', {'vor': 110.65, 'localizer': None, 'glideslope': None}),
        ('44X', {'vor': None, 'localizer': 110.7, 'glideslope': 330.2}),
        ('44Y', {'vor': None, 'localizer': 110.75, 'glideslope': 330.05}),
        ('45X', {'vor': 110.8, 'localizer': None, 'glideslope': None}),
        ('45Y', {'vor': 110.85, 'localizer': None, 'glideslope': None}),
        ('46X', {'vor': None, 'localizer': 110.9, 'glideslope': 330.8}),
        ('46Y', {'vor': None, 'localizer': 110.95, 'glideslope': 330.65}),
        ('47X', {'vor': 111.0, 'localizer': None, 'glideslope': None}),
        ('47Y', {'vor': 111.05, 'localizer': None, 'glideslope': None}),
        ('48X', {'vor': None, 'localizer': 111.1, 'glideslope': 331.7}),
        ('48Y', {'vor': None, 'localizer': 111.15, 'glideslope': 331.55}),
        ('49X', {'vor': 111.2, 'localizer': None, 'glideslope': None}),
        ('49Y', {'vor': 111.25, 'localizer': None, 'glideslope': None}),
        ('50X', {'vor': None, 'localizer': 111.3, 'glideslope': 332.3}),
        ('50Y', {'vor': None, 'localizer': 111.35, 'glideslope': 332.15}),
        ('51X', {'vor': 111.4, 'localizer': None, 'glideslope': None}),
        ('51Y', {'vor': 111.45, 'localizer': None, 'glideslope': None}),
        ('52X', {'vor': None, 'localizer': 111.5, 'glideslope': 332.9}),
        ('52Y', {'vor': None, 'localizer': 111.55, 'glideslope': 332.75}),
        ('53X', {'vor': 111.6, 'localizer': None, 'glideslope': None}),
        ('53Y', {'vor': 111.65, 'localizer': None, 'glideslope': None}),
        ('54X', {'vor': None, 'localizer': 111.7, 'glideslope': 333.5}),
        ('54Y', {'vor': None, 'localizer': 111.75, 'glideslope': 333.35}),
        ('55X', {'vor': 111.8, 'localizer': None, 'glideslope': None}),
        ('55Y', {'vor': 111.85, 'localizer': None, 'glideslope': None}),
        ('56X', {'vor': None, 'localizer': 111.9, 'glideslope': 331.1}),
        ('56Y', {'vor': None, 'localizer': 111.95, 'glideslope': 330.95}),
        ('57X', {'vor': 112.0, 'localizer': None, 'glideslope': None}),
        ('57Y', {'vor': 112.05, 'localizer': None, 'glideslope': None}),
        ('58X', {'vor': 112.1, 'localizer': None, 'glideslope': None}),
        ('58Y', {'vor': 112.15, 'localizer': None, 'glideslope': None}),
        ('59X', {'vor': 112.2, 'localizer': None, 'glideslope': None}),
        ('59Y', {'vor': 112.25, 'localizer': None, 'glideslope': None}),
        ('70X', {'vor': 112.3, 'localizer': None, 'glideslope': None}),
        ('70Y', {'vor': 112.35, 'localizer': None, 'glideslope': None}),
        ('71X', {'vor': 112.4, 'localizer': None, 'glideslope': None}),
        ('71Y', {'vor': 112.45, 'localizer': None, 'glideslope': None}),
        ('72X', {'vor': 112.5, 'localizer': None, 'glideslope': None}),
        ('72Y', {'vor': 112.55, 'localizer': None, 'glideslope': None}),
        ('73X', {'vor': 112.6, 'localizer': None, 'glideslope': None}),
        ('73Y', {'vor': 112.65, 'localizer': None, 'glideslope': None}),
        ('74X', {'vor': 112.7, 'localizer': None, 'glideslope': None}),
        ('74Y', {'vor': 112.75, 'localizer': None, 'glideslope': None}),
        ('75X', {'vor': 112.8, 'localizer': None, 'glideslope': None}),
        ('75Y', {'vor': 112.85, 'localizer': None, 'glideslope': None}),
        ('76X', {'vor': 112.9, 'localizer': None, 'glideslope': None}),
        ('76Y', {'vor': 112.95, 'localizer': None, 'glideslope': None}),
        ('77X', {'vor': 113.0, 'localizer': None, 'glideslope': None}),
        ('77Y', {'vor': 113.05, 'localizer': None, 'glideslope': None}),
        ('78X', {'vor': 113.1, 'localizer': None, 'glideslope': None}),
        ('78Y', {'vor': 113.15, 'localizer': None, 'glideslope': None}),
        ('79X', {'vor': 113.2, 'localizer': None, 'glideslope': None}),
        ('79Y', {'vor': 113.25, 'localizer': None, 'glideslope': None}),
        ('80X', {'vor': 113.3, 'localizer': None, 'glideslope': None}),
        ('80Y', {'vor': 113.35, 'localizer': None, 'glideslope': None}),
        ('81X', {'vor': 113.4, 'localizer': None, 'glideslope': None}),
        ('81Y', {'vor': 113.45, 'localizer': None, 'glideslope': None}),
        ('82X', {'vor': 113.5, 'localizer': None, 'glideslope': None}),
        ('82Y', {'vor': 113.55, 'localizer': None, 'glideslope': None}),
        ('83X', {'vor': 113.6, 'localizer': None, 'glideslope': None}),
        ('83Y', {'vor': 113.65, 'localizer': None, 'glideslope': None}),
        ('84X', {'vor': 113.7, 'localizer': None, 'glideslope': None}),
        ('84Y', {'vor': 113.75, 'localizer': None, 'glideslope': None}),
        ('85X', {'vor': 113.8, 'localizer': None, 'glideslope': None}),
        ('85Y', {'vor': 113.85, 'localizer': None, 'glideslope': None}),
        ('86X', {'vor': 113.9, 'localizer': None, 'glideslope': None}),
        ('86Y', {'vor': 113.95, 'localizer': None, 'glideslope': None}),
        ('87X', {'vor': 114.0, 'localizer': None, 'glideslope': None}),
        ('87Y', {'vor': 114.05, 'localizer': None, 'glideslope': None}),
        ('88X', {'vor': 114.1, 'localizer': None, 'glideslope': None}),
        ('88Y', {'vor': 114.15, 'localizer': None, 'glideslope': None}),
        ('89X', {'vor': 114.2, 'localizer': None, 'glideslope': None}),
        ('89Y', {'vor': 114.25, 'localizer': None, 'glideslope': None}),
        ('90X', {'vor': 114.3, 'localizer': None, 'glideslope': None}),
        ('90Y', {'vor': 114.35, 'localizer': None, 'glideslope': None}),
        ('91X', {'vor': 114.4, 'localizer': None, 'glideslope': None}),
        ('91Y', {'vor': 114.45, 'localizer': None, 'glideslope': None}),
        ('92X', {'vor': 114.5, 'localizer': None, 'glideslope': None}),
        ('92Y', {'vor': 114.55, 'localizer': None, 'glideslope': None}),
        ('93X', {'vor': 114.6, 'localizer': None, 'glideslope': None}),
        ('93Y', {'vor': 114.65, 'localizer': None, 'glideslope': None}),
        ('94X', {'vor': 114.7, 'localizer': None, 'glideslope': None}),
        ('94Y', {'vor': 114.75, 'localizer': None, 'glideslope': None}),
        ('95X', {'vor': 114.8, 'localizer': None, 'glideslope': None}),
        ('95Y', {'vor': 114.85, 'localizer': None, 'glideslope': None}),
        ('96X', {'vor': 114.9, 'localizer': None, 'glideslope': None}),
        ('96Y', {'vor': 114.95, 'localizer': None, 'glideslope': None}),
        ('97X', {'vor': 115.0, 'localizer': None, 'glideslope': None}),
        ('97Y', {'vor': 115.05, 'localizer': None, 'glideslope': None}),
        ('98X', {'vor': 115.1, 'localizer': None, 'glideslope': None}),
        ('98Y', {'vor': 115.15, 'localizer': None, 'glideslope': None}),
        ('99X', {'vor': 115.2, 'localizer': None, 'glideslope': None}),
        ('99Y', {'vor': 115.25, 'localizer': None, 'glideslope': None}),
        ('100X', {'vor': 115.3, 'localizer': None, 'glideslope': None}),
        ('100Y', {'vor': 115.35, 'localizer': None, 'glideslope': None}),
        ('101X', {'vor': 115.4, 'localizer': None, 'glideslope': None}),
        ('101Y', {'vor': 115.45, 'localizer': None, 'glideslope': None}),
        ('102X', {'vor': 115.5, 'localizer': None, 'glideslope': None}),
        ('102Y', {'vor': 115.55, 'localizer': None, 'glideslope': None}),
        ('103X', {'vor': 115.6, 'localizer': None, 'glideslope': None}),
        ('103Y', {'vor': 115.65, 'localizer': None, 'glideslope': None}),
        ('104X', {'vor': 115.7, 'localizer': None, 'glideslope': None}),
        ('104Y', {'vor': 115.75, 'localizer': None, 'glideslope': None}),
        ('105X', {'vor': 115.8, 'localizer': None, 'glideslope': None}),
        ('105Y', {'vor': 115.85, 'localizer': None, 'glideslope': None}),
        ('106X', {'vor': 115.9, 'localizer': None, 'glideslope': None}),
        ('106Y', {'vor': 115.95, 'localizer': None, 'glideslope': None}),
        ('107X', {'vor': 116.0, 'localizer': None, 'glideslope': None}),
        ('107Y', {'vor': 116.05, 'localizer': None, 'glideslope': None}),
        ('108X', {'vor': 116.1, 'localizer': None, 'glideslope': None}),
        ('108Y', {'vor': 116.15, 'localizer': None, 'glideslope': None}),
        ('109X', {'vor': 116.2, 'localizer': None, 'glideslope': None}),
        ('109Y', {'vor': 116.25, 'localizer': None, 'glideslope': None}),
        ('110X', {'vor': 116.3, 'localizer': None, 'glideslope': None}),
        ('110Y', {'vor': 116.35, 'localizer': None, 'glideslope': None}),
        ('111X', {'vor': 116.4, 'localizer': None, 'glideslope': None}),
        ('111Y', {'vor': 116.45, 'localizer': None, 'glideslope': None}),
        ('112X', {'vor': 116.5, 'localizer': None, 'glideslope': None}),
        ('112Y', {'vor': 116.55, 'localizer': None, 'glideslope': None}),
        ('113X', {'vor': 116.6, 'localizer': None, 'glideslope': None}),
        ('113Y', {'vor': 116.65, 'localizer': None, 'glideslope': None}),
        ('114X', {'vor': 116.7, 'localizer': None, 'glideslope': None}),
        ('114Y', {'vor': 116.75, 'localizer': None, 'glideslope': None}),
        ('115X', {'vor': 116.8, 'localizer': None, 'glideslope': None}),
        ('115Y', {'vor': 116.85, 'localizer': None, 'glideslope': None}),
        ('116X', {'vor': 116.9, 'localizer': None, 'glideslope': None}),
        ('116Y', {'vor': 116.95, 'localizer': None, 'glideslope': None}),
        ('117X', {'vor': 117.0, 'localizer': None, 'glideslope': None}),
        ('117Y', {'vor': 117.05, 'localizer': None, 'glideslope': None}),
        ('118X', {'vor': 117.1, 'localizer': None, 'glideslope': None}),
        ('118Y', {'vor': 117.15, 'localizer': None, 'glideslope': None}),
        ('119X', {'vor': 117.2, 'localizer': None, 'glideslope': None}),
        ('119Y', {'vor': 117.25, 'localizer': None, 'glideslope': None}),
        ('120X', {'vor': 117.3, 'localizer': None, 'glideslope': None}),
        ('120Y', {'vor': 117.35, 'localizer': None, 'glideslope': None}),
        ('121X', {'vor': 117.4, 'localizer': None, 'glideslope': None}),
        ('121Y', {'vor': 117.45, 'localizer': None, 'glideslope': None}),
        ('122X', {'vor': 117.5, 'localizer': None, 'glideslope': None}),
        ('122Y', {'vor': 117.55, 'localizer': None, 'glideslope': None}),
        ('123X', {'vor': 117.6, 'localizer': None, 'glideslope': None}),
        ('123Y', {'vor': 117.65, 'localizer': None, 'glideslope': None}),
        ('124X', {'vor': 117.7, 'localizer': None, 'glideslope': None}),
        ('124Y', {'vor': 117.75, 'localizer': None, 'glideslope': None}),
        ('125X', {'vor': 117.8, 'localizer': None, 'glideslope': None}),
        ('125Y', {'vor': 117.85, 'localizer': None, 'glideslope': None}),
        ('126X', {'vor': 117.9, 'localizer': None, 'glideslope': None}),
        ('126Y', {'vor': 117.95, 'localizer': None, 'glideslope': None}),
    )

    def _test_constructor_error(self, *values, exception=None):
        for value in values:
            with self.subTest(value):
                with self.assertRaisesRegex(exception, f'^Invalid TACAN channel: {re.escape(repr(value))}$'):
                    TACAN(value)

    def test_invalid_type(self):
        self._test_constructor_error(1, 1.2, None, True, False, set(), (), [], {}, b'', exception=TypeError)

    def test_invalid_value(self):
        self._test_constructor_error('', '10Z', exception=ValueError)

    def test_out_of_range(self):
        self._test_constructor_error('0X', '0Y', '127X', '127Y', exception=ValueError)

    def test_immutable(self):
        with self.assertRaisesRegex(TypeError, r'^TACAN objects are immutable\.$'):
            TACAN('1X').channel = '1X'

    def test_str(self):
        obj = TACAN('1X')
        self.assertEqual(str(obj), '1X')
        self.assertEqual(str(obj), obj.channel)

    def test_repr(self):
        self.assertEqual(repr(TACAN('1X')), "TACAN('1X')")

    def test_ordering(self):
        self.assertEqual(TACAN('1X'), TACAN('1X'))
        self.assertNotEqual(TACAN('1X'), TACAN('1Y'))
        self.assertLess(TACAN('1X'), TACAN('1Y'))
        self.assertLessEqual(TACAN('1X'), TACAN('1X'))
        self.assertGreater(TACAN('2X'), TACAN('1Y'))
        self.assertGreaterEqual(TACAN('2X'), TACAN('1X'))
        self.assertIs(TACAN('1X').__eq__(None), NotImplemented)
        self.assertIs(TACAN('1X').__ne__(None), NotImplemented)
        self.assertIs(TACAN('1X').__lt__(None), NotImplemented)
        self.assertIs(TACAN('1X').__le__(None), NotImplemented)
        self.assertIs(TACAN('1X').__gt__(None), NotImplemented)
        self.assertIs(TACAN('1X').__ge__(None), NotImplemented)

    def test_to_frequency(self):
        for channel, data in self.DATA:
            for navaid, frequency in data.items():
                with self.subTest(channel=channel, navaid=navaid):
                    result = TACAN(channel).to_frequency(navaid)
                    if frequency is None:
                        self.assertIsNone(result)
                    else:
                        self.assertAlmostEqual(result, frequency, places=2)

    def test_from_frequency(self):
        for channel, data in self.DATA:
            for navaid, frequency in data.items():
                if frequency is None:
                    continue
                with self.subTest(frequency=frequency):
                    result = TACAN.from_frequency(frequency)
                    self.assertEqual(result, (channel, navaid))
