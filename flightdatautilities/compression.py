'''
Context managers to decompress/compress files.

Useful to provide files in uncompressed format to procedures which don't
support compressed files. The files are stored compress to reduce storage
space.
'''

import os
import tempfile

import bz2
import gzip

import shutil
import logging


COMPRESSION_FORMATS = {
    'gz': gzip.GzipFile,
    'bz2': bz2.BZ2File,
}

logger = logging.getLogger(name=__name__)


class CompressedFile(object):
    '''
    Context manager wrapping decompression and compression of given file.

    On enter the file is decompressed, based on `format` or autodetected based
    on filename extension (if ``format==None``).

    Uncompressed filename (in temp dir) is returned, allowing the context to do
    anything with the file.

    On exit the resulting file is compressed back to the original place.
    '''
    def __init__(self, compressed_path, format=None, temp_dir=None,
                 create=False):
        '''
        :param compressed_path: Path to the compressed file.
        :type compressed_path: str
        :param format: Format of the archive, if None the filename extension is
            used.
        :type format: str
        :param temp_dir: Temporary directory to store the uncompressed file. If
            None, a random temporary directory name will be generated.
        :type temp_dir: str
        :param create: Create a new file instead of opening (will overwrite).
        :type create: bool
        '''
        if format is None:
            __, extension = os.path.splitext(compressed_path)
            format = extension.strip('.')

        if format in COMPRESSION_FORMATS:
            self.compressor = COMPRESSION_FORMATS[format]
            logger.debug('Using compressor `%s` for format `%s`',
                         self.compressor, format)
        else:
            logger.warning('Compression format `%s` not recognised, '
                           'passing the file %s unchanged', format,
                           compressed_path)
            # We use bare file object, which will effectively copy the file to
            # the temp location and back.
            self.compressor = file
            format = None

        self.compressed_path = compressed_path
        self.uncompressed_path = None
        self.temporary_dir = temp_dir
        self.format = format
        self.create = create

    def uncompress(self):
        '''
        Uncompress the file to temporary location.
        '''
        # Uncompress to temp file
        with file(self.uncompressed_path, 'w+b') as uncompressed_file:
            with self.compressor(self.compressed_path, 'r') as compressed_file:
                uncompressed_file.write(compressed_file.read())

        logger.debug('Uncompressed file stored in temporary location `%s`',
                     self.uncompressed_path)

    def load(self):
        '''
        Decompress the file and return the path to the contents.
        '''
        if self.format is None:
            # No-Op: return the original file
            self.uncompressed_path = self.compressed_path
            return self.compressed_path

        extension = '.' + self.format
        basename = os.path.basename(self.compressed_path)

        if self.temporary_dir is None:
            self.temporary_dir = tempfile.mkdtemp()

        if extension and basename.endswith(extension):
            # Strip the compression extension
            basename, ext = os.path.splitext(basename)

        new_path = os.path.join(self.temporary_dir, basename)

        if not os.path.isdir(self.temporary_dir):
            os.makedirs(self.temporary_dir)

        self.uncompressed_path = new_path

        if not self.create:
            self.uncompress()

        return self.uncompressed_path

    def compress(self):
        '''
        Decompress the file and return the path to the contents.
        '''
        logger.debug('Recompressing file `%s` from temporary location `%s`',
                     self.compressed_path, self.uncompressed_path)

        with self.compressor(self.compressed_path, 'w') as compressed_file:
            with file(self.uncompressed_path, 'rb') as uncompressed_file:
                compressed_file.write(uncompressed_file.read())

    def cleanup(self):
        '''
        Clean-up the temporary files.
        '''
        if self.temporary_dir and os.path.exists(self.temporary_dir):
            logger.debug('Deleting temporary directory `%s`',
                         self.uncompressed_path)
            shutil.rmtree(self.temporary_dir)

    def save(self):
        '''
        Compress the file and delete the temporary path.
        '''
        if self.format:
            self.compress()
            self.cleanup()

    def __enter__(self):
        '''
        Load the archive contents with the defaults.
        '''
        return self.load()

    def __exit__(self, a_type, value, traceback):
        '''
        Save the archive contents with the defaults: the path the file was
        decompressed to in ``load()``.
        '''
        return self.save()


class ReadOnlyCompressedFile(CompressedFile):
    '''
    Compressed file wrapper with caching.

    If the uncompressed file is found it will be reused instead of
    uncompressing from source again.

    This is a read-only solution: the changes to the uncompressed file are not
    saved back to archive (``self.compress()`` does not do anything)!
    '''
    def save(self):
        '''
        Don't save, only clean up the temporary files.
        '''
        self.cleanup()


class CachedCompressedFile(CompressedFile):
    '''
    Compressed file wrapper with caching.

    If the uncompressed file is found it will be reused instead of
    uncompressing from source again.

    This is a read-only solution: the changes to the uncompressed file are not
    saved back to archive (``self.compress()`` does not do anything)!
    '''
    def uncompress(self):
        '''
        Uncompress the file **if not found** in the temporary location.
        '''
        if not os.path.exists(self.uncompressed_path):
            logger.debug('Cached file `%s` not found', self.uncompressed_path)
            super(CachedCompressedFile, self).uncompress()
        else:
            logger.debug('Found cached file `%s`, reuse it',
                         self.uncompressed_path)

    def save(self):
        '''
        Do nothing: we leave the temporary file for later use.
        '''
        pass


###############################################################################
# vim:et:ft=python:nowrap:sts=4:sw=4:ts=4
