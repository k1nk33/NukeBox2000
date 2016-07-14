#!/usr/bin/env python

# Main Twisted Imports
from twisted.internet import reactor, protocol, defer
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

from shutil import move
from mutagen.id3 import ID3
from StringIO import StringIO
from socket import SOL_SOCKET, SO_BROADCAST

# NukeBox Package Imports
from NukeBoxQueue import NukeBoxQueue
from MongoBox import NukeBoxDB
from NukeBoxFileMeta import NukeBoxMeta
from pymongo.errors import DuplicateKeyError


# TCP Protocol
class NukeBoxProtocol(LineReceiver):

    '''
    B{NukeBox 2000 Protocol Class}

      - Main Nukebox Protocol Object
      - Responsible for:

        - File Transfer
        - DB Access
        - Queuing
        - Error Checking
    '''

    def __init__(self, factory):

        '''
        Protocol Constructor
        '''

        # Create the Instance Variables

        # Create a Reference to the Parent Factory
        self.factory = factory

        # Set the Users State to New
        self.state = 'New'

        # Set the Initial Total File Size & Percent Variables
        self.sizeTotal = 0
        self.oldPercent = 0

        # Set the Intial State of the Buffer & Filename
        self.buffer = None
        self.fname = None

        self.nbdb = NukeBoxDB()
        # self.busy = False

    def connectionMade(self):

        '''
        Called when the Server receives a new connection
        '''

        # Retrieve Info on the Client
        self.peer = self.transport.getPeer()
        self.ip = self.transport.getHost().host
        print('New Connection\n')

    def connectionLost(self, reason):

        '''
        Called when the Server loses a connection
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
        Controls the Flow of Incoming Line Data

        - Un-pickles Line Data
        - Directs New User Instances to the Factory "On Data" method
        '''

        # self.busy = True
        obj = pickle.loads(data)

        self.factory.onData(self, obj)

    def rawDataReceived(self, data):

        '''
        Receives the Raw File data

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
        Responsible for Buffering Raw Data

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
        Pickles any Data it Receives and Writes to Transport,
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
        Constructor Method for the UDP Receiver
        '''

        # Create a Reference to the Parent Factory Class
        self.factory = factory

    def startProtocol(self):

        '''
        Sets the underlying socket to receive UDP packets
        '''

        # Set the underlying socket for UDP
        self.transport.socket.setsockopt(
            SOL_SOCKET,
            SO_BROADCAST,
            True
        )

    def datagramReceived(self, data, addr):

        '''
        Called when a UDP discover message is received
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

    def __init__(self, q, default_dir, temp_dir, art_dir):

        '''
        Constructor for the Nukebox Factory
        '''

        # Factory Up
        self.running = True

        # Number of Current Protocols
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
        # self.q_info = {}

        # Set Currently Playing Track to False
        self.playing = False

        # Set up the HTTP Art Server
        factory = Site(File(self.art_dir))
        reactor.listenTCP(8888, factory)

        print('********  Server Up!  ********\n')

    def buildProtocol(self, addr):

        '''
        Builds instances of Nukebox Protocol

          - Increases Num Proto's by 1
          - Returns Proto Instance for Each New Client
        '''

        self.num_protos += 1

        # Build the Protocol Instance
        return NukeBoxProtocol(self)

    def register(self, protocol, data):

        '''
        Registers New Clients

          - Deconstructs Data
          - Adds User Entry to NukeBox DB
          - Sets the User Instance State
        '''

        client = data["name"]
        mac_id = data['mac_id']

        print('Registering New User:\n{}\n{}'.format(
            client,
            mac_id)
        )

        # New Mongo bit
        print('Attempting to create user {} DB entry'.format(client))

        user = protocol.nbdb.createUser(
            {
                'name': client,
                'mac_id': mac_id
            }
        )

        print('Created user: {}'.format(user))

        # Set the User Sate to Registered
        protocol.state = 'Reg'

    def onData(self, protocol, data):
        '''
        Method Called When Any Data is Received

          - Controls the Flow of Incoming Data

            - If Not Already Registered, Passes to Register Method
            - If Registered, Passes to Process Method
        '''

        if protocol.state == 'New':
            self.register(protocol, data)

        else:
            self.process(protocol, data)

    def process(self, protocol, data):
        '''
        Process Method Used to Determine Response to Data

          - If Incoming File is Signalled

            - Set the Proto Instance File-name & File-size
            - Change the Proto Line Mode to "Raw"
            - Create the Buffer Obj to Buffer Incoming Data

          - If a Query is Signalled

            - Send the Current Q Info
        '''

        # If the "Func" key is "File"
        if data['func'] == 'file':

            # Look into os path spliT !!!

            # Parse the Filename
            fname = data["filename"].split('/')

            # Sets the Instance Filename & File size
            protocol.fname = fname[-1]
            protocol.sizeTotal = data["size"]

            # Set the Line Mode to "Raw"
            protocol.setRawMode()
            protocol.buffer = StringIO()

        # If the "Func" key is "Query"
        elif data['func'] == 'query':

            # Send the Current Q Info
            print('Sending Q Info: {}'.format(self.q.info))
            protocol.sendData(self.q.info)

    # For Retrieving Cover Art When None Embedded
    def onFile(self, protocol):
        '''
        '''

        temp_f = protocol.temp_f_name
        ip = protocol.ip
        nbdb = protocol.nbdb

        # Create a New File Obj & Run it's "onFile" Method in a Thread
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
                # return

                # reactor.callLater(0, new_file.onFile)
        # else:

        #     del(new_file)
        #     self.num_threads -= 1
        print('Number of Current Threads - {}'.format(self.num_threads))

    def printResult(self, result):

        print(result)


# New File Objects
class NewFile():

    '''
    New Incoming File Object

      - Processes Incoming Files
      - Retrieves Metadata
      - Moves File(s) to Default Dir
      - Appends the NukeBoxQ
      - Writes Data to NukeBox DB
    '''

    def __init__(self, factory, protocol, file, ip, nbdb):
        '''
        Constructor method
        '''

        # Required Instance Variables
        # self.d = d
        self.factory = factory
        self.protocol = protocol
        self.file = file
        self.file_data = {'art': None}
        self.base_url = 'http://{}:8888/'.format(str(ip))
        self.nbdb = nbdb

    def onFile(self):
        '''
        Method Called on New File Received

          - Controls the Flow for the File Data
          - Retrieves Metadata
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
                    self.metaSuccess()

            if not art:

                import json

                print('No Embedded Art\nUsing Alternative Method')
                self.meta = True

                nbm = NukeBoxMeta()

                d = nbm.fingerPrint(self.file)
                d.addCallbacks(json.loads, nbm.fpFail)
                d.addCallback(nbm.parseDetails)
                d.addCallbacks(nbm.metaData, nbm.parseFail)
                d.addCallbacks(self.metaResult, self.metaError)

        # Except if there is No Metadata
        except Exception as err:

            # No Metadata (but there should be!)
            print('New File Error is {}'.format(err))

    def metaResult(self, result):
        '''
        '''

        print('Meta Result is: ', result)

        self.file_data['art'] = result['art'][0]

        self.metaSuccess(result)

    def metaError(self, error):
        '''
        '''

        print('Error in Meta ', error)

    def metaSuccess(self, result=None):
        '''
        '''

        # print('X is ', result)

        # Move the File to the Default Directory
        self.moveFile()

        position = 'Track {}\nPosition: {}'.format(
            self.file_data['track'],
            len(self.factory.q) + 1
        )

        # Append NukeBox Q
        self.factory.q.append(self.file_data, self.factory.playing)

        self.protocol.sendData(
            {
                'position': position
            }
        )

        # Write the Entry to the NukeBox DB
        self.writeToDB()

    def moveFile(self):
        '''
        Responsible for:

          - Moving the Temp file from /tmp to ~/Music/NukeBox2000/
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
        if not self.meta:  # self.file_data['art'] is not None:

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
            print('Moved Success!')

            # If it Succeeds, Add the Path to the Instance Dict
            self.file_data['path'] = dst

        # Except on Error
        except Exception as err:

            print('Error Moving: {}'.format(err))

    def writeToDB(self):
        '''
        Called to Write File Details to NukeBox DB
        '''

        # Try to Call the Create method on the Instance Dict
        try:

            new_file = self.nbdb.createFile(
                self.file_data
            )

            print('New File Entry: {}\nDB Appended! :)\n'.format(new_file))

        # Except When an Entry Already Exists (may not be needed now!)
        except DuplicateKeyError:

            print('DB Entry Already Exists')

        # Except Some Other Error
        except Exception as err:

            print('Something happened with Mongo!\n{}'.format(err))

        return True


class Closer:
    '''A context manager to automatically close an object with a close method
    in a with statement.'''

    def __init__(self, obj):
        self.obj = obj

    def __enter__(self):
        return self.obj  # bound to target

    def __exit__(self, exception_type, exception_val, trace):

        try:
            self.obj.close()
            del(self.obj)

        except AttributeError:  # obj isn't closable
            print 'Not closable.'
            return True  # exception handled successfully


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
