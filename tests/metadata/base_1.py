#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- NukeBox File Metadata: metadata.tests.test_base_1 -*-

from nukebox2000.NukeBoxFileMeta import NukeBoxMeta
from twisted.internet import defer

"""
test_nukeboxMetadata
----------------------------------

Tests for `nukebox2000` module.
"""


class Metadata(object):

    def get_artist_id(self, data):
        
        d = defer.Deferred()
        nbmd = NukeBoxMeta()
        result = nbmd.getArtistID(data)
        return d
    
    def get_album_id(self, data):

        d = defer.Deferred()
        nbmd = NukeBoxMeta()
        result = nbmd.getAlbumID(data)
        return d
    
    def get_art_url(self, data):

        d = defer.Deferred()
        nbmd = NukeBoxMeta()
        result = nbmd.getCoverArt(data)[0]
        return d

    def get_all_data(self, data):
        
        d = defer.Deferred()
        nbmd = NukeBoxMeta()
        result = nbmd.getMetaDetails(data)
        return d
