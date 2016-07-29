#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_nukeboxMetadata
----------------------------------

Tests for `nukebox2000` module.
"""

from twisted.trial import unittest
from base_1 import Metadata


class TestNukeBoxMeta(unittest.TestCase):

    '''
    B{NukeBoxMeta} Test Case 001 & 002
    '''

    def test_get_artist_id(self):
        
        test_data = {
            'artist': 'radiohead',
            'title': 'fake plastic trees',
            'album': 'the bends',
            'genre': 'indie',
            'art': 'False'
        }
        
        md = Metadata()
        test_response = md.get_artist_id(test_data)
        test_response.addCallback(
            self.assertEqual, 'a74b1b7f-71a5-4011-9441-d0b5e4122711'
        )
    
    def test_get_album_id(self):
        
        test_data = {
            'artist': 'radiohead',
            'title': 'fake plastic trees',
            'album': 'the bends',
            'genre': 'indie',
            'art': 'False',
            'artist_id': 'a74b1b7f-71a5-4011-9441-d0b5e4122711'
        }
        
        md = Metadata()
        test_response = md.get_album_id(test_data)
        test_response.addCallback(
            self.assertEqual, 'b8048f24-c026-3398-b23a-b5e50716cbc7'
        )
        
    def test_get_art_url(self):
        
        test_data = {
            'artist': 'radiohead',
            'title': 'fake plastic trees',
            'album': 'the bends',
            'genre': 'indie',
            'art': 'False',
            'artist_id': 'a74b1b7f-71a5-4011-9441-d0b5e4122711',
            'album_id': 'b8048f24-c026-3398-b23a-b5e50716cbc7'
        }
        
        md = Metadata()
        test_response = md.get_art_url(test_data)
        test_response.addCallback(
            self.assertEqual,
            'http://coverartarchive.org/release/'
            'b3b28d75-e474-43b8-a9ec-4c6856fc10b2/2563874552-500.jpg'
        )

    def test_all_methods(self):

        test_data = {
            'artist': 'foals',
            'title': 'late night',
            'album': 'holy fire',
            'genre': 'indie',
            'art': 'False'
        }
        
        md = Metadata()
        test_response = md.get_all_data(test_data)
        test_response.addCallback(self.all_methods_callback)
        
    def all_methods_callback(self, result):
        
        self.assertTrue(
            result['artist_id'] == '6a65d878-fcd0-42cf-aff9-ca1d636a8bcc'
        )
        
        self.assertTrue(
            result['album_id'] == 'fdcf14da-08bf-407a-a0af-6f9582b82131'
        )
        
        self.assertTrue(
            result['art'][0] == \
            'http://coverartarchive.org/release/'
            '927525ca-be51-4ea3-acf4-13c034ed2188/12328334334-500.jpg'
        )

