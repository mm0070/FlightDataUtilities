import io
import numpy as np
import zipfile
from collections import Iterator

from flightdatautilities.compression import open_compressed
from flightdatautilities.iterext import (
    chunk,
    join,
    iter_data_start_idx,
    iter_data_stop_idx,
    iter_dtype,
)
from flightdatautilities.type import (
    as_dtype,
    is_array_like,
    is_data,
    is_data_iterable,
)


class abstract_reader(Iterator):  # TODO: abc abstract class
    '''
    reader abstract base class.
    '''
    def __init__(self, dtype=None, count=16 * 1024 * 1024, start=None, stop=None, byte=True, callback=None, **kwargs):
        '''
        :param dtype: numpy array dtype to yield. If None, data will be read as a string.
        :type dtype: np.dtype or type or None
        :param count: Number of values to read from a file. The number of bytes depends on the size of the dtype. If None, the entire file will be read in one operation.
        :type count: int or None
        :param start: Start reading at this number of bytes if byte else items.
        :type start: int or None
        :param stop: Stop reading at this number of bytes if byte else items.
        :type stop: int or None
        :param byte: If True, start and stop are byte indices, otherwise they are a count of items.
        :type byte: bool
        :param callback: Progress callback.
        :type callback: callable or None
        '''
        self.dtype = np.dtype(dtype) if isinstance(dtype, type) else dtype
        self.itemsize = 1 if self.dtype is None else self.dtype.itemsize
        self.count = count
        if not byte:
            if start:
                start *= self.itemsize
            if stop:
                stop *= self.itemsize
        self.pos = start or 0
        self.prev_pos = self.pos
        self.stop = stop
        self.callback = callback
        self.byte = byte

    def __next__(self):
        read_count = min((self.stop - self.pos) // self.itemsize, self.count) if self.stop else self.count
        if read_count is not None and read_count <= 0:
            raise StopIteration

        data = self.next_data(read_count)

        if not len(data):
            raise StopIteration

        self.pos += len(data) * self.itemsize
        if self.callback and self.pos != self.prev_pos:  # TODO: callback progress
            self.callback(self.pos)
        self.prev_pos = self.pos
        return data

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        pass

    def __iter__(self):
        return self

    def all(self):
        '''
        Read all data and close file.
        '''
        with self as data_gen:
            return join(list(data_gen))

    def first(self):
        '''
        Read first iteration of data and close file.
        '''
        with self as data_gen:
            return next(iter(data_gen), None)


class data_reader(abstract_reader):
    '''
    Read data incrementally from an array or bytes.
    '''
    def __init__(self, data, *args, **kwargs):
        '''
        :param data: data to read from
        :type data: bytes or np.array
        '''
        super(data_reader, self).__init__(*args, **kwargs)
        data_dtype = data.dtype if is_array_like(data) else None
        data_itemsize = 1 if data_dtype is None else data_dtype.itemsize
        if self.pos % data_itemsize:
            stop = (len(data) if self.stop is None else self.stop) // data_itemsize * data_itemsize
            data = data.view(np.uint8)[self.pos:stop].view(data_dtype)
        self.data = as_dtype(data, self.dtype)

    def next_data(self, read_count):
        return self.data[self.pos // self.itemsize:(self.pos // self.itemsize) + read_count]


class generator_reader(abstract_reader):
    '''
    Read data from a data generator.
    '''
    def __init__(self, data_gen, *args, **kwargs):
        '''
        :param data_gen: data generator
        :type data_gen: generator
        '''
        super(generator_reader, self).__init__(*args, **kwargs)
        self.data_gen = data_gen

    def __enter__(self):
        if self.dtype is not None:
            self.data_gen = iter_dtype(self.data_gen, self.dtype)
        if self.pos:
            self.data_gen = iter_data_start_idx(self.data_gen, self.pos, byte=True)
        if self.stop is not None:
            self.data_gen = iter_data_stop_idx(self.data_gen, self.stop - self.pos, byte=True)
        if self.count:
            self.data_gen = chunk(self.data_gen, self.count, flush=True)
        return self

    def __next__(self):
        return next(self.data_gen)


class file_reader(abstract_reader):
    '''
    Read data from a file.
    '''
    def __init__(self, path, *args, **kwargs):
        '''
        :param path: file path or fileobj
        :type path: str or fileobj
        '''
        super(file_reader, self).__init__(**kwargs)
        self.path = path

    def __enter__(self):
        # TODO: Handle '-' as stdin, e.g. getattr(sys.stdin, 'buffer', sys.stdin)?
        self.fileobj = open_compressed(self.path) if isinstance(self.path, str) else self.path

        if self.pos:
            try:
                self.fileobj.seek(self.pos)
            except zipfile.io.UnsupportedOperation:
                # read when seek is not supported
                self.fileobj.read(self.pos)
        return self

    def __exit__(self, *exc_info):
        if not getattr(self.fileobj, 'closed', True):
            self.fileobj.close()

    def next_data(self, read_count):
        if self.dtype is not None and self.fileobj.__class__ is open:
            kwargs = {'dtype': self.dtype}
            if read_count:
                kwargs['count'] = read_count
            data = np.fromfile(self.fileobj, **kwargs)
        else:
            data = self.fileobj.read(read_count * self.itemsize) if read_count else self.fileobj.read()
            if self.dtype is not None:
                remainder = len(data) % self.itemsize
                if remainder:
                    data = data[:-remainder]
                data = np.frombuffer(data, dtype=self.dtype).copy()  # TODO: fast read-only option without copy
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

    :type obj: abstract_reader subclass object, bytes, str, np.array or generator
    :rtype: abstract_reader subclass object
    '''
    if isinstance(obj, abstract_reader):
        abstract_reader.__init__(obj, *args, **kwargs)  # update obj with constructor
        return obj
    elif is_data(obj):
        cls = data_reader
    elif is_data_iterable(obj):
        cls = generator_reader
    else:
        cls = file_reader  # filepath or fileobj
    return cls(obj, *args, **kwargs)


def read(data):
    '''
    Helper generator which enters and exits reader as a context manager (required for opening and closing files).
    '''
    with reader(data) as r:
        yield from r
