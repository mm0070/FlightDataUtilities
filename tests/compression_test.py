import os
import time
import tempfile
import unittest

from flightdatautilities.compression import (
    COMPRESSION_CLASSES,
    CompressedFile,
    ReadOnlyCompressedFile,
    CachedCompressedFile,
)


class TestCompression(unittest.TestCase):
    '''
    We use real file I/O here in temporary directory.
    '''
    def setUp(self):
        self.filenames = [tempfile.mktemp(suffix='.%s' % s) for s in COMPRESSION_CLASSES.keys() if s]

    def tearDown(self):
        for filename in self.filenames:
            if os.path.exists(filename):
                os.unlink(filename)

    def generateContent(self, filename):
        # Create a new compressed file
        with CompressedFile(filename, create=True) as uncompressed:
            with open(uncompressed, 'w+') as f:
                text = ' 1. This is the first line of content\n'
                f.write(text)

    def test_append(self):
        '''
        Normal mode: any changes in the uncompressed file will be saved on
        exit from the context manager.
        '''
        for filename in self.filenames:
            # Create contents of the files
            self.generateContent(filename)
            # Now let's try to write to it
            with CompressedFile(filename) as uncompressed:
                with open(uncompressed, 'a') as f:
                    text = ' 2. This is the second line of content\n'
                    f.write(text)

            # Now let's check the content of the file
            expected = [
                ' 1. This is the first line of content\n',
                ' 2. This is the second line of content\n',
            ]
            with CompressedFile(filename) as uncompressed:
                with open(uncompressed) as f:
                    self.assertListEqual(f.readlines(), expected)

    def test_ro(self):
        '''
        Read-only mode: any changes in the uncompressed file will be lost on
        exit from the context manager.
        '''
        # Read-only mode: the file is uncompressed, but it is not recompressed
        # on exit from `with` block, so any changes performed in the file are
        # lost.

        for filename in self.filenames:
            # Create contents of the file
            self.generateContent(filename)

            # Now let's open it in read-only mode:
            with ReadOnlyCompressedFile(filename) as uncompressed:
                with open(uncompressed, 'a') as f:
                    # This is ineffective, the compressed file will not be changed
                    text = 'WARNING: this will not be saved in the file!\n'
                    f.write(text)

            # The content of the file should be as created in the setUp()
            with ReadOnlyCompressedFile(filename) as uncompressed:
                with open(uncompressed) as f:
                    self.assertListEqual(f.readlines(), [' 1. This is the first line of content\n'])

    def test_cache(self):
        '''
        Cache mode: the file is not deleted after being uncompressed, so each
        subsequent access will use the cache. Any changes in the cache will
        '''

        cache_dir = tempfile.mkdtemp()

        for filename in self.filenames:
            # Create contents of the file
            self.generateContent(filename)
            # Now let's open it in cache mode:
            with CachedCompressedFile(filename, output_dir=cache_dir) as uncompressed:
                with open(uncompressed, 'a') as f:
                    text = ' 2. This is the second line of content, only available in the cached copy!\n'
                    f.write(text)

            # Let's open it in cache mode again, the file will be found, so it will
            # not be uncompressed again:
            expected = [
                ' 1. This is the first line of content\n',
                ' 2. This is the second line of content, only available in the cached copy!\n'
            ]
            with CachedCompressedFile(filename, output_dir=cache_dir) as uncompressed:
                # The contents of the cached file will be changed
                # read-only
                with open(uncompressed) as f:
                    self.assertListEqual(f.readlines(), expected)

            # Sleep for 1 sec. to let the mtimes differ
            time.sleep(1)

            # "touch" the original file
            os.utime(filename, None)

            # Let's open it in cache mode again, the file will be found, but older
            # than the original, so the cache will be refreshed. The extra content
            # will disappear.
            with CachedCompressedFile(filename, output_dir=cache_dir) as uncompressed:
                with open(uncompressed) as f:
                    self.assertListEqual(f.readlines(), expected[:1])

            os.unlink(uncompressed)

    def test_exc(self):
        '''
        Any exception raised in context manager should be propagated through.
        Changes made in the context manager should not be saved.
        '''
        def _raiseValueError(filename):
            with CompressedFile(filename, create=True) as uncompressed:
                with open(uncompressed, 'w+') as f:
                    text = ' This is a failed content, it should not appear in the compressed file\n'
                    f.write(text)
                raise ValueError

        for filename in self.filenames:
            self.assertRaises(ValueError, _raiseValueError, filename)
            # File should not have been created
            self.assertFalse(os.path.exists(filename))

            self.generateContent(filename)

            self.assertRaises(ValueError, _raiseValueError, filename)
            # File should still exist
            self.assertTrue(os.path.exists(filename))
            # The content of the file should not have changed
            with ReadOnlyCompressedFile(filename) as uncompressed:
                with open(uncompressed) as f:
                    self.assertListEqual(f.readlines(), [' 1. This is the first line of content\n'])


class TestCompressionFromFile(unittest.TestCase):
    '''
    Test creation of the compressed file from an existing uncompressed file.
    '''
    def setUp(self):
        self.filenames = {}
        self.uncompressed_filenames = {}

        for compression_format in COMPRESSION_CLASSES.keys():
            filename = tempfile.mktemp(suffix='.gz')
            uncompressed_filename = tempfile.mktemp()

            with open(uncompressed_filename, 'w+') as f:
                text = ' 1. This is the first line of content\n'
                f.write(text)
                text = ' 2. This is the second line of content\n'
                f.write(text)
            self.filenames[compression_format] = filename
            self.uncompressed_filenames[compression_format] = uncompressed_filename

    def tearDown(self):
        for uncompressed_filename in self.uncompressed_filenames.values():
            if os.path.exists(uncompressed_filename):
                os.unlink(uncompressed_filename)

        for filename in self.filenames.values():
            if os.path.exists(filename):
                os.unlink(filename)

    def test_fromfile(self):
        '''
        Create the compressed file from an existing one and compare the
        contents of the compressed version.
        '''
        for compression_format in COMPRESSION_CLASSES.keys():
            filename = self.filenames[compression_format]
            uncompressed_filename = self.uncompressed_filenames[compression_format]
            # Create the compressed version first
            cf = CompressedFile(filename, uncompressed_filename)
            cf.compress()

            with open(uncompressed_filename) as f:
                expected = f.readlines()

            # next uncompress the file and compare the contents
            with CompressedFile(filename) as uncompressed:
                with open(uncompressed) as f:
                    self.assertListEqual(f.readlines(), expected)


if __name__ == '__main__':
    unittest.main()
