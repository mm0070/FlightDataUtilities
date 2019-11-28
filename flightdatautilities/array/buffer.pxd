# cython: language_level=3, boundscheck=False
cdef class Buffer:
    cdef:
        bint _array
        object _chunks
        object _empty
        public Py_ssize_t size

    #cdef csize(self)
    #cpdef size(self)
    cdef _join(self, chunks)
    cpdef clear(self)
    cpdef add(self, data)
    cpdef truncate(self, Py_ssize_t size)
    cpdef peek(self, Py_ssize_t size)
    cpdef read(self, Py_ssize_t size)