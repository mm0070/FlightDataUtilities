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

import bz2
import hashlib
import logging
import mimetypes
import os
import platform
import shutil
import subprocess
import unittest
import tarfile
import time
import zipfile


if platform.system() == "Linux":
    
    from grp import getgrnam    
    from pwd import getpwnam
    
    try:
        import dbus
    except ImportError:
        pass
    
    
    def chown(file_path, username, group_name):
        '''
        Change ownership of a file using username and group name rather than
        uid and gid. Raises key error if either username or group name do not exist
        on the system.
        '''
        uid = getpwnam(username)[2]
        gid = getgrnam(group_name)[2]
        os.chown(file_path, uid, gid)    
    
    
    def run_mkfs(device_name, fstype, options):
        formatted_options = ' '.join("-%s %s" % (option, value)
                                     for option, value in options.items())
        formatted_command = "mkfs.%s %s %s" % (fstype, formatted_options,
                                               device_name)
        # Sometimes this method freezes executing the next line
        logging.info(
            "Running command to make a filesystem on the device",
            formatted_command)
        # Sleep for a few seconds to let the new partition settle
        time.sleep(5)
        # We were using subprocess to run this command. However, we have
        # switched for now as subprocess.Popen was blocking and never creating
        # a proc object. This meant that a process was getting created but
        # never dying and never allowing us to get any information about it or
        # ability to kill it. The os.system command appears to get rid of this
        # issue. It would be preferable at some point to find out why subprocess
        # was failing in such a way and fix it since os.system is pretty much
        # depreciated.
        result = os.system(formatted_command)
        
        if result == -15:
            raise IOError('Formatting timed out.')
        elif result != 0:
            raise IOError('Formatting failed.')
    
    
    def system_partition(device):
        '''
        :returns: Filesystem location of new partition.
        '''
        result_sfdisk = run_sfdisk(device)
        if result_sfdisk != 0:
            raise IOError('Partitioning failed.')
        
        rescan_return = run_sfdisk_rescan(device)
        if rescan_return != 0:
            raise IOError('Partitioning failed.')
        
        return device + '1'
        
        # Q: Should we be running mkfs automatically?
        #new_partition = drive + '1'
        #result_mkfs = run_mkfs(new_partition, fstype, options)
        #if result_mkfs == 'timed_out':
            #return result_mkfs
        #elif result_mkfs != 0:
            #return 1
        #return 0
    
    
    def run_sfdisk(drive):
        '''
        sfdisk must be run as root.
        '''
        command_string = """sfdisk %s << EOF
;
EOF
""" % drive
        proc = subprocess.Popen(command_string, shell=True)
        return proc.wait()       
    
    
    def run_sfdisk_rescan(drive):
        '''
        sfdisk must be run as root.
        '''
        command_string = "sfdisk -R %s" % drive
        proc = subprocess.Popen(command_string, shell=True)
        return proc.wait()
        
    
    def linux_format_filesystem(device, filesystem_type):
        '''
        Use devicekit to delete the partitions, if any, and then recreate them.
        
        :raises IOError: If formatting fails.
        '''
        # Since DeviceKit formatting is simpler and more self-contained, use it
        # if the filesystem type/options are supported via a "device_kit_fstype"
        # key, corresponding to a DeviceKit fstype to be passed into the
        # PartitionCreate method. If this key does not exist, the only other
        # supported formatting key is "mkfs_fstype", which will be the OS
        # command called in the form "mkfs.vfat" for the key "vfat".
        # Options for this command can be specified via the "mkfs_options" key.
        filesystem = {
            "FAT12": {
                'device_kit': {
                    'partition_code': '01',
                    'max_size': 32 * 1024 * 1024,
                    },
                'mkfs': {
                    'fstype': 'vfat',
                    'options': {"F": 12},
                    },
                },
            "FAT16": {
                'device_kit': {
                    'partition_code': '06',
                    'max_size': 2 * 1024 * 1024 * 1024,
                    },
                'mkfs': {
                    'fstype': 'vfat',
                    'options': {"F":16},
                    },
                },
            "FAT32": {
                'device_kit': {
                    'partition_code': '0x0B',
                    'fstype': 'vfat',
                    'max_size': 8 * 1024 * 1024 * 1024, # without LBA   
                    },
                },
            "EXT3": {
                'device_kit': {
                    'partition_code': '0x0B',
                    'fstype': 'vfat',
                    'max_size': 8 * 1024 * 1024 * 1024, # without LBA                     
                },
            },
        }[filesystem_type]
        
        bus = dbus.SystemBus()
        dbus_name = device.dbus_name
        proxy = bus.get_object('org.freedesktop.DeviceKit.Disks',
                               '/org/freedesktop/DeviceKit/Disks')
        # Q: Is dbus.Inteface required?
        dbus.Interface(proxy, "org.freedesktop.DeviceKit.Disks")
        cur_dev = bus.get_object('org.freedesktop.DeviceKit.Disks',
                                 dbus_name)
        device_int = dbus.Interface(
            cur_dev,
            'org.freedesktop.DeviceKit.Disks.Device')
        
        # Unmount the device if it is mounted.
        for child_device in device.dbus_child_dev_name:
            child_device_name = bus.get_object(
                'org.freedesktop.DeviceKit.Disks', child_device) 
            child_dev_int = dbus.Interface(
                child_device_name, 'org.freedesktop.DeviceKit.Disks.Device') 
            try:
                child_dev_int.FilesystemUnmount(dbus.Array([], 's'))
            except dbus.DBusException as err:
                if err.get_dbus_message() == 'Device is not mounted':
                    logging.warning(
                        'Device %s was not mounted. Attempting to continue '
                        'with formatting', child_device)
                    pass
                else:
                    raise
        
        cur_dev_prop = dbus.Interface(cur_dev,
                                      'org.freedesktop.DBus.Properties')
        
        if cur_dev_prop.Get('org.freedesktop.DeviceKit.Disks.Device',
                            'device-is-mounted'):
            try:
                device_int.FilesystemUnmount(dbus.Array([], 's'))
            except dbus.DBusException as err:
                logging.error(
                    'Could not unmount device %s. Formatting will be attempted '
                    'regardless but expect an exception to be raised. Error '
                    'was: %s', device, err)
        
        # Recreate the partition table.
        device_int.PartitionTableCreate('none', [])
        try:
            device_int.PartitionTableCreate('mbr', [])
        except dbus.DBusException as err:
            logging.warning("Failed to create partition table on disk %s, "
                            "trying again using system tools", device.location)
            try:
                system_partition(device.location)
            except IOError:
                logging.error("Failed to partition device! Device is %s",
                              device.location)
                raise
        
        device_kit = filesystem['device_kit']
        dev_prop = dbus.Interface(cur_dev, 'org.freedesktop.DBus.Properties')
        size = dev_prop.Get('org.freedesktop.DeviceKit.Disks.Device',
                            'device-size')
        max_size = filesystem.get('max_size')
        
        if max_size and size >= max_size:
            size = max_size
        
        device_kit_fstype = device_kit.get('fstype', '')
        
        try:
            device_name = device_int.PartitionCreate(
                0, size, device_kit['partition_code'], '', [], [],
                device_kit_fstype, [])
            
        except dbus.DBusException, err:
            logging.warning("Failed to create partition on disk %s, trying "
                            "again using system tools", device.location)
            device_name = system_partition(device.location)
            ##if sys_part_result != 0:
                ### Something went wrong and we failed to partition drive
                ##logging.error("Failed to partition device! Device is %s",
                              ##device.location)
                ##if sys_part_result == 'timed_out':
                    ##return sys_part_result
                ##else:
                    ##return 1
            ##return 0
    
        for counter in range(3):
            try:
                device = bus.get_object(
                    'org.freedesktop.DeviceKit.Disks', device_name)
                dev_prop = dbus.Interface(
                    device, 'org.freedesktop.DBus.Properties')
                device_name = dev_prop.Get(
                    "org.freedesktop.DeviceKit.Disks.Device", "device-file")
                break
            except dbus.DBusException, err:
                # Try again if an error happens
                logging.warning("Formatting failed on try number: %s",
                                counter)
                time.sleep(0.5)
                continue
        else:
            logging.critical("Formatting Failed on device %s!", device)
            raise IOError('Formatting failed.')
        
        if not device_kit_fstype and 'mkfs' in filesystem:
            # The partition has been created, but not formatted by device kit.
            try:
                run_mkfs(device_name, filesystem['mkfs']['fstype'],
                         options=filesystem['mkfs']['options'])
            except IOError:
                logging.error(
                    "Failed to make filesystem on device! Device is %s",
                    device.location)
                raise

    format_filesystem = linux_format_filesystem


if platform.system() == 'Windows':
    
    def windows_format_filesystem(device, filesystem_type):
        '''
        Formts drive on Widnows.
        :param drive_letter: Drive letter with colon - C:.
        :type drive_letter: str
        :param format_type: String with format type: FAT16, FAT32, NTFS.
        :type format_type: str
        :return: None
        :rtype: None
        '''
        # Expected format is C: but \\.\C: 
        # also contains drive letter.
        assert filesystem_type in ['FAT16', 'FAT32', 'NTFS'], \
               "Wrong format - '%s'!" % filesystem_type
        drive_letter = device.location
        if len(drive_letter) > 2:
            drive_letter = drive_letter[-2:]
        if filesystem_type == 'FAT16':
            filesystem_type = 'FAT'
        command = 'format %s /Q /FS:%s' % (drive_letter,filesystem_type)    
        p = subprocess.Popen(command,
                             shell=True,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        p.communicate('\ny\n\n')
        return p.wait()
    
    format_filesystem = windows_format_filesystem
    

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
    
    
def break_windows_file_system_lock(logical_location,physical_drive):
    fd = open_device(logical_location)
    _block_size = 512
    _data = '\x00' * _block_size
    _size = 10*1024*1024
    try:
        while _size>0:
            os.write(fd,_data)
            _size -= _block_size
    except Exception, err:
        logging.exception("Initialising windows exception - expected on device with filesystem. - %s", err)
    finally:
        os.close(fd)
    time.sleep(5)
    
    fd = open_device(physical_drive)
    _size = 10*1024*1024
    try:
        while _size>0:
            os.write(fd,_data)
            _size -= _block_size
    except Exception:
        logging.exception("Initialising windows exception - expected on device with filesystem.")
    finally:
        os.close(fd)
    time.sleep(5)

def split_path(path):
    head,tail = os.path.split(path)
    path_list = []
    while tail:
        path_list =[tail] + path_list
        head,tail = os.path.split(head)
    return [head] + path_list

def join_path(path_list):
    path = ''
    for element in path_list:
        path = os.path.join(path,element)
    return path

def dir_path(path):
    """List all files recursivly in path
    :param path: Path to folder.
    :type: str
    :return: List of all files - full paths.
    :rtype: list(str)"""
    file_list = []
    for (path, dirs, files) in os.walk(os.path.abspath(path)):
        for _file in files:
            file_path = os.path.join(path,_file)
            file_list.append(file_path)
    return file_list

def is_in_subdir(path,_file):
    if len(path)>=len(_file):
        return False
    for i in range(0,len(path)):
        if path[i] != _file[i]:
            return False
    return True


def normalise_path(path):
    normalised_path = path.replace("\\","/")
    if not normalised_path.endswith("/"):
        normalised_path += '/'
    return split_path(normalised_path)


def is_paths_equal(path1,path2):
    """Mainly for windows where path can be represented
    in two forms C:/abc/def or C:\\abc\\def. In such case
    comparing string will give incorrect result."""
    system = platform.system()
    if system == 'Linux':
        return path1 == path2
    elif system == 'Windows':
        return normalise_path(path1) == normalise_path(path2)
    else:
        raise NotImplementedError
    
class IsPathEqualTest(unittest.TestCase):
    def test_simple(self):
        self.assertTrue(is_paths_equal("C:/abc/def","C:\\abc\\def"))
        self.assertTrue(is_paths_equal("C:/abc/def/","C:\\abc\\def"))
        self.assertTrue(is_paths_equal("C:/abc/def/","C:\\abc\\def\\"))
        self.assertTrue(is_paths_equal("C:/abc/def","C:\\abc\\def\\"))


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
    """ Returns the SHA256 file hash from the file_path_in.
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
    