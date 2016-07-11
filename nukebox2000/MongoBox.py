#!/usr/bin/env python2

from pymongo import MongoClient, ASCENDING, errors
from bson.objectid import ObjectId


class NukeBoxDB():

    '''
    Provides NukeBox MongoDB Access
    '''

    def __init__(self):
        '''
        Constructor method
        - Creates the instance variables surrounding
        the Database
        - Attempts to Create Indexes
        -- Prevents Duplicates!
        '''

        self.client = MongoClient()
        self.db = self.client['NukeBox']
        self.createIndex()

        # # Attempt to create indexes
        # # 1 Fail = All Fail
        # try:
        #     self.db.users.create_index(
        #         [('mac_id', ASCENDING)],
        #         unique=True,
        #         sparse=True
        #     )

        # except:

        #     print('DB Users Error')

        # try:

        #     self.db.users.create_index(
        #         [('files', ASCENDING)],
        #         unique=True,
        #         sparse=True
        #     )

        # except:

        #     print('DB Users Error')

        # try:

        #     self.db.files.create_index(
        #         [('track', ASCENDING)],
        #         unique=True,
        #         sparse=True
        #     )

        # except errors.DuplicateKeyError:

        #     pass

    def createIndex(self):
        '''
        '''

        # Attempt to create indexes
        # 1 Fail = All Fail
        try:
            self.db.users.create_index(
                [('mac_id', ASCENDING)],
                unique=True,
                sparse=True
            )

        except:

            print('DB Users Error')

        try:

            self.db.users.create_index(
                [('files', ASCENDING)],
                unique=True,
                sparse=True
            )

        except:

            print('DB Users Error')

        try:

            self.db.files.create_index(
                [('track', ASCENDING)],
                unique=True,
                sparse=True
            )

        except errors.DuplicateKeyError:

            pass

    def createUser(self, data):
        '''
        Method for creating new User Entries
        '''

        # Save a reference to Client Name
        self.name = data['name']

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

        # Insert a new entry (if not User Exists)
        except:

            _id = users.insert_one(
                data
            ).inserted_id

        return _id

    def createFile(self, file):
        '''
        Method to Create File Entries

          - Accepts Dict of File Params
        '''

        # Files Collection
        files = self.db.files

        # Check to see if the File Exists
        try:

            # print('Trying to Find an Existing Entry')

            _id = files.find_one(
                {
                    'track': file['track']
                }
            )

            _id = _id['_id']

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

        # Insert an Entry (if it doesn't exists)
        except:

            _id = files.insert_one(
                file
            ).inserted_id

        # Get Users Collection
        users = self.db.users

        # print('Trying to Update the User...')
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

        return _id

    def getTrack(self, track):
        '''
        '''

        files = self.db.files

        try:
            _id = files.find_one(
                {
                    'track': track
                }
            )

            _id = _id['_id']

            return True, _id

        except:

            return False, None

if __name__ == '__main__':

    nbdb = NukeBoxDB()

    u_result = nbdb.createUser(
        {
            'name': 'darren',
            'mac_id': '0987654321'
        }
    )

    print(u_result)

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

    print(f_result)

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

    print(f_result)

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

    print(f_result)

    b_value, _id = nbdb.getTrack('Mountain At My Gates')

    if b_value:
        print('ID is {}'.format(_id))

    else:
        print('Does Not Exist!')

    b_value, _id = nbdb.getTrack('Mountain At My Gates'.lower())

    if b_value:
        print('ID is {}'.format(_id))

    else:
        print('Does Not Exist!')
