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
        B{Test} Data

          - 2 User dict obj.
            - contains basic data required by the MongoDB collection "Users"
            - indexes exist on "mac_id" and "files" entries
            - user entries contain a "set" of File elements which reference
              the files (by obj id) that they have uploaded

          - 2 File dict obj.
            - contains basic data required for a File entry in the DB
            - indexes exist on "track id"
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
        B{Teardown} Test Data

          - Deletes instance Data created in Setup
        '''

        for i in self.file_1, self.file_2, self.user_1, self.user_2:

            del i

    def test_Ensure_Indexes(self):
        '''
        B{Test 01}

        Tests the DB method used to create the required indexes

          - ensureInexes returns a list of booleans
          - each item is True on success
        '''

        nbdb = NukeBoxDB(Debug=True)

        _a, _b, _c = nbdb.ensureIndexes()

        self.assertTrue(_a and _b and _c)

        nbdb = None

    def test_Create_User(self):
        '''
        B{Test 02}

        Tests User entry creation in the DB

          - createUser first checks if an matching entry already exists,
          updating the existing entry if it does
          - either way it returns the entries object id
        '''

        nbdb = NukeBoxDB()

        user_1_result = nbdb.createUser(self.user_1)

        self.assertTrue(user_1_result)

        nbdb = None

    def test_Create_User_Files(self):
        '''
        B{Test 03}

        Tests File entry creation in th DB

          - createFile first tries to retrieve an existing entry, updating it
          if a match is found
          - the method then uses the current "mac_id" instance variable to
          retrieve the current user and updates their set of files
        '''

        nbdb = NukeBoxDB()

        user_2_result = nbdb.createUser(self.user_2)
        file_1_result = nbdb.createFile(self.file_1)
        file_2_result = nbdb.createFile(self.file_2)

        self.assertEquals(
            file_1_result, nbdb.getTrack(self.file_1['track'])[1]
        )

        self.assertEquals(
            file_2_result, nbdb.getTrack(self.file_2['track'])[1]
        )

        del user_2_result
        nbdb = None

    def test_Get_Valid_Track(self):
        '''
        '''

        nbdb = NukeBoxDB()

        track_value, track_id = nbdb.getTrack(self.file_1['track'])

        self.assertTrue(track_value)
        self.assertIsNotNone(track_id)

        nbdb = None

    def test_Get_Invalid_Track(self):
        '''
        '''

        nbdb = NukeBoxDB()

        track_value, track_id = nbdb.getTrack(
            'Some Track That Should Not Exists in DB'
        )

        self.assertFalse(track_value)
        self.assertIsNone(track_id)

        nbdb = None


if __name__ == '__main__':

    sys.exit(unittest.main())
