import unittest


import bz2
import mock
import os
import platform
import shutil

import flightdatautilities.filesystem_tools as fst



class TestPrettySize(unittest.TestCase):
    def test_pretty_size(self):
        # convert sizes to be user friendly
        self.assertEqual(fst.pretty_size(213458923), '203.57MB')
        self.assertEqual(fst.pretty_size(1234), '1.21KB')


class TestFilesystemTools(unittest.TestCase):
    def _create_tmp_test_data_dir(self):
        if not os.path.exists(self._tmp_test_data_dir):
            os.mkdir(self._tmp_test_data_dir)

    def setUp(self):
        # Make path for all tests
        test_data_path = os.path.join(os.path.dirname(__file__), 'test_data')
        self.path = os.path.abspath(os.path.join(test_data_path, 'test_removal'))
        # Create directories
        if not os.path.exists(os.path.join(self.path, 'remove_me1', 'remove_me2')):
            os.makedirs(os.path.join(self.path, 'remove_me1', 'remove_me2'))
        if not os.path.exists(os.path.join(self.path, 'ignore_me')):
            os.makedirs(os.path.join(self.path, 'ignore_me'))
        # Ignore list
        self.ignore_list = ['ignore_me']

        self.non_bz2_filename = os.path.join(os.path.dirname(__file__), "test_data",
                                                             "many_files")
        self.bz2_filename = self.non_bz2_filename + ".tar.bz2"

        self._tmp_test_data_dir = os.path.join(test_data_path,
                                               "tmp_feel_free_to_remove")
        self._create_tmp_test_data_dir()
        self.flist = [os.path.join(self._tmp_test_data_dir, x+'.txt') \
                                 for x in 'abcd']
        for f in self.flist:
            with open(f, 'w') as fh:
                fh.write(f*10)

    def tearDown(self):
        if os.path.exists(self._tmp_test_data_dir):
            shutil.rmtree(self._tmp_test_data_dir)

        # perform cleanup
        for f in self.flist + [self.bz2_filename]:
            if os.path.isfile(f):
                os.remove(f)

    # TODO: Move out tests.
    #def test_tarbz2(self):
        #fn = fst.tarbz2(self.non_bz2_filename, self.flist)
        #many_files_tar_bz2 = self.bz2_filename
        #self.assertEqual(fn, self.bz2_filename)
        #self.assertTrue(os.path.isfile(self.bz2_filename))
        #bz2_file_obj = open(self.bz2_filename, "rb")
        #bz2_file_header = bz2_file_obj.read(2)
        #bz2_file_obj.close()
        #self.assertEqual(bz2_file_header, "BZ")

    #def test_tarbz2_extension(self):
        #fn = fst.tarbz2(self.non_bz2_filename, self.flist)
        #self.assertEqual(fn, self.non_bz2_filename + ".tar.bz2")
    
    def test_is_path_equal(self):
        if platform.system() == 'Windows':
            self.assertTrue(fst.is_paths_equal("C:/abc/def", "C:\\abc\\def"))
            self.assertTrue(fst.is_paths_equal("C:/abc/def/", "C:\\abc\\def"))
            self.assertTrue(fst.is_paths_equal("C:/abc/def/", "C:\\abc\\def\\"))
            self.assertTrue(fst.is_paths_equal("C:/abc/def", "C:\\abc\\def\\"))

    def test_find_patterns_in_file(self):
        file_with_pattern = os.path.join(os.path.dirname(__file__), 'test_data', 'pattern_exists.txt')
        with open(file_with_pattern, 'w') as fh:
            fh.writelines(['some_thing',
                           'another_thing',
                           'yet_another_item'])

        self.assertEqual(fst.find_patterns_in_file(file_with_pattern, ['thing']),
                         ['thing'])
        self.assertEqual(fst.find_patterns_in_file(file_with_pattern, ['another_']),
                         ['another_'])
        self.assertEqual(fst.find_patterns_in_file('no_file_here', ('thing',)), [])
        self.assertEqual(fst.find_patterns_in_file(file_with_pattern, ['anything']), [])
        self.assertRaises(IOError, fst.find_patterns_in_file, 'no_file_here', ['pattern'], ignore_errors=False)
        # if file doesn't exist, and find missing, return original list
        self.assertEqual(fst.find_patterns_in_file('no_file_here', ['pattern', 'another_pattern'], find_missing=True, ignore_errors=True), 
                         ['another_pattern', 'pattern'])
        self.assertEqual(fst.find_patterns_in_file(file_with_pattern, ['some', 'other', 'fish']),
                         sorted(['some', 'other']))
        self.assertEqual(fst.find_patterns_in_file(file_with_pattern, ['some', 'other', 'fish'], find_missing=True),
                         ['fish'])


    def test_is_file_bzipped(self):
        # Create test file.
        self._create_tmp_test_data_dir()
        test_file_path = os.path.join(self._tmp_test_data_dir,
                                      "test_is_file_bzipped.false")
        test_file_obj = open(test_file_path, "wb")
        test_file_obj.write("uncompressed")
        test_file_obj.close()
        self.assertFalse(fst.is_file_bzipped(test_file_path))
        test_file_path = os.path.join(self._tmp_test_data_dir,
                                      "test_is_file_bzipped.true")
        test_file_obj = bz2.BZ2File(test_file_path, "wb")
        test_file_obj.write("uncompressed")
        test_file_obj.close()
        self.assertTrue(fst.is_file_bzipped(test_file_path))


if __name__ == '__main__':
    TestFilesystemTools('test_remove_all_with_ignore').run()
    print "Finished all tests"
