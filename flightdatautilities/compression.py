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


BUFFER_SIZE = 4096


logger = logging.getLogger(name=__name__)


COMPRESSION_LEVEL = 6
COMPRESSION_FORMATS = {
    'gz': gzip.GzipFile,
    'bz2': bz2.BZ2File,
}


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
                 compression_level=COMPRESSION_LEVEL, buffer_size=BUFFER_SIZE):
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
            logger.debug(
                'Format `%s` not recognised as compressed, passing the file %s '
                'unchanged', format, compressed_path)
            # We use bare file object, which will effectively copy the file to
            # the temp location and back.
            self.compressor = open
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
        self.buffer_size = buffer_size

    def __repr__(self):
        args = [
            self.compressed_path,
            self.uncompressed_path,
            self.format,
            self.output_dir,
            self.temp_dir,
            self.create,
            self.compression_level,
        ]
        args = [self.__class__.__name__] + [
            "'%s'" % v if isinstance(v, str) else v for v in args]
        return "%s(%s, uncompressed_path=%s, format=%s, output_dir=%s, " \
            "temp_dir=%s, create=%s, compression_level=%s)" % tuple(args)

    def _buffer_support(self):
        '''
        Check that the compressor class supports buffered reading and writing.
        Required for blosc limitations.
        '''
        return getattr(self.compressor, 'BUFFER_SUPPORT', True)

    def uncompress(self):
        '''
        Uncompress the file to temporary location.
        '''
        # Uncompress to temp file
        with open(self.uncompressed_path, 'w+b') as uncompressed_file:
            with self.compressor(self.compressed_path, 'rb') as compressed_file:
                if self.buffer_size is None or not self._buffer_support():
                    buffer = compressed_file.read()
                    uncompressed_file.write(buffer)
                else:
                    while True:
                        buffer = compressed_file.read(self.buffer_size)
                        uncompressed_file.write(buffer)
                        if len(buffer) < self.buffer_size:
                            break

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
                self.compressed_path, 'wb',
                compresslevel=self.compression_level) as compressed_file:
            with open(self.uncompressed_path, 'rb') as uncompressed_file:
                if self.buffer_size is None or not self._buffer_support():
                    buffer = uncompressed_file.read()
                    compressed_file.write(buffer)
                else:
                    while True:
                        buffer = uncompressed_file.read(self.buffer_size)
                        compressed_file.write(buffer)
                        if len(buffer) < self.buffer_size:
                            break

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


class CachedCompressedFile(ReadOnlyCompressedFile):
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


class CompressedFileWithoutCleanup(CompressedFile):
    '''
    Cleanup will not be performed if an exception is raised. The remaining file
    can be inspected for bug fixing purposes.
    '''
    def __exit__(self, exc_type, exc_value, traceback):
        '''
        Do not clean up if exception raised.
        '''
        if exc_type is None:
            # save and cleanup
            self.save()

        return False  # re-raise exception, if any


try:
    import blosc
except ImportError:
    pass
else:
    class BloscFile(object):
        # Size of bits to be compressed.
        TYPE_SIZE = 8
        BUFFER_SUPPORT = False

        def __init__(self, file_path, mode='rb', compression='blosclz',
                     compresslevel=9):
            '''
            Compression is only required for writing files.

            Q: Force maximum compresslevel?
            '''
            self.file_path = file_path
            self.compression = compression
            self.compresslevel = compresslevel
            self.file = open(self.file_path, mode)

        def __enter__(self):
            return self

        def __exit__(self, a_type, value, traceback):
            self.close()

        def read(self, buffer_size=None):
            '''
            Does not support buffer_size.
            '''
            return blosc.decompress(self.file.read())

        def write(self, bytes):
            compressed_bytes = blosc.compress(
                bytes, 8, clevel=self.compresslevel, cname=self.compression)
            self.file.write(compressed_bytes)

        def close(self):
            self.file.close()

    COMPRESSION_FORMATS['blosc'] = BloscFile


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file_path')
    parser.add_argument('-o', '--output-file-path')
    subparser = parser.add_subparsers(dest='command')
    compress_parser = subparser.add_parser('compress')
    compress_parser.add_argument('compressor')
    decompress_parser = subparser.add_parser('decompress')

    args = parser.parse_args()

    output_path = args.output_file_path

    if args.command == 'compress':
        compressor = COMPRESSION_FORMATS[args.compressor]
        if not output_path:
            output_path = args.input_file_path + '.%s' % args.compressor
        with compressor(output_path, 'w') as output_file, open(args.input_file_path) as input_file:
            output_file.write(input_file.read())
    elif args.command == 'decompress':
        for extension, decompressor in COMPRESSION_FORMATS.items():
            if args.input_file_path.endswith(extension):
                if not output_path:
                    output_path = args.input_file_path[:-(len(extension) + 1)]
                break
        else:
            parser.error('Unknown file extension')
        with open(output_path, 'w') as output_file:
            output_file.write(decompressor(args.input_file_path).read())


###############################################################################
# vim:et:ft=python:nowrap:sts=4:sw=4:ts=4
