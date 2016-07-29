#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_nukeboxQueue
----------------------------------

Tests for `nukebox2000` module.
"""


import sys
import unittest
from nukebox2000.NukeBoxQueue import NukeBoxQueue


class TestNukeBoxQueue(unittest.TestCase):

    '''
    B{NukeBoxQueue} Test Case 001 (Linear) & 002 (Non-linear)

    Tests Adding & Removing Items from the Queue, both in a linear
    & non-linear way. The Q obj. has an associated "info" dict which
    keeps track of the Current/Next track. This info is relayed to the
    client so they can determine "What is Playing" & "What is Up Next".

    These tests simply tests that both the queue methods work as expected
    and that the info associated with it is the right info for the current
    queue.
    '''

    def setUp(self):
        '''
        B(Setup}

        Provides Dataset & Queue Instance
        '''

        # Test Data
        self.to_q_1 = {
            'track': 'Song Title 1',
            'artist': 'Artist 1',
            'art': 'http://some_art_1',
            'path': '/path/to/song_1',
            '_id': 001
        }

        self.to_q_2 = {
            'track': 'Song Title 2',
            'artist': 'Artist 2',
            'art': 'http://some_art_2',
            'path': '/path/to/song_2',
            '_id': 002
        }

        self.to_q_3 = {
            'track': 'Song Title 3',
            'artist': 'Artist 3',
            'art': 'http://some_art_3',
            'path': '/path/to/song_3',
            '_id': 003
        }

        self.to_q_4 = {
            'track': 'Song Title 4',
            'artist': 'Artist 4',
            'art': 'http://some_art_4',
            'path': '/path/to/song_4',
            '_id': 004
        }

        self.q = NukeBoxQueue()

    def tearDown(self):

        self.assertEquals(len(self.q), 0)

    def testLinear(self):
        '''
        B{Q Test 001} - Simulates Unrealistic Usage of the Q

        Tests the values of Current & Next Tracks in NukeBoxQueue.info

          - Items Appended in Linear Fachion
          - Items Removed in Linear Fashion

        Flow

          1. Append Item 1
          2. Append Item 2
          3. Append Item 3
          4. Append Item 4
          5. Pop Item 1
          6. Pop Item 2
          7. Pop Item 3
          8. Pop Item 4
        '''

        self.q.append(self.to_q_1, playing=False)

        self.assertTrue(
            self.q.info['current']['track'] == 'Song Title 1' and
            self.q.info['next']['track'] == ''
        )

        for to_q in [self.to_q_2, self.to_q_3, self.to_q_4]:

            self.q.append(to_q, playing=True)

            self.assertTrue(
                self.q.info['current']['track'] == 'Song Title 1' and
                self.q.info['next']['track'] == 'Song Title 2'
            )

        for item in [self.to_q_1, self.to_q_2, self.to_q_3, self.to_q_4]:

            self.assertTrue(item == self.q.popleft())

        self.assertIsNone(self.q.popleft())

    def testNonLinear(self):
        '''
        B{Q Test 002} - Simulates Realistic Usage of the Q

        Tests the values of Current & Next Tracks in NukeBoxQueue.info

          - Items Appended in Non-Linear Fachion
          - Items Removed in Non-Linear Fashion

        Flow

          1. Item 1 Added
          2. Item 2 Added
          3. Item 1 Popped
          4. Item 3 Added
          5. Item 2 Popped
          6. Item 3 Popped
          7. Item 4 Added
          8. Item 4 Popped
        '''

        # --- 1 --- #
        self.q.append(self.to_q_1, playing=False)

        self.assertTrue(
            self.q.info['current']['track'] == 'Song Title 1' and
            self.q.info['next']['track'] == ''
        )

        # --- 2 --- #
        self.q.append(self.to_q_2, playing=True)

        self.assertTrue(
            self.q.info['current']['track'] == 'Song Title 1' and
            self.q.info['next']['track'] == 'Song Title 2'
        )

        # --- 3 --- #
        self.assertTrue(self.to_q_1 == self.q.popleft())

        self.assertTrue(
            self.q.info['current']['track'] == 'Song Title 1' and
            self.q.info['next']['track'] == 'Song Title 2'
        )

        # --- 4 --- #
        self.q.append(self.to_q_3, playing=True)

        self.assertTrue(
            self.q.info['current']['track'] == 'Song Title 1' and
            self.q.info['next']['track'] == 'Song Title 2'
        )

        # --- 5 --- #
        self.assertTrue(self.to_q_2 == self.q.popleft())

        self.assertTrue(
            self.q.info['current']['track'] == 'Song Title 2' and
            self.q.info['next']['track'] == 'Song Title 3'
        )

        # --- 6 --- #
        self.assertTrue(self.to_q_3 == self.q.popleft())

        self.assertTrue(
            self.q.info['current']['track'] == 'Song Title 3' and
            self.q.info['next']['track'] == ''
        )

        # --- 7 --- #
        self.q.append(self.to_q_4, playing=True)

        self.assertTrue(
            self.q.info['current']['track'] == 'Song Title 3' and
            self.q.info['next']['track'] == 'Song Title 4'
        )

        # --- 8 --- #
        self.assertTrue(self.to_q_4 == self.q.popleft())

        self.assertTrue(
            self.q.info['current']['track'] == 'Song Title 4' and
            self.q.info['next']['track'] == ''
        )

if __name__ == '__main__':
    sys.exit(unittest.main())
