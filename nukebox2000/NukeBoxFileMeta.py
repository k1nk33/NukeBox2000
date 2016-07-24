#!/usr/bin/env python

from twisted.internet import reactor, defer, task, threads
# from twisted.web.client import getPage

# import acoustid
# import math
# import json
import musicbrainzngs
# from mutagen.mp3 import MP3
import taglib
import sys

from fuzzywuzzy import fuzz


class NukeBoxMeta:

    '''
    '''

    # Constructor
    def __init__(self, Logger=None):
        '''
        B{Metadata Constructor Method}
        '''

        # Logging
        if Logger is None:

            from twisted.python import log as Logger
            Logger.startLogging(sys.stdout)

        self.Logger = Logger
        self.Logger.msg('Metadata Module Up')

        self.api_key = '5htdnbd6y5'

        self.base_url = 'http://api.acoustid.org/v2/lookup?client={}'\
            '&meta=recordings+releasegroups+compress&duration={}'\
            '&fingerprint={}'

        musicbrainzngs.set_useragent(
            "python-nukebox2000-testing",
            "0.1"
        )

    # Control Method
    def getMetaDetails(self, known_data):

        '''
        Base Metadata Method

        Calls the other methods to retrieve relevant song data
        Receives and Returns a dict obj.
          - Input dict must have an 'artist' & 'album' entry
          - Output dict is the same obj. with additional info
        '''
        known_data['artist_id'] = self.getArtistID(known_data)
        known_data['album_id'] = self.getAlbumID(known_data)
        known_data['art'] = self.getCoverArt(known_data)

        self.Logger.msg('Artist ID: {}\t\tAlbum ID: {}\t\tArt: {}'.format(
            known_data['artist_id'],
            known_data['album_id'],
            known_data['art'])
        )

        return known_data

    # Retrieve MBrainz Artist ID
    def getArtistID(self, known_data):

        '''
        Match the given 'artist' entry to a MBrainz Artist ID
        Returns Artist MB-ID
        '''

        # Blocking Call to MBrainz Server
        result = musicbrainzngs.search_artists(known_data['artist'])

        for x, r in enumerate(result['artist-list']):

            # Added attempt to make a match if search is anbiguous
            # eg. (more than 1 artist called "X")
            # if 'disambiguation' in r:
            try:

                self.Logger.msg('Genre-> {} : Disambig-> {}'.format(
                    known_data['genre'].lower(),
                    r['disambiguation'].lower())
                )

                if 'genre' in known_data:

                    if known_data['genre'].lower() in \
                       r['disambiguation'].lower():

                        self.Logger.msg('Returning Artist ID - {}'.format(
                            result['artist-list'][x]['id'])
                        )

                        return result['artist-list'][x]['id']

            except:

                continue

        self.Logger.msg('Returning Artist ID - {}'.format(
            result['artist-list'][0]['id'])
        )
        # Return a default result if no other match is made
        return result['artist-list'][0]['id']

    # Retrieve MBrainz Album ID
    def getAlbumID(self, known_data):

        '''
        Match the given 'artist_id' entry to their 'releases'
        Returns Release-Group MB-ID
        '''

        # Blocking call to MBrainz
        result = musicbrainzngs.get_artist_by_id(
            known_data['artist_id'],
            includes=[
                'release-groups',
            ],
            release_type=[
                'album'
            ]
        )

        current_best_ratio = 0
        # current_best_match = ''

        for release_grp in result['artist']['release-group-list']:

            ratio = fuzz.ratio(
                known_data['album'].lower(),
                release_grp['title'].lower()
            )

            self.Logger.msg('Ratio-> {}'.format(ratio))

            # if ratio > 50:

            #     self.Logger.msg('Match Found')

            #     current_best_match = release_grp['id']
            #     break

            # else:
            if current_best_ratio < ratio:

                current_best_ratio = ratio
                current_best_match = release_grp['id']

                self.Logger.msg('Better Ratio Found')
                continue

            self.Logger.msg('Better Ratio in Storage')

            self.Logger.msg('Album ID-> {}'.format(current_best_match))

        self.Logger.msg('Returning Current Best match')
        return current_best_match

    # Retrieve Cover Art URL
    def getCoverArt(self, known_data):

        '''
        Retrieve Cover Art URL
        Retruns a list of URLs (limited to 1 at the mo)
        '''

        self.Logger.msg('Trying Cover Art for Album - {}'.format(
            known_data['album_id']))
        cover_result = musicbrainzngs.get_release_group_image_list(
            known_data['album_id']
        )

        covers = []

        for image in cover_result["images"]:

            if "Front" in image["types"] and image["approved"]:

                self.Logger.msg('Approved front image found :)')
                covers.append(image["thumbnails"]["large"])

                return covers


if __name__ == '__main__':

    from twisted.python import log as Logger

    nbm = NukeBoxMeta(Logger)
    nbm.Logger.startLogging(sys.stdout)

    # Print Tests
    def printResult(result):

        if result:
            nbm.Logger.msg('Result Success :)\t\t{}'.format(str(result)))

        else:
            nbm.Logger.err('Result Failed :(')

        reactor.stop()

    # Main Test Function
    def main():

        def getTags(_file):

            song = taglib.File(_file)
            tags = song.tags

            try:
                Logger.msg('Tags: {}'.format(tags))
                return {
                    'title': tags['TITLE'][0].encode('utf8'),
                    'artist': tags['ARTIST'][0].encode('utf8'),
                    'album': tags['ALBUM'][0].encode('utf8'),
                    'genre': tags['GENRE'][0].encode('utf8'),
                    'art': False
                }
            except Exception as err:

                Logger.error('Error on file {} - {}'.format(
                    str(_file),
                    err)
                )

            return False

        def loopingPrint(text):
            print(text)

        t = task.LoopingCall(loopingPrint, 'Nothing Yet')
        t.start(0.5)

        # path = '/home/darren/Development/Testing/ImageURLs/unknown.mp3'
        # path = '/home/darren/Development/Testing/ImageURLs/unknown1.mp3'
        # path = '/home/darren/Development/Testing/ImageURLs/unknown2.mp3'
        # path = '/home/darren/Development/Testing/ImageURLs/unknown3.mp3'
        # path = '/home/darren/Development/Testing/ImageURLs/unknown4.mp3'

        # path = '/home/darren/Development/Testing/ImageURLs/unknown1.flac'
        # path = '/home/darren/Development/Testing/ImageURLs/unknown2.flac'
        # path = '/home/darren/Development/Testing/ImageURLs/unknown3.flac'
        # path = '/home/darren/Development/Testing/ImageURLs/unknown4.flac'
        path = '/home/darren/Development/Testing/ImageURLs/unknown5.flac'

        # data = {'artist': 'radiohead', 'album': 'the bends'}

        data = getTags(path)

        Logger.msg('Trying to retrieve data for: {}\t\t{}'.format(
            data['artist'],
            data['album'])
        )

        d = threads.deferToThread(nbm.getMetaDetails, data)
        d.addCallback(printResult)

    reactor.callLater(0, main)
    reactor.run()
