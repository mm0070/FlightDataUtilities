# cython: language_level=3, boundscheck=False


cdef class base_reader:
    cdef:
        public object dtype
        public Py_ssize_t count
        public Py_ssize_t pos
        public Py_ssize_t stop
        object _callback
        bint _callback_exists
        Py_ssize_t _itemsize
        Py_ssize_t _prev_pos
    cpdef all(self)
    cpdef first(self)

cdef class data_reader(base_reader):
    cdef:
        object _data
    cpdef read(self, Py_ssize_t read_count)

cdef class iterable_reader(base_reader):
    cdef:
        object _data_iter

cdef class file_reader(base_reader):
    cdef:
        public object name
        object fileobj
    cpdef read(self, Py_ssize_t read_count)

