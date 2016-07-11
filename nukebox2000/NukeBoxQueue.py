#!/usr/bin/env python

import collections


class NukeBoxQueue(collections.deque):

    '''
    Constructor for NukeBoxQueue
    - Subclass of collections.deque
    '''

    def __init__(self):

        super(NukeBoxQueue, self).__init__()
        self.info = {
            'current': '',
            'next': ''
        }

        self.pop = False

    def popleft(self):

        '''
        Call on the Deque Pop Method to Retrieve an Entry
        - Returns the Retrieved Object
        '''

        try:

            item = collections.deque.popleft(self)
            self.updateInfo('pop', item)
            return item

        except:

            print('Nothing to Queue')
            self.reset()

    def append(self, value, playing=False):

        '''
        Calls on the Deque Append Method to Add an Entry
        '''

        collections.deque.append(self, value)
        self.updateInfo('append', value, playing)

    def updateInfo(self, func, data, playing=False):
        '''
        '''

        print('Inside Function, Q Len is ', str(len(self)))

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

    def reset(self):

        self.info['current'] = self.info['next'] = {
            'track': '',
            'artist': '',
            'art': ''
        }

        self.pop = False

if __name__ == '__main__':

# Test Data

    print('#######\n Tests \n#######')

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

    q = NukeBoxQueue()

    print('\nAbout to Start Appending\n')

# Test Set 1

# 1 - Append:
    print('\nAppending Element 1')
    q.append(to_q_1, playing=False)
    print('Appended\n')

    if q.info['current']['track'] is not 'Song Title 1' and \
       q.info['next']['track'] is not '':

        print('Append 1 ### Error ###: {}{}'.format(
            q.info['current']['track'],
            q.info['next']['track'])
        )

    else:
        print('Append 1 ### Success ###')
        print('Current Len of Q ', str(len(q)))

# 2 - Append:
    print('\nAppending Element 2')
    q.append(to_q_2, playing=False)
    print('Appended\n')

    if q.info['current']['track'] is not 'Song Title 1' and \
       q.info['next']['track'] is not 'Song Title 2':

        print('Append 2 ### Error ###: {}{}'.format(
            q.info['current']['track'],
            q.info['next']['track'])
        )

    else:
        print('Append 2 ### Success ###')
        print('Current Len of Q ', str(len(q)))

# 3 - Append:
    print('\nAppending Element 3')
    q.append(to_q_3, playing=False)
    print('Appended\n')

    if q.info['current']['track'] is not 'Song Title 1' and \
       q.info['next']['track'] is not 'Song Title 2':

        print('Append 3 ### Error ###: {}{}'.format(
            q.info['current']['track'],
            q.info['next']['track'])
        )

    else:
        print('Append 3 ### Success ###')
        print('Current Len of Q ', str(len(q)))

# 4 - Append:
    print('\nAppending Element 4')
    q.append(to_q_4, playing=False)
    print('Appended\n')

    if q.info['current']['track'] is not 'Song Title 1' and \
       q.info['next']['track'] is not 'Song Title 2':

        print('Append 4 ### Error ###: {}{}'.format(
            q.info['current']['track'],
            q.info['next']['track'])
        )

    else:
        print('Append 4 ### Success ###')
        print('Current Len of Q ', str(len(q)))

    print('\nAbout to Start Popping')

# 5 - Pop:
    print('\nPopping Item 1')
    item_1 = q.popleft()
    print('Popped\n')

    if q.info['current']['track'] is not 'Song Title 1' and \
       q.info['next']['track'] is not 'Song Title 2':

        print('Pop 1 ### Error ###: {}{}'.format(
            q.info['current']['track'],
            q.info['next']['track'])
        )

    else:
        print('Pop 1 ### Success ###')
        print('Current Len of Q ', str(len(q)))

# 6 - Pop:
    print('\nPopping Item 2')
    item_2 = q.popleft()
    print('Popped\n')

    if q.info['current']['track'] is not 'Song Title 2' and \
       q.info['next']['track'] is not 'Song Title 3':

        print('Pop 2 ### Error ###: {}{}'.format(
            q.info['current']['track'],
            q.info['next']['track'])
        )

    else:
        print('Pop 2 ### Success ###')
        print('Current Len of Q ', str(len(q)))

# 7 - Pop:
    print('\nPopping Item 3')
    item_3 = q.popleft()
    print('Popped\n')

    if q.info['current']['track'] is not 'Song Title 3' and \
       q.info['next']['track'] is not 'Song Title 4':

        print('Pop 3 ### Error ###: {}{}'.format(
            q.info['current']['track'],
            q.info['next']['track'])
        )

    else:
        print('Pop 3 ### Success ###')
        print('Current Len of Q ', str(len(q)))

# 8 - Pop:
    print('\nPopping Item 4')
    item_4 = q.popleft()
    print('Popped\n')

    if q.info['current']['track'] is not 'Song Title 4' and \
       q.info['next']['track'] is not '':

        print('Pop 4 ### Error ###: {}{}'.format(
            q.info['current']['track'],
            q.info['next']['track'])
        )

    else:
        print('Pop 4 ### Success ###')
        print('Current Len of Q ', str(len(q)))

# 9 - Empty Pop:
    try:

        print('\nAttempting to Pop from Empty Q')
        result = q.popleft()
        print('Popped\n')

        if q.info['current']['track'] is not '' and \
           q.info['next']['track'] is not '':

            print('Empty Pop ### Error ###: {}{}'.format(
                q.info['current']['track'],
                q.info['next']['track'])
            )

        else:

            print('Empty Pop ### Success ###')
            print('Current Len of Q ', str(len(q)))

    except Exception as e:

        print('Error is {}\n\n'.format(e))

    print('\n\nStarting with Empty Q & Not Playing\n')

# Test Set 2

# 1 - Append:
    print('\nAppending Element 1')
    q.append(to_q_1, playing=False)
    print('Appended\n')

    if q.info['current']['track'] is not 'Song Title 1' and \
       q.info['next']['track'] is not '':

        print('Append 1 ### Error ###: {}{}'.format(
            q.info['current']['track'],
            q.info['next']['track'])
        )

    else:
        print('Append 1 ### Success ###')
        print('Current Len of Q ', str(len(q)))

# 2 - Append:
    print('\nAppending Element 2')
    q.append(to_q_2, playing=True)
    print('Appended\n')

    if q.info['current']['track'] is not 'Song Title 1' and \
       q.info['next']['track'] is not 'Song Title 2':

        print('Append 2 ### Error ###: {}{}'.format(
            q.info['current']['track'],
            q.info['next']['track'])
        )

    else:
        print('Append 2 ### Success ###')
        print('Current Len of Q ', str(len(q)))

# 3 - Pop:
    print('\nPopping Item 1')
    item_1 = q.popleft()
    print('Popped\n')

    if q.info['current']['track'] is not 'Song Title 1' and \
       q.info['next']['track'] is not 'Song Title 2':

        print('Pop 1 ### Error ###: {}{}'.format(
            q.info['current']['track'],
            q.info['next']['track'])
        )

    else:
        print('Pop 1 ### Success ###')
        print('Current Len of Q ', str(len(q)))

# 4 - Append:
    print('\nAppending Element 3')
    q.append(to_q_3, playing=True)
    print('Appended\n')

    if q.info['current']['track'] is not 'Song Title 1' and \
       q.info['next']['track'] is not 'Song Title 2':

        print('Append 3 ### Error ###: {}{}'.format(
            q.info['current']['track'],
            q.info['next']['track'])
        )

    else:
        print('Append 3 ### Success ###')
        print('Current Len of Q ', str(len(q)))

# 5 - Pop:
    print('\nPopping Item 2')
    item_1 = q.popleft()
    print('Popped\n')

    if q.info['current']['track'] is not 'Song Title 2' and \
       q.info['next']['track'] is not 'Song Title 3':

        print('Pop 2 ### Error ###: {}{}'.format(
            q.info['current']['track'],
            q.info['next']['track'])
        )

    else:
        print('Pop 2 ### Success ###')
        print('Current Len of Q ', str(len(q)))

# 6 - Pop:
    print('\nPopping Item 3')
    item_1 = q.popleft()
    print('Popped\n')

    if q.info['current']['track'] is not 'Song Title 3' and \
       q.info['next']['track'] is not '':

        print('Pop 3 ### Error ###: {}{}'.format(
            q.info['current']['track'],
            q.info['next']['track'])
        )

    else:
        print('Pop 3 ### Success ###')
        print('Current Len of Q ', str(len(q)))

# 7 - Append:
    print('\nAppending Element 4')
    q.append(to_q_4, playing=True)
    print('Appended\n')

    if q.info['current']['track'] is not 'Song Title 3' and \
       q.info['next']['track'] is not 'Song Title 4':

        print('Append 4 ### Error ###: {}{}'.format(
            q.info['current']['track'],
            q.info['next']['track'])
        )

    else:
        print('Append 4 ### Success ###')
        print('Current Len of Q ', str(len(q)))

# 8 - Pop:
    print('\nPopping Item 4')
    item_1 = q.popleft()
    print('Popped\n')

    if q.info['current']['track'] is not 'Song Title 4' and \
       q.info['next']['track'] is not '':

        print('Pop 4 ### Error ###: {}{}'.format(
            q.info['current']['track'],
            q.info['next']['track'])
        )

    else:
        print('Pop 4 ### Success ###')
        print('Current Len of Q ', str(len(q)))

# Tests Output

# #######
#  Tests 
# #######

# About to Start Appending


# Appending Element 1
# ('Inside Function, Q Len is ', '1')
# Not Playing
# Appended

# Append 1 ### Success ###
# ('Current Len of Q ', '1')

# Appending Element 2
# ('Inside Function, Q Len is ', '2')
# Len is 2
# Appended

# Append 2 ### Success ###
# ('Current Len of Q ', '2')

# Appending Element 3
# ('Inside Function, Q Len is ', '3')
# Queue Longer than 2
# Appended

# Append 3 ### Success ###
# ('Current Len of Q ', '3')

# Appending Element 4
# ('Inside Function, Q Len is ', '4')
# Queue Longer than 2
# Appended

# Append 4 ### Success ###
# ('Current Len of Q ', '4')

# About to Start Popping

# Popping Item 1
# ('Inside Function, Q Len is ', '3')
# Popped

# Pop 1 ### Success ###
# ('Current Len of Q ', '3')

# Popping Item 2
# ('Inside Function, Q Len is ', '2')
# Popped

# Pop 2 ### Success ###
# ('Current Len of Q ', '2')

# Popping Item 3
# ('Inside Function, Q Len is ', '1')
# Popped

# Pop 3 ### Success ###
# ('Current Len of Q ', '1')

# Popping Item 4
# ('Inside Function, Q Len is ', '0')
# Popped

# Pop 4 ### Success ###
# ('Current Len of Q ', '0')

# Attempting to Pop from Empty Q
# Nothing to Queue
# Popped

# Empty Pop ### Success ###
# ('Current Len of Q ', '0')


# Starting with Empty Q & Not Playing


# Appending Element 1
# ('Inside Function, Q Len is ', '1')
# Not Playing
# Appended

# Append 1 ### Success ###
# ('Current Len of Q ', '1')

# Appending Element 2
# ('Inside Function, Q Len is ', '2')
# Len is 2
# Appended

# Append 2 ### Success ###
# ('Current Len of Q ', '2')

# Popping Item 1
# ('Inside Function, Q Len is ', '1')
# Popped

# Pop 1 ### Success ###
# ('Current Len of Q ', '1')

# Appending Element 3
# ('Inside Function, Q Len is ', '2')
# Len is 2
# Appended

# Append 3 ### Success ###
# ('Current Len of Q ', '2')

# Popping Item 2
# ('Inside Function, Q Len is ', '1')
# Popped

# Pop 2 ### Success ###
# ('Current Len of Q ', '1')

# Popping Item 3
# ('Inside Function, Q Len is ', '0')
# Popped

# Pop 3 ### Success ###
# ('Current Len of Q ', '0')

# Appending Element 4
# ('Inside Function, Q Len is ', '1')
# Appended

# Append 4 ### Success ###
# ('Current Len of Q ', '1')

# Popping Item 4
# ('Inside Function, Q Len is ', '0')
# Popped

# Pop 4 ### Success ###
# ('Current Len of Q ', '0')