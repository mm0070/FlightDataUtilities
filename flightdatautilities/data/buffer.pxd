# cython: language_level=3, boundscheck=False
cimport numpy as np

#cdef class WriteBuffer:
    #cdef:
        #np.uint16_t[:] _buffer
        #public Py_ssize_t size
        #cpdef bint write(self, np.uint16_t[:] data)
        #cpdef np.uint16_t[:] read(self)


#cdef class OutputBufferUint16:
    #cdef:
        #list _chunks
        #Py_ssize_t size
    #cdef add(self, np.uint16_t[:] data)
    #cdef flush(self)


cdef class Buffer:
    cdef:
        bint _array
        object _chunks
        object _empty
        public Py_ssize_t size
    cdef _join(self, chunks)
    cpdef clear(self)
    cpdef add(self, data)
    cpdef truncate(self, Py_ssize_t size)
    cpdef peek(self, Py_ssize_t size)
    cpdef read(self, Py_ssize_t size)


cdef class DataBufferUint8:
    cdef:
        object _chunks
        const np.uint8_t[:] _head
        Py_ssize_t _head_idx
        public Py_ssize_t size
    cdef Py_ssize_t _head_size(self) nogil
    cdef Py_ssize_t _pop(self)
    cdef const np.uint8_t[:] _read_head(self, Py_ssize_t size) nogil
    cdef void _truncate_head(self, Py_ssize_t size) nogil
    cpdef clear(self)
    cpdef add(self, const np.uint8_t[:] data)
    cpdef const np.uint8_t[:] read(self, Py_ssize_t size)
    cpdef const np.uint8_t[:] peek(self, Py_ssize_t size)
    cpdef truncate(self, Py_ssize_t size)
