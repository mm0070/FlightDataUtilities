import argparse
import os

from flightdataprocessing.formats.byte_aligned import inspect
from flightdatautilities.filesystem_tools import open_raw_data


BUFFER_SIZE = 1024 ** 2
WORDS_TO_READ = 16384


def slice_file(source, _slice, words_to_read=WORDS_TO_READ, buffer_size=BUFFER_SIZE):
    '''
    Slice source file object using a range defined in seconds of flight data.
    TODO: Handle sync being lost within the file.
    
    :param source: the file object to be sliced.
    :type source: file
    :type _slice: slice
    :param words_to_read: Number of words to read from the file while attempting to find sync.
    :type words_to_read: int
    :param buffer_size: Size of data to store in memory while writing to dest_file_path.
    :type buffer_size: int
    '''
    output = inspect([source], count=words_to_read * 2)[source]
    if output is None:
        raise LookupError("Could not find byte-aligned flight data.")
    idx, wps = output[:2]

    bytes_per_second = wps * 2
    slice_start = _slice.start if _slice.start else 0
    start_byte = (slice_start * bytes_per_second) + idx
    if _slice.stop:
        end_byte = (_slice.stop * bytes_per_second) + idx
    else:
        source.seek(0, os.SEEK_END)
        end_byte = source.tell()
    
    total_bytes = end_byte - start_byte

    bytes_read = 0
    
    source.seek(start_byte)

    while (bytes_read + buffer_size) < total_bytes:
        yield source.read(buffer_size)
        bytes_read += buffer_size

    remaining_bytes = total_bytes - bytes_read
    yield source.read(remaining_bytes)


def parse_args():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('source_file_path')
    parser.add_argument('dest_file_path')
    parser.add_argument('--slice-start', type=int)
    parser.add_argument('--slice-stop', type=int)
    parser.add_argument('-w', '--words-to-read', type=int, default=WORDS_TO_READ)
    parser.add_argument('-b', '--buffer-size', type=int, default=BUFFER_SIZE)
    
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    with open(args.dest_file_path, 'wb') as dest_file_obj:
        data_gen = slice_file(
            open_raw_data(args.source_file_path),
            slice(args.slice_start, args.slice_stop),
            words_to_read=args.words_to_read,
            buffer_size=args.buffer_size,
        )
        for data in data_gen:
            dest_file_obj.write(data)

if __name__ == '__main__':
    main()
