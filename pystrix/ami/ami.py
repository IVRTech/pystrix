"""
pystrix.ami.ami
===============

Provides a class, `Manager`, that exposes an interface for communicating with
Asterisk via AMI.

For internal use, action superclasses and event/response generic classes are
also defined.

Legal
-----
This file is part of pystrix.
pystrix is free software; you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published
by the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU General Public License and
GNU Lesser General Public License along with this program. If not, see
<http://www.gnu.org/licenses/>.

(C) Ivrnet, inc., 2011

Authors:

- Neil Tallim <n.tallim@ivrnet.com>
"""
import collections
import Queue
import re
import socket
import threading
import time
import traceback
import types
import warnings

_EVENT_REGISTRY = {} #Meant to be internally managed only, this provides mappings from event-class-names to the classes, to enable type-mutation

_EOC = '--END COMMAND--' #A string used by Asterisk to mark the end of some of its responses.
_EOL = '\r\n' #Asterisk uses CRLF linebreaks to mark the ends of its lines.
_EOL_FAKE = ('\n\r\n', '\r\r\n') #End-of-line patterns that indicate data, not headers.

_EOC_INDICATOR = re.compile(r'Response:\s*Follows\s*$') #A regular expression that matches response headers that indicate the payload is attached

_Response = collections.namedtuple('Response', [
 'result', 'response', 'request', 'action_id', 'success', 'time',
]) #A container for responses to requests.

RESPONSE_GENERIC = 'Generic Response' #A header-value provided as a surrogate for unidentifiable responses
EVENT_GENERIC = 'Generic Event' #A header-value provided as a surrogate for unidentifiable unsolicited events

KEY_ACTION = 'Action' #The key used to identify an action being requested of Asterisk
KEY_ACTIONID = 'ActionID' #The key used to hold the ActionID of a request, for matching with responses
KEY_EVENT = 'Event' #The key used to hold the event-name of a response
KEY_RESPONSE = 'Response' #The key used to hold the event-name of a request

class Manager(object):
    _alive = True #False when this manager object is ready to be disposed of
    _action_id = None #The ActionID last sent to Asterisk
    _action_id_lock = None #A lock used to prevent race conditions on ActionIDs
    _connection = None #A connection to the Asterisk manager, realised as a `_SynchronisedSocket`
    _connection_lock = None #A means of preventing race conditions on the connection
    _debug = False #If True, development information is printed to console
    _event_callbacks = None #A dictionary of sets of event callbacks keyed by the string to match
    _event_callbacks_cls = None #A dictionary of tuples of classes and sets of event callbacks
    _event_callbacks_re = None #A dictionary of tuples of expressions and sets of event callbacks
    _event_callbacks_lock = None #A lock used to prevent race conditions on event callbacks
    _event_callbacks_thread = None #A thread used to process event callbacks
    _hostname = socket.gethostname() #The hostname of this system, used to prevent repeated calls through the C layer
    _message_reader = None #A thread that continuously collects messages from the Asterisk server
    _outstanding_requests = None #A set of ActionIDs sent to Asterisk, currently awaiting responses
    _logger = None #A logger that may be used to record warnings
    
    def __init__(self, debug=False, logger=None):
        """
        Sets up an environment for interacting with an Asterisk Management Interface.

        To proceed, register any necessary callbacks, then call `connect()`, then pass the core
        `Login` or `Challenge` request to `send_action()`.

        `logger` may be a logging.Logger object to use for logging problems in AMI threads. If not
        provided, problems will be emitted through the Python warnings interface.

        `debug` should only be turned on for library development.
        """
        self._debug = debug
        self._logger = logger
        
        self._action_id = 0
        self._action_id_lock = threading.Lock()

        self._connection_lock = threading.Lock()

        self._outstanding_requests = set()

        self._event_callbacks = {}
        self._event_callbacks_cls = {}
        self._event_callbacks_re = {}
        self._event_callbacks_lock = threading.Lock()
        self._event_callbacks_thread = threading.Thread(target=self._event_dispatcher)
        self._event_callbacks_thread.daemon = True
        self._event_callbacks_thread.start()
        
    def __del__(self):
        """
        Ensure that all resources are freed quickly upon garbage-collection.
        """
        self.close()

    def _event_dispatcher(self):
        """
        Intended to be run as an internal thread, this continuously invokes callbacks registered
        against Asterisk events and orphaned responses.

        If any callbacks throw exceptions, warnings are issued, but processing continues.
        """
        while self._alive:
            #Determine whether there's actually anything to read from
            message_reader = None
            with self._connection_lock as lock:
                message_reader = self._message_reader
            if not message_reader:
                time.sleep(0.02)
                continue
                
            sleep = True #If False, the next cycle begins without delay

            #Handle events
            try:
                event = message_reader.event_queue.get_nowait()
                sleep = False
            except Queue.Empty:
                pass
            else:
                event_name = event.name
                callbacks = set()
                with self._event_callbacks_lock as lock:
                    callbacks.update(self._event_callbacks.get(event_name) or ()) #Start with exact matches, if any
                    callbacks.update(self._event_callbacks.get('') or ()) #Add the universal handlers, if any
                    for (pattern, functions) in self._event_callbacks_re.items(): #Add all regular expression matches
                        if pattern.match(event_name):
                            callbacks.update(functions)
                    for (cls, functions) in self._event_callbacks_cls.items(): #Add all class matches
                        if type(event) == cls:
                            callbacks.update(functions)

                if self._logger:
                    self._logger.debug("Received event '%(name)s' with %(callbacks)i callbacks" % {
                     'name': event_name,
                     'callbacks': len(callbacks),
                    })
                for callback in callbacks:
                    try:
                        callback(event, self)
                    except Exception as e:
                        (self._logger and self._logger.error or warnings.warn)("Exception occurred while processing event callback: event='%(event)r'; handler='%(function)s' exception: %(error)s; trace:\n%(trace)s" % {
                         'event': event,
                         'function': str(callback),
                         'error': str(e),
                         'trace': traceback.format_exc(),
                        })

            #Handle orphaned responses
            try:
                response = message_reader.response_queue.get_nowait()
                sleep = False
            except Queue.Empty:
                pass
            else:
                callbacks = None
                with self._event_callbacks_lock as lock:
                    callbacks = self._event_callbacks.get(None) or () #Only select the explicit orphan-handlers
                    
                if self._logger:
                    self._logger.debug("Received orphaned response '%(name)s' with %(callbacks)i callbacks" % {
                     'name': response.name,
                     'callbacks': len(callbacks),
                    })
                for callback in callbacks:
                    try:
                        callback(response, self)
                    except Exception as e:
                        (self._logger and self._logger.error or warnings.warn)("Exception occurred while processing orphaned response handler: response=%(response)r; handler='%(function)s'; exception: %(error)s; trace:\n%(trace)s" % {
                         'response': response,
                         'function': str(callback),
                         'error': str(e),
                         'trace': traceback.format_exc(),
                        })
                        
            if sleep:
                time.sleep(0.02)
                
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

    def close(self):
        """
        Release all resources associated with this manager and ensure that all threads have stopped.
        
        This function is automatically invoked when garbage-collected.
        """
        self.disconnect()
        
        self._alive = False
        self._event_callbacks_thread.join()
        
    def connect(self, host, port=5038, timeout=5):
        """
        Establishes a connection to the specified Asterisk manager, closing any existing connection
        first.

        `timeout` specifies the number of seconds to allow Asterisk to go between producing lines of
        a response; it differs from the timeout that may be set on individual requests and exists
        primarily to avoid having a thread stay active forever, to allow for clean shutdowns.
        
        If the connection fails, `ManagerSocketError` is raised.
        """
        self.disconnect()
        with self._connection_lock as lock:
            self._connection = _SynchronisedSocket(host=host, port=port, timeout=timeout)
            
            self._message_reader = _MessageReader(self)
            self._message_reader.start()
            
    def disconnect(self):
        """
        Gracefully closes a connection to the Asterisk manager.
        
        If not connected, this is a no-op.
        """
        with self._connection_lock as lock:
            if self._connection: #Close the old connection, if any.
                self._connection.close()
                self._connection = None
            self._outstanding_requests.clear()
            
            if self._message_reader: #Kill, but don't drop, the reader, since it may have unprocessed data
                self._message_reader.kill()

    def get_asterisk_info(self):
        """
        Provides the name and version of Asterisk as a tuple of strings.

        If not connected, `None` is returned.
        """
        with self._connection_lock as lock:
            return (self.is_connected and self._connection.get_asterisk_info()) or None

    def get_connection(self):
        """
        Returns the current `_SynchronisedSocket` in use by the active connection, or `None` if no
        manager is attached.
        
        This function is exposed for debugging purposes and should not be used by normal
        applications that do not have very special reasons for interacting with Asterisk directly.
        """
        return self._connection
        
    def is_connected(self):
        """
        Indicates whether the manager is connected.
        """
        with self._connection_lock as lock:
            return bool(self._connection and self._connection.is_connected())

    def monitor_connection(self, interval=2.5):
        """
        Spawns a thread that watches the AMI connection to indicate a disruption when the connection
        goes down.
        
        `interval` is the number of seconds to wait between automated Pings to see if Asterisk
        is still alive; defaults to 2.5.
        """
        def _monitor_connection():
            import core
            while self.is_connected():
                self.send_action(core.Ping())
                time.sleep(interval)
                
        monitor = threading.Thread(target=_monitor_connection, name='pystrix-ami-monitor')
        monitor.daemon = True
        monitor.start()

    def register_callback(self, event, function):
        """
        Registers an Asterisk event with the name `event`, which may be a string for exact matches,
        a compiled regular expression to be matched with the 'match' function against the name, or
        a reference to the specific event class.

        `function` is the callable to be invoked with the event `_Message` and a reference to the
        manager object as two positional arguments.

        Registering the same function twice for the same event or two events that have overlapping
        regular expressions is effectively a no-op. When the callbacks are invoked, each function
        will be called at most once per event.

        Registering against the special event `None` will cause the given function to receive all
        responses not associated with a request, which normally shouldn't exist, but may be observed
        in practice. Events will not be included.

        Registering against the emptry string will cause the given function to receive every event,
        suitable for logging purposes.

        Callbacks are not guaranteed to be executed in any particular order.
        """
        with self._event_callbacks_lock as lock:
            callbacks_dict = self._event_callbacks
            if not event is None and not isinstance(event, types.StringType): #Regular expression or class
                if isinstance(event, (types.ClassType, types.TypeType)):
                    callbacks_dict = self._event_callbacks_cls
                else:
                    callbacks_dict = self._event_callbacks_re
            callbacks = callbacks_dict.get(event, set())
            callbacks.add(function)
            callbacks_dict[event] = callbacks
            
    def send_action(self, request, action_id=None, **kwargs):
        """
        Sends a command, contained in `request`, a `_Request`, to the Asterisk manager, referred to
        interchangeably as "actions". Any additional keyword arguments are added directly into the
        request command as though they were native headers, though the original object is
        unaffected.
        
        `action_id` is an optional Asterisk ActionID to use; if unspecified, whatever is in the
        request, keyed at 'ActionID', is used with the output of `id_generator` being a fallback.
        
        Asterisk's response is returned as a named tuple of the following form, or `None` if the
        request timed out:
        
        - result: The processed response from Asterisk, nominally the same as `response`; see the
          specific `_Request` subclass for details in case it provides additional processing
        - response: The formatted, but unprocessed, response from Asterisk
        - request: The `_Request` object supplied when the request was placed; not a copy of the
          original
        - action_id: The 'ActionID' sent with this request
        - success: A boolean value indicating whether the request was met with success
        - time: The number of seconds, as a float, that the request took to be serviced
        
        For forward-compatibility reasons, elements of the tuple should be accessed by name, rather
        than by index.
        
        Raises `ManagerError` if the manager is not connected.

        Raises `ManagerSocketError` if the socket is broken during transmission.

        This function is thread-safe.
        """
        if not self.is_connected():
            raise ManagerError("Not connected to an Asterisk manager")
            
        with self._connection_lock as lock:
            (command, action_id) = request.build_request(action_id and str(action_id), self._get_host_action_id, **kwargs)
            self._connection.send_message(command)
            self._outstanding_requests.add(action_id)

        start_time = time.time()
        timeout = start_time + request.timeout
        while time.time() < timeout:
            with self._connection_lock as lock:
                response = self._message_reader.get_response(action_id)
                if response:
                    processed_response = request.process_response(response)
                    return _Response(
                     processed_response,
                     response,
                     request,
                     action_id,
                     hasattr(processed_response, 'success') and processed_response.success,
                     time.time() - start_time
                    )
            time.sleep(0.05)
        self._serve_outstanding_request(action_id) #Get the ActionID out of circulation
        return None

    def _serve_outstanding_request(self, action_id):
        """
        Returns `True` if the given `action_id` is waiting to be served and removes it from the
        local set as a side-effect.
        """
        with self._connection_lock as lock:
            served = action_id in self._outstanding_requests
            if served:
                self._outstanding_requests.discard(action_id)
            return served
            
    def unregister_callback(self, event, function):
        """
        Unregisters an Asterisk event with the name `event`, which may be a string for exact
        matches, a compiled regular expression to be matched with the 'match' function against the
        name, or a reference to the event's class. If a regular expression, it must be the same
        object passed in to register the event.
        
        `function` is the callable previously associated with the event. It must be the same object.

        If the same function was registered under two different event qualifiers, only the one being
        deregistered will be removed.
        """
        with self._event_callbacks_lock as lock:
            callbacks_dict = self._event_callbacks
            if not event is None and not isinstance(event, types.StringType): #Regular expression or class
                if isinstance(event, (types.ClassType, types.TypeType)):
                    callbacks_dict = self._event_callbacks_cls
                else:
                    callbacks_dict = self._event_callbacks_re
            callbacks = callbacks_dict.get(event)
            if callbacks:
                callbacks.discard(function)
                
class _Message(dict):
    """
    The common base-class for both replies and events, this is any structured response received
    from Asterisk.

    All message headers are exposed as dictionary items on this object directly.
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
        self.headers = self #For simplicity's sake, the 'headers' property is a recursive reference to this object
        self.raw = response
        self._parse(response)

        #Apply some tests to see if Asterisk sent back a malformed response and try to make it
        #salvagable. This typically only happens with specific events, so applications can deal
        #with it more effectively than the processing core.
        if KEY_EVENT not in self and KEY_RESPONSE not in self:
            if self.has_header(KEY_ACTIONID): #If 'ActionID' is present, it's a response to an action.
                self.headers[KEY_RESPONSE] = RESPONSE_GENERIC
            else: #It's an unsolicited event
                self.headers[KEY_EVENT] = EVENT_GENERIC
                
    def __eq__(self, o):
        """
        A convenience qualifier for decision-blocks to allow the message to be compared to strings for
        readability purposes.
        """
        if isinstance(o, types.StringType):
            return self.name == o
        return dict.__eq__(self, o)
        
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

    @property
    def name(self):
        """
        Provides the name of the event or response.
        """
        return self.get(KEY_EVENT) or self.get(KEY_RESPONSE)
        
    def process(self):
        """
        Provides a tuple containing a copy of all headers as a dictionary and a copy of all response
        lines. The value of this data is negligible, but subclasses may apply further processing,
        replacing the values of headers with Python types or making the data easier to work with.
        """
        return (self.copy(), self.data[:])
        
class _MessageReader(threading.Thread):
    event_queue = None #A queue containing unsolicited events received from Asterisk
    response_queue = None #A queue containing orphaned or unparented responses from Asterisk
    _alive = True #False when this thread has been killed
    _manager = None #A reference to the manager instance that serves as the parent of this thread
    _served_requests = None #A dictionary of responses from Asterisk, keyed by ActionID
    _served_requests_lock = None #A means of preventing race conditions from affecting the served-request set

    def __init__(self, manager):
        threading.Thread.__init__(self)
        self.daemon = True
        self.name = 'pystrix-ami-message-reader'
        
        self._manager = manager

        self.event_queue = Queue.Queue()
        self.response_queue = Queue.Queue()
        self._served_requests = {}
        self._served_requests_lock = threading.Lock()

    def kill(self):
        self._alive = False

    def get_response(self, action_id):
        """
        Returns the response from Asterisk associated with the given `action_id`, if any.
        """
        with self._served_requests_lock as lock:
            response = self._served_requests.get(action_id)
            if not response is None:
                del self._served_requests[action_id]
            return response
            
    def run(self):
        """
        Continuously reads messages from the Asterisk server, placing them in the appropriate queue.

        Stops running when the connection dies or when explicitly told to stop.
        """
        global _EVENT_REGISTRY
        global KEY_ACTIONID
        socket = self._manager.get_connection()
        
        while self._alive:
            try:
                message = socket.read_message()
                if not message:
                    continue
            except ManagerSocketError:
                break #Nothing can be reported, but the socket died, so there's no point in running
            else:
                action_id = message.get(KEY_ACTIONID)
                if not action_id is None and self._manager._serve_outstanding_request(action_id):
                    with self._served_requests_lock as lock:
                        if not action_id in self._served_requests: #If there's already an associated response, treat this one as orphaned to avoid data-loss
                            self._served_requests[action_id] = message
                        else:
                            self.response_queue.put(message)
                elif KEY_EVENT in message:
                    #See if the event has a corresponding subclass and mutate it if it does
                    event_class = _EVENT_REGISTRY.get(message.name)
                    if event_class:
                        message.__class__ = event_class
                    elif self._manager._debug:
                        print("Unknown event received: " + repr(message))
                        
                    self.event_queue.put(message)
                else:
                    self.response_queue.put(message)
                    
class _Request(dict):
    """
    Provides a generic container for assembling AMI requests, the basis of all actions.
    
    Subclasses may override `__init__` and define any additional behaviours they may need, as well
    as override `process_response()` to specially format the data to be returned after a request
    has been served.
    """
    timeout = 5 #The number of seconds to wait before considering this request timed out; may be a float
    
    def __init__(self, action):
        """
        `action` is the type of action being requested of the Asterisk server.
        """
        self['Action'] = action
        
    def build_request(self, action_id, id_generator, **kwargs):
        """
        Returns a string formatted for transmission to Asterisk to place a request and the action ID
        associated with the request.
        
        `action_id` is the Asterisk ActionID to use, or None to use whatever is in the request, if
        anything, or the output of `id_generator` if not.
        
        `id_generator` is a function that generates an Asterisk ActionID.
        
        `**kwargs` is a dictionary of additional arguments that may be passed along with the request
        at submission time.
        
        The 'Action' line is always first.
        """
        items = [(KEY_ACTION, self[KEY_ACTION])]
        for (key, value) in [(k, v) for (k, v) in self.items() if not k in (KEY_ACTION, KEY_ACTIONID)] + kwargs.items():
            key = str(key)
            if type(value) in (tuple, list, set, frozenset):
                for val in value:
                    items.append((key, str(val)))
            else:
                items.append((key, str(value)))

        if action_id or not KEY_ACTIONID in self: #Replace or add an ActionID, if necessary
            if not action_id:
                action_id = str(id_generator())
            elif KEY_ACTIONID in self:
                action_id = self[KEY_ACTIONID]
            items.append((KEY_ACTIONID, action_id))
            
        return (
         _EOL.join(['%(key)s: %(value)s' % {
          'key': key,
          'value': value,
         } for (key, value) in items] + [_EOL]),
         action_id,
        )

    def process_response(self, response):
        """
        Provides an opportunity to parse, filter, or react to a response from Asterisk.
        
        This implementation just passes the response back to the caller as received, adding a new
        'success' attribute on the response object with a boolean value.
        """
        response.success = response.get('Response') in ('Success', 'Follows')
        return response
        
class _SynchronisedSocket(object):
    """
    Provides a threadsafe conduit for communication with an Asterisk manager interface.
    """
    _asterisk_name = '<unknown>' #The name of the Asterisk server to which the socket is connected
    _asterisk_version = '<unknown>' # The version of the Asterisk server to which the socket is connected
    _connected = False #True while a connection is active
    _socket = None #The socket used to communicate with the Asterisk server
    _socket_file = None #The socket exposed as a file-like object
    _socket_read_lock = None #A lock used to prevent race conditions from affecting the Asterisk link
    _socket_write_lock = None #A lock used to prevent race conditions from affecting the Asterisk link
    _timeout = None #The number of seconds to wait before considering communications with the Asterisk server timed out
    
    def __init__(self, host, port=5038, timeout=5):
        """
        Establishes a connection to the specified Asterisk manager, setting session variables as
        needed.

        `timeout` is the number of seconds to wait before considering the Asterisk server
        unresponsive.
        
        If the connection fails, `ManagerSocketError` is raised.
        """
        self._timeout = timeout
        self._connect(host, port)
        self._socket_read_lock = threading.Lock()
        self._socket_write_lock = threading.Lock()
        
    def __del__(self):
        """
        Ensure the resources are freed.
        """
        self.close()
        
    def close(self):
        """
        Release resources associated with this connection.
        """
        with self._socket_write_lock as write_lock:
            self._close()
            
    def _close(self):
        """
        Performs the actual closing; needed to avoid a deadlock.
        """
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
        with self._socket_write_lock as lock:
            return self._connected

    def read_message(self):
        """
        Reads a full message from Asterisk.

        The message read is returned as a `_Message` after being parsed. Or `None` if a timeout
        occurred while waiting for a full message.
        
        `ManagerSocketError` is raised if the connection is broken.
        """
        if not self.is_connected():
            raise ManagerSocketError("Not connected to Asterisk server")
            
        #Bring some often-referenced values into the local namespace
        global _EOC
        global _EOC_INDICATOR
        global _EOL
        
        wait_for_marker = False #When true, the special string '--END COMMAND--' is used to end a message, rather than a CRLF
        response_lines = [] #Lines collected from Asterisk
        while True: #Keep reading lines until a full message has been collected
            line = None
            with self._socket_read_lock as lock:
                try:
                    line = self._socket_file.readline()
                except socket.timeout:
                    return None
                except socket.error as (errno, message):
                    self._close()
                    raise ManagerSocketError("Connection to Asterisk manager broken while reading data: [%(errno)i] %(error)s" % {
                     'errno': errno,
                     'error': message,
                    })
                except AttributeError:
                    raise ManagerSocketError("Local socket no longer defined, caused by system shutdown and blocking I/O")

            if line == _EOL and not wait_for_marker:
                if response_lines: #A full response has been collected
                    return _Message(response_lines)
                continue #Asterisk is allowed to send empty lines before and after real data, so ignore them

            #Test to see if this line is related to the requirements for an explicit end to the message
            if wait_for_marker:
                if line.startswith(_EOC): #The message is complete
                    return _Message(response_lines)
            elif _EOC_INDICATOR.match(line): #Data that may contain the _EOL pattern is now legal
                wait_for_marker = True
                
            response_lines.append(line) #Add the line to the response
            
    def send_message(self, message):
        """
        Locks the socket and writes the entire `message` into the stream.

        `ManagerSocketError` is raised if the connection is broken.
        """
        if not self.is_connected():
            raise ManagerSocketError("Not connected to Asterisk server")
            
        with self._socket_write_lock as lock:
            try:
                self._socket.sendall(message)
            except socket.error as (errno, reason):
                self._close()
                raise ManagerSocketError("Connection to Asterisk manager broken while writing data: [%(errno)i] %(error)s" % {
                 'errno': errno,
                 'error': message,
                })
                
    def _connect(self, host, port):
        """
        Establishes a connection to the specified Asterisk manager, then dissects its greeting.

        If the connection fails, `ManagerSocketError` is raised.
        """
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(self._timeout)
            self._socket.connect((host, port))
            self._socket_file = self._socket.makefile()
        except socket.error as (errno, reason):
            raise ManagerSocketError("Connection to Asterisk manager could not be established: [%(errno)i] %(reason)s" % {
             'errno': errno,
             'reason': reason,
            })
        self._connected = True

        #Pop the greeting off the head of the pipe and set the version information
        try:
            line = self._socket_file.readline()
        except socket.error as (errno, reason):
            raise ManagerSocketError("Connection to Asterisk manager broken while reading greeting: [%(errno)i] %(reason)s" % {
             'errno': errno,
             'reason': reason,
            })
        else:
            if '/' in line:
                (self._asterisk_name, self._asterisk_version) = (token.strip() for token in line.split('/', 1))
                

#Exceptions
###############################################################################
class Error(Exception):
    """
    The base exception from which all errors native to this module inherit.
    """
    
class ManagerError(Error):
    """
    Represents a generic error involving the Asterisk manager.
    """
    
class ManagerSocketError(Error):
    """
    Represents a generic error involving the Asterisk connection.
    """

