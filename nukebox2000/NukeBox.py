#!/usr/bin/env python

# Main Twisted Imports
from twisted.internet import reactor
from twisted.python import log as Logger

# Additional Imports
import os
import vlc
import time
import signal
import sys

# NukeBox Package Imports
from NukeBoxQueue import NukeBoxQueue
from NukeBoxServer import NukeBoxFactory, NukeBoxBroadcastReceiver


# Main Functions
def main():

    '''
    B{Main} function of the NukeBox Server

      - Contains 3 functions:
        - "makeDirs" -> Creates required NukeBox Server directory structure
        - "playBack" -> Plays each track in turn
        - "cleanUp"  -> Stops the Reactor

      - Takes  no arguments (currently)
      - Returns no value
    '''

    def makeDir(_path, permission):
        '''
        B{Make Dirs}

          - Only really used due to some possible issues involved
          - Calls B{umask} & tries to make the new directory
          - Resets B{umask} on exit
          - Requires 2 arguments
            - "Path" -> to the new directory
            - "Permission" -> B{Octal} permission to be assigned
        '''

        # Try to Create the Directory
        try:
            original_umask = os.umask(0)
            os.makedirs(_path, permission)

        # Reset the umask value if try succeeds
        finally:
            os.umask(original_umask)

    # Create a VLC Instance Obj for creating Media Players
    vlc_instance = vlc.Instance()

    # Create the NukeBox Deque
    q = NukeBoxQueue()

    # Reference the Current Users Home Dir
    HOME = os.path.expanduser('~')

    # Create the Directory Structure Paths
    # Deafault Music Storage
    default_dir = os.path.join(HOME, 'Music/NukeBox2000')

    # Cover Art directory (is later served up to Clients)
    art_dir = os.path.join(HOME, 'Music/NukeBox2000/art')

    # Temp Sandbox while Metadata is retrieved
    temp_dir = '/tmp/NukeBox2000/'

    # If Default Location does not exist, Create it
    if not os.path.isdir(default_dir):

        makeDir(default_dir, 0755)

    # If Temporary Location Does not exist, Create it
    if not os.path.isdir(temp_dir):

        makeDir(temp_dir, 0755)

    # If the Art Dir does not exist, Create it
    if not os.path.isdir(art_dir):

        makeDir(art_dir, 0755)

    # Simple Playback Function
    def playBack(f):

        '''
        B{PlayBack} Function

          - Continously checks the Queue for new Tracks
          - Pops each entry in turn
          - Creates Media PLayer via VLC
          - Plays out the Track
          - Takes a NukeBoxFactory object
          - Returns no value

        '''

        # While the Server is UP
        while reactor.running:

            # If there is an entry in the Q and the Player is at rest
            if len(q) > 0 and not f.playing:

                # Grab the Next Track (dict obj)
                next_file = q.popleft()

                Logger.msg('Popped New Track')

                # If the File Does Exist
                if os.path.isfile(next_file['path']):

                    Logger.msg('Attempting Playback of {}...'.format(
                        os.path.split(next_file['path'])[1])
                    )

                    try:

                        player = vlc_instance.media_player_new()
                        _path = vlc_instance.media_new(next_file['path'])
                        player.set_media(_path)
                        player.play()

                        f.playing = True

                        # Allow for Opening Time i.e. State = vlc.State.Opening
                        time.sleep(2)

                        Logger.msg('Playing Instance: {}'.format(
                            player.is_playing())
                        )

                        while player.is_playing():

                            if reactor.running:
                                time.sleep(1)
                                continue

                            else:
                                return

                    except Exception as err:
                        Logger.err('Playback Error: {}'.format(err))

                    f.playing = False

                    Logger.msg('Finished Playback of {}'.format(
                        os.path.split(next_file['path'])[1])
                    )

                # Other there is an error with the path
                else:

                    Logger.err('File Path Does not Exist')

            # If the Q is empty, Player is resting and
            # the Q has undergone at least 1 Pop
            if len(q) is 0 and not f.playing and f.q.pop:

                # Reset the Q variables
                f.q.reset()
                time.sleep(2)

    # Simple Teardown Function
    def cleanUp(signal, frame):

        '''
        B{CleanUp} Function

          - CleanUp is called via B{Signal Interrupt} (Ctrl + c)
          - Sets the media players B{"running"} variable to False
          - Stops the Reactor
        '''

        f.running = False

        Logger.msg('Shutting down the Reactor')

        reactor.stop()

    # Create the Factory Instance
    f = NukeBoxFactory(
        q,
        default_dir,
        temp_dir,
        art_dir,
        Logger
    )

    # Notify the Reactor to Listen for TCP Connections
    reactor.listenTCP(18008, f)

    Logger.msg('TCP Listening')

    # Create a UDP Protocol Instance
    protocol = NukeBoxBroadcastReceiver(f)

    # Notify the Reactor to Listen for UDP Connections
    reactor.listenUDP(19009, protocol)

    Logger.msg('UDP Listening')

    # Add the Shutdown Signal Handler
    signal.signal(signal.SIGINT, cleanUp)

    # System Event - Triggered by CTRL+C
    # reactor.addSystemEventTrigger('before', 'shutdown', cleanUp)
    reactor.addSystemEventTrigger('after', 'shutdown', os._exit, 0)

    # Defer the Playback Function to its Own Thread
    pb = reactor.callInThread(playBack, f)

    Logger.msg('PlayBack Thread: {}'.format(pb))
    Logger.msg('Starting the Reactor')

    # Run the Reactor
    reactor.run()


if __name__ == '__main__':

    Logger.startLogging(sys.stdout)
    main()
