#!/usr/bin/env python

from twisted.internet import reactor, defer
from twisted.web.client import getPage

import acoustid
import math
import json
import musicbrainzngs
from mutagen.mp3 import MP3


class NukeBoxMeta:

    '''
    '''

    def __init__(self):
        '''
        '''

        self.api_key = '5htdnbd6y5'

        self.base_url = 'http://api.acoustid.org/v2/lookup?client={}'\
            '&meta=recordings+releasegroups+compress&duration={}'\
            '&fingerprint={}'

        musicbrainzngs.set_useragent(
            "python-nukebox2000-testing",
            "0.1"
        )

    def fingerPrint(self, path):
        '''
        Deferred NukeBox AcoustID Fingerprinting Method

        - Requires the path to the file in question as an argument
        - Forms part of a In-line Deferred Chain
        '''

        try:

            # for score, rec_id, title, artist in acoustid.match(
            #     self.api_key,
            #     path
            # ):

            #     if score > 0.9:
            #         print(score, rec_id, title, artist + '\n')

            audio = MP3(path)
            duration = int(math.ceil(audio.info.length))

            d = defer.Deferred()
            _, fingerprint = acoustid.fingerprint_file(
                path, maxlength=15
            )

            d.addCallback(getPage)

            if fingerprint:

                url = self.base_url.format(
                    self.api_key,
                    duration,
                    fingerprint
                )

                d.callback(url)

        except Exception as err:

            d.errback(err)

        return d

    def parseDetails(self, data):
        '''
        Parses the details retrieved by the fingerPrint method

        - Requires an AcoustID Response Object as an argument
        - Returns a Deferred, d
        - Fires d.callback on success
        - Fires d.errback on exception
        '''
        print('Parsing Details')

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
                                        print('Got Data ', str(album_data))
                                        break

                                except:

                                    album_data = entry
                                    print('Got Data ', str(album_data))
                                    break

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

            cover_result = musicbrainzngs.get_release_group_image_list(
                album_id
            )

            if cover_result:

                d.callback(cover_result)

        except Exception as err:

            print('Error ', err)
            d.errback()

        return d

    def metaData(self, meta):

        covers = []

        for image in meta["images"]:

            if "Front" in image["types"] and image["approved"]:

                print('\n{} is an approved front image!\n\n'.format(
                    image["thumbnails"]["large"])
                )

                covers.append(image["thumbnails"]["large"])

        self.data['art'] = covers

        return self.data

    # MBrainz/Parser Fail
    def parseFail(self, failure):
        '''
        '''

        print('Failure: {}'.format(failure))
        raise Exception('MBrainz/Parser Failure {}'.format(failure))

    # FingerPrint Failure
    def fpFail(self, failure):
        '''
        '''

        print('Something Happened with FingerPrinting!\n{}'.format(
            failure)
        )
        raise Exception('FPrint Error')


if __name__ == '__main__':

    # Print Tests
    def printResult(result):

        if result:
            print(result)

        else:
            print('Failed')

        reactor.stop()

    # Main Test Function
    def main():

        path = '/home/darren/Development/Testing/ImageURLs/unknown.mp3'
        # path = '/home/darren/Development/Testing/ImageURLs/unknown1.mp3'
        # path = '/home/darren/Development/Testing/ImageURLs/unknown2.mp3'
        # path = '/home/darren/Development/Testing/ImageURLs/unknown3.mp3'
        # path = '/home/darren/Development/Testing/ImageURLs/unknown4.mp3'

        nbm = NukeBoxMeta()

        d = nbm.fingerPrint(path)
        d.addCallback(json.loads)
        d.addErrback(nbm.fpFail)
        d.addCallback(nbm.parseDetails)
        d.addErrback(nbm.parseFail)
        d.addCallback(nbm.metaData)
        d.addBoth(printResult)

    reactor.callLater(0, main)
    reactor.run()
