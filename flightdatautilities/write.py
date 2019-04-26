import numpy as np
import os
import six

from io import BufferedWriter

from flightdatautilities.compression import (
    DEFAULT_COMPRESSION,
    FILE_CLASSES,
    iter_compress,
)
from flightdatautilities.iterext import iter_data, iter_dtype
from flightdatautilities.type import (
    is_array_like,
    is_data,
    is_split,
)


# Defines a standard postfix order for file metadata.
METADATA_KEYS = ('serial_number', 'wps', 'frame_double', 'split')


def iter_hash(data_gen, hash):
    '''
    Update a hash object with data from a generator.
    '''
    for data in data_gen:
        hash.update(data)
        yield data


def open_writable_file(filepath, compression=DEFAULT_COMPRESSION):
    '''
    :rtype: None
    '''
    if compression:
        filepath += '.' + compression
    return filepath, FILE_CLASSES[compression](filepath, ('wb' if six.PY2 else 'xb'))


def decompressed_filepath(filepath):
    '''
    Remove one extension of a compressed file format as it is unexpected
    that a writer would be passed pre-compressed data.
    '''
    name, ext = os.path.splitext(filepath)
    return name if ext.lstrip('.') in FILE_CLASSES else filepath


def write_data(fileobj, data):
    if is_array_like(data):
        data = np.asarray(data)  # convert memoryview if required
        if isinstance(fileobj, BufferedWriter):
            data.tofile(fileobj)
        else:
            fileobj.write(data.tostring())
    elif isinstance(data, six.binary_type):
        fileobj.write(data)
    else:
        raise NotImplementedError('Cannot write object: %s' % data)


def split_extension(metadata, metadata_keys=METADATA_KEYS):
    '''
    Generate a split extension from metadata.

    :rtype: str
    '''
    parts = []
    for key in metadata_keys:
        if key not in metadata:
            continue
        val = metadata[key]
        if key == 'frame_double':
            val = 'D' if val else 'S'
        fmt = '%03d' if key == 'split' else '%s'
        parts.append(fmt % val)
    return '.'.join(parts)


def memory_writer(data_gen):
    '''
    Write data iterable to list.
    '''
    return list(iter_data(data_gen))


def file_writer(filelike, data_gen, compression=DEFAULT_COMPRESSION):
    '''
    Write data iterable to filepath or file-like object (ignores splits).
    '''
    if isinstance(filelike, six.string_types):
        filepath = decompressed_filepath(filelike)
        filepath, fileobj = open_writable_file(filepath, compression=compression)
        for data in iter_data(data_gen):
            write_data(fileobj, data)
        return filepath
    else:
        data_gen = iter_dtype(iter_data(data_gen), None)

        if compression:
            data_gen = iter_compress(data_gen, compression)

        for data in data_gen:
            filelike.write(data)

        return filelike


def file_split_writer(filepath, data_gen, compression=DEFAULT_COMPRESSION):
    '''
    Write data iterable to multiple files with flight splitting.
    '''
    filepath = decompressed_filepath(filepath)
    metadata = {'split': 1}
    file = {}

    def iterate(data_gen):
        for data in data_gen:
            if data is None:
                continue
            elif is_split(data):
                metadata.update(data)
                if file:
                    file['fileobj'].close()
                    yield file['extension'], file['filepath']
                    file.clear()
                    metadata['split'] += 1
                continue
            elif not is_data(data):
                iterate(data)
                continue

            if not file:
                extension = split_extension(metadata)
                split_filepath, fileobj = open_writable_file(
                    filepath + '.' + extension,
                    compression=compression)
                file.update(extension=extension, fileobj=fileobj, filepath=split_filepath)

            write_data(file['fileobj'], data)

    for s in iterate(data_gen):
        yield s

    if file:
        file['fileobj'].close()
        yield file['extension'], file['filepath']


def memory_split_writer(data_gen):
    '''
    Write data to multiple lists with flight splitting.
    '''
    metadata = {'split': 1}
    split = {'chunks': []}

    def iterate(data_gen):
        for data in data_gen:
            if is_split(data):
                metadata.update(data)
                if split['chunks']:
                    yield split['extension'], split['chunks']
                    metadata['split'] += 1
                    split['chunks'] = []
                continue
            elif is_data(data):
                if not split['chunks']:
                    split['extension'] = split_extension(metadata)
                split['chunks'].append(data)

    for s in iterate(data_gen):
        yield s

    if split['chunks']:
        yield split['extension'], split['chunks']

