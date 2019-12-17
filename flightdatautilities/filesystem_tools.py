import bz2
import hashlib
import io
import os
import pathlib
import shutil
import zipfile
import zlib

from deprecated import deprecated


# TODO: Convert into a context manager to ensure data file is closed properly?
# TODO: Retire in favour of upcoming new routines in stream-handling helpers?
def open_raw_data(filepath, binary=True):
    '''
    Open the input file which may be compressed.

    :param filepath: Path of raw data file which can either be zip, bz2 or uncompressed.
    :type filepath: str

    :returns: An opened file object.
    :rtype: file
    '''
    extension = os.path.splitext(filepath)[1].lower()

    if extension in {'.sac', '.zip'}:
        zf = zipfile.ZipFile(filepath, 'r')
        filenames = zf.namelist()
        if len(filenames) != 1:
            raise OSError('Zip files must contain only a single data file.')
        return zf.open(filenames[0])

    if extension in {'.bz2'}:
        return bz2.BZ2File(filepath, 'r')

    return open(filepath, 'rb' if binary else 'r')


def copy_file(orig_path, dest_dir=None, postfix='_copy'):
    '''
    Creates a copy of the file with the postfix inserted between the filename
    and the extension. Can create copy into a different path (will create
    folders as required)

    :param orig_path: Path to original file
    :type orig_path: path
    :param dest_dir: Put copy of file into a different directory, e.g. 'temp/'
    :type dest_dir: path
    :param postfix: Rename copy of file with postfix before file extension
    :type postfix: string
    '''
    assert dest_dir or postfix, "Must define either dest_dir or postfix"
    path_minus_ext, ext = os.path.splitext(orig_path)
    if dest_dir:
        filename = os.path.basename(path_minus_ext)
        path_minus_ext = os.path.join(dest_dir, filename)
        os.makedirs(dest_dir, exist_ok=True)
    copy_path = path_minus_ext + postfix + ext
    if os.path.isfile(copy_path):
        os.remove(copy_path)
    shutil.copy(orig_path, copy_path)
    return copy_path


def checksum(x, *, algorithm='sha256'):
    """Calculate the checksum of a file using the specified algorithm."""
    def reader(x, *, size=32768):
        if isinstance(x, io.IOBase) and x.seekable():
            pointer = x.tell()
            x.seek(0, io.SEEK_SET)
            yield from iter(lambda: x.read(size), b'')
            x.seek(pointer)
        elif isinstance(x, (bytes, str, os.DirEntry, os.PathLike, pathlib.Path)):
            with open(x, 'rb') as f:
                yield from iter(lambda: f.read(size), b'')
        else:
            raise TypeError(f'Unable to handle object type: {type(x)}')

    if algorithm in hashlib.algorithms_available:
        h = hashlib.new(algorithm)
        for data in reader(x, size=h.block_size * 512):
            h.update(data)
        return h.hexdigest()
    elif algorithm in {'adler32', 'crc32'}:
        h = getattr(zlib, algorithm)
        value = 1 if algorithm == 'adler32' else 0
        for data in reader(x):
            value = h(data, value)
        return value & 0xffffffff
    else:
        raise ValueError(f'Unknown hash algorithm: {algorithm!r}.')


@deprecated(reason='Superseded by flightdatautilities.filesystem_tools:checksum().')
def sha_hash_file(path):
    return checksum(path, algorithm='sha256')


def is_empty(x):
    """
    Check whether a file is empty.

    This also supports checking for empty files compressed as *.7z, *.blosc, *.br, *.bz2, *.gz, *.lz, *.lz4, *.lzma,
    *.xz, *.zip, or *.zst.

    Note that we cannot reliably detect empty files for certain compression formats as the header or trailer may have
    variable metadata such as the original filename, access and modification times, ownership modes, checksums, etc.
    Notable compressors affected by this include gzip (*.gz) and lzop (*.lzo).
    """
    if isinstance(x, io.IOBase) and x.seekable():
        pointer = x.tell()
        x.seek(0, io.SEEK_END)
        size = x.tell()
        x.seek(pointer)
        name = getattr(x, 'name', None)
        suffix = os.path.splitext(name)[-1].lower() if name else None
    elif isinstance(x, (bytes, str, os.DirEntry, os.PathLike, pathlib.Path)):
        size = x.stat().st_size if hasattr(x, 'stat') else os.path.getsize(x)
        suffix = x.suffix.lower() if hasattr(x, 'suffix') else os.path.splitext(x)[-1].lower()
    else:
        raise TypeError(f'Unable to handle object type: {type(x)}')

    if size == 0:
        return True

    if isinstance(suffix, bytes):
        suffix = suffix.decode()

    if suffix and suffix not in {'.7z', '.blosc', '.br', '.bz2', '.gz', '.lz', '.lz4', '.lzma', '.xz', '.zip', '.zst'}:
        return None

    # Optimisation to skip if not a well-known size of an empty compressed file:
    # 1/2=.br, 13=.zst, 14=.bz2, 15=.lz4, 16=.blosc, 20=.gz, 22=.zip, 23=.lzma, 32=.7z/.xz, 36=.lz
    if size not in {1, 2, 13, 14, 15, 16, 20, 22, 23, 32, 36}:
        return None

    return checksum(x, algorithm='sha256') in {
        'c82685296a2d914c9acd6f6f6db1d1ad364f502b26af5e6ca8874c09880d5cf9',  # bzip2, 1 +/- --small
        'b9fb4c98c8b9fe5f20b5a5b3af8c8477e78395d7fd3e8ea504bb8ba4258f0b2d',  # bzip2, 2 w/o --small or 2-9 w/ --small
        '8e82a986c60ed805cf123a32032ffdd559b77a0c425b4a14335f7f18bca7675c',  # bzip2, 3 w/o --small
        '06b194dc7a53155fa05e948adf16f82dfeb0df4257fd43d5b10e19b059f8b215',  # bzip2, 4 w/o --small
        '4755d72e05f47024e53b2ee49ee6914c991941267c14c1ad532fc5b86eb86972',  # bzip2, 5 w/o --small
        'bfadeac6559924112cd591fab97af8a5df2c552b6cc282ade4578a9038cd0036',  # bzip2, 6 w/o --small
        'c43e7f7211d58037c7f11dafd279884c2a46d68edcdce655b864565208cd973b',  # bzip2, 7 w/o --small
        '5b5fffad5d41bdba930e8cf5492e1601ce0d6c79a50a093ea2f6a50b0fdc67d6',  # bzip2, 8 w/o --small
        'd3dda84eb03b9738d118eb2be78e246106900493c0ae07819ad60815134a8058',  # bzip2, 9 w/o --small
        'c2b340c40a9ea7e513d383f3913ac15269df08b3f73ce1ec10318e56f9f4ea3e',  # lzma, 1 +/- --extreme
        '4d10fc9b8f9ffd4918f73a4acbbab209b8a24fa380c997e13f511942fbe0639d',  # lzma, 2 +/- --extreme
        'af1cf3011696c1e403ac24bccbecca387edf435aac7f04c64abd9ddd1f4d05c2',  # lzma, 3/4 +/- --extreme
        'b8d8686989e9c36d659dddb4f0c7e800c778cf973adf59fc3e1022bfeaac4874',  # lzma, 5/6 +/- --extreme
        'fd869b8e8ceaedb75fa5cfa6bc589204d4e36a448a752545da9254c79fa1449a',  # lzma, 7 +/- --extreme
        'cbb5dd309d168c72128be5929f1e1952b358e5744c0480a06bf060080a4155c1',  # lzma, 8 +/- --extreme
        '6e84449b5ce658ae9d8e46ed3538a72d5af935672854ceb16d9a6aaad397e8d5',  # lzma, 9 +/- --extreme
        'f96deff1816083fdff8bc3e46c3fe6ca46a6bb49f4d5a00627616c13237a512c',  # zstd, 1-19, 20-22 w/ --ultra
        '0040f94d11d0039505328a90b2ff48968db873e9e7967307631bf40ef5679275',  # xz, 1-9 +/- --extreme
        'a01ab6c73734fbe3eac2971567666b6cd7d9586d5becc29c4a57b2c5a9225237',  # lz4, 1-12
        '8739c76e681f900923b900c9df0ef75cf421d39cabb54650c4b9ad19b6a76d85',  # zip, 0-9
        'c080ea5a055b0d5d8e98881b8c3cb4885beb8f274a0a8f9484a880d289c76a5f',  # lzip, 0-9
        '5bc3a0638e7c9286a5b28dd5f32cd096bf5dd9c56e2c45afbd5e27d5353ce4ba',  # 7zip
        'd1111b245f685176180e6f1631e6dc49badf6672368e9ce260c71355165effdf',  # gzip, 1 (flg=0, mtime=0, xfl=4, os=3)
        '59869db34853933b239f1e2219cf7d431da006aa919635478511fabbfc8849d2',  # gzip, 2-8 (flg=0, mtime=0, xfl=0, os=3)
        'f61f27bd17de546264aa58f40f3aafaac7021e0ef69c17f6b1b4cd7664a037ec',  # gzip, 9 (flg=0, mtime=0, xfl=2, os=3) (zopfli)
        '458c5a203299dd326aa747fee1bbc7709bfbd560507d1603459d9f7d9eb6be76',  # gzip, 1 (flg=0, mtime=0, xfl=4, os=255)
        'ac73670af3abed54ac6fb4695131f4099be9fbe39d6076c5d0264a6bbdae9d83',  # gzip, 2-8 (flg=0, mtime=0, xfl=0, os=255)
        '9ceffb7310338057cfe71a4ae1e2c98d2c485d81cdef906532a801f457a38d64',  # gzip, 9 (flg=0, mtime=0, xfl=1, os=255)
        '4e07408562bedb8b60ce05c1decfe3ad16b72230967de01f640b7e4729b49fce',  # brotli, 1
        'ef1534d0c6cfe8a961a19e64689dc8ba07d92b0498121852cc77c7fab995e9e2',  # brotli, 2-11
        '1e244a80ee64dcf11099fc361a1f1e9aa8534d0f38e875cd54111b9af55b484f',  # blosc, zlib, shuffle, 1-9
        'ea16b9795ab7026ce58f2f0929a1d663bb3ca0b98c61c664ec53541467b8b624',  # blosc, zstd, shuffle, 1-9
        '3292707af0db32a240f9d4df355437970bf768d139133dd492134e5122a82c5f',  # blosc, blosclz, shuffle, 1-9
        '57f409d1fce7d3b394844201a17b67f9ba5bf6d95ebe9fa050aa516f83d4b7e3',  # blosc, lz4/lz4hc, shuffle, 1-9
        '05c744c602e37f8a3cb16cbcb2d372a0a51c106eed58190f407d91c4a5d2fd1e',  # blosc, zlib, bit shuffle, 1-9
        '85ae460986ac3e37395213e6d974f22c3085ff10785afc0c0b7047bba1dd5edb',  # blosc, zstd, bit shuffle, 1-9
        'eda1f32c1c48de870820fb9c460deabbfcc59e6fac56de5e481e72101b1efe5b',  # blosc, blosclz, bit shuffle, 1-9
        'd38835d69d60c2008bcc9277d55bea1415bef0b6d6a062ee8350b7d4d5f05c03',  # blosc, lz4/lz4hc, bit shuffle, 1-9
        'f84c30654118cc0e92749d21e705fe0bd5ee6eb3e06a17342920bf5c6e332dc0',  # blosc, zlib, no shuffle, 1-9
        '5498eb93cede7a4673fe2b7b83b7c74689fe8b3e65fd661464cdaf14e9b6d677',  # blosc, zstd, no shuffle, 1-9
        '74ed569d179bfb98b9be10faf9accbde1df588649f72949b2f7eea18eebdfceb',  # blosc, blosclz, no shuffle, 1-9
        '6aa7bef39a2786d35a2370f1bcfcce794fb055e5ace6a4d890b5d200af5022a4',  # blosc, lz4/lz4hc, no shuffle, 1-9
    }


def pretty_size(size, *, prefix='jedec'):
    """
    Convert size in bytes into human readable format.

    See https://en.wikipedia.org/wiki/byte for information on prefixes.
    """
    if prefix == 'si':
        step = 1000.0
        units = ('', 'kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')
    elif prefix == 'iec':
        step = 1024.0
        units = ('', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB')
    elif prefix == 'jedec':
        step = 1024.0
        units = ('', 'KB', 'MB', 'GB')
    else:
        raise ValueError("Expected prefix to be one of 'si', 'iec', or 'jedec'.")

    for unit in units[:-1]:
        if abs(size) < step:
            return f'{size:3.1f}\xa0{unit}'
        size /= step
    return f'{size:3.1f}\xa0{units[-1]}'
