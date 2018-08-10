import bz2
import hashlib
import os
import shutil
import zipfile


##############################################################################
# Functions


# FIXME: Convert into a context manager to ensure data file is closed properly?
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


def pretty_size(size, suffix='B'):
    '''
    Converts size in bytes into human readable format.
    '''
    for unit in ('', 'K', 'M', 'G', 'T', 'P', 'E', 'Z'):
        if abs(size) < 1024.0:
            return '%3.1f%s%s' % (size, unit, suffix)
        size /= 1024.0
    return '%.1f%s%s' % (size, 'Y', suffix)


def sha_hash_file(filepath):
    '''
    Returns the SHA256 file hash from the file_path_in.
    '''
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(512 * h.block_size), b''):
            h.update(chunk)
    return h.hexdigest()
