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


COMPRESSION_LEVEL = 6
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
    def __init__(self, compressed_path, uncompressed_path=None, format=None,
                 output_dir=None, temp_dir=None, create=False,
                 compression_level=COMPRESSION_LEVEL):
        '''
        :param compressed_path: Path to the compressed file.
        :type compressed_path: str
        :param format: Format of the archive, if None the filename extension is
            used.
        :type format: str
        :param output_dir: Output directory to store the uncompressed file. If
            None, a temporary directory will be created and deleted on exit.
        :type output_dir: str
        :param temp_dir: Temporary directory to store the uncompressed file. If
            None, a system default will be used. Mutually exclusive with
            ``output_dir``.
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
        # Path to the uncompressed file
        self.uncompressed_path = uncompressed_path
        # Path where the uncompressed files will be stored
        self.output_dir = output_dir
        self.format = format
        # Prefix for temporary directory (if None, the system default will be
        # used)
        self.temp_dir = temp_dir
        # Temporary path containing uncompressed file. This directory will be
        # deleted in self.cleanup()!
        self.temp_path = None
        self.create = create
        self.compression_level = compression_level

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

        if extension and basename.endswith(extension):
            # Strip the compression extension
            basename, ext = os.path.splitext(basename)

        if self.output_dir is None:
            # This may fail if the process has no right to create files in
            # parent directory of self.temp_dir
            if self.temp_dir and not os.path.exists(self.temp_dir):
                os.makedirs(self.temp_dir)

            # Prepare the temporary directory to store the file
            # This directory will be deleted on exit!
            self.output_dir = tempfile.mkdtemp(dir=self.temp_dir)
            self.temp_path = self.output_dir

            if not os.path.isdir(self.output_dir):
                os.makedirs(self.output_dir)

        self.uncompressed_path = os.path.join(self.output_dir, basename)

        if not self.create:
            self.uncompress()

        return self.uncompressed_path

    def compress(self):
        '''
        Decompress the file and return the path to the contents.
        '''
        logger.debug('Recompressing file `%s` from temporary location `%s`',
                     self.compressed_path, self.uncompressed_path)

        with self.compressor(
                self.compressed_path, 'w',
                compresslevel=self.compression_level) as compressed_file:
            with file(self.uncompressed_path, 'rb') as uncompressed_file:
                compressed_file.write(uncompressed_file.read())

    def cleanup(self):
        '''
        Clean-up the temporary files.
        '''
        if self.temp_path and os.path.exists(self.temp_path):
            logger.debug('Deleting temporary directory `%s`',
                         self.temp_path)
            shutil.rmtree(self.temp_path)

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

    def __exit__(self, exc_type, exc_value, traceback):
        '''
        Save the archive contents with the defaults: the path the file was
        decompressed to in ``load()``.
        '''
        if exc_type is not None:
            # cleanup only
            self.cleanup()
        else:
            # save and cleanup
            self.save()

        return False  # re-raise exception, if any


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
        Uncompress the file if not found in the temporary location or the
        cached version is older than the compressed one.
        '''
        if not os.path.exists(self.uncompressed_path):
            need_to_update = True
        else:
            compressed_st = os.stat(self.compressed_path)
            uncompressed_st = os.stat(self.uncompressed_path)
            if uncompressed_st.st_mtime < compressed_st.st_mtime:
                need_to_update = True
            else:
                need_to_update = False

        if need_to_update:
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
