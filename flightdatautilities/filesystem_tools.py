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
import sys
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


def open_device(device):
    try:
        if platform.system() == 'Windows':
            fd = os.open(device, os.O_RDWR | os.O_BINARY)
        else:
            fd = os.open(device, os.O_RDWR)
    except OSError, err:
        print "Error: could not open the output file '%s'" % err
        raise

    # Return the file decriptor
    return fd


def close_device(fd):
    # Windows does not have os.fsync()
    if platform.system() == 'Linux':
        os.fsync(fd)
    os.close(fd)
    

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
            return round(size/float(lim/2**10),2).__str__()+suf


def read_in_chunks(file_object, chunk_size=1048576):
    """Lazy function (generator) to read a file piece by piece.
    Default chunk size: 1MB.
    """
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data


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


def make_image(path,size,dst_path,callback=None):
    """:param callback: callback(float)
       :type callack: function"""
    position = 0
    block_size = 4*1024*1024
    fd = open_device(path)
    compressor = bz2.BZ2Compressor()
    with open(dst_path,'wb') as dst:
        while True:
            left = size - position
            if left<block_size:
                block_size = 4096 if left>4096 else 512
            position += block_size
            try:
                data = os.read(fd,block_size)
                if not data: 
                    break
                
                compressed_data = compressor.compress(data)
                dst.write(compressed_data)
                if callback: callback((100.0*position)/size)
            except OSError:
                if left>size/20:
                    raise
                else:
                    break
        data = compressor.flush()
        dst.write(data)
        close_device(fd)


def bz2_write_in_chunks(file_path_in_or_file_obj, file_path_out):
    """ Writes a compressed file in chunks to the output destination in binary.
    Returns the number of bytes written (compressed).
    """
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


def tarbz2(tar_file_path, file_list, ext='.tar.bz2'):
    '''
    Tars all files in file_list and Bz2 compresses the output.
    Returns the filename.
    appends extension ext if it is not in the tar_file_path.
    '''
    if not tar_file_path.endswith(ext):
        tar_file_path += ext
    tar_archive = tarfile.open(tar_file_path, 'w:bz2')
    try:
        for item in file_list:
            tar_archive.add(item)
    finally:
        tar_archive.close()
    return tar_file_path


class FilesystemTools(object):
    def get_all_files(self, regex_list, source_list, copy_dir, delay=10,
                      retain_depth=1, delete=True):
        '''
        This is an example method for watching directories in a list.
        Please be careful using this in any production code, it's not
        built for purpose!
        '''
        self.files = {}

        try:
            #while True:
            self.files.clear()
            result = self.monitor(regex_list, source_list)
            cur_time = time.time()

            # Build dictionary of files and timestamps
            for item in result:
                for file in item:
                    self.files[file] = os.path.getmtime(file)

            # Check timestamp against current time
            for item in self.files:
                directory = self.get_directory(item, retain_depth)
                filename = self.get_filename(item)
                print "Filenames:", filename
                path = copy_dir + directory
                self.make_structure(path)
                
                if self.files[item] < (cur_time - delay):
                    dest_file = copy_dir + directory + filename
                    if not os.path.exists(dest_file):
                        shutil.copyfile(item, dest_file)
                        good_copy = self.check_file_integ(item, dest_file)
                        if good_copy:
                            print "Found new file:", filename, "-->", dest_file
                            # The files don't always want deleting
                            # (e.g. on a CD)
                            if delete == True:
                                self.delete_file(item)
                        else:
                            print ("Found new file:", filename, "-->",
                                   dest_file, "File copy failed!")
                    else:
                        print "File", item, "already exists! Skipping"

        except KeyboardInterrupt:
            print "Quitting"
            sys.exit(0)
    
    def delete_file(self, filepath):
        os.remove(filepath)

    def get_directory(self, path, depth):
        '''
        This method will get the directory structure <depth> directories
        deep from the top (the file).
        
        E.g. if the path is:
        
        /foo/bar/wibble/meep.txt
        
        and the user wants bar/wibble/meep.txt then the call is:
        get_directory(path, 2)
        '''
        dir_split = path.split('/')
        depth += 1
        # Don't find the last item
        up_to = len(dir_split) - 1
        directory_struct = dir_split[-depth:up_to]
        return '/'.join(directory_struct) + '/'

    def get_filename(self, path):
        path_split = path.split('/')[-1]
        return path_split
    
    def make_structure(self, path):
        '''
        Makes a file structure if it doesn't already exist
        Taken from http://code.activestate.com/recipes/82465/ since it's a
        nice way of recursivly making all parent directories
        '''
        if os.path.isdir(path):
            pass
        else:
            head, tail = os.path.split(path)
            if head and not os.path.isdir(head):
                self.make_structure(head)
            if tail:
                os.mkdir(path)

    def rmdir(self, path, ignore=[]):
        '''
        Remove directories. Allow user to enter directories to ignore into
        ignore list.
        '''
        # Replace non absolute directories with their absolute values
        for direc in ignore:
            if not os.path.isabs(direc):
                ignore.append(os.path.join(path, direc))
                ignore.remove(direc)
        
        tree = list(os.walk(path))
        tree.reverse()
        for branch in tree:
            # Allow removal of empty directories not in ignore list
            if os.path.abspath(branch[0]) not in ignore and not branch[-1]:
                try:
                    os.rmdir(branch[0])
                except OSError:
                    continue

    def remove_all_with_ignore(self, path, ignore=[]):
        '''
        This function will remove all files and directories in path,
        with the exception of any directories named in ignore.
        
        Directories in ignore may be relative (to the path) or absolute
        '''
        abs_path = os.path.abspath(path)
        self.remove_all_files(abs_path, ignore=ignore)
        self.rmdir(abs_path, ignore=ignore)

    def remove_structure(self, path, depth):
        '''
        Removes directory structure from base point path. Directory
        structure must be empty.
        '''
        if depth == 0:
            return True
        
        if os.path.isdir(path):
            head, tail = os.path.split(path)
            print "Head:", head
            print "Tail:", tail
            if head and os.path.isdir(head):
                os.rmdir(path)
                # New but untested
            elif head and os.path.isfile(head):
                os.remove(path)
            if tail:
                self.remove_structure(head, depth - 1)
        else:
            print "No such path:", path

    def remove_all(self, path):
        '''
        Remove all files and directories in a path (including the path base)
        '''
        print "Starting removal"
        self.remove_all_files(path)
        print "Finished removing files"
        shutil.rmtree(path)
        #os.removedirs(path)

    def remove_all_files(self, path, ignore=[], file_ignore=[]):
        '''
        Remove all files in a directory structure
        '''
        # Replace non absolute directories with their absolute values
        for direc in ignore:
            if not os.path.isabs(direc):
                ignore.append(os.path.join(path, direc))
                ignore.remove(direc)
            if os.path.isfile(direc):
                file_ignore.append(os.path.basename(direc))
                
        listing = os.listdir(path)
        for item in listing:
            item_name = os.path.join(path, item)
            if os.path.isfile(item_name) and not item in file_ignore:
                os.remove(item_name)
            elif os.path.isdir(item_name) and item_name not in ignore:
                self.remove_all_files(item_name, file_ignore=file_ignore)

    def get_dir(self, path):
        '''
        Returns the directory tree starting from point path
        '''
        dir_tree = os.walk(path)
        return dir_tree
    
#    def find_directories(self, tree):
#        """ Test method. Not for production code.
#        """
#        dirs = []
#        for item in tree:
#            for file in item[-1]:
#                m = re.search('(.)+\.tsc$', file)
#                if m:
#                    temp_name = m.group(0)
#                    text_file = (os.path.abspath(item[0]) + '/' + \
#                                 temp_name.split('.')[0] + '.txt')
#                    if os.path.exists(text_file):
#                        dirs.append(text_file)
#                    dir = os.path.abspath(item[0]) + '/' + m.group(0)
#                    dirs.append(dir)
#        return dirs

    def find_files(self, regex_list, tree):
        dirs = []
        for item in tree:
            # Look at the filename
            for file in item[-1]:
                # Check each file against all required regexps
                for regex in regex_list:
                    s_result = regex.search(file)
                    if s_result:
                        dir = os.path.abspath(item[0]) + '/' + s_result.group(0)
                        dirs.append(dir)
        return dirs

#    def get_data_files(self, dirs):
#        copy_dir = './test_copy/'
#        # Copy all files in dirs to a directory
#        for dir in dirs:
#            dir_split = dir.split('/')
#            directory = dir_split[-2]
#            filename = dir_split[-1]
#            path = copy_dir + directory
#            if not os.path.exists(path):
#                os.mkdir(path)
#            dest_file = copy_dir + directory + '/' + filename
#            shutil.copyfile(dir, dest_file)

    def monitor(self, regex_list, path):
        # Do monitoring stuff and then yield
        if type(path is not list):
            path = list(path)
        for source in path:
            tree = self.get_dir(source)
            result = self.find_files(regex_list, tree)
            yield result

    def check_file_integ(self, source_file, dest_file):
        """ Check integrety of copied file against original before deletion
        """
        fd_source = open(source_file, 'r')
        fd_dest = open(dest_file, 'r')
        
        # Get source file hash
        fd_source_result = fd_source.read() 
        hash_source = hashlib.sha1(fd_source_result).hexdigest()
        fd_source.close()
        
        # Get dest file hash
        fd_dest_result = fd_dest.read() 
        hash_dest = hashlib.sha1(fd_dest_result).hexdigest()
        fd_dest.close()
        
        if hash_source == hash_dest:
            return True
        else:
            return False


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
    

if __name__ == '__main__':
    unittest.main()
    