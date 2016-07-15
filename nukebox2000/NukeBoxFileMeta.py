#!/usr/bin/env python

from twisted.internet import reactor, defer
from twisted.web.client import getPage

import acoustid
import math
import json
import musicbrainzngs
from mutagen.mp3 import MP3
import sys


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

    # Fingerprint File
    def fingerPrint(self, path):
        '''
        B{NukeBox Fingerprinting Method}

          - Requires the File Path (str) as an argument
          - Fingerprints the file
          - Sends file details to the Musicbrainz server (for identification)
          - Fires callback method on success
          - Fires errback method on failure
          - Returns a twisted Deferred obj.
        '''

        self.Logger.msg('Attempting to Fingerprint File :)')

        try:

            # for score, rec_id, title, artist in acoustid.match(
            #     self.api_key,
            #     path
            # ):

            #     if score > 0.9:
            #         print(score, rec_id, title, artist + '\n')

            # Retrieve file duration
            audio = MP3(path)
            duration = int(math.ceil(audio.info.length))

            # Create a Deferred obj. (twisted.defer.Deferred)
            d = defer.Deferred()

            # Fingerprint the File
            _, fingerprint = acoustid.fingerprint_file(
                path, maxlength=15
            )

            # Add "getPage" as 1st callback (when defer returns)
            # Note: getPage returns a deferred result also
            d.addCallback(getPage)

            # If the variable exists, send it to musicbrainz for analysis
            if fingerprint:

                self.Logger.msg('Fingerprint Done :)')

                url = self.base_url.format(
                    self.api_key,
                    duration,
                    fingerprint
                )

                self.Logger.msg('Firing Metadata callback chain :)')

                # Fire the defers callback chain
                d.callback(url)

        except Exception as err:

            self.Logger.err('Firing deferred errback chain :(')
            # Fire the defers errback chain
            d.errback(err)

        self.Logger.msg('Returning Metadata Deferred :)')
        # Must return a Deferred
        return d

    # Parse Response
    def parseDetails(self, data):
        '''
        B{Metadata Parsing method}

          - Parses the details (data) retrieved by the fingerPrint method
          - Requires json loaded, AcoustID Response obj. as an argument (data)
          - Returns a Deferred, d
          - Fires deferred callback chain on success
          - Fires deferred errback chain on failure
        '''

        self.Logger.msg('Parsing Details')

        d = defer.Deferred()

        try:

            artist_data = data['results'][0]['recordings'][0]['artists'][0]
            artist_id = artist_data['id']
            artist_name = artist_data['name']

            for res in data['results'][0]['recordings']:

                song_title = res['title']

                try:
                    for entry in res['releasegroups']:

                        if entry['type'] == 'Album':

                            if 'secondarytypes' not in entry.keys():

                                try:

                                    filt_on = entry['artists'][0]['name']

                                    if 'Various' not in filt_on:

                                        album_data = entry

                                        break

                                except:

                                    album_data = entry

                                    break

                    self.Logger.msg('Got Data :)')

                except:

                    continue

            album_name = album_data['title']
            album_id = album_data['id']

            self.data = {
                'track': song_title,
                'album': album_name,
                'album_id': album_id,
                'artist': artist_name,
                'artist_id': artist_id
            }

            self.Logger.msg('Transmitting details to Musicbrainz sever :)')

            cover_result = musicbrainzngs.get_release_group_image_list(
                album_id
            )

            if cover_result:

                self.Logger.msg('Cover Result Success :)')
                self.logger.msg('Firing Callback Chain :)')
                d.callback(cover_result)

        except Exception as err:

            self.Logger.err('Error {}'.format(err))
            self.Logger.msg('Firing Errback Chain :(')
            d.errback()

        return d

    # Metadata Cover Art
    def metaData(self, meta):
        '''
        B{Cover Art Metadata Method}

          - Is called with Cover Art (cover_result -> meta) via Parse Details
          - Forms part of the Deferred Callback chain
          - Returns data (dict)
        '''

        self.Logger.msg('Parsing Cover Metadata')

        covers = []

        for image in meta["images"]:

            if "Front" in image["types"] and image["approved"]:

                self.Logger.msg('Approved front image found :)')

                covers.append(image["thumbnails"]["large"])

        self.data['art'] = covers

        return self.data

    # MBrainz/Parser Fail
    def parseFail(self, failure):
        '''
        B{Parse Failure Method}

          - Forms part of the Deferred Errback chain
          - Called with the a twisted failure obj. (exception)
          - Raises exception
        '''

        print('Failure: {}'.format(failure))
        raise Exception('MBrainz/Parser Failure {}'.format(failure))

    # FingerPrint Failure
    def fpFail(self, failure):
        '''
        B{Fingerprint Failure Method}

          - Forms part of the Deferred Errback chain
          - Called with a twisted failure obj. (exception)
          - Raises 
        '''

        print('Something Happened with FingerPrinting!\n{}'.format(
            failure)
        )
        raise Exception('FPrint Error')


if __name__ == '__main__':

    from twisted.python import log as Logger

    nbm = NukeBoxMeta(Logger)

    # Print Tests
    def printResult(result):

        if result:
            Logger.msg('Result Success :)')

        else:
            Logger.err('Result Failed :(')

        reactor.stop()

    # Main Test Function
    def main():

        path = '/home/darren/Development/Testing/ImageURLs/unknown.mp3'
        # path = '/home/darren/Development/Testing/ImageURLs/unknown1.mp3'
        # path = '/home/darren/Development/Testing/ImageURLs/unknown2.mp3'
        # path = '/home/darren/Development/Testing/ImageURLs/unknown3.mp3'
        # path = '/home/darren/Development/Testing/ImageURLs/unknown4.mp3'


        d = nbm.fingerPrint(path)
        d.addCallback(json.loads)
        d.addErrback(nbm.fpFail)
        d.addCallback(nbm.parseDetails)
        d.addErrback(nbm.parseFail)
        d.addCallback(nbm.metaData)
        d.addBoth(printResult)

    reactor.callLater(0, main)
    reactor.run()
