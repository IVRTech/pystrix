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
(C) Neil Tallim <flan@uguu.ca>, 2014

Authors:

- Neil Tallim <flan@uguu.ca>
"""
import abc
import collections
import Queue
import random
import re
import socket
import threading
import time
import traceback
import types
import warnings

_EVENT_REGISTRY = {} #Meant to be internally managed only, this provides mappings from event-class-names to the classes, to enable type-mutation
_EVENT_REGISTRY_REV = {} #Provides the friendly names of events as strings, keyed by class object

_EOC = '--END COMMAND--' #A string used by Asterisk to mark the end of some of its responses.
_EOL = '\r\n' #Asterisk uses CRLF linebreaks to mark the ends of its lines.
_EOL_FAKE = ('\n\r\n', '\r\r\n') #End-of-line patterns that indicate data, not headers.

_EOC_INDICATOR = re.compile(r'Response:\s*Follows\s*$') #A regular expression that matches response headers that indicate the payload is attached

_Response = collections.namedtuple('Response', [
 'result', 'response', 'request', 'action_id', 'success', 'time', 'events', 'events_timeout',
]) #A container for responses to requests.

RESPONSE_GENERIC = 'Generic Response' #A header-value provided as a surrogate for unidentifiable responses
EVENT_GENERIC = 'Generic Event' #A header-value provided as a surrogate for unidentifiable unsolicited events

KEY_ACTION = 'Action' #The key used to identify an action being requested of Asterisk
KEY_ACTIONID = 'ActionID' #The key used to hold the ActionID of a request, for matching with responses
KEY_EVENT = 'Event' #The key used to hold the event-name of a response
KEY_RESPONSE = 'Response' #The key used to hold the event-name of a request

_CALLBACK_TYPE_REFERENCE = 1 #Identifies a callback-definition as an event-reference
_CALLBACK_TYPE_UNIVERSAL = 2 #Identifies a callback-definition as universal
_CALLBACK_TYPE_ORPHANED = 3 #Identifies a callback-definition for orphaned responses

def _format_socket_error(exception):
    """
    Ensures that, regardless of the form that a `socket.error` takes, it is
    formatted into a readable string.
    
    @param str exception: The `socket.error` to be formatted.
    @return str: A nicely formatted summary of the exception.
    """
    try:
        (errno, message) = exception
        return "[%(errno)i] %(error)s" % {
         'errno': errno,
         'error': message,
        }
    except Exception:
        return str(exception)
        
class Manager(object):
    _alive = True #False when this manager object is ready to be disposed of
    _action_id = None #The ActionID last sent to Asterisk
    _action_id_random_token = None #A randomly generated token, used to help avoid conflicts when multiple AMI connections are in use
    _action_id_lock = None #A lock used to prevent race conditions on ActionIDs
    _connection = None #A connection to the Asterisk manager, realised as a `_SynchronisedSocket`
    _connection_lock = None #A means of preventing race conditions on the connection
    _debug = False #If True, development information is emitted along the normal logging stream
    _event_aggregates = None #A list of aggregates awaiting fulfillment
    _event_aggregates_lock = None #A lock used to prevent race conditions on event aggregation
    _event_aggregates_timeout = None #The amount of time to wait before considering an aggregate timed-out
    _event_callbacks = None #A list of tuples of type-identifiers, match-criteria, and callback functions
    _event_callbacks_lock = None #A lock used to prevent race conditions on event callbacks
    _event_callbacks_thread = None #A thread used to process event callbacks
    _hostname = socket.gethostname() #The hostname of this system, used to prevent repeated calls through the C layer
    _message_reader = None #A thread that continuously collects messages from the Asterisk server
    _orphaned_response_timeout = None #The number of seconds to hold on to request-responses before considering them to be timed-out
    _outstanding_requests = None #A dictionary of ActionIDs sent to Asterisk, currently awaiting responses; values are a tuple of (events, pending_finalisers), if synchronous, and None otherwise
    _logger = None #A logger that may be used to record warnings
    
    def __init__(self, debug=False, logger=None, aggregate_timeout=5, orphaned_response_timeout=5):
        """
        Sets up an environment for interacting with an Asterisk Management Interface.

        To proceed, register any necessary callbacks, then call `connect()`, then pass the core
        `Login` or `Challenge` request to `send_action()`.

        `logger` may be a logging.Logger object to use for logging problems in AMI threads. If not
        provided, problems will be emitted through the Python warnings interface.
        
        `aggregate_timeout` is the number of seconds to wait for aggregates to be fully assembled
        before considering them timed-out.
        
        `orphaned_response_timeout` is the number of seconds to wait for responses to requests to be
        collected before considering them timed out. (This should never happen, but a guarantee must
        be made that the buffer can stay clean)

        `debug` should only be turned on for library development.
        """
        self._debug = debug
        self._logger = logger
        
        self._action_id = 0
        action_id_random_token = []
        for i in range(5):
            if random.random() < 0.25: #Append a digit
                action_id_random_token.append(chr(random.randint(48, 57)))
            else:
                if random.random() < 0.5: #Append a upper-case letter
                    action_id_random_token.append(chr(random.randint(65, 90)))
                else: #Append a lower-case letter
                    action_id_random_token.append(chr(random.randint(97, 122)))
        self._action_id_random_token = ''.join(action_id_random_token)
        self._action_id_lock = threading.Lock()

        self._connection_lock = threading.Lock()

        self._outstanding_requests = {}
        self._orphaned_response_timeout = orphaned_response_timeout

        self._event_aggregates = []
        self._event_aggregates_lock = threading.Lock()
        self._event_aggregates_timeout = aggregate_timeout

        self._event_callbacks = []
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
        event_aggregates_complete = collections.deque()
        event_aggregate_cycle = 0
        while self._alive:
            #Determine whether there's actually anything to read from
            message_reader = None
            with self._connection_lock:
                message_reader = self._message_reader
            if not message_reader:
                time.sleep(0.02)
                continue
                
            #Emit events, sleeping if nothing was sent during this cycle
            sleep = not self._event_dispatcher_events(message_reader, event_aggregates_complete)
            sleep = not self._event_dispatcher_orphaned_responses(message_reader) and sleep
            if sleep:
                time.sleep(0.02)
                #Clean up old aggregates about once every second
                if event_aggregate_cycle == 0:
                    event_aggregate_cycle = 50
                    current_time = time.time()
                    with self._event_aggregates_lock:
                        for (i, aggregate) in enumerate(self._event_aggregates):
                            if aggregate[0] <= current_time: #Expired
                                del self._event_aggregates[i]
                                (self._logger and self._logger.warn or warnings.warn)("Aggregate '%(name)s' for action-ID '%(action-id)s' timed out before all events were gathered" % {
                                 'name': aggregate[1].name,
                                 'action-id': aggregate[1].action_id,
                                })
                else:
                    event_aggregate_cycle -= 1
                    
    def _event_dispatcher_events(self, message_reader, event_aggregates_complete):
        """
        Pulls events from the message-reader, then sends them to all registered callbacks. The
        returned value indicates whether anything was done during the current cycle.
        
        If aggregates are in use, they are assembled and broadcast here, as well.
        """
        event = None
        if event_aggregates_complete: #Check for completed aggregates first
            event = event_aggregates_complete.popleft()
        else:
            try:
                event = message_reader.event_queue.get_nowait()
            except Queue.Empty:
                pass
            else:
                #Bind it to a request, if appropriate
                if self._process_outstanding_request_event(event):
                    return #Synchronous requests do not generate asynchronous events
                    
                #Evaluate the new event against all pending aggregates
                with self._event_aggregates_lock:
                    for (i, (_, aggregate)) in enumerate(self._event_aggregates):
                        aggregation_result = aggregate.evaluate_event(event)
                        if aggregation_result is None: #Not relevant
                            continue
                        else:
                            if aggregation_result: #Finalised
                                event_aggregates_complete.append(aggregate)
                                del self._event_aggregates[i]
                            break
        
        if event:
            event_name = event.name
            callbacks = None
            global _CALLBACK_TYPE_REFERENCE
            global _CALLBACK_TYPE_UNIVERSAL
            with self._event_callbacks_lock:
                callbacks = [c for (t, e, c) in self._event_callbacks if (t == _CALLBACK_TYPE_REFERENCE and event_name == e) or (t == _CALLBACK_TYPE_UNIVERSAL)]
                
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
                    
            return True
        return False
        
    def _event_dispatcher_orphaned_responses(self, message_reader):
        """
        Pulls orphaned responses from the message-reader, then sends them to orhpan-handler
        callbacks. The returned value indicates whether anything was done during the current cycle.
        """
        response = None
        try:
            response = message_reader.response_queue.get_nowait()
        except Queue.Empty:
            pass
            
        if response:
            callbacks = None
            global _CALLBACK_TYPE_ORPHANED
            with self._event_callbacks_lock:
                callbacks = [c for (t, e, c) in self._event_callbacks if t == _CALLBACK_TYPE_ORPHANED]
                
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
                    
            return True
        return False
        
    def _get_action_id(self):
        """
        Produces a session-unique int, suitable for passing to Asterisk as an ActionID.
        """
        with self._action_id_lock:
            self._action_id += 1
            if self._action_id > 0xFFFFFFFF:
                self._action_id = 1
            return self._action_id

    def _get_host_action_id(self):
        """
        Generates a host-qualified, random-token-augmented ActionID as a string, for greater
        identifiability.
        """
        return '%(hostname)s-%(random)s-%(id)08x' % {
         'hostname': self._hostname,
         'random': self._action_id_random_token,
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
        with self._connection_lock:
            self._connection = _SynchronisedSocket(host=host, port=port, timeout=timeout)
            
            self._message_reader = _MessageReader(self, self._orphaned_response_timeout)
            self._message_reader.start()
            
    def disconnect(self):
        """
        Gracefully closes a connection to the Asterisk manager.
        
        If not connected, this is a no-op.
        """
        with self._connection_lock:
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
        with self._connection_lock:
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
        with self._connection_lock:
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
        
    def _compile_callback_definition(self, event, function):
        """
        Provides a triple of type, match-criteria, and callback for the given event-identifier and
        function.
        """
        if isinstance(event, types.StringTypes):
            if not event:
                return (_CALLBACK_TYPE_UNIVERSAL, None, function)
            return (_CALLBACK_TYPE_REFERENCE, event, function)
        elif isinstance(event, types.TypeType):
            event_name = _EVENT_REGISTRY_REV.get(event)
            if event_name:
                return (_CALLBACK_TYPE_REFERENCE, event_name, function)
        elif event is None:
            return (_CALLBACK_TYPE_ORPHANED, None, function)
            
        raise ValueError("Attempted to build callback definition using an unsupported identifier")
        
    def register_callback(self, event, function):
        """
        Registers a callback for an Asterisk event identified by `event`, which may be a string for
        exact matches or a reference to the specific event class.

        `function` is the callable to be invoked whenever a matching `_Event` is emitted; it must
        accept the positional arguments "event" and "manager", with "event" being the `_Event`
        object and "manager" being a reference to generating instance of this class.
        
        Registering the same function twice for the same event will unset the first callback,
        placing the new one at the end of the list.

        Registering against the special event `None` will cause the given function to receive all
        responses not associated with a request, which normally shouldn't exist, but may be observed
        in practice. Events will not be included.

        Registering against the empty string will cause the given function to receive every event,
        suitable for logging purposes.

        Callbacks are executed in the order in which they were registered.
        """
        callback_definition = self._compile_callback_definition(event, function)
        self._unregister_callback(callback_definition)
        with self._event_callbacks_lock:
            self._event_callbacks.append(callback_definition)
            
    def _unregister_callback(self, definition):
        """
        Removes the indicated callback from the list of those registered, if a match is found.
        
        The value returned indicates whether anything was removed.
        """
        with self._event_callbacks_lock:
            for (i, d) in enumerate(self._event_callbacks):
                if definition == d:
                    del self._event_callbacks[i]
                    return True
        return False
        
    def unregister_callback(self, event, function):
        """
        Unregisters a previously bound callback.
        
        A boolean value is returned, indicating whether anything was removed.
        """
        callback_definition = self._compile_callback_definition(event, function)
        return self._unregister_callback(callback_definition)
        
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
        - events: A dictionary containing related events if the request is synchronous or None otherwise
        - events_timeout: Whether the request timed out while waiting for events
        
        For forward-compatibility reasons, elements of the tuple should be accessed by name, rather
        than by index.
        
        Raises `ManagerError` if the manager is not connected.

        Raises `ManagerSocketError` if the socket is broken during transmission.

        This function is thread-safe.
        """
        if not self.is_connected():
            raise ManagerError("Not connected to an Asterisk manager")
            
        (command, action_id) = request.build_request(action_id and str(action_id), self._get_host_action_id, **kwargs)
        events = self._add_outstanding_request(action_id, request)
        with self._connection_lock:
            self._connection.send_message(command)
            
        if request.aggregate and not request.synchronous: #Set up aggregate-event generation
            with self._event_aggregates_lock:
                for aggregate_class in request.get_aggregate_classes():
                    self._event_aggregates.append((time.time() + self._event_aggregates_timeout, aggregate_class(action_id)))
                    if self._debug:
                        (self._logger and self._logger.debug or warnings.warn)("Started building aggregate-event '%(event)s' for action-ID '%(action-id)s'" % {
                         'event': _EVENT_REGISTRY_REV.get(aggregate_class),
                         'action-id': action_id,
                        })

        start_time = time.time()
        timeout = start_time + request.timeout
        response = processed_response = success = None
        events_timeout = False
        while time.time() < timeout:
            if not response: #If blocking for event synchronisation, don't bother polling for the already-received response
                with self._connection_lock:
                    response = self._message_reader.get_response(action_id)
                if response:
                    processed_response = request.process_response(response)
                    success = hasattr(processed_response, 'success') and processed_response.success
                    if not request.synchronous or not success:
                        break #No events to watch for
            else: #Synchronous processing
                if self._check_outstanding_request_complete(action_id): #Not waiting for any more events
                    break
            time.sleep(0.05)
        else: #Timed out
            if request.synchronous:
                events_timeout = True
                (self._logger and self._logger.warn or warnings.warn)("Timed out while collecting events for synchronised action-ID '%(action-id)s'" % {
                 'action-id': action_id,
                })
                
        self._serve_outstanding_request(action_id) #Get the ActionID out of circulation
        if response:
            return _Response(
                processed_response,
                response,
                request,
                action_id,
                success,
                time.time() - start_time,
                events,
                events_timeout
            )
        else:
            (self._logger and self._logger.warn or warnings.warn)("Timed out while waiting for response for action-ID '%(action-id)s'" % {
             'action-id': action_id,
            })
            return None

    def _add_outstanding_request(self, action_id, request):
        """
        Beings tracking the given `action_id` to synchronise communication with Asterisk.
        
        If full event-synchronisation is requested, that's set up here, too.
        
        The value returned is the events-map, if one was set up.
        """
        with self._connection_lock:
            if request.synchronous:
                global _EVENT_REGISTRY_REV
                events = {}
                (uniques, lists, finalisers) = request.get_synchronous_classes()
                for c in uniques:
                    events[c] = events[_EVENT_REGISTRY_REV.get(c)] = None
                for c in lists:
                    events[c] = events[_EVENT_REGISTRY_REV.get(c)] = []
                for c in finalisers:
                    events[c] = events[_EVENT_REGISTRY_REV.get(c)] = None
                    
                self._outstanding_requests[action_id] = (events, set(finalisers))
                return events
            else:
                self._outstanding_requests[action_id] = None
                return None
                
    def _check_outstanding_request_complete(self, action_id):
        """
        Yields a boolean value that indicates whether the indicated request has been fully served,
        in terms of having received all expected requests if synchronised.
        
        If not synchronised or if the request isn't tracked, the value returned is True.
        """
        with self._connection_lock:
            status = self._outstanding_requests.get(action_id)
            if not status: #Undefined or not synchronous
                return True
            return not status[1] #True if all finalisers have been received
            
    def _process_outstanding_request_event(self, event):
        """
        Checks the event against pending requests and adds it to the appropriate event-list, if one
        exists, updating pending finalisers as needed.
        
        The value returned indicates whether the event was bound to an action.
        """
        with self._connection_lock:
            status = self._outstanding_requests.get(event.action_id)
            if status: #It's being tracked
                event_type = type(event)
                
                status[1].discard(event_type) #Mark it as received if it's a finaliser
                
                value = status[0].get(event_type)
                if type(value) is list: #If it's part of a list-type, add it to the collection
                    value.append(event) #No need to add it to both the named and class-type value, since they share the same list
                else: #Set it as the relevant entry, for both the class-def and named keys
                    status[0][event_type] = status[0][_EVENT_REGISTRY_REV.get(event_type)] = event
                return True
        return False

    def _serve_outstanding_request(self, action_id):
        """
        Returns `True` if the given `action_id` is waiting to be served and removes it from the
        local dictionary as a side-effect.
        """
        with self._connection_lock:
            served = action_id in self._outstanding_requests
            if served:
                del self._outstanding_requests[action_id]
            return served

class _MessageTemplate(object):
    """
    An abstract base-class for all message-types, including aggregates.
    """
    __meta__ = abc.ABCMeta
    
    def __eq__(self, o):
        """
        A convenience qualifier for decision-blocks to allow the message to be compared to strings for
        readability purposes.
        """
        if isinstance(o, types.StringType):
            return self.name == o
        return dict.__eq__(self, o)
        
    @property
    def action_id(self):
        """
        Provides the action-ID associated with the message, if any.
        """
        raise NotImplementedError("Action-IDs must be implemented by subclasses")
        
    @property
    def name(self):
        """
        Provides the name of the message.
        """
        raise NotImplementedError("Names must be implemented by subclasses")
        
class _Aggregate(_MessageTemplate, dict):
    """
    Provides, as a dictionary, access to all events that make up the aggregation, keyed by
    event-class. Repeatable event-types are exposed as lists, while others are direct references to
    the event itself.
    """
    _name = None #The name of the aggregate-type
    _action_id = None #The action-ID associated with the aggregate, if any
    _valid = True #Indicates whether the aggregate's contents are consistent with Asterisk's protocol
    _error_message = None #A string that explains why validation failed, if it failed
    
    _aggregation_members = () #A tuple containing all classes that can be members of this aggregation
    _aggregation_finalisers = () #A tuplecontaining all class that must be received for the aggregation to be complete
    _pending_finalisers = None #All finalisers yet to be received
    
    def __init__(self, action_id):
        """
        Associates the aggregate with an action-ID.
        """
        self._action_id = action_id
        self._pending_finalisers = set(self._aggregation_finalisers)
        
        global _EVENT_REGISTRY_REV
        for c in self._aggregation_members:
            self[c] = self[_EVENT_REGISTRY_REV.get(c)] = []
        for c in self._aggregation_finalisers:
            self[c] = self[_EVENT_REGISTRY_REV.get(c)] = None
            
    def _evaluate_action_id(self, event):
        """
        Indicates whether the aggregate's action-ID matches that of the event.
        """
        return self._action_id == event.action_id
        
    def _aggregate(self, event):
        """
        Adds the `event` to this aggregate, if appropriate, inheriting properties as necessary.
        
        The value returned indicates whether `event` was added.
        """
        if self._evaluate_action_id(event):
            self[type(event)].append(event) #Lists are shared between class-object and string elements
            return True
        return False
        
    def _finalise(self, event):
        """
        Finalises this aggregate, if appropriate, performing any additional checks as needed, based
        on the properties of the `event`.
        
        The value returned indicates whether finalisation succeeded.
        """
        if self._evaluate_action_id(event):
            event_type = type(event)
            self[event_type] = self[_EVENT_REGISTRY_REV.get(event_type)] = event
            self._pending_finalisers.discard(event_type)
            return len(self._pending_finalisers) == 0
        return False
        
    def _check_list_items_count(self, event, count_header):
        """
        Most finalisers have a count-property, so check it to assert validity.
        
        `count_header` identifies the header-item to check to validate the number of received
        entries.
        """
        event = event.process()[0]
        list_items_count = event.get(count_header)
        if list_items_count is not None:
            items_count = sum(len(v) for (k, v) in self.items() if type(v) is list and isinstance(k, types.StringType))
            self._valid = list_items_count == items_count
            if not self._valid:
                self._error_message = "Expected %(event)i list-items; received %(count)i" % {
                 'event': list_items_count,
                 'count': items_count,
                }
                
    def evaluate_event(self, event):
        """
        Folds the event into the aggregation, if it's associated with the same action-ID and is of a
        relevant type.
        
        `True` is returned if the aggregate is finalised after this event, `False` if it was simply
        merged, or `None` if the aggregate was unrelated.
        """
        event_type = type(event)
        if event_type in self._aggregation_members:
            self._aggregate(event)
            return False
        elif event_type in self._aggregation_finalisers:
            return self._finalise(event)
        return None
        
    @property
    def action_id(self):
        """
        Provides the action-ID associated with the message, if any.
        """
        return self._action_id
        
    @property
    def name(self):
        """
        Provides the name of the event or response.
        """
        return self._name
        
    @property
    def valid(self):
        """
        Indicates whether the aggregate is consistent with Asterisk's protocol.
        """
        return self._valid
        
    @property
    def error_message(self):
        """
        If `valid` is `False`, this will offer a string explaining why validation failed.
        """
        return self._error_message
        
class _Message(_MessageTemplate, dict):
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
            if KEY_ACTIONID in self: #If 'ActionID' is present, it's a response to an action.
                self.headers[KEY_RESPONSE] = RESPONSE_GENERIC
            else: #It's an unsolicited event
                self.headers[KEY_EVENT] = EVENT_GENERIC
                
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
    def action_id(self):
        """
        Provides the action-ID associated with the message, if any.
        """
        return self.get(KEY_ACTIONID)
        
    @property
    def name(self):
        """
        Provides the name of the event or response.
        """
        return self.get(KEY_EVENT) or self.get(KEY_RESPONSE)

class _Event(_Message):
    """
    The base-class of any event received from Asterisk, either unsolicited or as part of an extended
    response-chain.
    """
    def process(self):
        """
        Provides a tuple containing a copy of all headers as a dictionary and a copy of all response
        lines. The value of this data is negligible, but subclasses may apply further processing,
        replacing the values of headers with Python types or making the data easier to work with.
        """
        return (self.copy(), self.data[:])
        
class _Request(dict):
    """
    Provides a generic container for assembling AMI requests, the basis of all actions.
    
    Subclasses may override `__init__` and define any additional behaviours they may need, as well
    as override `process_response()` to specially format the data to be returned after a request
    has been served.
    """
    aggregate = False #Only has an effect on certain types of requests; will result in an aggregate-event being generated after a list of independent events
    synchronous = False #If True, requests will block until all response events have been collected; these events will appear in a `response` dictionary-attribute
    timeout = 5 #The number of seconds to wait before considering this request timed out; may be a float
    
    _aggregates = () #A tuple containing all aggregate-types associated with this request
    _synchronous_events_unique = () #A tuple containing all unique events associatable with this request
    _synchronous_events_list = () #A tuple containing all list-type events associatable with this request
    _synchronous_events_finalising = () #A tuple containing all events that must be received to consider this request complete
    
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
        
    def get_aggregate_classes(self):
        """
        Provides a tuple of all aggregate event-classes associated with this request.
        """
        return self._aggregates
        
    def get_synchronous_classes(self):
        """
        Provides a triple of (unique, list, finalising) tuples of sychronous event-classes
        associated with this request.
        """
        return (self._synchronous_events_unique, self._synchronous_events_list, self._synchronous_events_finalising)
        
class _MessageReader(threading.Thread):
    event_queue = None #A queue containing unsolicited events received from Asterisk
    response_queue = None #A queue containing orphaned or unparented responses from Asterisk
    _alive = True #False when this thread has been killed
    _manager = None #A reference to the manager instance that serves as the parent of this thread
    _orphaned_response_timeout = None #The number of seconds to hold on to request-responses before considering them to be timed-out
    _served_requests = None #A dictionary of responses from Asterisk, keyed by ActionID
    _served_requests_lock = None #A means of preventing race conditions from affecting the served-request set

    def __init__(self, manager, orphaned_response_timeout):
        threading.Thread.__init__(self)
        self.daemon = True
        self.name = 'pystrix-ami-message-reader'
        
        self._manager = manager
        self._orphaned_response_timeout = orphaned_response_timeout

        self.event_queue = Queue.Queue()
        self.response_queue = Queue.Queue()
        self._served_requests = {}
        self._served_requests_lock = threading.Lock()
        
    def _clean_orphaned_responses(self):
        """
        Ensures that old responses are moved to the orphaned queue, even though they should never
        exist.
        """
        current_time = time.time()
        with self._served_requests_lock:
            expired_action_ids = []
            for (action_id, (response, timeout)) in self._served_requests.items():
                if timeout <= current_time:
                    expired_action_ids.append(action_id)
                    self.response_queue.put(response) #Move it to the queue
                    
            for action_id in expired_action_ids:
                del self._served_requests[action_id]
                
    def kill(self):
        self._alive = False

    def get_response(self, action_id):
        """
        Returns the response from Asterisk associated with the given `action_id`, if any.
        """
        with self._served_requests_lock:
            response = self._served_requests.get(action_id)
            if response is not None:
                del self._served_requests[action_id]
                return response[0]
            return None
            
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
                if KEY_EVENT in message:
                    #See if the event has a corresponding subclass and mutate it if it does
                    event_class = _EVENT_REGISTRY.get(message.name)
                    if event_class:
                        message.__class__ = event_class
                    else:
                        message.__class__ = _Event
                        if self._manager._debug:
                            (self._manager._logger and self._manager._logger.warn or warnings.warn)("Unknown event received: " + repr(message))
                            
                    self.event_queue.put(message)
                elif action_id is not None:
                    self._clean_orphaned_responses()
                    with self._served_requests_lock:
                        if action_id not in self._served_requests:
                            self._served_requests[action_id] = (message, time.time() + self._orphaned_response_timeout)
                        else: #If there's already an associated response, treat this one as orphaned to avoid data-loss
                            self.response_queue.put(message)
                else: #It's an orphaned response
                    self.response_queue.put(message)
                    
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
        with self._socket_write_lock:
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
            with self._socket_read_lock:
                try:
                    line = self._socket_file.readline()
                except socket.timeout:
                    return None
                except socket.error as e:
                    self._close()
                    raise ManagerSocketError("Connection to Asterisk manager broken while reading data: %(error)s" % {
                     'error': _format_socket_error(e),
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
            
        with self._socket_write_lock:
            try:
                self._socket.sendall(message)
            except socket.error as e:
                self._close()
                raise ManagerSocketError("Connection to Asterisk manager broken while writing data: %(error)s" % {
                 'error': _format_socket_error(e),
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
        except socket.error as e:
            self._socket.close()
            raise ManagerSocketError("Connection to Asterisk manager could not be established: %(error)s" % {
             'error': _format_socket_error(e),
            })
        self._connected = True

        #Pop the greeting off the head of the pipe and set the version information
        try:
            line = self._socket_file.readline()
        except socket.error as e:
            self._socket.close()
            raise ManagerSocketError("Connection to Asterisk manager broken while reading greeting: %(error)s" % {
             'error': _format_socket_error(e),
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

