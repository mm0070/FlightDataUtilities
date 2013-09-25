import argparse
import logging
import numpy as np


logging.basicConfig(format='%(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


SYNC_PATTERNS = {'Standard': (0x0247, 0x05B8, 0x0A47, 0x0DB8),
                 'Reversed': (0x0E24, 0x01DA, 0x0E25, 0x01DB)}

SUPPORTED_WPS = [64, 128, 256, 512, 1024, 2048]


def inspect(file_obj, words_to_read):
    words = np.fromfile(file_obj, dtype=np.short, count=words_to_read) & 0xFFF

    for word_index, word in enumerate(words[:words_to_read - max(SUPPORTED_WPS)]):
        for pattern_name, pattern in SYNC_PATTERNS.items():
            try:
                pattern_index = pattern.index(word)
                logger.debug('Found first sync word at %d.', word_index)
                break
            except ValueError:
                continue
        else:
            # Current word did not match any sync word.
            continue

        pattern_index = (pattern_index + 1) % 4

        for wps in SUPPORTED_WPS:
            if words[word_index + wps] == pattern[pattern_index]:
                logger.debug('Found second sync word at %d.', word_index)
                break
        else:
            # Sync word not found at any expected subframe boundary.
            continue

        pattern_index = (pattern_index + 1) % 4

        if words[word_index + (2 * wps)] == pattern[pattern_index]:
            logger.debug('Found third sync word at %d', word_index)
        else:
            continue

        pattern_index = (pattern_index + 1) % 4

        if words[word_index + (3 * wps)] == pattern[pattern_index]:
            logger.debug('Found fourth sync word at %d', word_index)
        else:
            continue
        logger.info('Found complete %d wps frame at word %d (byte %d) with %s sync pattern.',
                    wps, word_index, word_index * 2, pattern_name)
        return
    logger.info('Could not find synchronised flight data.')


def main():
    print 'FlightDataInspector (c) Copyright 2013 Flight Data Services, Ltd.'
    print '  - Powered by POLARIS'
    print '  - http://www.flightdatacommunity.com'
    print ''

    parser = argparse.ArgumentParser()

    parser.add_argument('file_path')
    parser.add_argument('--words', action='store', default=16384, type=int,
                        help='Number of words to read from the file.')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug logging.')

    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)
    
    if args.file_path.splitext()[1].lower() == 'bz2':
        import bz2
        bz2.BZ2File()
    with open(args.file_path, 'rb') as file_obj:
        inspect(file_obj, args.words)


if __name__ == '__main__':
    main()
