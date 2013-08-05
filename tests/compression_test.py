#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import tempfile
import unittest

from flightdatautilities.compression import (
    CompressedFile,
    ReadOnlyCompressedFile,
    CachedCompressedFile,
)


class CompressionTest(unittest.TestCase):
    '''
    We use real file I/O here in temporary directory.
    '''
    def setUp(self):
        self.filename = tempfile.mktemp(suffix='.gz')

    def tearDown(self):
        if os.path.exists(self.filename):
            os.unlink(self.filename)

    def generateContent(self):
        # Create a new compressed file
        with CompressedFile(self.filename, create=True) as uncompressed:
            with file(uncompressed, 'w+') as f:
                text = ' 1. This is the first line of content\n'
                f.write(text)

    def test_append(self):
        '''
        Normal mode: any changes in the uncompressed file will be saved on
        exit from the context manager.
        '''
        # Create contents of the file
        self.generateContent()

        # Now let's try to write to it
        with CompressedFile(self.filename) as uncompressed:
            with file(uncompressed, 'a') as f:
                text = ' 2. This is the second line of content\n'
                f.write(text)

        # Now let's check the content of the file
        expected = [
            ' 1. This is the first line of content\n',
            ' 2. This is the second line of content\n',
        ]
        with CompressedFile(self.filename) as uncompressed:
            with file(uncompressed) as f:
                self.assertListEqual(f.readlines(), expected)

    def test_ro(self):
        '''
        Read-only mode: any changes in the uncompressed file will be lost on
        exit from the context manager.
        '''
        # Create contents of the file
        self.generateContent()
        self.generateContent()

        # Read-only mode: the file is uncompressed, but it is not recompressed
        # on exit from `with` block, so any changes performed in the file are
        # lost.

        # Now let's open it in read-only mode:
        with ReadOnlyCompressedFile(self.filename) as uncompressed:
            with file(uncompressed, 'a') as f:
                # This is ineffective, the compressed file will not be changed
                text = 'WARNING: this will not be saved in the file!\n'
                f.write(text)

        # The content of the file should be as created in the setUp()
        expected = [
            ' 1. This is the first line of content\n',
        ]
        with ReadOnlyCompressedFile(self.filename) as uncompressed:
            with file(uncompressed) as f:
                self.assertListEqual(f.readlines(), expected)

    def test_cache(self):
        '''
        Cache mode: the file is not deleted after being uncompressed, so each
        subsequent access will use the cache. Any changes in the cache will
        '''

        # Create contents of the file
        self.generateContent()

        cache_dir = tempfile.mkdtemp()

        # Now let's open it in cache mode:
        with CachedCompressedFile(self.filename, output_dir=cache_dir) \
                as uncompressed:
            with file(uncompressed, 'a') as f:
                text = ' 2. This is the second line of content, ' \
                    'only available in the cached copy!\n'
                f.write(text)

        # Let's open it in cache mode again, the file will be found, so it will
        # not be uncompressed again:
        expected = [
            ' 1. This is the first line of content\n',
            ' 2. This is the second line of content, '
            'only available in the cached copy!\n'
        ]
        with CachedCompressedFile(self.filename, output_dir=cache_dir) \
                as uncompressed:
            # The contents of the cached file will be changed
            # read-only
            with file(uncompressed) as f:
                self.assertListEqual(f.readlines(), expected)

        # Sleep for 1 sec. to let the mtimes differ
        time.sleep(1)

        # "touch" the original file
        os.utime(self.filename, None)

        # Let's open it in cache mode again, the file will be found, but older
        # than the original, so the cache will be refreshed. The extra content
        # will disappear.
        expected = [
            ' 1. This is the first line of content\n',
        ]
        with CachedCompressedFile(self.filename, output_dir=cache_dir) \
                as uncompressed:
            with file(uncompressed) as f:
                self.assertListEqual(f.readlines(), expected)

        os.unlink(uncompressed)

    def test_exc(self):
        '''
        Any exception raised in contest manager should be propagated through.
        Changes made in the context manager should not be saved.
        '''
        def _raiseValueError():
            with CompressedFile(self.filename, create=True) as uncompressed:
                with file(uncompressed, 'w+') as f:
                    text = ' This is a failed content, ' \
                        'it should not appear in the compressed file\n'
                    f.write(text)
                raise ValueError

        self.assertRaises(ValueError, _raiseValueError)
        # File should not have been created
        self.assertFalse(os.path.exists(self.filename))

        self.generateContent()
        self.assertRaises(ValueError, _raiseValueError)
        # File should still exist
        self.assertTrue(os.path.exists(self.filename))
        # The content of the file should not have changed
        expected = [
            ' 1. This is the first line of content\n',
        ]
        with ReadOnlyCompressedFile(self.filename) as uncompressed:
            with file(uncompressed) as f:
                self.assertListEqual(f.readlines(), expected)


if __name__ == '__main__':
    unittest.main()


###############################################################################
# vim:et:ft=python:nowrap:sts=4:sw=4:ts=4
