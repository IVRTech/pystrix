import Queue
import re
import socket
import threading
import time
import types

_EOC = '--END COMMAND--' #A string used by Asterisk to mark the end of some of its responses.
_EOL = '\r\n' #Asterisk uses CRLF linebreaks to mark the ends of its lines.
_EOL_FAKE = ('\n\r\n', '\r\r\n') #End-of-line patterns that indicate data, not headers.

_EOC_INDICATOR = re.compile(r'Response:\s*Follows\s*$') #A regular expression that matches response headers that indicate the payload is attached

RESPONSE_GENERIC = 'Generic Response' #A header-value provided as a surrogate for unidentifiable responses
EVENT_GENERIC = 'Generic Event' #A header-value provided as a surrogate for unidentifiable unsolicited events

KEY_ACTIONID = 'ActionID' #The key used to hold the ActionID of a request, for matching with responses


import sys,os
from cStringIO import StringIO
from types import *

class Manager(object):
    _action_id = None #The ActionID last sent to Asterisk
    _action_id_lock = None #A lock used to prevent race conditions on ActionIDs
    _connection = None #A connection to the Asterisk manager, realised as a `_SynchronisedSocket`
    _connection_lock = None #A means of preventing race conditions on the connection
    _hostname = socket.gethostname() #The hostname of this system, used to prevent repeated calls through the C layer
    _outstanding_requests = None #A set of ActionIDs sent to Asterisk, currently awaiting responses
    _served_requests = None #A dictionary of responses from Asterisk, keyed by ActionID
    
    def __init__(self):
        self._action_id = 0
        self._action_id_lock = threading.Lock()

        self._connection_lock = threading.Lock()

        self._outstanding_requests = set()
        self._served_requests = {}



        self._running = threading.Event()

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
        """
        Ensure that all resources are freed quickly upon garbage-collection.
        """
        self.close()
        
    def _get_action_id(self):
        """
        Produces a session-unique int, suitable for passing to Asterisk as an ActionID.
        """
        with self._action_id_lock as lock:
            self._action_id += 1
            if self._action_id > 0xFFFFFFFF:
                self._action_id = 1
            return self._action_id

    def _get_host_action_id(self):
        """
        Generates a host-qualified ActionID as a string, for greater resolution.
        """
        return '%(hostname)s-%(id)08x' % {
         'hostname': self._hostname,
         'id': self._get_action_id(),
        }

    def connect(self, host, port=5038):
        """
        Establishes a connection to the specified Asterisk manager.
        
        If the connection fails, `ManagerSocketException` is raised.
        """
        self.disconnect()
        with self._connection_lock as lock:
            self._connection = _SynchronisedSocket(host, port)
            
    def disconnect(self):
        """
        Gracefully closes a connection to the Asterisk manager.
        """
        with self._connection_lock as lock:
            if self._connection: #Close the old connection, if any.
                self._connection.close()
                self._connection = None
            self._outstanding_requests.clear()
            self._served_requests.clear()
            
    def get_asterisk_info(self):
        """
        Provides the name and version of Asterisk as a tuple of strings.

        If not connected, `None` is returned.
        """
        with self._connection_lock as lock:
            return (self.is_connected and self._connection.get_asterisk_info()) or None
            
    def is_connected(self):
        """
        Indicates whether the manager is connected.
        """
        with self._connection_lock as lock:
            return bool(self._connection and self._connection.is_connected())
            
    def send_action(self, request, **kwargs):
        """
        Sends a command, contained in `request`, a `_Request`, to the Asterisk manager. Any
        additional keyword arguments are added directly into the request message as though they
        were native headers.
        
        Asterisk's response is returned as a tuple of a `_Message` object, the original request, and
        the time-delta in seconds, or `None` if the request timed out.
        
        Raises `ManagerException` if the manager is not connected.

        Raises `ManagerSocketException` if the socket is broken during transmission.

        This function is thread-safe.
        """
        with self._connection_lock as lock:
            if not self.is_connected():
                raise ManagerException("Not connected to an Asterisk manager")
                
            (command, action_id) = request.build_request(self._get_host_action_id, kwargs)
            self._connection.send_message(command)

            self._outstanding_requests[action_id] = request

        start_time = time.time()
        timeout = start_time + request.get_timeout()
        while time.time() < timeout:
            with self._connection_lock as lock:
                response = self._served_requests.get(action_id)
                if response:
                    del self._served_requests[action_id]
                    return (response, request, time.time() - start_time)
            time.sleep(0.05)
        return None

        
        
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

    def close(self):
        """
        Release all resources associated with this manager and ensure that all threads have stopped.
        """
        self.disconnect()

        """ 
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
        """

    
class _Message(dict):
    """
    An event received from Asterisk.

    All message headers are exposed as dictionary items on this object directly, for simplicity's
    sake. For purposes of being explicit, the 'headers' property is a recursive reference to its
    parent `_Event`.
    """
    data = None #The payload received from Asterisk
    headers = None #A reference to this object, which is a dictionary with header responses from Asterisk
    raw = None #The raw response received from Asterisk
    
    def __init__(self, response):
        """
        Parses the `response` received from Asterisk and assembles a structured event object
        suitable for processing by application logic.
        """
        self.data = []
        self.headers = self
        self.raw = response
        self._parse(response)

        #Apply some tests to see if Asterisk sent back a malformed response and try to make it
        #salvagable. This typically only happens with specific events, so applications can deal
        #with it more effectively than the processing core.
        if 'Event' not in self and 'Response' not in self:
            if self.has_header(KEY_ACTIONID): #If 'ActionID' is present, it's a response to an action.
                self.headers['Response'] = RESPONSE_GENERIC
            elif '--END COMMAND--' in self.data: #It's an unsolicited event
                self.headers['Event'] = EVENT_GENERIC
            self.headers['Event'] = EVENT_GENERIC #If neither case holds, assume it's an unsolicited event.
            
    def _parse(self, response):
        """
        Parses the response from Asterisk.

        All headers are added to the core dictionary and all data is exposed as a list of lines.
        """
        while response:
            line = response[0]
            if line.endswith(_EOL_FAKE) or not line.endswith(_EOL) or not ':' in line: #All lines from this point forth are data
                self.data.extend((l.strip() for l in response))
                break
            (key, value) = response.pop(0).split(':', 1)
            self[key.strip()] = value.strip()
            
    def __eq__(self, o):
        """
        A convenience qualifier for decision-blocks to allow the event to be compared to strings for
        readability purposes.
        """
        if isinstance(o, types.StringType):
            return self['Event'] == o
        return dict.__eq__(self, o)
        
class _Request(dict):
    """
    Provides a generic container for assembling AMI requests.
    
    Subclasses may override `__init__` and define any additional behaviours they may need, as well
    as override `process_response()` to specially format the data to be returned after a request
    has been served.
    """
    _timeout = 0
    
    def __init__(self, action):
        """
        `action` is the type of action being requested of the Asterisk server.
        """
        self['Action'] = action
        
    def build_request(self, id_generator, **kwargs):
        """
        Returns a string formatted for transmission to Asterisk to place a request and the action ID
        associated with the request.
        
        `id_generator` is a function that generates an Asterisk ActionID.
        
        `**kwargs` is a dictionary of additional arguments that may be passed along with the request
        at submission time.
        
        The 'Action' line is always first.
        """
        items = [('Action', self['Action'])]
        for (key, value) in [(k, v) for (k, v) in self.items() if not k == 'Action'] + kwargs.items():
            key = str(key)
            if type(value) in (tuple, list, set, frozenset):
                for val in value:
                    items.append((key, str(val)))
            else:
                items.append((key, str(value)))

        action_id = self.get(KEY_ACTIONID)
        if action_id is None: #Add an ActionID if not already defined
            action_id = str(id_generator())
            items.append((KEY_ACTIONID, action_id))
            
        return (
         _EOL.join(['%(key)s: %(value)s' % {
          'key': key,
          'value': value,
         } for (key, value) in items] + [_EOL]),
         action_id,
        )

    def get_timeout(self):
        """
        Gets the number of seconds to wait for a response from Asterisk for this request.
        """
        return self._timeout
        
    def process_response(self, response):
        """
        Provides an opportunity to parse, filter, or react to a response from Asterisk.
        
        This implementation just passes the response back to the caller as received.
        """
        return response

    def set_timeout(self, timeout):
        """
        Sets the `timeout` of this request to the specified number of seconds, with the default
        being 5. Indefinite waiting is not supported, but arbitrarily large values may be provided.

        Seconds may be specified in fractions. A request that has timed out may still be serviced by
        Asterisk, but no notification will be given. Changing the timeout value of the request
        object has no effect on issued requests.
        """
        self._timeout = timeout
        
class _SynchronisedSocket(object):
    """
    Provides a threadsafe conduit for communication with an Asterisk manager interface.
    """
    _asterisk_name = '<unknown>' #The name of the Asterisk server to which the socket is connected
    _asterisk_version = '<unknown>' # The version of the Asterisk server to which the socket is connected
    _connected = False #True while a connection is active
    _socket = None #The socket used to communicate with the Asterisk server
    _socket_file = None #The socket exposed as a file-like object
    _socket_lock = None #A lock used to prevent race conditions from affecting the Asterisk link
    
    def __init__(self, host, port=5038):
        """
        Establishes a connection to the specified Asterisk manager, setting session variables as
        needed.
        
        If the connection fails, `ManagerSocketException` is raised.
        """
        self._connect(host, port)
        self._socket_lock = threading.RLock()
        
    def __del__(self):
        """
        Ensure the resources are freed.
        """
        self.close()
        
    def close(self):
        """
        Release resources associated with this connection.
        """
        with self._socket_lock as lock:
            self._connected = False
            for closable in (self._socket_file, self._socket):
                try:
                    closable.close()
                except Exception:
                    pass #Can't do anything about it

    def get_asterisk_info(self):
        """
        Provides the name and version of Asterisk as a tuple of strings.
        """
        return (self._asterisk_name, self._asterisk_version)
        
    def is_connected(self):
        """
        Indicates whether the socket is connected.
        """
        with self._socket_lock as lock:
            return self._connected

    def read_message(self):
        """
        Reads a full message from Asterisk.

        The message read is returned as a `_Message` after being parsed. `None` is returned if
        the server didn't send a response, which nominally means that something is wrong.
        
        `ManagerSocketException` is raised if the connection is broken.
        """
        if not self.is_connected():
            return None
            
        #Bring some often-referenced values into the local namespace
        global _EOC
        global _EOC_INDICATOR
        global _EOL
        
        wait_for_marker = False #When true, the special string '--END COMMAND--' is used to end a message, rather than a CRLF
        while True: #Keep reading lines until a full message has been collected
            line = None
            with self._socket_lock as lock:
                try:
                    line = self._socket_file.readline()
                except socket.error as (errno, message):
                    self.close()
                    raise ManagerSocketException("Connection to Asterisk manager broken while reading data: [%(errno)i] %(error)s" % {
                     'errno': errno,
                     'error': message,
                    })

            response_lines = [] #Lines collected from Asterisk
            if line == _EOL and not wait_for_marker:
                if response_lines: #A full response has been collected
                    return response_lines
                continue #Asterisk is allowed to send empty lines before and after real data, so ignore them

            response_lines.append(line) #Add the line to the response

            #Test to see if this line implies that there needs to be an explicit end to the message
            if wait_for_marker:
                if line.startswith(_EOC): #The message is complete
                    return response_lines
            elif _EOC_INDICATOR.match(line): #Data that may contain the _EOL pattern is now legal
                wait_for_marker = True

    def send_message(self, message):
        """
        Locks the socket and writes the entire `message` into the stream.

        `ManagerSocketException` is raised if the connection is broken.
        """
        with self._socket_lock as lock:
            try:
                self._socket.write(message)
                self._socket.flush()
            except socket.error as (errno, reason):
                self.close()
                raise ManagerSocketException("Connection to Asterisk manager broken while writing data: [%(errno)i] %(error)s" % {
                 'errno': errno,
                 'error': message,
                })
                
    def _connect(self, host, port):
        """
        Establishes a connection to the specified Asterisk manager, then dissects its greeting.

        If the connection fails, `ManagerSocketException` is raised.
        """
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.connect((host, port))
            self._socket_file = self._socket.makefile()
        except socket.error as (errno, reason):
            raise ManagerSocketException("Connection to Asterisk manager could not be established: [%(errno)i] %(reason)s" % {
             'errno': errno,
             'reason': reason,
            })
        self._connected = True

        #Pop the greeting off the head of the pipe and set the version information
        try:
            line = self._socket_file.readline()
        except socket.error as (errno, reason):
            raise ManagerSocketException("Connection to Asterisk manager broken while reading greeting: [%(errno)i] %(reason)s" % {
             'errno': errno,
             'reason': reason,
            })
        else:
            if '/' in line:
                (self._asterisk_name, self._asterisk_version) = (token.strip() for token in line.split('/', 1))
                
                
class ManagerException(Exception):
    pass
    
class ManagerError(ManagerException):
    pass
    
class ManagerSocketException(ManagerException):
    pass


