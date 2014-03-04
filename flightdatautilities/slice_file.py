import argparse
import os

from flightdatautilities.byte_aligned import inspect


def slice_file(source_file_path, dest_file_path, _slice,
               words_to_read=16384, buffer_size=1024 * 1024):
    '''
    Slice source_file_path using a range defined in seconds of flight data.
    
    TODO: Support bz2 files.
    TODO: Handle sync being lost within the file.
    
    :param source_file_path:
    :param _slice: Slice of data to include, indices are defined in seconds.
    :type _slice: slice
    :param words_to_read: Number of words to read from the file while attempting to find sync.
    :type words_to_read: int
    :param buffer_size: Size of data to store in memory while writing to dest_file_path.
    :type buffer_size: int
    '''
    with open(source_file_path, 'rb') as source_file_obj:
        wps, word_index, pattern_name = inspect(source_file_obj, words_to_read)
        if not wps:
            raise LookupError("Could not find byte-aligned flight data.")
        
        bytes_per_second = wps * 2
        slice_start = _slice.start if _slice.start else 0
        start_byte = (slice_start * bytes_per_second) + word_index
        if _slice.stop:
            end_byte = (_slice.stop * bytes_per_second) + word_index
        else:
            end_byte = os.path.getsize(source_file_path)
        
        total_bytes = end_byte - start_byte
        
        bytes_read = 0
        with open(dest_file_path, 'wb') as dest_file_obj:
            source_file_obj.seek(start_byte)
            
            while (bytes_read + buffer_size) < total_bytes:
                dest_file_obj.write(source_file_obj.read(buffer_size))
                bytes_read += buffer_size
            
            remaining_bytes = total_bytes - bytes_read
            dest_file_obj.write(source_file_obj.read(remaining_bytes))
    print 'Wrote %d bytes to %s.' % (total_bytes, dest_file_path)


def parse_args():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('source_file_path')
    parser.add_argument('dest_file_path')
    parser.add_argument('--slice-start', type=int)
    parser.add_argument('--slice-stop', type=int)
    parser.add_argument('-w', '--words-to-read', type=int, default=65536)
    parser.add_argument('-b', '--buffer-size', type=int, default=1024*1024)
    
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    slice_file(
        args.source_file_path,
        args.dest_file_path,
        slice(args.slice_start, args.slice_stop),
        words_to_read=args.words_to_read,
        buffer_size=args.buffer_size,
    )

if __name__ == '__main__':
    main()