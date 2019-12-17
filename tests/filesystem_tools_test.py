import io
import pathlib
import re
import tempfile
import unittest.mock

import flightdatautilities.filesystem_tools as fst


class TestChecksum(unittest.TestCase):

    @unittest.skip('Not implemented.')
    def test_checksum(self):
        pass

    def test_empty(self):
        b = io.BytesIO()
        self.assertEqual(fst.checksum(b, algorithm='md5'), 'd41d8cd98f00b204e9800998ecf8427e')
        self.assertEqual(fst.checksum(b, algorithm='sha1'), 'da39a3ee5e6b4b0d3255bfef95601890afd80709')
        self.assertEqual(fst.checksum(b, algorithm='sha256'), 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855')
        self.assertEqual(fst.checksum(b, algorithm='crc32'), 0)
        self.assertEqual(fst.checksum(b, algorithm='adler32'), 1)

    def test_unknown_algorithm(self):
        b = io.BytesIO()
        with self.assertRaisesRegex(ValueError, r"^Unknown hash algorithm: 'unknown'\.$"):
            fst.checksum(b, algorithm='unknown')

    def test_deprecated_function(self):
        msg = re.escape(
            'Call to deprecated function (or staticmethod) sha_hash_file. '
            '(Superseded by flightdatautilities.filesystem_tools:checksum().)',
        )
        with self.assertWarnsRegex(DeprecationWarning, msg):
            with tempfile.NamedTemporaryFile(mode='xb', suffix='.bz2') as f:
                f.write(b'\x42\x5a\x68\x39\x17\x72\x45\x38\x50\x90\x00\x00\x00\x00')
                f.flush()
                self.assertEqual(fst.sha_hash_file(f.name), 'd3dda84eb03b9738d118eb2be78e246106900493c0ae07819ad60815134a8058')


class TestIsEmpty(unittest.TestCase):

    @unittest.mock.patch('os.path.getsize', return_value=0)
    def test_zero_bytes(self, *ignored):
        suffixes = ('7z', 'blosc', 'br', 'bz2', 'gz', 'lz', 'lz4', 'lzma', 'xz', 'zip', 'zst', 'lzo', 'txt', 'png')
        for path in ('filename.%s' % i for i in suffixes):
            with self.subTest(path):
                self.assertIs(fst.is_empty(path), True)

    @unittest.mock.patch('os.path.getsize', return_value=1)  # Bypass size check optimisation.
    @unittest.mock.patch('flightdatautilities.filesystem_tools.checksum', return_value=False)
    def test_extensions(self, *ignored):
        suffixes = ('7z', 'blosc', 'br', 'bz2', 'gz', 'lz', 'lz4', 'lzma', 'xz', 'zip', 'zst')
        for path in ('filename.%s' % i for i in suffixes):
            with self.subTest(path):
                self.assertIsNotNone(fst.is_empty(path))
        suffixes = ('lzo', 'txt', 'png')
        for path in ('filename.%s' % i for i in suffixes):
            with self.subTest(path):
                self.assertIsNone(fst.is_empty(path))

    @unittest.mock.patch('os.path.getsize', return_value=102400)  # Simulate non-empty 1 kibibyte file.
    def test_size_optimisation(self, *ignored):
        suffixes = ('7z', 'blosc', 'br', 'bz2', 'gz', 'lz', 'lz4', 'lzma', 'xz', 'zip', 'zst')
        for path in ('filename.%s' % i for i in suffixes):
            with self.subTest(path):
                self.assertIsNone(fst.is_empty(path))

    def _test_checksum(self, data, suffix, *, expected):
        # Test with actual file:
        with tempfile.NamedTemporaryFile(mode='xb', suffix=suffix) as f:
            f.write(data)
            f.flush()
            self.assertIs(fst.is_empty(f.name), expected)
            self.assertIs(fst.is_empty(f.name.encode()), expected)
            self.assertIs(fst.is_empty(pathlib.Path(f.name)), expected)
        # Test with in-memory buffer:
        b = io.BytesIO(data)
        self.assertIs(fst.is_empty(b), expected)

    def test_checksum_match(self):
        tests = (
            (b'\x42\x5a\x68\x31\x17\x72\x45\x38\x50\x90\x00\x00\x00\x00', '.bz2', 'bzip2, 1 +/- --small'),
            (b'\x42\x5a\x68\x32\x17\x72\x45\x38\x50\x90\x00\x00\x00\x00', '.bz2', 'bzip2, 2 w/o --small or 2-9 w/ --small'),
            (b'\x42\x5a\x68\x33\x17\x72\x45\x38\x50\x90\x00\x00\x00\x00', '.bz2', 'bzip2, 3 w/o --small'),
            (b'\x42\x5a\x68\x34\x17\x72\x45\x38\x50\x90\x00\x00\x00\x00', '.bz2', 'bzip2, 4 w/o --small'),
            (b'\x42\x5a\x68\x35\x17\x72\x45\x38\x50\x90\x00\x00\x00\x00', '.bz2', 'bzip2, 5 w/o --small'),
            (b'\x42\x5a\x68\x36\x17\x72\x45\x38\x50\x90\x00\x00\x00\x00', '.bz2', 'bzip2, 6 w/o --small'),
            (b'\x42\x5a\x68\x37\x17\x72\x45\x38\x50\x90\x00\x00\x00\x00', '.bz2', 'bzip2, 7 w/o --small'),
            (b'\x42\x5a\x68\x38\x17\x72\x45\x38\x50\x90\x00\x00\x00\x00', '.bz2', 'bzip2, 8 w/o --small'),
            (b'\x42\x5a\x68\x39\x17\x72\x45\x38\x50\x90\x00\x00\x00\x00', '.bz2', 'bzip2, 9 w/o --small'),
            (b'\x5d\x00\x00\x10\x00\xff\xff\xff\xff\xff\xff\xff\xff\x00\x83\xff\xfb\xff\xff\xc0\x00\x00\x00', '.lzma', 'lzma, 1 +/- --extreme'),  # noqa: B950
            (b'\x5d\x00\x00\x20\x00\xff\xff\xff\xff\xff\xff\xff\xff\x00\x83\xff\xfb\xff\xff\xc0\x00\x00\x00', '.lzma', 'lzma, 2 +/- --extreme'),  # noqa: B950
            (b'\x5d\x00\x00\x40\x00\xff\xff\xff\xff\xff\xff\xff\xff\x00\x83\xff\xfb\xff\xff\xc0\x00\x00\x00', '.lzma', 'lzma, 3/4 +/- --extreme'),  # noqa: B950
            (b'\x5d\x00\x00\x80\x00\xff\xff\xff\xff\xff\xff\xff\xff\x00\x83\xff\xfb\xff\xff\xc0\x00\x00\x00', '.lzma', 'lzma, 5/6 +/- --extreme'),  # noqa: B950
            (b'\x5d\x00\x00\x00\x01\xff\xff\xff\xff\xff\xff\xff\xff\x00\x83\xff\xfb\xff\xff\xc0\x00\x00\x00', '.lzma', 'lzma, 7 +/- --extreme'),  # noqa: B950
            (b'\x5d\x00\x00\x00\x02\xff\xff\xff\xff\xff\xff\xff\xff\x00\x83\xff\xfb\xff\xff\xc0\x00\x00\x00', '.lzma', 'lzma, 8 +/- --extreme'),  # noqa: B950
            (b'\x5d\x00\x00\x00\x04\xff\xff\xff\xff\xff\xff\xff\xff\x00\x83\xff\xfb\xff\xff\xc0\x00\x00\x00', '.lzma', 'lzma, 9 +/- --extreme'),  # noqa: B950
            (b'\x28\xb5\x2f\xfd\x24\x00\x01\x00\x00\x99\xe9\xd8\x51', '.zst', 'zstd, 1-19, 20-22 w/ --ultra'),
            (b'\xfd\x37\x7a\x58\x5a\x00\x00\x04\xe6\xd6\xb4\x46\x00\x00\x00\x00\x1c\xdf\x44\x21\x1f\xb6\xf3\x7d\x01\x00\x00\x00\x00\x04\x59\x5a', '.xz', 'xz, 1-9 +/- --extreme'),  # noqa: B950
            (b'\x04\x22\x4d\x18\x64\x40\xa7\x00\x00\x00\x00\x05\x5d\xcc\x02', '.lz4', 'lz4, 1-12'),
            (b'\x50\x4b\x05\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', '.zip', 'zip, 0-9'),
            (b'\x4c\x5a\x49\x50\x01\x0c\x00\x83\xff\xfb\xff\xff\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x24\x00\x00\x00\x00\x00\x00\x00', '.lz', 'lzip, 0-9'),  # noqa: B950
            (b'\x37\x7a\xbc\xaf\x27\x1c\x00\x04\x8d\x9b\xd5\x0f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', '.7z', '7zip'),  # noqa: B950
            (b'\x1f\x8b\x08\x00\x00\x00\x00\x00\x04\x03\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00', '.gz', 'gzip, 1 (flg=0, mtime=0, xfl=4, os=3)'),  # noqa: B950
            (b'\x1f\x8b\x08\x00\x00\x00\x00\x00\x00\x03\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00', '.gz', 'gzip, 2-8 (flg=0, mtime=0, xfl=0, os=3)'),  # noqa: B950
            (b'\x1f\x8b\x08\x00\x00\x00\x00\x00\x02\x03\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00', '.gz', 'gzip, 9 (flg=0, mtime=0, xfl=2, os=3) (zopfli)'),  # noqa: B950
            (b'\x1f\x8b\x08\x00\x00\x00\x00\x00\x04\xff\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00', '.gz', 'gzip, 1 (flg=0, mtime=0, xfl=4, os=255)'),  # noqa: B950
            (b'\x1f\x8b\x08\x00\x00\x00\x00\x00\x00\xff\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00', '.gz', 'gzip, 2-8 (flg=0, mtime=0, xfl=0, os=255)'),  # noqa: B950
            (b'\x1f\x8b\x08\x00\x00\x00\x00\x00\x02\xff\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00', '.gz', 'gzip, 9 (flg=0, mtime=0, xfl=1, os=255)'),  # noqa: B950
            (b'\x33', '.br', 'brotli, 1'),
            (b'\xa1\x01', '.br', 'brotli, 2-11'),
            (b'\x02\x01\x73\x08\x00\x00\x00\x00\x01\x00\x00\x00\x10\x00\x00\x00', '.blosc', 'blosc, zlib, shuffle, 1-9'),
            (b'\x02\x01\x93\x08\x00\x00\x00\x00\x01\x00\x00\x00\x10\x00\x00\x00', '.blosc', 'blosc, zstd, shuffle, 1-9'),
            (b'\x02\x01\x13\x08\x00\x00\x00\x00\x01\x00\x00\x00\x10\x00\x00\x00', '.blosc', 'blosc, blosclz, shuffle, 1-9'),
            (b'\x02\x01\x33\x08\x00\x00\x00\x00\x01\x00\x00\x00\x10\x00\x00\x00', '.blosc', 'blosc, lz4/lz4hc, shuffle, 1-9'),
            (b'\x02\x01\x76\x08\x00\x00\x00\x00\x01\x00\x00\x00\x10\x00\x00\x00', '.blosc', 'blosc, zlib, bit shuffle, 1-9'),
            (b'\x02\x01\x96\x08\x00\x00\x00\x00\x01\x00\x00\x00\x10\x00\x00\x00', '.blosc', 'blosc, zstd, bit shuffle, 1-9'),
            (b'\x02\x01\x16\x08\x00\x00\x00\x00\x01\x00\x00\x00\x10\x00\x00\x00', '.blosc', 'blosc, blosclz, bit shuffle, 1-9'),
            (b'\x02\x01\x36\x08\x00\x00\x00\x00\x01\x00\x00\x00\x10\x00\x00\x00', '.blosc', 'blosc, lz4/lz4hc, bit shuffle, 1-9'),
            (b'\x02\x01\x72\x08\x00\x00\x00\x00\x01\x00\x00\x00\x10\x00\x00\x00', '.blosc', 'blosc, zlib, no shuffle, 1-9'),
            (b'\x02\x01\x92\x08\x00\x00\x00\x00\x01\x00\x00\x00\x10\x00\x00\x00', '.blosc', 'blosc, zstd, no shuffle, 1-9'),
            (b'\x02\x01\x12\x08\x00\x00\x00\x00\x01\x00\x00\x00\x10\x00\x00\x00', '.blosc', 'blosc, blosclz, no shuffle, 1-9'),
            (b'\x02\x01\x32\x08\x00\x00\x00\x00\x01\x00\x00\x00\x10\x00\x00\x00', '.blosc', 'blosc, lz4/lz4hc, no shuffle, 1-9'),
        )
        for data, suffix, description in tests:
            with self.subTest(description):
                self._test_checksum(data, suffix, expected=True)

    def test_checksum_non_match(self):
        tests = (
            (b'\x1f\x8b\x08\x00\x00\x00\x00\x00\x04\x01\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00', '.gz', 'unhandled gzip variant'),  # noqa: B950
            (b'\xa1\x02', '.br', 'invalid brotli'),
        )
        for data, suffix, description in tests:
            with self.subTest(description):
                self._test_checksum(data, suffix, expected=False)


class TestPrettySize(unittest.TestCase):

    def test_pretty_size(self):
        tests = (
            (1234, 'jedec', '1.2\xa0KB'),
            (1234, 'iec', '1.2\xa0KiB'),
            (1234, 'si', '1.2\xa0kB'),
            (213458923, 'jedec', '203.6\xa0MB'),
            (213458923, 'iec', '203.6\xa0MiB'),
            (213458923, 'si', '213.5\xa0MB'),
            (213458923000000000000000000, 'jedec', '198799113743007168.0\xa0GB'),
            (213458923000000000000000000, 'iec', '176.6\xa0YiB'),
            (213458923000000000000000000, 'si', '213.5\xa0YB'),
        )
        for size, prefix, expected in tests:
            with self.subTest(size=size, prefix=prefix):
                self.assertEqual(fst.pretty_size(size, prefix=prefix), expected)

    def test_unknown_prefix(self):
        with self.assertRaisesRegex(ValueError, r"^Expected prefix to be one of 'si', 'iec', or 'jedec'\.$"):
            fst.pretty_size(1234, prefix='unknown')
