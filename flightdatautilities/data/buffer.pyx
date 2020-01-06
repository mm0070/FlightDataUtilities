# cython: language_level=3, boundscheck=False
from collections import deque

cimport cython
import numpy as np
cimport numpy as np

from flightdatautilities.data cimport cython as cy, types


cdef class WriteBufferUint8:
    '''
    Write buffer storing uint8 data for use within Cython only.

    OPT: This is an alternative to creating a list of very small arrays/memoryviews and concatenating them which is up
         to hundreds of times slower due to a high number of memory allocations rather than once in the case of the
         buffer.
    '''
    def __cinit__(self, Py_ssize_t size):
        if size <= 0:
            raise ValueError('buffer size must be positive')
        self.buffer = cy.empty_uint8(size)
        self.size = 0

    cdef inline Py_ssize_t free(self) nogil:
        '''
        Remaining free space within the buffer.
        '''
        return self.buffer.shape[0] - self.size

    cdef void write(self, data) except *:
        '''
        Write memoryview compatible object to buffer.

        OPT: slower than write_uint8
        '''
        self.write_uint8(types.view_dtype(data, np.uint8))

    cdef void write_uint8(self, const np.uint8_t[:] data) except *:
        '''
        Write uint8 memoryview to buffer.
        '''
        if data.shape[0] > self.free():
            raise ValueError('data too large for remaining buffer')
        self.buffer[self.size:self.size + data.shape[0]] = data
        self.size += data.shape[0]

    cdef np.uint8_t[:] writable_uint8(self, Py_ssize_t size, bint zero=False):
        '''
        Returns a memoryview slice of the buffer for writing to. As the memory of the buffer is uninitialized and not
        zeros by default, pass zero=True if all bytes aren't going to be written to.
        '''
        if size > self.free():
            raise ValueError('writable size too large for remaining buffer')
        elif size <= 0:
            raise ValueError('writable size must be positive')
        self.size += size
        return self.buffer[self.size - size:self.size]

    cdef np.uint8_t[:] flush(self) nogil:
        '''
        Flushes the buffer and returns a memoryview of the content. To avoid unnecessary copying, a view of the data
        is returned rather than a copy. Since the underlying memory shared between the buffer and the returned view will
        be overwritten if the buffer is subsequently written to, it may be required to make a copy of the returned
        memoryview.

        In the following example, copying is not required as the data will be written/copied elsewhere:

        for data in generator_which_writes_to_buffer_each_iteration():
            write_to_file_or_serialise(data)

        In this example, copying is required as the data will be referenced after the buffer has been rewritten:

        all_data = [d.copy() for d in generator_which_writes_to_buffer_each_iteration()]

        If it is expected that flushed data will be referenced after the buffer has been rewritten, it is safest to
        always copy flushed data:

        data = write_buffer.flush().copy()
        '''
        cdef np.uint8_t[:] flushed_data = self.buffer[:self.size]
        self.size = 0
        return flushed_data


cdef class WriteBufferUint16:
    '''
    Write buffer storing uint16 data for use within Cython only.

    OPT: This is an alternative to creating a list of very small arrays/memoryviews and concatenating them which is up
         to hundreds of times slower due to a high number of memory allocations rather than once in the case of the
         buffer.
    '''
    def __cinit__(self, Py_ssize_t size):
        if size <= 0:
            raise ValueError('buffer size must be positive')
        self.buffer = cy.empty_uint16(size)
        self.size = 0

    cdef inline Py_ssize_t free(self) nogil:
        '''
        Remaining free space (number of shorts rather thn bytes) within the buffer.
        '''
        return self.buffer.shape[0] - self.size

    cdef void write(self, data) except *:
        '''
        Write memoryview compatible object to buffer.

        OPT: slower than write_uint8/write_uint16
        '''
        self.write_uint16(types.view_dtype(data, np.uint16))

    cdef void write_uint16(self, const np.uint16_t[:] data) except *:
        '''
        Write uint16 memoryview to buffer.
        '''
        if self.size + data.shape[0] > self.buffer.shape[0]:
            raise ValueError('data too large for remaining buffer')
        self.buffer[self.size:self.size + data.shape[0]] = data
        self.size += data.shape[0]

    @cython.cdivision(True)
    @cython.wraparound(False)
    cdef void write_uint8(self, const np.uint8_t[:] data, bint byteswap=False) except *:
        '''
        Write uint8 memoryview to buffer. By default this will be written little-endian, pass byteswap=True for
        big-endian.
        '''
        if data.shape[0] % 2:
            raise ValueError('data size must be a multiple of 2')
        cdef Py_ssize_t short_size = data.shape[0] // 2
        if self.size + short_size > self.buffer.shape[0]:
            raise ValueError('data too large for remaining buffer')
        cdef Py_ssize_t buffer_offset, data_idx
        for buffer_offset in range(short_size):
            data_idx = buffer_offset * 2
            self.buffer[self.size + buffer_offset] = (data[data_idx] << 8 | data[data_idx + 1]) if byteswap else \
                (data[data_idx + 1] << 8 | data[data_idx])
        self.size += short_size

    cdef np.uint16_t[:] writable_uint16(self, Py_ssize_t size):
        '''
        Write uint16 memoryview to buffer.
        '''
        if size > self.free():
            raise ValueError('writable size too large for remaining buffer')
        elif size <= 0:
            raise ValueError('writable size must be positive')
        self.size += size
        return self.buffer[self.size - size:self.size]

    cdef np.uint16_t[:] flush(self):
        '''
        Flushes the buffer and returns a memoryview of the content. To avoid unnecessary copying, a view of the data
        is returned rather than a copy. Since the underlying memory shared between the buffer and the returned view will
        be overwritten if the buffer is subsequently written to, it may be required to make a copy of the returned
        memoryview.

        In the following example, copying is not required as the data will be written/copied elsewhere:

        for data in generator_which_writes_to_buffer_each_iteration():
            write_to_file_or_serialise(data)

        In this example, copying is required as the data will be referenced after the buffer has been rewritten:

        all_data = [d.copy() for d in generator_which_writes_to_buffer_each_iteration()]

        If it is expected that flushed data will be referenced after the buffer has been rewritten, it is safest to
        always copy flushed data:

        data = write_buffer.flush().copy()
        '''
        cdef np.uint16_t[:] flushed_data = self.buffer[:self.size]
        self.size = 0
        return flushed_data


cdef class DataBufferUint8:
    '''
    Buffer optimised for adding megabytes of uint8 data and reading smaller sizes repeatedly.

    OPT: By storing the head memoryview as a pointer within the extension class's struct, data can be read, peeked and
         truncated from the buffer without Python overhead. ~8x faster than non-pointer for reading 16 bytes at a time.
    '''
    def __cinit__(self):
        self._chunks = deque()

    @cython.initializedcheck(False)
    cdef inline Py_ssize_t _head_size(self) nogil:
        '''
        Size of the head memoryview adjusted for the current position.
        '''
        return self._head.shape[0] - self._head_idx

    @cython.initializedcheck(False)
    cdef Py_ssize_t _pop(self):
        '''
        Pop the head memoryview and replace with a chunk. There must be at least one chunk after the head.
        '''
        cdef Py_ssize_t head_size = self._head_size()
        self.size -= head_size
        self._head = self._chunks.popleft()
        self._head_idx = 0
        return head_size

    @cython.initializedcheck(False)
    cdef inline const np.uint8_t[:] _read_head(self, Py_ssize_t size) nogil:
        '''
        Reads data from the head of the buffer (also truncates). Size must be within the size of the head memoryview.
        '''
        cdef const np.uint8_t[:] data = self._head[self._head_idx:self._head_idx + size]
        self._truncate_head(size)
        return data

    @cython.initializedcheck(False)
    cdef inline void _truncate_head(self, Py_ssize_t size) nogil:
        '''
        Truncates data from the head of the buffer. Size must be within the size of the head memoryview.
        '''
        self._head_idx += size
        self.size -= size

    @cython.initializedcheck(False)
    cpdef clear(self):
        '''
        Clear the buffer of all data.
        '''
        if not self.size:
            return
        if self.size <= self._head_size():
            self.size = 0
            return
        self.size = 0
        self._chunks.clear()

    @cython.initializedcheck(False)
    cpdef add(self, const np.uint8_t[:] data):
        '''
        Add data to the buffer.
        '''
        if not data.shape[0]:
            return
        if not self.size:
            self._head = data
            self._head_idx = 0
        else:
            self._chunks.append(data)
        self.size += data.shape[0]

    @cython.initializedcheck(False)
    cpdef const np.uint8_t[:] read(self, Py_ssize_t size):
        '''
        Read data size from the start of the buffer (also truncates).
        '''
        cdef const np.uint8_t[:] data
        if size <= 0 or not self.size:
            return cy.empty_uint8(0)

        if size > self.size:
            size = self.size

        if size <= self._head_size():
            return self._read_head(size)
        elif size == self.size:
            self._chunks.appendleft(self._head[self._head_idx:])
            data = np.concatenate(self._chunks)  #cy.concatenate_uint8(self._chunks)
            self.clear()
            return data

        cdef list chunks = [self._head[self._head_idx:]]
        size -= self._pop()

        while size >= self._head_size():
            chunks.append(self._head)
            size -= self._pop()

        if size:
            chunks.append(self._read_head(size))

        return np.concatenate(chunks)  #cy.concatenate_uint8(chunks)

    @cython.initializedcheck(False)
    cpdef const np.uint8_t[:] peek(self, Py_ssize_t size):
        '''
        Peek data size from the start of the buffer.
        '''
        if size <= 0 or not self.size:
            return cy.empty_uint8(0)
        elif size <= self._head_size():
            return self._head[self._head_idx:self._head_idx + size]

        cdef list chunks = [self._head[self._head_idx:]]
        size -= self._head_size()
        for chunk in self._chunks:
            if size < len(chunk):
                if size:
                    chunks.append(chunk[:size])
                break
            chunks.append(chunk)
            size -= len(chunk)

        return cy.concatenate_uint8(chunks)

    @cython.initializedcheck(False)
    cpdef truncate(self, Py_ssize_t size):
        '''
        Truncate data size from the start of the buffer.
        '''
        if size <= 0 or not self.size:
            return
        elif size >= self.size:
            self.clear()
            return
        elif size < self._head_size():
            self._truncate_head(size)
            return

        while size >= self._head_size():
            size -= self._pop()

        if size:
            self._truncate_head(size)


cdef class Buffer:
    '''
    Buffer optimised for adding megabytes of data and reading smaller sizes repeatedly.

    Can store arrays, memoryviews or bytes. bytes are stored as memoryviews internally for copy-less slicing.
    '''
    def __init__(self, dtype=None):
        self._array = bool(dtype)
        self._empty = np.zeros(0, dtype=dtype) if self._array else b''
        self._chunks = deque()

    cdef _join(self, chunks):
        '''
        Join chunks as either bytes or a numpy array depending on dtype.
        '''
        return np.concatenate(chunks) if self._array else b''.join(chunks)

    cpdef clear(self):
        '''
        Clear the buffer of all data.
        '''
        self._chunks.clear()
        self.size = 0

    cpdef add(self, data):
        '''
        Add data to theend of the buffer.

        :type data: np.ndarray, memoryview or bytes
        '''
        cdef Py_ssize_t data_size = len(data)
        if not data_size:
            return
        self.size += data_size
        self._chunks.append(data if self._array else memoryview(data))

    cpdef truncate(self, Py_ssize_t size):
        '''
        Remove size of data from the buffer.
        '''
        if size <= 0 or not self.size:
            return
        elif size >= self.size:
            self.clear()
            return
        cdef Py_ssize_t chunk_size
        while True:
            chunk_size = len(self._chunks[0])
            if size >= chunk_size:
                self._chunks.popleft()
                self.size -= chunk_size
                size -= chunk_size
            else:
                if size:
                    self._chunks[0] = self._chunks[0][size:]
                    self.size -= size
                break

    cpdef peek(self, Py_ssize_t size):
        '''
        Peek data from the start of the buffer.
        '''
        if size <= 0 or not self.size:
            return self._empty
        elif size >= self.size:
            return self._join(self._chunks)

        cdef Py_ssize_t chunk_size = len(self._chunks[0])
        if size < chunk_size:
            return self._chunks[0][:size]

        peek_chunks = []
        for chunk in self._chunks:
            if not peek_chunks:
                peek_chunks.append(chunk)
                size -= chunk_size
                continue
            chunk_size = len(chunk)
            if size >= chunk_size:
                peek_chunks.append(chunk)
                if size == chunk_size:
                    break
                size -= chunk_size
            elif size:
                peek_chunks.append(chunk[:size])
                break

        return self._join(peek_chunks)

    cpdef read(self, Py_ssize_t size):
        '''
        Read data from the start of the buffer (also truncates).
        '''
        if size <= 0 or not self.size:
            return self._empty
        elif size >= self.size:
            data = self._join(self._chunks)
            self.clear()
            return data

        cdef Py_ssize_t chunk_size = len(self._chunks[0])
        if size < chunk_size:
            data = self._chunks[0][:size]
            self._chunks[0] = self._chunks[0][size:]
            self.size -= size
            return data

        read_chunks = []
        while True:
            if size >= chunk_size:
                read_chunks.append(self._chunks.popleft())
                self.size -= chunk_size
                if size == chunk_size:
                    break
                size -= chunk_size
            elif size:
                read_chunks.append(self._chunks[0][:size])
                self._chunks[0] = self._chunks[0][size:]
                self.size -= size
                break
            chunk_size = len(self._chunks[0])

        return self._join(read_chunks)

