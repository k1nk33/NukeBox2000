#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_nukeboxQueue
----------------------------------

Tests for `nukebox2000` module.
"""


import sys
import unittest
from nukebox2000.MongoBox import NukeBoxDB


class TestNukeBoxDB(unittest.TestCase):

    '''
    '''

    def setUp(self):
        '''
        '''

        self.user_1 = {
            'name': 'Terry',
            'mac_id': '12341234'
        }

        self.user_2 = {
            'name': 'Eric',
            'mac_id': '43211234'
        }

        self.file_1 = {
            'filetype': '.mp3',
            'artist': 'Foals',
            'path': 'temp_dir',
            'track': 'Birch Tree',
            'size': '10000',
            'art': 'http://foals_art.jpeg'
        }

        self.file_2 = {
            'filetype': '.mp3',
            'artist': 'Foals',
            'path': 'temp_dir',
            'track': 'What Went Down',
            'size': '10000',
            'art': 'http://foals_art.jpeg'
        }

    def tearDown(self):
        '''
        '''
        pass

    def testCreateUser(self):
        '''
        '''
        nbdb = NukeBoxDB()

        user_1_result = nbdb.createUser(self.user_1)

        self.assertTrue(user_1_result)

    def testCreateUserFiles(self):
        '''
        '''

        nbdb = NukeBoxDB()

        user_2_result = nbdb.createUser(self.user_2)

        file_1_result = nbdb.createFile(self.file_1)

        file_2_result = nbdb.createFile(self.file_2)

        self.assertFalse(file_1_result == file_2_result)


if __name__ == '__main__':

    sys.exit(unittest.main())
