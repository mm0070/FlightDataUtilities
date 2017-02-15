""" This module contains methods (and an app) that gets a list of regexps
    a list of source directories to monitor and will look in each sub-directory
    of each listed source directory for any file matching any of the regexps.
    If one is found it is copied into another directory and added to a list of
    "known" files.
    
    A file must be left alone for (by default) 10 seconds before it will be
    copied.
    
    TODO: Looks like some files are being found twice dispite being added
    to the known files. Perhaps they should be deleted instead of added to a
    list?
"""


import hashlib
import mimetypes
import os
import platform
import shutil
import subprocess
import unittest
import zipfile

try:
    # bz2file provides support for multiple streams and a compatible interface.
    import bz2file as bz2
except ImportError:
    # Fallback to standard library.
    import bz2


def open_raw_data(source_file_path, binary=True):
    '''
    Open the input file which may be compressed.

    :param source_file_path: Path of raw data file which can either be zip
        (.SAC), bz2 or uncompressed.
    :type source_file_path: str
    :returns: Opened file object.
    '''
    extension = os.path.splitext(source_file_path)[1].lower()

    if extension in ('.sac', '.zip'):
        zip_file_obj = zipfile.ZipFile(source_file_path, 'r')
        # Opening a file within the zip returns a file-like object.
        filenames = zip_file_obj.namelist()
        if len(filenames) == 1:
            file_obj = zip_file_obj.open(filenames[0])
        else:
            raise IOError("Zip files must contain only a single data file.")
    elif extension == '.bz2':
        file_obj = bz2.BZ2File(source_file_path, 'r')
    else:
        file_obj = open(source_file_path, 'rb' if binary else 'r')

    return file_obj


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
        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)
    copy_path = path_minus_ext + postfix + ext
    if os.path.isfile(copy_path):
        os.remove(copy_path)
    shutil.copy(orig_path, copy_path)
    return copy_path


def split_path(path):
    '''
    Split a path string into a list of path elements.
    
    :type path: str
    :rtype: [str]
    '''
    head,tail = os.path.split(path)
    path_list = []
    while tail:
        path_list =[tail] + path_list
        head,tail = os.path.split(head)
    return [head] + path_list


def join_path(path_list):
    '''
    Join a list of path names together.
    
    :type path_list: [str]
    :rtype: str
    '''
    path = ''
    for element in path_list:
        path = os.path.join(path, element)
    return path


def dir_path(path):
    """
    List all files recursively in path.
    :param path: Path to folder.
    :type: str
    :return: List of all files - full paths.
    :rtype: list(str)
    """
    file_list = []
    for (path, dirs, files) in os.walk(os.path.abspath(path)):
        for _file in files:
            file_path = os.path.join(path, _file)
            file_list.append(file_path)
    return file_list


def subdir_paths(path):
    '''
    List all subdirectory paths.
    '''
    dir_paths = []
    for (path, dirs, files) in os.walk(os.path.abspath(path)):
        dir_paths.extend(os.path.join(path, d) for d in dirs)
    return dir_paths


def is_in_subdir(path, _file):
    '''
    :type path: str
    :rtype bool:
    '''
    if len(path) >= len(_file):
        return False
    
    for i in range(0, len(path)):
        if path[i] != _file[i]:
            return False
    
    return True


def normalise_path(path):
    '''
    Normalise Windows paths into Unix paths.
    
    :type path: str
    :rtype: [str]
    '''
    normalised_path = path.replace("\\","/")
    if not normalised_path.endswith("/"):
        normalised_path += '/'
    return split_path(normalised_path)


def is_paths_equal(path1,path2):
    """
    Mainly for windows where path can be represented
    in two forms C:/abc/def or C:\\abc\\def. In such case
    comparing string will give incorrect result.
    
    :type path1: str
    :type path2: str
    :rtype: bool
    """
    system = platform.system()
    if system == 'Linux':
        return path1 == path2
    elif system == 'Windows':
        return normalise_path(path1) == normalise_path(path2)
    else:
        raise NotImplementedError


def pretty_size(size):
    """
    Converts size in Bytes into Human readable format
    e.g. pretty_size(20*1024*1024*1024) = '20.0G'
    http://snippets.dzone.com/posts/show/5434
    """
    suffixes = [("B",2**10), ("KB",2**20), ("MB",2**30), ("GB",2**40), ("TB",2**50)]
    for suf, lim in suffixes:
        if size > lim:
            continue
        else:
            return round(size/float(lim/2**10),2).__str__() + suf


def sha_hash_file(file_path_in):
    """
    Returns the SHA256 file hash from the file_path_in.
    Works in 1MB chunks to iteratively create the hash.
    
    Hash is the hexvalues of the digest which is 64 chars long, e.g.
    'eb83d9e68a16c072307e8f5165ad56ac70fa6c4f8524b684077b46216194909c'
    
    In Linux, the command sha256sum will create the same hexdigest.
    """
    h = hashlib.sha256()
    with open(file_path_in, 'rb') as file_obj_to_hash:
        for piece in read_in_chunks(file_obj_to_hash):
            h.update(piece)
    # digest example:
    #'\xeb\x83\xd9\xe6\x8a\x16\xc0r0~\x8fQe\xadV\xacp\xfalO\x85$\xb6\x84\x07{F!a\x94\x90\x9c'
    # hexdigest example:
    #'eb83d9e68a16c072307e8f5165ad56ac70fa6c4f8524b684077b46216194909c'
    return h.hexdigest()


def bz2_decompress(bz2_file_path, output_file_path=None):
    """
    Decompress files
    """
    if not output_file_path:
        output_file_path = bz2_file_path.rstrip('.bz2')
    with open(bz2_file_path, 'rb') as temp_file_obj:
        with open(output_file_path, 'wb') as unbzipped_file_obj:
            bz2_decompressor = bz2.BZ2Decompressor()
            while True:
                read_bytes = temp_file_obj.read(16384)
                # if EOF
                if not read_bytes:
                    break
                unbzipped_file_obj.write(bz2_decompressor.decompress(read_bytes))
    return output_file_path


def zip_compress(file_path_in):
    '''
    Zip compress, stores file with only filename, not complete path within the
    zip
    '''
    archive = file_path_in + '.zip'
    a = zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED)
    a.write(file_path_in, os.path.split(file_path_in)[-1])
    a.close()
    return archive


def mime_type(file_path):
    '''
    Uses the 'file' command on Linux which examines files more
    rigorously than the mimetypes module in the standard library used by other
    platforms.
    
    TODO: Use a python project which wraps libmagic. May be cross-platform.
    '''
    if platform.system() == 'Linux':
        # -b (brief/do not include filename)
        process = subprocess.Popen(['file', '-b', '--mime-type', file_path],
                                   stdout=subprocess.PIPE)
        stdout, stderr = process.communicate()
        file_mime_type = stdout.strip()
        
    elif os.path.splitext(file_path)[1].upper() == '.SAC':
        file_mime_type = 'application/zip'
    else:
        file_mime_type, _ = mimetypes.guess_type(file_path)
    return file_mime_type


def find_patterns_in_file(file_path, search_strings, find_missing=False,
                          ignore_errors=True):
    """
    Searches each line for content of the search patterns. Does not work on
    patterns which span across multiple lines. Use find_missing to inverse the
    resulting list
    
    :param file_path: file to find pattern within
    :type file_path: str
    :param search_string: string to find within a line
    :type search_string: string
    :param find_missing: Returns the set of missing patterns
    :type find_missing: Boolean
    :param ignore_errors: suppress expected IO/OSErrors
    :type ignore_errors: Boolean
    """
    try:
        assert type(search_strings) in (list, tuple)
    except AssertionError:
        raise ValueError("Search strings argument must be a list")
        
    found_checklist = set()
    try:
        with open(file_path, 'r') as f:
            for line in f.readlines():
                [found_checklist.add(st) for st in search_strings if st in line]
    except (IOError, OSError):
        if not ignore_errors:
            raise
        else:
            pass
    if find_missing:
        return sorted(list(set(search_strings) - found_checklist))
    else:
        return sorted(list(found_checklist))


def is_file_of_type(file_path, file_obj_class):
    """
    With a file object class of some kind, find out if a file can be
    successfully read. Will raise any other exceptions, for instance
    if the file does not exist.
    """
    try:
        file_obj = file_obj_class(file_path, "rb")
        file_obj.read(1)
        file_obj.close()
        return True
    except IOError:
        return False


def is_file_bzipped(file_path):
    return is_file_of_type(file_path, bz2.BZ2File)


def bz2_write_in_chunks(file_path_in_or_file_obj, file_path_out):
    '''
    Writes a compressed file in chunks to the output destination in binary.
    Returns the number of bytes written (compressed).
    '''
    output_fhandle = bz2.BZ2File(file_path_out, mode='wb')
    try:
        file_path_in_or_file_obj + ''
        file_obj = open(file_path_in_or_file_obj, 'rb')
    except TypeError:
        # assumed file object, use existing open file
        file_obj = file_path_in_or_file_obj
        # ensure we're at the start of the device
        file_obj.seek(0)
    try:
        # write out all the data
        for piece in read_in_chunks(file_obj):
            output_fhandle.write(piece)
    finally:
        file_obj.close()
    output_fhandle.close()
    return os.path.getsize(file_path_out)


def read_in_chunks(file_object, chunk_size=1048576):
    '''
    Lazy function (generator) to read a file piece by piece.
    Default chunk size: 1MB.
    '''
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data
    

if __name__ == '__main__':
    unittest.main()
    