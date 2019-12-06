import functools
import re
from datetime import date, datetime, timezone

LOCALIZER_TO_GLIDESLOPE_FREQUENCY_MAPPING = {
    108.10: 334.70,
    108.15: 334.55,
    108.30: 334.10,
    108.35: 333.95,
    108.50: 329.90,
    108.55: 329.75,
    108.70: 330.50,
    108.75: 330.35,
    108.90: 329.30,
    108.95: 329.15,
    109.10: 331.40,
    109.15: 331.25,
    109.30: 332.00,
    109.35: 331.85,
    109.50: 332.60,
    109.55: 332.45,
    109.70: 333.20,
    109.75: 333.05,
    109.90: 333.80,
    109.95: 333.65,
    110.10: 334.40,
    110.15: 334.25,
    110.30: 335.00,
    110.35: 334.85,
    110.50: 329.60,
    110.55: 329.45,
    110.70: 330.20,
    110.75: 330.05,
    110.90: 330.80,
    110.95: 330.65,
    111.10: 331.70,
    111.15: 331.55,
    111.30: 332.30,
    111.35: 332.15,
    111.50: 332.90,
    111.55: 332.75,
    111.70: 333.50,
    111.75: 333.35,
    111.90: 331.10,
    111.95: 330.95,
}
GLIDESLOPE_TO_LOCALIZER_FREQUENCY_MAPPING = {v: k for k, v in LOCALIZER_TO_GLIDESLOPE_FREQUENCY_MAPPING.items()}


@functools.total_ordering
class AIRAC:
    BASE = -188092800  # 1964-01-16 / 6401
    DELTA = 2419200  # 28 days

    __slots__ = ['timestamp']

    def __init__(self, value):
        if isinstance(value, str):
            if not value.isdigit() or len(value) != 4:
                raise ValueError(f'Invalid AIRAC identifier: {value}')
            year, ordinal = int(value[:2]), int(value[2:])
            year += 2000 if year < 64 else 1900
            timestamp = datetime(year - 1, 12, 31, tzinfo=timezone.utc).timestamp()
            extra = ordinal * self.DELTA
        elif isinstance(value, (date, datetime)):
            timestamp, extra = value.timestamp(), None
        else:
            timestamp, extra = value, None
        if timestamp < self.BASE:
            raise ValueError('AIRAC identifiers were not defined before 1964-01-16.')
        super().__setattr__('timestamp', timestamp + extra - (timestamp - self.BASE) % self.DELTA)
        if extra is not None:
            if extra <= 0 or self.timestamp > datetime(year, 12, 31, tzinfo=timezone.utc).timestamp():
                raise ValueError(f'Invalid AIRAC identifier: {value}')

    @property
    def year(self):
        return self.effective.year % 100

    @property
    def ordinal(self):
        return (self.effective.timetuple().tm_yday - 1) // 28 + 1

    @property
    def effective(self):
        return datetime.fromtimestamp(self.timestamp, timezone.utc)

    @property
    def identifier(self):
        return f'{self.year:02d}{self.ordinal:02d}'

    def __setattr__(self, key, value):
        raise Exception('AIRAC instances are immutable.')

    def __repr__(self):
        return f'{self.__class__.__qualname__}({self.identifier!r})'

    def __str__(self):
        return self.identifier

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.timestamp == other.timestamp

    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.timestamp < other.timestamp


@functools.total_ordering
class TACAN:
    PATTERN = re.compile(r'^(?:[1-9]|[1-9][0-9]|1[01][0-9]|12[0-6])[XY]$')

    __slots__ = ['channel']

    def __init__(self, value):
        if not isinstance(value, str) or not self.PATTERN.match(value):
            raise ValueError(f'Invalid TACAN channel: {value}')
        super().__setattr__('channel', value)

    def __setattr__(self, key, value):
        raise Exception('TACAN instances are immutable.')

    def __repr__(self):
        return f'{self.__class__.__qualname__}({self.channel!r})'

    def __str__(self):
        return self.channel

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.channel == other.channel

    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.channel < other.channel

    def to_frequency(self, navaid):
        """Convert a TACAN channel number to a frequency for a navigational aid."""
        if navaid not in {'glideslope', 'localizer', 'vor'}:
            raise ValueError('Expected navaid argument to be glideslope, localizer or vor.')
        number, letter = int(self.channel[:-1]), self.channel[-1:].upper()
        if number < 16 or 60 <= number <= 60:
            return None
        if (number % 2 or number > 57) and navaid in {'glideslope', 'localizer'}:
            return None
        if not number % 2 and number < 57 and navaid == 'vor':
            return None
        frequency = number / 10 + (0.05 if letter == 'Y' else 0.00)
        if 17 <= number <= 59:
            frequency = frequency + 106.30
        if 70 <= number <= 126:
            frequency = frequency + 105.30
        frequency = round(frequency, 2)
        if navaid == 'glideslope':
            return LOCALIZER_TO_GLIDESLOPE_FREQUENCY_MAPPING[frequency]
        return frequency

    @staticmethod
    def from_frequency(frequency):
        """Convert a frequency for a navigational aid to a TACAN channel number."""
        frequency = round(float(frequency) * 20) / 20  # round to nearest 0.05
        converted = GLIDESLOPE_TO_LOCALIZER_FREQUENCY_MAPPING.get(frequency, frequency)
        letter = 'Y' if converted * 100 // 1 % 10 else 'X'
        if letter == 'Y':
            converted = round(converted - 0.05, 2)
        if 328.60 <= frequency <= 335.40:
            number = (converted - 106.3) * 10
            return f'{number:.0f}{letter:s}', 'glideslope'
        if 108.0 <= frequency <= 112.25:
            number = (converted - 106.3) * 10
            navaid = 'localizer' if converted < 112 and converted * 10 // 1 % 10 % 2 else 'vor'
            return f'{number:.0f}{letter:s}', navaid
        if 112.30 <= frequency <= 117.95:
            number = (converted - 105.3) * 10
            return f'{number:.0f}{letter:s}', 'vor'
