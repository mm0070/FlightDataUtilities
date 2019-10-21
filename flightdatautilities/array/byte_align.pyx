# cython: language_level=3, boundscheck=False
'''
For '717' sync pattern see ARINC 717-12 document section 5.3.1.2.
For '573' sync pattern see ARINC 573-7 document Attachment 8-2.
'Custom 1' is a non-standard customised sync pattern.
573 may not be technically correct as the bit order is ambiguous in the specification.
This was rectified in the ARINC 717 standard.
'''
import cython
import numpy as np
cimport numpy as np

from libc.math cimport ceil

from flightdatautilities.array cimport cython as cy
from flightdatautilities.type import is_array_like


WPS = (64, 128, 256, 512, 1024, 2048)
SYNC_PATTERNS = {
    '573': (0xE24, 0x1DA, 0xE25, 0x1DB),
    '717': (0x247, 0x5B8, 0xA47, 0xDB8),
    'Custom 1': (0x0E0, 0x0E4, 0x0E8, 0x0EC),
}
MODES = SYNC_PATTERNS.keys()
STANDARD_MODES = ('573', '717')


@cython.wraparound(False)
cdef np.uint16_t[:] sync_words_from_modes(modes):
    '''
    Creates an array containing sync words in a contiguous 1d-array.

    e.g. sync_words_from_modes(['717'])
    '''
    cdef:
        np.uint16_t[:] sync_words = cy.empty_uint16(len(modes) * 4)
        Py_ssize_t sync_word_idx = 0
    for mode in modes:
        for sync_word in SYNC_PATTERNS[mode]:
            sync_words[sync_word_idx] = sync_word
            sync_word_idx += 1
    return sync_words


cdef class ByteAligner:
    '''
    Process (filter non-byte-aligned data) and identify the words per second of byte-aligned data.
    '''

    # TODO: Return count of synchronised bytes and bytes read from idenfity().
    # TODO: Add a flag for supporting the hfdams format:
    #       - Add support for checking the hdfams nibble bits, e.g. frame marker, etc.
    # TODO: Add a flag for supporting the rose format:
    #       - Automatically add one to each value of WPS.
    #       - Add support for stripping the rose word.
    #       - Perform some sort of check on the value of the rose word.
    def __init__(self, modes=None, wps=None, bint little_endian=True, Py_ssize_t output_buffer=16777216,
                 bint frames_only=False):
        '''
        :param modes: Sync pattern modes as defined within SYNC_PATTERNS. Default is all, running with a limited set is an optimisation.
        :type modes: iterable of str or None
        :param wps: All words per seconds which will be supported during processing. Default is all, running with a limited set is an optimisation.
        :type wps: iterable of str or None
        :param little_endian: Whether or not the byte-order is little_endian.
        :param output_buffer: Approximate number of bytes to store within the output buffer before yielding.
        :param frames_only: Only align complete frames and ignore extra subframes.
        '''
        if modes is None:
            modes = MODES
        if wps is None:
            wps = WPS

        self.sync_words = sync_words_from_modes(modes)
        self.little_endian = little_endian
        self._wps_array = np.array(sorted(wps), dtype=np.uint16)
        self._min_frame_size = self._wps_array[0] * 4 * 2
        self._max_frame_size = self._wps_array[-1] * 4 * 2
        self._output_buffer = output_buffer
        self._frames_only = frames_only
        self.reset()

    cpdef void reset(self):
        '''
        Reset the internal state to prepare for reuse with new data.
        '''
        self._buff = cy.empty_uint8(0)
        self._idx = 0
        self._frame_count = 0
        self._output_arrays = []

    cdef np.uint16_t _get_word(self, Py_ssize_t idx) nogil:
        '''
        Get the word value at specified byte index from the buffer. Masks out the unused most-significant nibble which
        is populated by HFDAMS.

        :param idx: byte index of the word within the buffer
        :returns: word value at byte index
        '''
        return (cy.read_uint16_le(self._buff, idx) if self.little_endian else cy.read_uint16_be(self._buff, idx)) \
            & 0xfff

    @cython.cdivision(True)
    @cython.wraparound(False)
    cdef Py_ssize_t _sync_word_idx(self, Py_ssize_t idx) nogil:
        '''
        Find the sync word index of the word within the buffer at specified byte index.

        :param idx: byte index of the word within the buffer
        :returns: sync word index if the word is a sync word, otherwise cy.NONE_IDX
        '''
        cdef:
            Py_ssize_t sync_word_idx
            np.uint16_t value = self._get_word(idx)
        for sync_word_idx in range(self.sync_words.shape[0]):
            if self._frames_only and (sync_word_idx % 4) != 0:
                continue
            if value == self.sync_words[sync_word_idx]:
                self._sync_word = value
                break
        else:
            return cy.NONE_IDX
        return sync_word_idx

    @cython.wraparound(False)
    cdef np.int16_t _frame_wps(self, Py_ssize_t idx) nogil:
        '''
        Find the wps of a frame starting at idx.

        :param idx: start index of potential frame to find wps for
        :returns: words per second if frame matches, otherwise -1
        '''
        cdef Py_ssize_t first_sync_word_idx = self._sync_word_idx(idx)

        if first_sync_word_idx == cy.NONE_IDX:
            return -1

        cdef:
            Py_ssize_t frame_idx, next_sync_word_idx, offset, wps_array_idx
            np.uint16_t wps

        for wps_array_idx in range(self._wps_array.shape[0]):
            wps = self._wps_array[wps_array_idx]
            if (idx + wps * 4 * 2) > self._buff.shape[0]:
                continue
            for offset in range(1, 5):
                frame_idx = idx + (wps * offset * 2)
                if frame_idx >= self._buff.shape[0]:
                    continue
                next_sync_word_idx = (first_sync_word_idx // 4 * 4) + ((first_sync_word_idx + offset) % 4)
                if self._get_word(frame_idx) != self.sync_words[next_sync_word_idx]:
                    break
            else:
                return wps
        return -1

    @cython.wraparound(False)
    cdef Py_ssize_t _next_frame_idx(self, Py_ssize_t idx) nogil:
        '''
        Find next frame start index within self._buff starting at idx.

        :param idx: index to start searching for frames within self._buff
        :returns: next frame index within self._buff or cy.NONE_IDX if frame is not found
        '''
        while True:
            if idx > (self._buff.shape[0] - self._min_frame_size):
                return cy.NONE_IDX
            self._wps = self._frame_wps(idx)
            if self._wps == -1:
                idx += 1
                continue
            return idx

    def _loop(self, data_gen, func):
        '''
        Find frame start indices and run provided func for each frame providing the start index as an argument.

        :type data_gen: generator yielding arrays or array
        :type func: callable
        :yields: value returned by func for each frame
        '''
        if is_array_like(data_gen):
            data_gen = (data_gen,)

        cdef Py_ssize_t idx, next_frame_idx, remainder_idx

        for data in data_gen:
            self._buff = np.concatenate((self._buff, data))
            idx = 0
            while True:
                next_frame_idx = self._next_frame_idx(idx)
                if next_frame_idx == cy.NONE_IDX:
                    remainder_idx = max(self._buff.shape[0] - self._max_frame_size, idx)
                    if remainder_idx <= 0:
                        break
                    self._idx += remainder_idx
                    self._buff = self._buff[remainder_idx:]
                    break
                self._frame_count += 1
                func_return = func(next_frame_idx)
                if func_return is not None:
                    yield func_return
                idx = next_frame_idx + self._wps * 4 * 2
        func_return = func(None) # flush
        if func_return is not None:
            yield func_return

    def process(self, data_gen, start=None, stop=None):
        '''
        Filter byte-aligned data. This version reimplements self._loop to avoid concatenating a frame worth of data each
        time which is ~10x faster for 64 words per second data.

        :type data_gen: generator yielding arrays or array
        :param start: data start position in seconds if not -1
        :type start: int or None
        :param stop: data stop position in seconds
        :type stop: int or None
        :yields: arrays containing synchronised byte-aligned data
        :ytype: np.array(dtype=np.uint8)
        '''

        if start is not None and stop is not None and stop <= start:
            raise ValueError('stop must be greater than start')
        elif start is not None and start < 0:
            raise ValueError('negative start index not supported')
        elif stop is not None and stop <= 0:
            raise ValueError('negative or zero stop index not supported')

        if is_array_like(data_gen):
            data_gen = (data_gen,)

        cdef:
            Py_ssize_t frame_start_idx = cy.NONE_IDX, frame_stop_idx = cy.NONE_IDX, idx = 0, \
                frame_start = cy.NONE_IDX if start is None else start // 4, \
                frame_stop = cy.NONE_IDX if stop is None else <Py_ssize_t>ceil(stop / 4.), next_frame_idx, remainder_idx

        for data in data_gen:
            self._buff = np.concatenate((self._buff, data))

            while True:
                next_frame_idx = self._next_frame_idx(idx)

                if next_frame_idx == cy.NONE_IDX:  # next frame not found
                    if frame_start_idx != cy.NONE_IDX:  # data has lost sync (possibly end of buffer)
                        yield np.asarray(self._buff[frame_start_idx:frame_stop_idx])
                        frame_start_idx = cy.NONE_IDX
                        frame_stop_idx = cy.NONE_IDX
                    # truncate buffer to remove already processed data
                    remainder_idx = self._buff.shape[0] - self._min_frame_size
                    idx = max(idx - remainder_idx, 0)
                    self._idx += remainder_idx
                    self._buff = self._buff[remainder_idx:]
                    break

                # next frame found
                self._frame_count += 1

                if frame_start != cy.NONE_IDX and self._frame_count <= frame_start:
                    # ignore frame before start index
                    idx = next_frame_idx + self._wps * 4 * 2
                    continue

                if frame_stop_idx != cy.NONE_IDX and next_frame_idx != frame_stop_idx:
                    # data was in sync, but next frame does not directly follow the previous frame
                    yield np.asarray(self._buff[frame_start_idx:frame_stop_idx])
                    frame_start_idx = next_frame_idx
                elif frame_start_idx == cy.NONE_IDX:
                    # data was previously not in sync
                    frame_start_idx = next_frame_idx

                frame_stop_idx = next_frame_idx + self._wps * 4 * 2

                if frame_stop != cy.NONE_IDX and frame_stop <= self._frame_count:
                    # reached stop index, stop searching for sync
                    yield np.asarray(self._buff[frame_start_idx:frame_stop_idx])
                    break

                idx = frame_stop_idx

            if frame_stop != cy.NONE_IDX and frame_stop <= self._frame_count:
                break

    def process_slow(self, data_gen, start=None, stop=None):
        '''
        Filter byte-aligned data. This version uses self._loop which is a consistent synchronisation implementation, but
        concatenating one frame at a time is ~10x slower at 64 words per second.

        :type data_gen: generator yielding arrays or array
        :param start: data start position in seconds if not -1
        :type start: int or None
        :param stop: data stop position in seconds
        :type stop: int or None
        :yields: arrays containing synchronised byte-aligned data
        :ytype: np.array(dtype=np.uint8)
        '''
        if start is not None and stop is not None and stop <= start:
            raise ValueError('stop must be greater than start')

        cdef:
            Py_ssize_t frame_start = cy.NONE_IDX if start is None else start // 4, \
                frame_stop = cy.NONE_IDX if stop is None else <Py_ssize_t>ceil(stop / 4.)

        def get_data(idx):
            if idx is None:
                return np.concatenate(self._output_arrays) if self._output_arrays else None
            if frame_start != cy.NONE_IDX and self._frame_count <= frame_start:
                return
            if frame_stop != cy.NONE_IDX and self._frame_count > frame_stop:
                if not self._output_arrays:
                    raise StopIteration
                output_array = np.concatenate(self._output_arrays)
                self._output_arrays = []
                return output_array
            cdef Py_ssize_t frame_size = self._wps * 4 * 2
            self._output_arrays.append(self._buff[idx:idx + frame_size])
            if sum(len(a) for a in self._output_arrays) >= self._output_buffer:
                output_array = np.concatenate(self._output_arrays)
                self._output_arrays = []
                return output_array
        return self._loop(data_gen, get_data)

    def identify(self, data_gen):
        '''
        Identify frame start indices and words per second.

        :type data_gen: generator yielding arrays or array
        :yields: tuples containing index, wps and type of frame starts
        :ytype: (int, int, str)
        '''
        def info(idx):
            if idx is None:
                return
            for mode, sync_words in SYNC_PATTERNS.items():
                if self._sync_word in sync_words:
                    break
            return (self._idx + idx, self._wps, mode)
        return self._loop(data_gen, info)


