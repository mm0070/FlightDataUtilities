# cython: language_level=3, boundscheck=False
import io
import zipfile

cimport cython
import numpy as np

from flightdatautilities.compression import open_compressed
from flightdatautilities.data cimport types
from flightdatautilities.data import iterate as it


cdef Py_ssize_t READ_SIZE = 16 * 1024 * 1024


cdef class base_reader:
    def __init__(self, dtype=False, Py_ssize_t count=READ_SIZE, Py_ssize_t start=0, Py_ssize_t stop=0, bint byte=True,
                 callback=None, **kwargs):
        if start < 0:
            raise ValueError('start must be 0 (default) or positive')
        if stop < 0:
            raise ValueError('stop must be 0 (default - continue until the end) or positive')
        if stop and stop <= start:
            raise ValueError('stop must be greater than start')
        if count <= 0:
            raise ValueError('count must be positive')

        self.dtype = dtype and np.dtype(dtype)
        self._itemsize = self.dtype.itemsize if dtype else 1

        if self._itemsize != 1 and not byte:
            start *= self._itemsize
            stop *= self._itemsize

        self.count = count
        self.pos = start
        self._prev_pos = self.pos
        self.stop = stop
        self._callback_exists = callback is not None
        if self._callback_exists:
            self._callback = callback

    def __next__(self):
        cdef Py_ssize_t read_count

        if self.stop:
            read_count = (self.stop - self.pos) // self._itemsize
            if read_count > self.count:
                read_count = self.count
        else:
            read_count = self.count

        if read_count <= 0:
            raise StopIteration

        data = self.read(read_count)

        cdef Py_ssize_t data_size = len(data)
        if not data_size:
            raise StopIteration

        self.pos += data_size * self._itemsize
        if self._callback_exists and self.pos != self._prev_pos:  # TODO: callback progress
            self._callback(self.pos)
        self._prev_pos = self.pos
        return data

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        pass

    def __iter__(self):
        return self

    cpdef all(self):
        with self as data_iter:
            return it.join(self)

    cpdef first(self):
        with self as data_iter:
            return next(iter(data_iter), None)


cdef class data_reader(base_reader):
    '''
    Read data incrementally from an array or bytes.
    '''
    def __init__(self, data, *args, **kwargs):
        '''
        :param data: data to read from
        :type data: types.is_data compatible
        '''
        super(data_reader, self).__init__(*args, **kwargs)
        if self.dtype is not False:
            data_dtype = types.get_dtype(data)
            if data_dtype != self.dtype:
                data = types.view_dtype(data, self.dtype)
        self._data = data

    cpdef read(self, Py_ssize_t read_count):
        return self._data[self.pos // self._itemsize:(self.pos // self._itemsize) + read_count]


cdef class iterable_reader(base_reader):
    '''
    Read data from a data iterable.

    OPT: This is not optimised for performance and is implemented so that existing readers/iterables can be wrapped
         consistently.
    '''
    def __init__(self, data_iter, *args, **kwargs):
        '''
        :param data_iter: data iterable
        :type data_iter: iterable
        '''
        super(iterable_reader, self).__init__(*args, **kwargs)
        self._data_iter = data_iter

    @cython.cdivision(True)
    def __enter__(self):
        if self.dtype is False:
            self._data_iter = it.chunk(self._data_iter, self.count, flush=True)
        else:
            # OPT: it.chunk_uint8 is faster than it.chunk, so always view as uint8 for simplicity
            self._data_iter = it.chunk_uint8(it.iter_view_dtype(self._data_iter, np.uint8), self.count * self._itemsize,
                                             flush=True)
        if self.pos:
            self._data_iter = it.iter_data_start_idx(self._data_iter, self.pos)
        if self.stop:
            self._data_iter = it.iter_data_stop_idx(self._data_iter, self.stop - self.pos)
        if self.dtype is not False:
            self._data_iter = it.iter_view_dtype(self._data_iter, self.dtype)
        return self

    def __next__(self):
        return next(self._data_iter)


cdef class file_reader(base_reader):
    '''
    Read data from a file.
    '''
    def __init__(self, path, *args, **kwargs):
        '''
        :param path: file path or fileobj
        :type path: str or fileobj
        '''
        kwargs['dtype'] = kwargs.get('dtype') or None  # change False to None
        super(file_reader, self).__init__(**kwargs)
        self.name = path

    def __enter__(self):
        # TODO: Handle '-' as stdin, e.g. getattr(sys.stdin, 'buffer', sys.stdin)?
        self.fileobj = open_compressed(self.name) if isinstance(self.name, str) else self.name

        if self.pos:
            try:
                self.fileobj.seek(self.pos)
            except zipfile.io.UnsupportedOperation:
                self.fileobj.read(self.pos)  # read as seek is not supported
        return self

    def __exit__(self, *exc_info):
        if not getattr(self.fileobj, 'closed', True):
            self.fileobj.close()

    cpdef read(self, Py_ssize_t read_count):
        if self.dtype is not None and self.fileobj.__class__ is open:
            kwargs = {'dtype': self.dtype}
            if read_count:
                kwargs['count'] = read_count
            data = np.fromfile(self.fileobj, **kwargs)
        else:
            data = self.fileobj.read(read_count * self._itemsize) if read_count else self.fileobj.read()
            if self.dtype is not None:
                remainder = len(data) % self._itemsize
                if remainder:
                    data = data[:-remainder]
                data = np.frombuffer(data, dtype=self.dtype)  #.copy()  # TODO: fast read-only option without copy
        return data


class StringIteratorIO(io.TextIOBase):
    '''
    Copied from https://stackoverflow.com/questions/12593576/adapt-an-iterator-to-behave-like-a-file-like-object-in-python
    '''

    def __init__(self, iter):
        self._iter = iter
        self._left = ''

    def readable(self):
        return True

    def _read1(self, n=None):
        while not self._left:
            try:
                self._left = next(self._iter)
            except StopIteration:
                break
        ret = self._left[:n]
        self._left = self._left[len(ret):]
        return ret

    def read(self, n=None):
        l = []
        if n is None or n < 0:
            while True:
                m = self._read1()
                if not m:
                    break
                l.append(m)
        else:
            while n > 0:
                m = self._read1(n)
                if not m:
                    break
                n -= len(m)
                l.append(m)
        return ''.join(l)

    def readline(self):
        l = []
        while True:
            i = self._left.find('\n')
            if i == -1:
                l.append(self._left)
                try:
                    self._left = next(self._iter)
                except StopIteration:
                    self._left = ''
                    break
            else:
                l.append(self._left[:i+1])
                self._left = self._left[i+1:]
                break
        return ''.join(l)


def reader(obj, *args, **kwargs):
    '''
    reader factory which creates a reader based on the type of obj.

    :type obj: base_reader subclass object, bytes, str, np.array or generator
    :rtype: base_reader subclass object
    '''
    if types.is_data(obj):
        cls = data_reader
    elif types.is_data_iterable(obj):
        cls = iterable_reader
    else:
        cls = file_reader  # filepath or fileobj
    return cls(obj, *args, **kwargs)


def read(data):
    '''
    Helper generator which enters and exits reader as a context manager (required for opening and closing files).
    '''
    with reader(data) as r:
        yield from r

