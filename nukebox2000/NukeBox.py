#!/usr/bin/env python

# Main Twisted Imports
from twisted.internet import reactor
# from twisted.internet.threads import deferToThread

# Additional Imports
import os
import vlc
import time
import signal

# NukeBox Package Imports
from NukeBoxQueue import NukeBoxQueue
from NukeBoxServer import NukeBoxFactory, NukeBoxBroadcastReceiver


# Main Functions
def main():

    '''
    Main function
    '''

    def makeDir(_dir, permission):
        '''
        '''

        try:
            original_umask = os.umask(0)
            os.makedirs(_dir, permission)

        finally:
            os.umask(original_umask)

    vlc_instance = vlc.Instance()

    # Create the Double Ended Queue (Deque)
    q = NukeBoxQueue()

    # Create a Reference to the Users Home Dir
    HOME = os.path.expanduser('~')

    # Create a String for the Default & Temporary Save Locations
    default_dir = os.path.join(HOME, 'Music/NukeBox2000')
    temp_dir = '/tmp/NukeBox2000/'
    art_dir = os.path.join(HOME, 'Music/NukeBox2000/art')

    # If Default Location Does not Exist, Create it
    if not os.path.isdir(default_dir):

        makeDir(default_dir, 0755)
        # os.makedirs(default_dir)

    # If Temporary Location Does not Exist, Create it
    if not os.path.isdir(temp_dir):

        makeDir(temp_dir, 0755)
        # os.makedirs(temp_dir)

    # If the Art Dir Does Not Exist
    if not os.path.isdir(art_dir):

        makeDir(art_dir, 0755)
        # os.makedirs(art_dir)

    def playBack(f):

        '''
        File PlayBack Function

          - Runs in Thread of its own
          - Continues to check the Queue for new entries
          - Calls VLC CLI command to play file
        '''

        # player = vlc.media_player_new()

        # vlc_instance = vlc.Instance()

        # While the Server is UP
        while reactor.running:

            # If there is an Entry in the Queue
            if len(q) > 0 and not f.playing:

                # Pull the Entry at Index 0
                next_file = q.popleft()

                # Split the String into a User ID & File Path
                path = next_file['path']

                # If the File Does Exist
                if os.path.isfile(path):

                    print('Attempting New Playback')

                    try:

                        player = vlc_instance.media_player_new()
                        _path = vlc_instance.media_new(path)
                        player.set_media(_path)
                        player.play()

                        f.playing = True

                        # Allow for Opening Time i.e. State = vlc.State.Opening
                        time.sleep(2)

                        print('Playing: ', str(player.is_playing()))

                        while player.is_playing():

                            if reactor.running:
                                time.sleep(1)
                                continue

                            else:
                                return

                    except Exception as err:
                        print('Playback Error: ', err)

                    f.playing = False
                    print('Finished Playing')

            if len(q) is 0 and not f.playing and f.q.pop:

                f.q.reset()
                time.sleep(2)

    def cleanUp(signal, frame):

        '''
        Called to Exit somewhat gracefully
        '''

        f.running = False
        reactor.stop()

    # Create the Factory Instance
    f = NukeBoxFactory(q, default_dir, temp_dir, art_dir)

    # Notify the Reactor to Listen for TCP Connections
    reactor.listenTCP(18008, f)

    # Create a UDP Protocol Instance
    protocol = NukeBoxBroadcastReceiver(f)

    # Notify the Reactor to Listen for UDP Connections
    reactor.listenUDP(19009, protocol)

    # Add the Shutdown Signal Handler
    signal.signal(signal.SIGINT, cleanUp)

    # System Event - Triggered by CTRL+C
    # reactor.addSystemEventTrigger('before', 'shutdown', cleanUp)
    reactor.addSystemEventTrigger('after', 'shutdown', os._exit, 0)

    # Defer the Playback Function to its Own Thread
    pb = reactor.callInThread(playBack, f)

    # Run the Reactor
    reactor.run()


if __name__ == '__main__':

    main()
