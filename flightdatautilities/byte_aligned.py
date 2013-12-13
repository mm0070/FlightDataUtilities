
try:
    # bz2file provides support for multiple streams and a compatible interface.
    import bz2file as bz2
except ImportError:
    # Fallback to standard library.
    import bz2

import argparse
import logging
import numpy as np
import os


logging.basicConfig(format='%(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


SYNC_PATTERNS = {'Standard': (0x0247, 0x05B8, 0x0A47, 0x0DB8),
                 'Reversed': (0x0E24, 0x01DA, 0x0E25, 0x01DB)}

ORDINAL = ('first', 'second', 'third', 'fourth')

SUPPORTED_WPS = [64, 128, 256, 512, 1024, 2048]


def check_sync(file_obj, wps, word_index, pattern_name):
    '''
    Check sync words in the array.

    Performs analysis of sync words in the file to check if there are no
    sync problems.
    '''
    array = np.fromfile(file_obj, dtype=np.short)

    array &= 0xFFF

    s1 = np.array(
        np.nonzero(array == SYNC_PATTERNS[pattern_name][0])).flatten()
    s2 = np.array(
        np.nonzero(array == SYNC_PATTERNS[pattern_name][1])).flatten()
    s3 = np.array(
        np.nonzero(array == SYNC_PATTERNS[pattern_name][2])).flatten()
    s4 = np.array(
        np.nonzero(array == SYNC_PATTERNS[pattern_name][3])).flatten()
    syncs = np.concatenate((s1, s2, s3, s4))
    syncs = np.sort(syncs)
    syncs_i = iter(syncs)
    # print 'Sync words\n', syncs
    prev_sync = next(syncs_i)
    ix = prev_sync
    while ix < array.size:
        next_sync = ix + wps
        found = syncs == next_sync
        if np.any(found):
            ix = next_sync
        else:
            try:
                last_ix = ix
                ix = next(syncs_i)
                while ix < next_sync:
                    ix = next(syncs_i)
                logger.warning(
                    'Sync lost at word %d, next sync not found at %d, '
                    'found at %d instead', last_ix, next_sync, ix)
            except StopIteration:
                break

    syncs = np.ediff1d(syncs, to_begin=0, to_end=0)
    syncs[0] = syncs[1]
    syncs[-1] = syncs[-2]
    # print 'Distances\n', syncs
    syncs = np.ediff1d(syncs, to_begin=0, to_end=0)
    # print 'Slips\n', syncs


def inspect(file_obj, words_to_read):
    if isinstance(file_obj, file):
        words = np.fromfile(file_obj, dtype=np.short, count=words_to_read)
    else:
        words = np.fromstring(file_obj.read(words_to_read * 2), dtype=np.short)

    words &= 0xFFF

    for word_index, word in enumerate(
            words[:words_to_read - max(SUPPORTED_WPS)]):
        # 1. looking for first sync word
        for pattern_name, pattern in SYNC_PATTERNS.items():
            try:
                pattern_index = pattern.index(word)
                logger.debug('Found %s sync word 0x%x at %d',
                             ORDINAL[pattern_index], word, word_index)
                if pattern_index > 0:
                    # if it isnot the first superframe, keep looking
                    continue

                break
            except ValueError:
                continue
        else:
            # Current word did not match any sync word.
            continue

        pattern_index = (pattern_index + 1) % 4

        for wps in SUPPORTED_WPS:
            ix = word_index + wps
            if words[ix] == pattern[pattern_index]:
                logger.debug('Found second sync word 0x%x at %d.',
                             words[ix], ix)
                break
        else:
            # Sync word not found at any expected subframe boundary.
            continue

        pattern_index = (pattern_index + 1) % 4

        ix = word_index + (2 * wps)
        if words[ix] == pattern[pattern_index]:
            logger.debug('Found third sync word 0x%x at %d', words[ix], ix)
        else:
            continue

        pattern_index = (pattern_index + 1) % 4

        ix = word_index + (3 * wps)
        if words[ix] == pattern[pattern_index]:
            logger.debug('Found fourth sync word 0x%x at %d', words[ix], ix)
        else:
            continue
        logger.info('Found complete %d wps frame at word %d (byte %d) '
                    'with %s sync pattern.',
                    wps, word_index, word_index * 2, pattern_name)
        
        return wps, word_index, pattern_name
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
    parser.add_argument('--check-sync', action='store_true',
                        help='Check sync in the whole data.')

    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    if os.path.splitext(args.file_path)[1].lower() == '.bz2':
        file_obj = bz2.BZ2File(args.file_path)
    else:
        file_obj = open(args.file_path, 'rb')

    res = inspect(file_obj, args.words)

    if res and args.check_sync:
        wps, word_index, pattern_name = res
        file_obj.seek(0)
        check_sync(file_obj, wps, word_index, pattern_name)

    file_obj.close()


if __name__ == '__main__':
    main()
