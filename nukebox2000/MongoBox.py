#!/usr/bin/env python2

from pymongo import MongoClient, ASCENDING, errors
from bson.objectid import ObjectId
import sys


class NukeBoxDB():

    '''
    B{MongoDB Access} for NukeBox2000

      - Provides 4 Methods to NukeBox2000
        - "createIndex" -> Creates required entry indexes in the DB
        - "createUser"  -> Creates a new user entry in the DB
        - "createFile"  -> Creates new file entry in the DB
        - "getTrack"    -> Retrieve a track from the DB
    '''

    # Constructor
    def __init__(self, Logger=None):
        '''
        B{NukeBoxDB Constructor Method}

          - Creates the Instance variables for NukeBoxDB
          - Receives Optional Logger obj.
          - Attempts to Create Indexes
            - Prevents Duplicate Entries!
        '''

        # Logging
        if Logger is None:

            from twisted.python import log as Logger
            Logger.startLogging(sys.stdout)

        self.Logger = Logger
        self.Logger.msg('Database Module Up')

        self.client = MongoClient()
        self.db = self.client['NukeBox']
        self.createIndex()

    # Create Indexes
    def createIndex(self):
        '''
        B{Create Indexes}

          - Tries to create various MongoDB Indexes
          - Speeds up DB lookup
          - Indexes Created on:
            - Users Collection -> "mac_id"
            - Users Collection -> "files"
            - Files Collection -> "track"
        '''

        # Attempt to create indexes
        self.Logger.msg('Creating DB Indexes')

        # Create Index on Mac ID
        try:
            self.db.users.create_index(
                [('mac_id', ASCENDING)],
                unique=True,
                sparse=True
            )

            self.Logger.msg('Users Collection - Mac ID Index Created :)')

        except Exception as err:

            self.Logger.err(
                'Users Collection - Mac ID Index Error -> {} <-'.format(err)
            )

        # Create Index on Files
        try:

            self.db.users.create_index(
                [('files', ASCENDING)],
                unique=True,
                sparse=True
            )

            self.Logger.msg('Users Collection - Files Index Created :)')

        except Exception as err:

            self.Logger.err(
                'Users Collection - Files Index Error -> {} <-'.format(err)
            )

        # Create Index on Tracks
        try:

            self.db.files.create_index(
                [('track', ASCENDING)],
                unique=True,
                sparse=True
            )

            self.Logger.msg('Files Collection - Track Index Created :)')

        except errors.DuplicateKeyError:

            self.Logger.err(
                'Files Collection - Track Error -> {} <-'.format(err)
            )

    # Create User Entry
    def createUser(self, data):
        '''
        B{Create User Method}

          - First tries to retrieve the User (may already exist in the DB)
          - Creates a new User Entry (if not already present in the DB)
          - Method receives a (data) dict with User info
          - Dumps info directly to DB
        '''

        # Save a reference to Client Name
        self.name = data['name']

        self.Logger.msg('Attempting to add -> {} <- to DB'.format(
            self.name)
        )

        # Users Collection
        users = self.db.users

        # Check to see if the User Exists
        try:
            _id = users.find_one(
                {
                    'name': self.name
                }
            )

            _id = _id['_id']

            self.Logger.msg('User already exists in DB :)')

        # Insert a new entry (if not User Exists)
        except:

            _id = users.insert_one(
                data
            ).inserted_id

            self.Logger.msg('User -> {} <- Created :)'.format(self.name))

        return _id

    # Create File Entry
    def createFile(self, file):
        '''
        B{Create File Method}

          - First tries to retrieve the File (may already exist in the DB)
          - Creates a new File Entry (if not already present in the DB)
          - Updates the Related User File(s) Set to reference the new entry
          - Method receives a (file) dict with File info
          - Returns the File Obj. ID
        '''

        self.Logger.msg('Attempting to add File -> {} <- to the DB :)'.format(
            file['track'])
        )

        # Files Collection
        files = self.db.files

        # Check to see if the File Exists - Update if True
        try:

            _id = files.find_one(
                {
                    'track': file['track']
                }
            )

            _id = _id['_id']

            self.Logger.msg(
                'File entry for -> {} <- already exists in DB :)'.format(
                    file['track']
                )
            )

            result = files.update_one(
                {
                    '_id': _id
                },
                {
                    '$set':
                    {
                        'art': file['art']
                    }
                },
                upsert=True
            )

            self.Logger.msg('File Entry for -> {} <- Updated :)'.format(
                file['track'])
            )

        # Insert an Entry (if it doesn't exists)
        except:

            _id = files.insert_one(
                file
            ).inserted_id

            self.Logger.msg('File -> {} <- Created :)'.format(file['track']))

        self.Logger.msg('Updating Users File(s) Set :)')

        # Get Users Collection
        users = self.db.users

        # Update the set of Clients Files
        result = users.update_one(
            {
                'name': self.name
            },
            {
                '$addToSet':
                    {
                        'files': ObjectId(_id)
                    }
            },
            upsert=True
        )

        self.Logger.msg('Users File(s) Set Updated - {} :)'.format(
            result)
        )

        return _id

    # Retrieve Track Entry
    def getTrack(self, track):
        '''
        B{Get Track Method}

          - Method receives a (track) str
          - Attempts to find a Match
          - Returns a Success/Fail Boolean & track ID or None
        '''

        print(track)

        self.Logger.msg('Trying to find track -> {} <- :)'.format(
            track)
        )

        files = self.db.files

        # Try to find a Match
        try:
            _id = files.find_one(
                {
                    'track': track
                }
            )

            _id = _id['_id']

            self.Logger.msg('Track -> {} <- Found :)'.format(_id))

            return True, _id

        # Except if there is None
        except:

            self.Logger.msg('No Track Found :(')

            return False, None

if __name__ == '__main__':

    nbdb = NukeBoxDB()

    u_result = nbdb.createUser(
        {
            'name': 'darren',
            'mac_id': '0987654321'
        }
    )

    nbdb.Logger.msg(u_result)

    f_result = nbdb.createFile(
        {
            'filetype': '.mp3',
            'artist': 'Foals',
            'path': 'temp_dir',
            'track': 'Birch Tree',
            'size': '10000',
            'art': 'http://foals_art.jpeg'
        }
    )

    nbdb.Logger.msg(f_result)

    f_result = nbdb.createFile(
        {
            'filetype': '.mp3',
            'artist': 'Foals',
            'path': 'temp_dir',
            'track': 'What Went Down',
            'size': '10000',
            'art': 'http://foals_art.jpeg'
        }
    )

    nbdb.Logger.msg(f_result)

    f_result = nbdb.createFile(
        {
            'filetype': '.mp3',
            'artist': 'Foals',
            'path': 'temp_dir',
            'track': 'Mountain At My Gates',
            'size': '10000',
            'art': 'http://foals_art.jpeg'
        }
    )

    nbdb.Logger.msg(f_result)

    # Should Exist
    b_value, _id = nbdb.getTrack('Mountain At My Gates')

    if b_value:
        nbdb.Logger.msg('ID is {}'.format(_id))

    else:
        nbdb.Logger.msg('Does Not Exist!')

    # Should Not Exist
    b_value, _id = nbdb.getTrack('Mountain At My Gates'.lower())

    if b_value:
        nbdb.Logger.msg('ID is {}'.format(_id))

    else:
        nbdb.Logger.msg('Does Not Exist!')
