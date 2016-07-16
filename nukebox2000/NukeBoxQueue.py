#!/usr/bin/env python

import collections
import sys


class NukeBoxQueue(collections.deque):

    '''
    B{NukeBoxQueue} Class

      - Subclass of collections deque
      - Provides 4 Methods
      - "popLeft" -> Retrieve the Left Most Entry
        - "append" -> Add an Entry (right most index)
        - "updateInfo" -> Updates the Q's Current/Next Track Info (dict)
        - "reset" -> Resets the Q's Current/Next Track Info (dict)
    '''

    def __init__(self, Logger=None):

        '''
        B{NukeBoxQ Constructor Method}

          - Receive an Optional Logger obj. (twisted.python.log)
          - Calls super on Inherited Class (collections.deque)
          - Sets Instance variables
        '''

        # Logging
        if Logger is None:

            from twisted.python import log as Logger
            Logger.startLogging(sys.stdout)

        self.Logger = Logger
        self.Logger.msg('NukeBox Q Module Up :)')

        super(NukeBoxQueue, self).__init__()
        self.info = {
            'current': '',
            'next': ''
        }

        self.pop = False

    def popleft(self):

        '''
        B{Pop Left Method}

          - Overloads the Deque Pop Method to Retrieve an (left most) Entry
          - Returns the obj. (if it exists)
          - Calls Reset Method if Q is empty
        '''

        self.Logger.msg('Attempting to Pop Entry :)')

        # Try to Retrieve an Entry
        try:

            item = collections.deque.popleft(self)
            self.updateInfo('pop', item)

            self.Logger.msg('Popped -> {} <- Success :)'.format(item['track']))

            return item

        # Except if there is an error, reset the Q info
        except Exception as err:

            self.Logger.err('Queue Error -> {} <- :('.format(err))
            self.reset()
            # raise Exception(err)

    def append(self, value, playing=False):

        '''
        B{Append Q Method}

          - Overloads the Deque Append Method (collections.deque)
          - Adds an Entry
          - Calls "upDateInfo" method
          - Receives 2 arguments
            - "value"   -> The entry (dict) to append
            - "playing" -> The player (state) variable

        '''

        collections.deque.append(self, value)
        self.updateInfo('append', value, playing)

        self.Logger.msg('Appended Entry -> {} <- :)'.format(value['track']))

    def updateInfo(self, func, data, playing=False):
        '''
        B{Update Q Info Method}

          - Checks the Function being performed
          - Checks the length of the Q (currently)
          - Updates Q with relevant info
          - Receives 3 arguments
            - "func" -> The Q function being performed (append or popleft)
            - "data" -> The Entry data (dict)
            - "playing" -> The player (state) variable

        '''

        self.Logger.msg('Updating Q Info :)')

        if func is 'append':

            if len(self) > 2:

                print('Queue Longer than 2')
                return

            if len(self) is 2:  # current already set

                print('Len is 2')

                if self.pop:

                    return

                _data = self[1]

                self.info['next'] = {
                    'track': _data['track'],
                    'artist': _data['artist'],
                    'art': _data['art']
                }

            if len(self) is 1:

                if playing:  # current already set

                    _data = data

                    self.info['next'] = {
                        'track': _data['track'],
                        'artist': _data['artist'],
                        'art': _data['art']
                    }

                if not playing:

                    print('Not Playing')

                    _data = data

                    self.info['current'] = {
                        'track': _data['track'],
                        'artist': _data['artist'],
                        'art': _data['art']
                    }

                    self.info['next'] = {
                        'track': '',
                        'artist': '',
                        'art': ''
                    }

        elif func is 'pop':

            self.pop = True

            _data = data

            self.info['current'] = {
                'track': _data['track'],
                'artist': _data['artist'],
                'art': _data['art']
            }

            if len(self) is 0:

                self.info['next'] = {
                    'track': '',
                    'artist': '',
                    'art': ''
                }

            elif len(self) >= 1:

                _data = self[0]

                self.info['next'] = {
                    'track': _data['track'],
                    'artist': _data['artist'],
                    'art': _data['art']
                }

        self.Logger.msg('Q Info Update Complete :)')

    def reset(self):

        '''
        B{Q Info Reset Method}

          - Resets the Q Info to default values
        '''

        self.info['current'] = self.info['next'] = {
            'track': '',
            'artist': '',
            'art': ''
        }

        self.pop = False

if __name__ == '__main__':

    # Test Data

    q = NukeBoxQueue()

    Logger = q.Logger  # twisted.python.log obj.

    to_q_1 = {
        'track': 'Song Title 1',
        'artist': 'Artist 1',
        'art': 'http://some_art_1',
        'path': '/path/to/song_1',
        '_id': 001
    }

    to_q_2 = {
        'track': 'Song Title 2',
        'artist': 'Artist 2',
        'art': 'http://some_art_2',
        'path': '/path/to/song_2',
        '_id': 002
    }

    to_q_3 = {
        'track': 'Song Title 3',
        'artist': 'Artist 3',
        'art': 'http://some_art_3',
        'path': '/path/to/song_3',
        '_id': 003
    }

    to_q_4 = {
        'track': 'Song Title 4',
        'artist': 'Artist 4',
        'art': 'http://some_art_4',
        'path': '/path/to/song_4',
        '_id': 004
    }

#
# Test Set 1
#
    Logger.msg('Test 1 - Start Appending an Empty Q :)')

# 1 - Append:
    Logger.msg('Appending Element 1')

    q.append(to_q_1, playing=False)

    # Because we start with an Empty Q, Current should be Element 1,
    # Next should be empty!

    # If the Current Track does not match Element 1 & the Next Track
    # is not Empty, Something went wrong!

    if q.info['current']['track'] is not 'Song Title 1' and \
       q.info['next']['track'] is not '':

        Logger.err('Append 1 Error: {}{} :('.format(
            q.info['current']['track'],
            q.info['next']['track'])
        )

    # Otherwise all is as it should be
    else:
        Logger.msg('Append Element 1 - Success :)')

# 2 - Append:
    Logger.msg('Appending Element 2')

    q.append(to_q_2, playing=True)

    # Now Current should be Element 1 & Next should be Element 2

    if q.info['current']['track'] is not 'Song Title 1' and \
       q.info['next']['track'] is not 'Song Title 2':

        Logger.err('Append Element 2 Error - {}{} :('.format(
            q.info['current']['track'],
            q.info['next']['track'])
        )

    else:
        Logger.msg('Append Element 2 - Success :)')

# 3 - Append:
    Logger.msg('Appending Element 3')

    q.append(to_q_3, playing=True)

    # Current & Next should remain the same

    if q.info['current']['track'] is not 'Song Title 1' and \
       q.info['next']['track'] is not 'Song Title 2':

        Logger.err('Append Element 3 Error - {}{} :('.format(
            q.info['current']['track'],
            q.info['next']['track'])
        )

    else:
        Logger.msg('Append Element 3 - Success :)')

# 4 - Append:
    Logger.msg('Appending Element 4')
    q.append(to_q_4, playing=True)

    # Again, there should be no change (as we haven't popped yet!)

    if q.info['current']['track'] is not 'Song Title 1' and \
       q.info['next']['track'] is not 'Song Title 2':

        Logger.err('Append Element 4 Error - {}{}'.format(
            q.info['current']['track'],
            q.info['next']['track'])
        )

    else:
        Logger.msg('Append Element 4 - Success :)')

    Logger.msg('About to Start Popping :)')

# 5 - Pop:
    Logger.msg('Popping Item 1')

    item_1 = q.popleft()

    # Current & Next values should not change at this time

    if q.info['current']['track'] is not 'Song Title 1' and \
       q.info['next']['track'] is not 'Song Title 2':

        Logger.err('Pop Item 1 Error - {}{} :('.format(
            q.info['current']['track'],
            q.info['next']['track'])
        )

    else:
        Logger.msg('Pop Item 1 - Success :)')

# 6 - Pop:
    Logger.msg('Popping Item 2')

    item_2 = q.popleft()

    # Current & Next should shift to the Right by 1 Index
    if q.info['current']['track'] is not 'Song Title 2' and \
       q.info['next']['track'] is not 'Song Title 3':

        Logger.err('Pop Item 2 Error - {}{} :('.format(
            q.info['current']['track'],
            q.info['next']['track'])
        )

    else:
        Logger.msg('Pop Item 2 - Success :)')

# 7 - Pop:
    Logger.msg('Popping Item 3')

    item_3 = q.popleft()

    # Again, Current & Next should shift right

    if q.info['current']['track'] is not 'Song Title 3' and \
       q.info['next']['track'] is not 'Song Title 4':

        Logger.err('Pop Item 3 Error - {}{} :('.format(
            q.info['current']['track'],
            q.info['next']['track'])
        )

    else:
        Logger.msg('Pop Item 3 - Success :)')

# 8 - Pop:
    Logger.msg('Popping Item 4')

    item_4 = q.popleft()

    # This time Current should be the last entry, Next should be empty

    if q.info['current']['track'] is not 'Song Title 4' and \
       q.info['next']['track'] is not '':

        Logger.err('Pop Item 4 Error - {}{} :('.format(
            q.info['current']['track'],
            q.info['next']['track'])
        )

    else:
        Logger.msg('Pop Item 4 - Success :)')

# 9 - Empty Pop:

    try:

        Logger.msg('Attempting to Pop from Empty Q')
        result = q.popleft()

        if q.info['current']['track'] is not '' and \
           q.info['next']['track'] is not '':

            Logger.err('Empty Pop Error - {}{} :('.format(
                q.info['current']['track'],
                q.info['next']['track'])
            )

        else:

            Logger.msg('Empty Pop - Success :)')

    except Exception as e:

        Logger.msg('Empty Pop Error is {}'.format(e))
        raise Exception('Empty Q')

#
# Test Set 2
#
    Logger.msg('Test 2 - Starting with Empty Q & Not Playing :)')

# 1 - Append:
    Logger.msg('Appending Element 1')

    q.append(to_q_1, playing=False)

    # Because we start with an Empty Q, Current should be Element 1,
    # Next should be empty!

    # If the Current Track does not match Element 1 & the Next Track
    # is not Empty, Something went wrong!

    if q.info['current']['track'] is not 'Song Title 1' and \
       q.info['next']['track'] is not '':

        Logger.err('Append 1 Error: {}{} :('.format(
            q.info['current']['track'],
            q.info['next']['track'])
        )

    # Otherwise all is as it should be
    else:
        Logger.msg('Append Element 1 - Success :)')

# 2 - Append:
    Logger.msg('Appending Element 2')

    q.append(to_q_2, playing=True)

    # Now Current should be Element 1 & Next should be Element 2

    if q.info['current']['track'] is not 'Song Title 1' and \
       q.info['next']['track'] is not 'Song Title 2':

        Logger.err('Append Element 2 Error - {}{} :('.format(
            q.info['current']['track'],
            q.info['next']['track'])
        )

    else:
        Logger.msg('Append Element 2 - Success :)')

# 3 - Pop:
    Logger.msg('Popping Item 1')

    item_1 = q.popleft()

    # Currently, the Player is playing and an Item has been popped!
    # Current & Next should remain the same!

    if q.info['current']['track'] is not 'Song Title 1' and \
       q.info['next']['track'] is not 'Song Title 2':

        Logger.err('Pop Item 1 Error - {}{} :('.format(
            q.info['current']['track'],
            q.info['next']['track'])
        )

    else:
        Logger.msg('Pop Item 1 - Success :)')

# 4 - Append:
    Logger.msg('Appending Element 3')

    q.append(to_q_3, playing=True)

    # Player is playing, items have been popped & a new Entry appended
    # Current & Next should remain the same

    if q.info['current']['track'] is not 'Song Title 1' and \
       q.info['next']['track'] is not 'Song Title 2':

        Logger.err('Append Item 3 Error - {}{} :('.format(
            q.info['current']['track'],
            q.info['next']['track'])
        )

    else:
        Logger.msg('Append Item 3 - Success :)')

# 5 - Pop:
    Logger.msg('Popping Item 2')

    item_2 = q.popleft()

    # A New pop occurs
    # Current & Next should shift right 1 Index

    if q.info['current']['track'] is not 'Song Title 2' and \
       q.info['next']['track'] is not 'Song Title 3':

        Logger.err('Pop Item 2 Error - {}{} :('.format(
            q.info['current']['track'],
            q.info['next']['track'])
        )

    else:
        Logger.msg('Pop Item 2 - Success :)')

# 6 - Pop:
    Logger.msg('Popping Item 3')

    item_1 = q.popleft()

    # A New pop occurs
    # Current & Next should shift right 1 Index
    # As there is only 1 Item in the Q, Next should be empty!

    if q.info['current']['track'] is not 'Song Title 3' and \
       q.info['next']['track'] is not '':

        Logger.err('Pop Item 3 Error - {}{} :('.format(
            q.info['current']['track'],
            q.info['next']['track'])
        )

    else:
        Logger.msg('Pop Item 3 - Success :)')

# 7 - Append:
    Logger.msg('Appending Element 4')

    q.append(to_q_4, playing=True)

    # Current should remain the same
    # As the Q was empty before appending, Next should now be
    # this new element

    if q.info['current']['track'] is not 'Song Title 3' and \
       q.info['next']['track'] is not 'Song Title 4':

        Logger.err('Append Element 4 Error - {}{} :('.format(
            q.info['current']['track'],
            q.info['next']['track'])
        )

    else:
        Logger.msg('Append Element 4 - Success :)')

# 8 - Pop:
    Logger.msg('Popping Item 4')

    item_1 = q.popleft()

    # With a new Pop, Current & Next should shift right 1 Index
    # Next should now by empty (no more items in Q)

    if q.info['current']['track'] is not 'Song Title 4' and \
       q.info['next']['track'] is not '':

        Logger.err('Pop Item 4 Error - {}{} :('.format(
            q.info['current']['track'],
            q.info['next']['track'])
        )

    else:
        Logger.msg('Pop Item 4 - Success :)')

# Tests Output

# Log opened.
# NukeBox Q Module Up :)
# Test 1 - Start Appending an Empty Q :)
# Appending Element 1
# Updating Q Info :)
# Not Playing
# Q Info Update Complete :)
# Appended Entry -> Song Title 1 <- :)
# Append Element 1 - Success :)
# Appending Element 2
# Updating Q Info :)
# Len is 2
# Q Info Update Complete :)
# Appended Entry -> Song Title 2 <- :)
# Append Element 2 - Success :)
# Appending Element 3
# Updating Q Info :)
# Queue Longer than 2
# Appended Entry -> Song Title 3 <- :)
# Append Element 3 - Success :)
# Appending Element 4
# Updating Q Info :)
# Queue Longer than 2
# Appended Entry -> Song Title 4 <- :)
# Append Element 4 - Success :)
# About to Start Popping :)
# Popping Item 1
# Attempting to Pop Entry :)
# Updating Q Info :)
# Q Info Update Complete :)
# Popped -> Song Title 1 <- Success :)
# Pop Item 1 - Success :)
# Popping Item 2
# Attempting to Pop Entry :)
# Updating Q Info :)
# Q Info Update Complete :)
# Popped -> Song Title 2 <- Success :)
# Pop Item 2 - Success :)
# Popping Item 3
# Attempting to Pop Entry :)
# Updating Q Info :)
# Q Info Update Complete :)
# Popped -> Song Title 3 <- Success :)
# Pop Item 3 - Success :)
# Popping Item 4
# Attempting to Pop Entry :)
# Updating Q Info :)
# Q Info Update Complete :)
# Popped -> Song Title 4 <- Success :)
# Pop Item 4 - Success :)
# Attempting to Pop from Empty Q
# Attempting to Pop Entry :)
# 'Queue Error -> pop from an empty deque <- :('
# Empty Pop - Success :)
# Test 2 - Starting with Empty Q & Not Playing :)
# Appending Element 1
# Updating Q Info :)
# Not Playing
# Q Info Update Complete :)
# Appended Entry -> Song Title 1 <- :)
# Append Element 1 - Success :)
# Appending Element 2
# Updating Q Info :)
# Len is 2
# Q Info Update Complete :)
# Appended Entry -> Song Title 2 <- :)
# Append Element 2 - Success :)
# Popping Item 1
# Attempting to Pop Entry :)
# Updating Q Info :)
# Q Info Update Complete :)
# Popped -> Song Title 1 <- Success :)
# Pop Item 1 - Success :)
# Appending Element 3
# Updating Q Info :)
# Len is 2
# Appended Entry -> Song Title 3 <- :)
# Append Item 3 - Success :)
# Popping Item 2
# Attempting to Pop Entry :)
# Updating Q Info :)
# Q Info Update Complete :)
# Popped -> Song Title 2 <- Success :)
# Pop Item 2 - Success :)
# Popping Item 3
# Attempting to Pop Entry :)
# Updating Q Info :)
# Q Info Update Complete :)
# Popped -> Song Title 3 <- Success :)
# Pop Item 3 - Success :)
# Appending Element 4
# Updating Q Info :)
# Q Info Update Complete :)
# Appended Entry -> Song Title 4 <- :)
# Append Element 4 - Success :)
# Popping Item 4
# Attempting to Pop Entry :)
# Updating Q Info :)
# Q Info Update Complete :)
# Popped -> Song Title 4 <- Success :)
# Pop Item 4 - Success :)
