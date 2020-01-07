# cython: language_level=3, boundscheck=False
from io import BufferedWriter
import os

import numpy as np

from flightdatautilities.compression import (
    COMPRESSION_CLASSES,
    DEFAULT_COMPRESSION,
    FILE_CLASSES,
    iter_compress,
)
from flightdatautilities.data cimport types
from flightdatautilities.data import iterate as it



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
    return filepath, COMPRESSION_CLASSES[compression](filepath, 'xb')


def decompressed_filepath(filepath):
    '''
    Remove one extension of a compressed file format as it is unexpected
    that a writer would be passed pre-compressed data.
    '''
    name, ext = os.path.splitext(filepath)
    return name if ext.lstrip('.') in FILE_CLASSES else filepath


def write_data(fileobj, data):
    if isinstance(data, np.ndarray) and isinstance(fileobj, BufferedWriter):
        data.tofile(fileobj)
    else:
        fileobj.write(data)


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
    return list(it.iter_data(data_gen))


def file_writer(filelike, data_gen, compression=DEFAULT_COMPRESSION):
    '''
    Write data iterable to filepath or file-like object (ignores splits).
    '''
    if isinstance(filelike, str):
        filepath = decompressed_filepath(filelike)
        filepath, fileobj = open_writable_file(filepath, compression=compression)
        for data in it.iter_data(data_gen):
            write_data(fileobj, data)
        return filepath
    else:
        data_gen = it.iter_as_dtype(it.iter_data(data_gen), None)

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
            elif types.is_split(data):
                metadata.update(data)
                if file:
                    file['fileobj'].close()
                    yield file['extension'], file['filepath']
                    file.clear()
                    metadata['split'] += 1
                continue
            elif not types.is_data(data):
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
            if types.is_split(data):
                metadata.update(data)
                if split['chunks']:
                    yield split['extension'], split['chunks']
                    metadata['split'] += 1
                    split['chunks'] = []
                continue
            elif types.is_data(data):
                if not split['chunks']:
                    split['extension'] = split_extension(metadata)
                split['chunks'].append(data)

    for s in iterate(data_gen):
        yield s

    if split['chunks']:
        yield split['extension'], split['chunks']

