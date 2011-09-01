import Queue
import re
import socket
import threading
import time

_EOL = '\r\n' #Asterisk uses CRLF linebreaks to mark the ends of its lines.


import sys,os
from cStringIO import StringIO
from types import *


class Manager(object):
    def __init__(self):
        self._sock = None     # our socket
        self.title = None     # set by received greeting
        self._connected = threading.Event()
        self._running = threading.Event()
        
        # our hostname
        self.hostname = socket.gethostname()

        # our queues
        self._message_queue = Queue.Queue()
        self._response_queue = Queue.Queue()
        self._event_queue = Queue.Queue()

        # callbacks for events
        self._event_callbacks = {}

        self._reswaiting = []  # who is waiting for a response

        # sequence stuff
        self._seqlock = threading.Lock()
        self._seq = 0
       
        # some threads
        self.message_thread = threading.Thread(target=self.message_loop)
        self.event_dispatch_thread = threading.Thread(target=self.event_dispatch)
        
        self.message_thread.setDaemon(True)
        self.event_dispatch_thread.setDaemon(True)


    def __del__(self):
        self.close()

    def connected(self):
        """
        Check if we are connected or not.
        """
        return self._connected.isSet()

    def next_seq(self):
        """Return the next number in the sequence, this is used for ActionID"""
        self._seqlock.acquire()
        try:
            return self._seq
        finally:
            self._seq += 1
            self._seqlock.release()
            
    def _generate_id(self):
        """
        For passing to request objects.
        """
        return '%(hostname)s-%(id)08x' % {
         'hostname': socket.gethostname(),
         'id': self.next_seq(),
        }
        
    def send_action(self, cdict={}, **kwargs):
        """
        Send a command to the manager
        
        If a list is passed to the cdict argument, each item in the list will
        be sent to asterisk under the same header in the following manner:

        cdict = {"Action": "Originate",
                 "Variable": ["var1=value", "var2=value"]}
        send_action(cdict)

        ...

        Action: Originate
        Variable: var1=value
        Variable: var2=value
        """

        if not self._connected.isSet():
            raise ManagerException("Not connected")
        
        # fill in our args
        cdict.update(kwargs)

        # set the action id
        if not cdict.has_key('ActionID'): cdict['ActionID'] = '%s-%08x' % (self.hostname, self.next_seq())
        clist = []

        # generate the command
        for key, value in cdict.items():
            if isinstance(value, list):
               for item in value:
                  item = tuple([key, item])
                  clist.append('%s: %s' % item)
            else:
               item = tuple([key, value])
               clist.append('%s: %s' % item)
        clist.append(EOL)
        command = EOL.join(clist)

        # lock the socket and send our command
        try:
            self._sock.write(command)
            self._sock.flush()
        except socket.error, (errno, reason):
            raise ManagerSocketException(errno, reason)
        
        self._reswaiting.insert(0,1)
        response = self._response_queue.get()
        self._reswaiting.pop(0)

        if not response:
            raise ManagerSocketException(0, 'Connection Terminated')

        return response

    def _receive_data(self):
        """
        Read the response from a command.
        """
        multiline = False
        wait_for_marker = False
        eolcount = 0
        # loop while we are sill running and connected
        while self._running.isSet() and self._connected.isSet():
            try:
                lines = []
                for line in self._sock :
                    # check to see if this is the greeting line    
                    if not self.title and '/' in line and not ':' in line:
                        # store the title of the manager we are connecting to:
                        self.title = line.split('/')[0].strip()
                        # store the version of the manager we are connecting to:
                        self.version = line.split('/')[1].strip()
                        # fake message header
                        lines.append ('Response: Generated Header\r\n')
                        lines.append (line)
                        break
                    # If the line is EOL marker we have a complete message.
                    # Some commands are broken and contain a \n\r\n
                    # sequence, in the case wait_for_marker is set, we
                    # have such a command where the data ends with the
                    # marker --END COMMAND--, so we ignore embedded
                    # newlines until we see that marker
                    if line == EOL and not wait_for_marker :
                        multiline = False
                        if lines or not self._connected.isSet():
                            break
                        # ignore empty lines at start
                        continue
                    lines.append(line)
                    # line not ending in \r\n or without ':' isn't a
                    # valid header and starts multiline response
                    if not line.endswith('\r\n') or ':' not in line:
                        multiline = True
                    # Response: Follows indicates we should wait for end
                    # marker --END COMMAND--
                    if not multiline and line.startswith('Response') and \
                        line.split(':', 1)[1].strip() == 'Follows':
                        wait_for_marker = True
                    # same when seeing end of multiline response
                    if multiline and line.startswith('--END COMMAND--'):
                        wait_for_marker = False
                        multiline = False
                    if not self._connected.isSet():
                        break
                else:
                    # EOF during reading
                    self._sock.close()
                    self._connected.clear()
                # if we have a message append it to our queue
                if lines and self._connected.isSet():
                    self._message_queue.put(lines)
                else:
                    self._message_queue.put(None)
            except socket.error:
                self._sock.close()
                self._connected.clear()
                self._message_queue.put(None)

    
    def register_event(self, event, function):
        """
        Register a callback for the specfied event.
        If a callback function returns True, no more callbacks for that
        event will be executed.
        """

        # get the current value, or an empty list
        # then add our new callback
        current_callbacks = self._event_callbacks.get(event, [])
        current_callbacks.append(function)
        self._event_callbacks[event] = current_callbacks

    def unregister_event(self, event, function):
        """
        Unregister a callback for the specified event.
        """
        current_callbacks = self._event_callbacks.get(event, [])
        current_callbacks.remove(function)
        self._event_callbacks[event] = current_callbacks

    def message_loop(self):
        """
        The method for the event thread.
        This actually recieves all types of messages and places them
        in the proper queues.
        """

        # start a thread to recieve data
        t = threading.Thread(target=self._receive_data)
        t.setDaemon(True)
        t.start()

        try:
            # loop getting messages from the queue
            while self._running.isSet():
                # get/wait for messages
                data = self._message_queue.get()

                # if we got None as our message we are done
                if not data:
                    # notify the other queues
                    self._event_queue.put(None)
                    for waiter in self._reswaiting:
                        self._response_queue.put(None)
                    break

                # parse the data
                message = ManagerMsg(data)

                # check if this is an event message
                if message.has_header('Event'):
                    self._event_queue.put(Event(message))
                # check if this is a response
                elif message.has_header('Response'):
                    self._response_queue.put(message)
                else:
                    print 'No clue what we got\n%s' % message.data
        finally:
            # wait for our data receiving thread to exit
            t.join()
                            

    def event_dispatch(self):
        """This thread is responsible for dispatching events"""

        # loop dispatching events
        while self._running.isSet():
            # get/wait for an event
            ev = self._event_queue.get()

            # if we got None as an event, we are finished
            if not ev:
                break
                
            # dispatch our events

            # first build a list of the functions to execute
            callbacks = (self._event_callbacks.get(ev.name, [])
                      +  self._event_callbacks.get('*', []))

            # now execute the functions  
            for callback in callbacks:
               if callback(ev, self):
                  break

    def connect(self, host, port=5038):
        """Connect to the manager interface"""

        if self._connected.isSet():
            raise ManagerException('Already connected to manager')

        # make sure host is a string
        assert type(host) in StringTypes

        port = int(port)  # make sure port is an int

        # create our socket and connect
        try:
            _sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            _sock.connect((host,port))
            self._sock = _sock.makefile ()
            _sock.close ()
        except socket.error, (errno, reason):
            raise ManagerSocketException(errno, reason)

        # we are connected and running
        self._connected.set()
        self._running.set()

        # start the event thread
        self.message_thread.start()

        # start the event dispatching thread
        self.event_dispatch_thread.start()

        # get our initial connection response
        return self._response_queue.get()

    def close(self):
        """Shutdown the connection to the manager"""
        
        # if we are still running, logout
        if self._running.isSet() and self._connected.isSet():
            self.logoff()
         
        if self._running.isSet():
            # put None in the message_queue to kill our threads
            self._message_queue.put(None)

            # wait for the event thread to exit
            self.message_thread.join()

            # make sure we do not join our self (when close is called from event handlers)
            if threading.currentThread() != self.event_dispatch_thread:
                # wait for the dispatch thread to exit
                self.event_dispatch_thread.join()
            
        self._running.clear()
        
    def login(self, username, secret):
        """Login to the manager, throws ManagerAuthException when login falis"""
           
        cdict = {'Action':'Login'}
        cdict['Username'] = username
        cdict['Secret'] = secret
        response = self.send_action(cdict)
        
        if response.get_header('Response') == 'Error':
           raise ManagerAuthException(response.get_header('Message'))
        
        return response
        
        
class ManagerMsg(object):
    """A manager interface message"""
    def __init__(self, response):
        # the raw response, straight from the horse's mouth:
        self.response = response
        self.data = ''
        self.headers = {}
        
        # parse the response
        self.parse(response)

        # This is an unknown message, may happen if a command (notably
        # 'dialplan show something') contains a \n\r\n sequence in the
        # middle of output. We hope this happens only *once* during a
        # misbehaved command *and* the command ends with --END COMMAND--
        # in that case we return an Event.  Otherwise we asume it is
        # from a misbehaving command not returning a proper header (e.g.
        # IAXnetstats in Asterisk 1.4.X)
        # A better solution is probably to retain some knowledge of
        # commands sent and their expected return syntax. In that case
        # we could wait for --END COMMAND-- for 'command'.
        # B0rken in asterisk. This should be parseable without context.
        if 'Event' not in self.headers and 'Response' not in self.headers:
            # there are commands that return the ActionID but not
            # 'Response', e.g., IAXpeers in Asterisk 1.4.X
            if self.has_header('ActionID'):
                self.headers['Response'] = 'Generated Header'
            elif '--END COMMAND--' in self.data:
                self.headers['Event'] = 'NoClue'
            else:
                self.headers['Response'] = 'Generated Header'
        
    def parse(self, response):
        """Parse a manager message"""

        data = []
        for n, line in enumerate (response):
            # all valid header lines end in \r\n
            if not line.endswith ('\r\n'):
                data.extend(response[n:])
                break
            try:
                k, v = (x.strip() for x in line.split(':',1))
                self.headers[k] = v
            except ValueError:
                # invalid header, start of multi-line data response
                data.extend(response[n:])
                break
        self.data = ''.join(data)

    def has_header(self, hname):
        """Check for a header"""
        return self.headers.has_key(hname)

    def get_header(self, hname, defval = None):
        """Return the specfied header"""
        return self.headers.get(hname, defval)

    def __getitem__(self, hname):
        """Return the specfied header"""
        return self.headers[hname]
    def __repr__(self):
        return self.headers['Response']
        
        
class Event(object):
    """Manager interface Events, __init__ expects and 'Event' message"""
    def __init__(self, message):

        # store all of the event data
        self.message = message
        self.data = message.data
        self.headers = message.headers

        # if this is not an event message we have a problem
        if not message.has_header('Event'):
            raise ManagerException('Trying to create event from non event message')

        # get the event name
        self.name = message.get_header('Event')
    
    def has_header(self, hname):
        """Check for a header"""
        return self.headers.has_key(hname)

    def get_header(self, hname, defval = None):
        """Return the specfied header"""
        return self.headers.get(hname, defval)
    
    def __getitem__(self, hname):
        """Return the specfied header"""
        return self.headers[hname]
    
    def __repr__(self):
        return self.headers['Event']

    def get_action_id(self):
        return self.headers.get('ActionID',0000)
        






class _ManagerRequest(dict):
    """
    Provides a generic container for assembling AMI requests.
    
    Subclasses may override `__init__` and define any additional behaviours they may need, as well
    as override `process_response()` to specially format the data to be returned after a request
    has been served.
    """
    def __init__(self, action):
        """
        `action` is the type of action being requested of the Asterisk server.
        """
        self['Action'] = action
        
    def build_request(self, id_generator, **kwargs):
        """
        Returns a string formatted for transmission to Asterisk to place a request.
        
        `id_generator` is a function that generates an Asterisk ActionID.
        
        `**kwargs` is a dictionary of additional arguments that may be passed along with the request
        at submission time.
        
        The 'Action' line is always first.
        """
        items = [('Action', self['Action'])]
        items += [(key, value) for (key, value) in self.items() if not key == 'Action']
        items += [(key, value) for (key, value) in kwargs.items()]
        
        if not 'ActionID' in self: #Add an ActionID if not already defined
            items += [('ActionID', id_generator())]
            
        return _EOL.join(['%(key)s: %(value)s' % {
         'key': key,
         'value': value,
        } for (key, value) in items] + [_EOL])
        
    def process_response(self, response):
        """
        Provides an opportunity to parse, filter, or react to a response from Asterisk.
        
        This implementation just passes the response back to the caller as received.
        """
        return response
        
        
class ManagerException(Exception):
    pass
    
class ManagerError(ManagerException):
    pass
    
"""
class ManagerSocketException(ManagerException):
    pass
"""

