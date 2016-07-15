#!/usr/bin/env python

# Main Twisted Imports
from twisted.internet import reactor, protocol
# from twisted.internet.threads import deferToThread
from twisted.protocols.basic import LineReceiver

# HTTP Related Twisted Imports
from twisted.web.server import Site
from twisted.web.static import File

# Additional Imports
import os
import re
import vlc
import time
import pickle
import signal
import subprocess
import sys

from mutagen.id3 import ID3
from shutil import move
from socket import SOL_SOCKET, SO_BROADCAST
from StringIO import StringIO

# NukeBox Package Imports
from NukeBoxFileMeta import NukeBoxMeta
from NukeBoxQueue import NukeBoxQueue
from MongoBox import NukeBoxDB
from pymongo.errors import DuplicateKeyError


# TCP Protocol
class NukeBoxProtocol(LineReceiver):

    '''
    B{NukeBox 2000 Protocol Class}

      - Main Nukebox Protocol
      - Responsible for:
        - File Transfer
        - DB Access
        - Queuing
        - Error Checking
    '''

    # Instance Constructor
    def __init__(self, factory):

        '''
        Protocol Constructor

          - Receives the Parent Factory as argumnet
        '''

        # Create the Instance Variables

        # Reference to the Parent Factory
        self.factory = factory

        # Set the Initial users state to New
        # (used to register new users - may not need!)
        self.state = 'New'

        # Set the Initial Total File Size & Percent Variables
        # (used mainly for file tx.)
        self.sizeTotal = 0
        self.oldPercent = 0

        # Set the Intial State of the Buffer & Filename
        self.buffer = None
        self.fname = None

        # Database Connection
        self.nbdb = NukeBoxDB(self.factory.Logger)

    # Event - New Client Connected
    def connectionMade(self):

        '''
        B{Server} receives a new connection
        '''

        # Retrieve Info on the Client
        self.peer = self.transport.getPeer()
        self.ip = self.transport.getHost().host
        self.factory.Logger.msg('New Connection')

    def connectionLost(self, reason):

        '''
        B{Server} loses a connection
        '''

        # If the user exists in the user dictionary, remove the value
        # associated with them

        print('Connection Lost')

        # if self.busy:

        #     print('Still Busy...')
        #     reactor.callLater(5, self.connectionLost, reason)

        # else:

        self.factory.num_protos -= 1
        self.transport.loseConnection()

    def lineReceived(self, data):

        '''
        B{Incoming} Line Data

          - Un-pickles Line Data
          - Directs New User Instances to the Factory "On Data" method
        '''

        # self.factory.Logger.msg('Received: -> {} <- :|'.format(str(data)))
        # self.busy = True
        obj = pickle.loads(data)

        self.factory.onData(self, obj)

    def rawDataReceived(self, data):

        '''
        B{Raw} File data

          - Controls the Flow of Raw Data
          - Calls "bufferFile" Method to Process Data
          - Resets the Line Mode Once Complete
          - Creates a New File Obj in a Thread
        '''

        # Set the Protocol to "Busy"
        # self.busy = True

        # Buffer the Incoming Data
        self.bufferFile(data)

        # As long as We're Still Buffering
        if self.oldPercent < 100:
            return

        # Close the Buffer Obj & Reset Line Mode
        else:

            self.buffer.close()
            self.clearLineBuffer()
            self.setLineMode()

            self.factory.onFile(self)

            # Reset the Protocols "Busy" Switch
            # self.busy = False

    def bufferFile(self, chunck):
        '''
        B{Buffering} Raw Data

          - Calculates the Overall % Received
          - Writes Buffered Data to Temp File Once Complete
          - Relays the Progress to the Client Each Iteration
        '''

        # Write the Ingress Data to the Buffer Obj
        self.buffer.write(chunck)

        # Calculate the Overall Percent of the File Received
        currentPercent = self.buffer.len * 100 / self.sizeTotal

        # If there is an Increase in Received Data (May Not be Needed)
        if self.oldPercent != currentPercent:

            # Increase the oldPercent by what has been Received
            self.oldPercent = currentPercent

        # If the Full % Received
        if currentPercent >= 100:

            # Create the Path to the Sandboxed Copy of the File
            self.temp_f_name = os.path.join(self.factory.temp, self.fname)

            # Open the Temp File & Write the Data from the Buffer
            f = open(self.temp_f_name, 'wb+')

            # Writing File from Buffer
            f.write(self.buffer.getvalue())

        # Send % of Progress to the Client
        self.sendData(
            {
                'progress': currentPercent + 1
            }
        )

    def sendData(self, data):
        '''
        B{Pickle} data and Writes to Transport
        '''

        self.sendLine(pickle.dumps(data))


# UDP Protocol
class NukeBoxBroadcastReceiver(protocol.DatagramProtocol):

    '''
    B{NukeBox 2000 UDP Class}

      - Nukebox UDP Datagram Protocol
      - Responsible for:
        - Listening for broadcast/discover messages
        - Responding to clients
    '''

    def __init__(self, factory):

        '''
        B{Constructor} Method for the UDP Receiver
        '''

        # Create a Reference to the Parent Factory Class
        self.factory = factory

    def startProtocol(self):

        '''
        B{Broadcast} build method

          - Sets the underlying socket to receive UDP packets
        '''

        # Set the underlying socket for UDP
        self.transport.socket.setsockopt(
            SOL_SOCKET,
            SO_BROADCAST,
            True
        )

    def datagramReceived(self, data, addr):

        '''
        B{Receives} Datagram & Responds

          - Called when a UDP discover message is received
        '''

        print('Datagram received\n')

        # If We Receive the Correst String, Respond
        if data == 'Hello Jukebox':
            self.transport.write(
                "This is the JukeBox Speaking. I'm Here",
                addr
            )


# Factory
class NukeBoxFactory(protocol.ServerFactory):

    '''
    B{NukeBox 2000 Factory Object}

      - Stores Relevant Instance Variables
      - Builds a Protocol Instance for Each New Client
      - Starts a HTTP Server to Serve Cover Art
      - Registers New Clients
      - Processes Incoming Data Transfer and Request Info
      - Provides Protocols with Method to Update NukeBox Q Information
     '''

    # Constructor Method
    def __init__(self, q, default_dir, temp_dir, art_dir, Logger=None):

        '''
        B{Initial State} of the Nukebox Factory

          - Sets Up:
            - Logging
            - Directory Variables
            - Additional HTTP Server for Cover Art
        '''

        # Logging
        if Logger is None:

            from twisted.python import log as Logger

        self.Logger = Logger
        self.Logger.startLogging(sys.stdout)

        # Factory Up
        self.running = True
        self.Logger.msg('Factory Up :)')

        # Number of Currently Active Protocols
        self.num_protos = 0

        # Number of Threads
        self.num_threads = 0

        # Threads
        self.threads = []

        # Default Save Location
        self.dir = default_dir

        # Temporary Save Location
        self.temp = temp_dir

        # Default Art Save Location (made available over http)
        self.art_dir = art_dir

        # Queue System
        # NukeBox Q and Q Info
        self.q = q

        # Set Currently Playing Track to False
        self.playing = False

        # Set up the HTTP Art Server
        factory = Site(File(self.art_dir))
        reactor.listenTCP(8888, factory)
        self.Logger.msg('Cover Art Service Up :)')

        self.Logger.msg('Server Started Successfully :)')

    # Build Method
    def buildProtocol(self, addr):

        '''
        B{Builds Instances} of Nukebox Protocol

          - Increases Num Proto's by 1
          - Returns Proto Instance for Each New Connection
        '''

        self.Logger.msg('Building New Protocol :)')

        self.num_protos += 1

        # Build the Protocol Instance
        return NukeBoxProtocol(self)

    # Register Method
    def register(self, protocol, data):

        '''
        B{Register New Clients}

          - Adds User Entry to NukeBox DB
          - Sets the User Instance State to True
          - Receives 2 arguments (in addition to self):
            - "protocol" -> The instance we're working on
            - "data" -> Client related data (dict)

          - Returns no value
        '''

        client = data["name"]
        mac_id = data['mac_id']

        self.Logger.msg(
            'Registering New User -> {} <- with mac -> {} <- :)'.format(
                client,
                mac_id
            )
        )

        self.Logger.msg('Attempting to create user {} DB entry...'.format(
            client)
        )

        # Add the client to the DB via NukeBoxDB.create
        user = protocol.nbdb.createUser(
            {
                'name': client,
                'mac_id': mac_id
            }
        )

        self.Logger.msg('Created User: {}'.format(user))

        # Set the User Sate to Registered
        protocol.state = 'Reg'

    # Control Data Flow
    def onData(self, protocol, data):
        '''
        When a protocol Receives Data
          - If Not Already Registered, Passes to Register Method
          - If Registered, Passes to Process Method
        '''

        if protocol.state == 'New':
            self.register(protocol, data)

        else:
            self.process(protocol, data)

    # Process Registered Users Data
    def process(self, protocol, data):
        '''
        B{Process Method} Used to Determine Response to Data

          - If Incoming File is Signalled (via data['func']):
            - Set the Proto Instance File-name & File-size
            - Change the Proto Line Mode to "Raw"
            - Create the Buffer Obj to Buffer Incoming Data

          - If a Query is Signalled

            - Send the Current Q Info
        '''

        # If the "Func" key is "file"
        if data['func'] == 'file':

            # Sets the Instance Filename & File size
            protocol.fname = os.path.basename(data["filename"])
            protocol.sizeTotal = data["size"]

            self.Logger.msg('File -> {} <- Incoming...'.format(
                protocol.fname)
            )

            # Set the Line Mode to "Raw"
            protocol.setRawMode()
            protocol.buffer = StringIO()

            self.Logger.msg('Line Mode set to "Raw", Buffer Created :)')

        # If the "Func" key is "query"
        elif data['func'] == 'query':

            self.Logger.msg('The Q has been queried..')

            # Send the Current Q Info to the Client
            protocol.sendData(self.q.info)
            self.Logger.msg('Current Q Info Transmitted')

    # When a File is Received
    def onFile(self, protocol):
        '''
        B{On File Method} to process Incoming File

          - Creates a "New File" obj. on each call
          - Wraps the NF obj. in a "Closer" class
            - Enters & Exits cleanly - hopefully :|

          - Calls NF.onFile Method in separate thread
        '''

        temp_f = protocol.temp_f_name
        ip = protocol.ip
        nbdb = protocol.nbdb

        # Create a New File Obj & Run it's "onFile" Method in a Thread
        # Some of these variables should go !!!

        self.Logger.msg('Creating New File...')
        with Closer(
            NewFile(
                self,
                protocol,
                temp_f,
                ip,
                nbdb
            )
        ) as new_file:

            if self.running:

                reactor.callInThread(new_file.onFile)
                self.num_threads += 1
                self.threads.append(new_file)

        self.Logger.msg('New File sent to Thread :)')

    def printResult(self, result):

        print(result)


# New File Objects
class NewFile():

    '''
    B{Incoming File}

      - Processes Incoming Files
      - Retrieves Metadata
      - Moves File to Default Dir
      - Appends the NukeBoxQ
      - Writes Data to NukeBox DB
    '''

    # New File Constructor Method
    def __init__(self, factory, protocol, file, ip, nbdb):
        '''
        B{Constructor} Method for New Files
        '''

        # Required Instance Variables
        # self.d = d
        self.factory = factory
        self.protocol = protocol
        self.file = file
        self.file_data = {'art': None}
        self.base_url = 'http://{}:8888/'.format(str(ip))
        self.nbdb = nbdb

        self.Logger = self.factory.Logger
        self.Logger.msg('New File Created :)')

    # On File Method
    def onFile(self):
        '''
        B{New File Received}

          - Controls the Flow for the File Data
          - Retrieves Metadata
            - Uses either ID3 lib
            - Custom Metadata methods

          - Calls "moveFile" method
          - Updates/Appends the Q
          - Calls "writeToDB" method
        '''

        # Try to retrieve some metadata
        try:

            media = ID3(self.file)

            # Write the Metadata to the Instance Dict
            self.file_data['artist'] = str(media['TPE1'].text[0])
            self.file_data['track'] = str(media['TIT2'].text[0])

            # # Program can hit error here - TCON etc.

            if 'TCON' in media:
                self.file_data['genre'] = str(media['TCON'].text[0])

            if 'TALB' in media:
                self.file_data['album'] = str(media['TALB'].text[0])

            # Check for Embedded Cover Art
            art = False

            for i in media:

                # If Embedded Art
                if i.startswith('APIC'):

                    self.file_data['art'] = media[i].data
                    art = True
                    self.meta = False

                    self.Logger.msg('Embedded Cover Art Found')

                    self.metaProcess()

            # If there is no art embedded
            if not art:

                import json

                self.Logger.msg('Using Alternative Metadata Methods')
                self.meta = True

                # Create the custom Metadata Instance
                nbm = NukeBoxMeta()

                # FP method which returns Twisted Deferred obj.
                d = nbm.fingerPrint(self.file)

                # Add the various callbacks
                # which will run when the process returns
                d.addCallbacks(json.loads, nbm.fpFail)
                d.addCallback(nbm.parseDetails)
                d.addCallbacks(nbm.metaData, nbm.parseFail)
                d.addCallbacks(self.metaResult, self.metaError)

                self.Logger.msg(
                    'Returning Deferred Object - Something May go Wrong!'
                )

                # return the Deferred
                return d

        # Except if there is No Metadata
        except Exception as err:

            # No Metadata (but there should be!)
            self.Logger.err('Error in New File: {}'.format(err))

    # Metadata Successful Result Callback
    def metaResult(self, result):
        '''
        B{Successful Result Method}

          - Forms part of a Deferred Callback Chain
          - Recieves the resulting dict obj. (only cover art at the mo)
          - Passes the result to metaSuccess method
        '''

        self.Logger.msg('Metadata Success :)')

        # Set the Cover Art value in the File Data dict
        self.file_data['art'] = result['art'][0]

        # Call the Meta Success method
        self.metaProcess(result)

    # Metadata Unsuccessful Metadata result
    def metaError(self, error):
        '''
        B{Failed Result Method}
        '''

        self.Logger.msg('Error in Metadata is -> {} <- :('.format(error))

    # Successful Metadata
    def metaProcess(self, result=None):
        '''
        B{Process Metadata Method}

          - Moves the File now that it has been veerified
          - Appends the Q with the new track
          - Notifies the Client of the tracks position in the Q
          - Calls "writeToDB" to add a New File entry to the DB
        '''

        # Move the File to the Default Directory
        self.moveFile()

        # This tracks position in the Q
        position = 'Track {}\nPosition: {}'.format(
            self.file_data['track'],
            len(self.factory.q) + 1
        )

        # Append NukeBox Q
        self.factory.q.append(self.file_data, self.factory.playing)

        # Send the tracks queue position to the Sender
        self.protocol.sendData(
            {
                'position': position
            }
        )

        # Write the Entry to the NukeBox DB
        self.writeToDB()

    # Move File Method
    def moveFile(self):
        '''
        B{Move File Method}

          - Moves the Temp file from sandbox to default storage location
          - Parsing the Cover Art Details
        '''

        # Substitute Special Characters and Spaces in the title
        track = re.sub('[^\w\-_\.]', '-', self.file_data['track'])
        album = re.sub('[^\w\-_\.]', '-', self.file_data['album'])

        # Path to the Validated File
        dst = os.path.join(self.factory.dir, track + '.mp3')

        # If the File does not exist in the Default Directory, Create It
        if not os.path.isfile(dst):

            cmd = 'touch {}'.format(dst)
            subprocess.call(cmd, shell=True)

        # If Cover Art Exists
        if not self.meta:

            # Build the Path to Cover Art file
            art_file = os.path.join(self.factory.art_dir, album + '.jpeg')

            # If it Does Not Exists, Create it
            if not os.path.isfile(art_file):

                print('Art File is: {}'.format(art_file))

                cmd = 'touch {}'.format(art_file)
                subprocess.call(cmd, shell=True)

                with open(art_file, 'w') as art:
                    art.write(self.file_data['art'])

            # Overwrite the Original Entry with the New Path
            self.file_data['art'] = self.base_url + album + '.jpeg'

        # Try to Move the Temp File to the Default Dir
        try:

            move(self.file, dst)
            self.Logger.msg('File Successfully Moved :)!')

            # If it Succeeds, Add the Path to the Instance Dict
            self.file_data['path'] = dst

        # Except on Error
        except Exception as err:

            self.Logger.err('Error Moving File: {} :('.format(err))

    def writeToDB(self):
        '''
        B{Write DB Entry Method}

          - Add File Details to NukeBox DB
          - Returns Boolean True (can't remeber why!)
        '''

        # Try to Call the Create method on the Instance Dict
        try:

            new_file = self.nbdb.createFile(
                self.file_data
            )

            self.Logger.msg('New DB File Entry Added! :)')
            self.Logger.msg('File {} DB id -> {} <- :)'.format(new_file))

        # Except When an Entry Already Exists (may not be needed now!)
        except DuplicateKeyError:

            self.Logger.msg('DB Entry Already Exists')

        # Except Some Other Error
        except Exception as err:

            self.Logger.err('Something happened with Mongo! {} :('.format(err))

        return True


# Context Wrapper Object
class Closer:
    '''
    B{Context Manager}

      - Allows the use of the "with" statement
      - Automatically Close out an obj.
    '''

    # Constructor
    def __init__(self, obj):
        '''
        B{Wrapper Class} for Closing out obj.
        '''

        # receive an obj
        self.obj = obj
        self.Logger = obj.factory.Logger

    # Enter Method
    def __enter__(self):
        '''
        B{Enter Method}
        '''

        # Return the obj
        return self.obj  # bound to target

    # Exit Method
    def __exit__(self, exception_type, exception_val, trace):

        '''
        B{Exit Method}
        '''
        # Try to close cleanly
        try:

            self.Logger.msg('Closing Wrapped obj.')

            self.obj.close()
            del(self.obj)

            self.Logger.msg('Closed :)')

        except AttributeError:

            self.Logger.err('Wrapped obj not closable :(')

            return True


# Main Function for testing - Mirrors NukeBox.main
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

    from twisted.python import log as Logger

    Logger.startLogging(sys.stdout)

    main()
