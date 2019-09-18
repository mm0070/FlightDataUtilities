'''
Context managers to decompress/compress files.

Useful to provide files in uncompressed format to procedures which don't
support compressed files. The files are stored compress to reduce storage
space.
'''

import bz2
import gzip
import io
import logging
import lzma
import os
import shutil
import tempfile
import zipfile
import zlib


logger = logging.getLogger(name=__name__)


# TODO: Add blosc
COMPRESSION_CLASSES = {
    'bz2': bz2.open,
    'gz': gzip.open,
    'xz': lzma.open,
    None: open,
}
ARCHIVE_CLASSES = {
    'sac': zipfile.ZipFile,  # AGS
    'zip': zipfile.ZipFile,
}
FILE_CLASSES = dict(COMPRESSION_CLASSES, **ARCHIVE_CLASSES)
COMPRESSORS = {
    'bz2': bz2.BZ2Compressor,
    'gz': zlib.compressobj,
    'xz': lzma.LZMACompressor,
}
DECOMPRESSORS = {
    'bz2': bz2.BZ2Decompressor,
    'gz': zlib.decompressobj,
    'xz': lzma.LZMADecompressor,
}
DEFAULT_COMPRESSION = 'bz2'


class CompressedFile(object):
    '''
    Context manager wrapping decompression and compression of given file.

    On enter the file is decompressed, based on `format` or autodetected based
    on filename extension (if ``format==None``).

    Uncompressed filename (in temp dir) is returned, allowing the context to do
    anything with the file.

    On exit the resulting file is compressed back to the original place.
    '''
    def __init__(self, compressed_path, uncompressed_path=None, format=None, mode='a', cache=False,
                 output_dir=None, temp_dir=None, create=False, compression_level=6, buffer_size=4096):
        '''
        :param compressed_path: Path to the compressed file.
        :type compressed_path: str
        :param format: Format of the archive, if None the filename extension is used.
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
        self.mode = mode[0] if mode else 'a'
        if create:
            # XXX: raise DeprecationWarning
            self.mode = 'w'
        if self.mode == 'r' and not os.path.exists(compressed_path):
            raise FileNotFoundError('File does not exist')

        if format is None:
            __, extension = os.path.splitext(compressed_path)
            format = extension.strip('.')

        if format in COMPRESSION_CLASSES:
            self.compressor = COMPRESSION_CLASSES[format]
            logger.debug('Using compressor `%s` for format `%s`', self.compressor, format)

        self.compressed_path = compressed_path
        # Path to the uncompressed file
        self.uncompressed_path = uncompressed_path
        # Path where the uncompressed files will be stored
        self.output_dir = output_dir

        self.format = format
        if self.format and self.mode == 'x' and os.path.exists(compressed_path):
            raise FileExistsError('File already exists')

        # Prefix for temporary directory (if None, the system default will be
        # used)
        self.temp_dir = temp_dir
        # Temporary path containing uncompressed file. This directory will be
        # deleted in self.cleanup()!
        self.temp_path = None
        self.compression_level = compression_level
        self.buffer_size = buffer_size
        self.cache = cache

    def __repr__(self):
        args = [
            self.compressed_path,
            self.uncompressed_path,
            self.format,
            self.output_dir,
            self.temp_dir,
            self.mode,
            self.compression_level,
        ]
        args = [self.__class__.__name__] + [
            "'%s'" % v if isinstance(v, str) else v for v in args]
        return "%s(%s, uncompressed_path=%s, format=%s, output_dir=%s, " \
            "temp_dir=%s, mode=%s, compression_level=%s)" % tuple(args)

    def uncompress(self):
        '''
        Uncompress the file to temporary location.
        '''
        if self.cache:
            cache_found = (
                os.path.exists(self.uncompressed_path)
                and os.stat(self.uncompressed_path).st_mtime >= os.stat(self.compressed_path).st_mtime
            )

            if cache_found:
                logger.debug('Found cached file `%s`, reuse it', self.uncompressed_path)
                return
            logger.debug('Cached file `%s` not found', self.uncompressed_path)

        with open(self.uncompressed_path, 'w+b') as uncompressed_file:
            with self.compressor(self.compressed_path, 'rb') as compressed_file:
                if self.buffer_size is None:
                    uncompressed_file.write(compressed_file.read())
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

        if self.mode != 'w':
            self.uncompress()

        return self.uncompressed_path

    def compress(self):
        '''
        Decompress the file and return the path to the contents.
        '''
        logger.debug('Recompressing file `%s` from temporary location `%s`',
                     self.compressed_path, self.uncompressed_path)

        with self.compressor(self.compressed_path, 'wb', **{'compresslevel': self.compression_level} if self.format in {'bz2', 'gz'} else {}) as compressed_file:
            with open(self.uncompressed_path, 'rb') as uncompressed_file:
                if self.buffer_size is None:
                    compressed_file.write(uncompressed_file.read())
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
            logger.debug('Deleting temporary directory `%s`', self.temp_path)
            shutil.rmtree(self.temp_path)

    def save(self):
        '''
        Compress the file and delete the temporary path.
        '''
        if self.format and not self.cache:
            if self.mode != 'r':
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
    """Deprecated: Compressed file wrapper for read-only access."""

    def __init__(self, *args, **kwargs):
        kwargs = kwargs.copy()
        kwargs['mode'] = 'r'
        super(ReadOnlyCompressedFile, self).__init__(*args, **kwargs)


class CachedCompressedFile(ReadOnlyCompressedFile):
    """Deprecated: Compressed file wrapper with caching."""

    def __init__(self, *args, **kwargs):
        kwargs = kwargs.copy()
        kwargs['cache'] = True
        super(CachedCompressedFile, self).__init__(*args, **kwargs)

    def uncompress(self):
        '''
        Uncompress the file if not found in the temporary location or the
        cached version is older than the compressed one.
        '''
        need_to_update = (
            not os.path.exists(self.uncompressed_path)
            or os.stat(self.uncompressed_path).st_mtime < os.stat(self.compressed_path).st_mtime
        )

        if need_to_update:
            logger.debug('Cached file `%s` not found', self.uncompressed_path)
            super(CachedCompressedFile, self).uncompress()
        else:
            logger.debug('Found cached file `%s`, reuse it', self.uncompressed_path)

    def save(self):
        '''
        Do nothing: we leave the temporary file for later use.
        '''
        pass


def iter_compress(data_iter, compression):
    '''
    Compress a data iterable with a compressor.
    '''
    compressor = COMPRESSORS[compression]()

    for data in data_iter:
        yield compressor.compress(data)

    yield compressor.flush()


def iter_decompress(data_iter, compression):
    '''
    Decompress a data iterable with a decompressor.
    '''
    decompressor = DECOMPRESSORS[compression]()

    for data in data_iter:
        yield decompressor.decompress(data)


def open_compressed(filepath, mode='rb'):
    '''
    Open filepath for reading which may be compressed or within an archive. Returns a file object and can therefore be used as a context manager.

    :param mode: either 'r' or 'rb', mode 'r' will always be in text mode, 'rb' in binary mode.
    :type mode: str
    '''
    if mode not in {'r', 'rb'}:
        raise ValueError('unsupported mode: %s' % mode)
    extension = os.path.splitext(filepath)[1].lstrip('.')
    archive_cls = ARCHIVE_CLASSES.get(extension)
    if archive_cls:
        archive = archive_cls(filepath)  # archive is closed automatically when fileobj within archive is closed
        filenames = archive.namelist()
        if len(filenames) != 1:
            raise IOError('Archives must contain a single file.')

        fileobj = archive.open(filenames[0], 'r')  # opens in binary mode
        if mode == 'r':
            fileobj = io.TextIOWrapper(fileobj)
    else:
        fileobj = COMPRESSION_CLASSES.get(extension, open)(filepath, 'rt' if mode == 'r' else mode)

    return fileobj


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
        compressor = COMPRESSION_CLASSES[args.compressor]
        if not output_path:
            output_path = args.input_file_path + '.%s' % args.compressor
        with compressor(output_path, 'w') as output_file, open(args.input_file_path) as input_file:
            output_file.write(input_file.read())
    elif args.command == 'decompress':
        for extension, decompressor in COMPRESSION_CLASSES.items():
            if args.input_file_path.endswith(extension):
                if not output_path:
                    output_path = args.input_file_path[:-(len(extension) + 1)]
                break
        else:
            parser.error('Unknown file extension')
        with open(output_path, 'w') as output_file:
            output_file.write(decompressor(args.input_file_path).read())

