#!/usr/bin/env python

from twisted.internet import reactor, task, threads
from fuzzywuzzy import fuzz
import musicbrainzngs
import sys
import taglib
from mutagen import File, flac, id3


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

        self.Logger.msg('Artist ID: {}\tAlbum ID: {}\tArt: {}'.format(
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

            # Added attempt to make a match if search is ambiguous
            # eg. (more than 1 artist called "X")
            try:

                if 'genre' in known_data:

                    if known_data['genre'].lower() in \
                       r['disambiguation'].lower():

                        self.Logger.msg('Returning Artist ID - {}'.format(
                            result['artist-list'][x]['id'])
                        )

                        return result['artist-list'][x]['id']

            except:

                continue

        self.Logger.msg('Returning Fallback Artist ID - {}'.format(
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

        for release_grp in result['artist']['release-group-list']:

            ratio = fuzz.ratio(
                known_data['album'].lower(),
                release_grp['title'].lower()
            )

            self.Logger.msg('Ratio-> {}'.format(ratio))

            if current_best_ratio < ratio:

                current_best_ratio = ratio
                current_best_match = release_grp['id']

                if current_best_ratio == 100:
                    break

                self.Logger.msg('Better Ratio Found')
                continue

            self.Logger.msg('Better Ratio in Storage')

        self.Logger.msg('Returning Current Best Match-> {}'.format(
            current_best_match)
        )

        return current_best_match

    # Retrieve Cover Art URL
    def getCoverArt(self, known_data):

        '''
        Retrieve Cover Art URL
        Retruns a list of URLs (limited to 1 at the mo)
        '''

        self.Logger.msg('Trying Cover Art for Album - {}'.format(
            known_data['album_id'])
        )

        # Blocking Call to MBrainz
        cover_result = musicbrainzngs.get_release_group_image_list(
            known_data['album_id']
        )

        covers = []

        for image in cover_result["images"]:

            if "Front" in image["types"] and image["approved"]:

                self.Logger.msg('Approved front image found :)')
                covers.append(image["thumbnails"]["large"])

                # Returns a single cover as of now but this can be edited to
                # grab more covers
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

            try:

                tags = File(_file, easy=True)

                return {
                    'title': tags['TITLE'][0].encode('utf8'),
                    'artist': tags['ARTIST'][0].encode('utf8'),
                    'album': tags['ALBUM'][0].encode('utf8'),
                    'genre': tags['GENRE'][0].encode('utf8'),
                    'art': hasEmbeddedArt(_file)
                }

            except Exception as err:

                Logger.error('Error on file {} - {}'.format(
                    str(_file),
                    err)
                )

                return False

        def hasEmbeddedArt(_file):
            '''
            '''

            if '.flac' in _file:

                media = flac.FLAC(_file)

                try:
                    if media.pictures[0].data:
                        return True

                except:
                    return False

            else:

                media = id3.ID3(_file)
                for i in media:
                    if i.startswith('APIC'):
                        return True

            return False

        paths = [
            '/home/darren/Development/Testing/ImageURLs/unknown.mp3',
            '/home/darren/Development/Testing/ImageURLs/unknown1.mp3',
            '/home/darren/Development/Testing/ImageURLs/unknown2.mp3',
            '/home/darren/Development/Testing/ImageURLs/unknown3.mp3',
            '/home/darren/Development/Testing/ImageURLs/unknown4.mp3',
            '/home/darren/Development/Testing/ImageURLs/unknown5.mp3',
            '/home/darren/Development/Testing/ImageURLs/unknown6.mp3',
            '/home/darren/Development/Testing/ImageURLs/unknown1.flac',
            '/home/darren/Development/Testing/ImageURLs/unknown2.flac',
            '/home/darren/Development/Testing/ImageURLs/unknown3.flac',
            '/home/darren/Development/Testing/ImageURLs/unknown4.flac',
            '/home/darren/Development/Testing/ImageURLs/unknown5.flac'
        ]

        for path in paths:

            data = getTags(path)

            if not data['art']:

                Logger.msg('Trying to retrieve data for: {}\t\t{}'.format(
                    data['artist'],
                    data['album'])
                )

                Logger.msg('Data-> {}'.format(data))

                d = threads.deferToThread(nbm.getMetaDetails, data)
                d.addCallback(printResult)

    reactor.callLater(0, main)
    reactor.run()
