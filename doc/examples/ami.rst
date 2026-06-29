Asterisk Management Interface (AMI)
===================================

A simple, if verbose, AMI implementation is provided below, demonstrating how to connect to Asterisk
with MD5-based authentication, how to connect callback handlers for events, and how to send requests
for information::

    import time
    
    import pystrix
    
    #Just a few constants for logging in. Putting them directly into code is usually a bad idea.
    _HOST = 'localhost'
    _USERNAME = 'admin'
    _PASSWORD = 'wordpass'
    
    class AMICore(object):
        """
        The class that will be used to hold the logic for this AMI session. You could also just work
        with the `Manager` object directly, but this is probably a better approach for most
        general-purpose applications.
        """
        _manager = None #The AMI conduit for communicating with the local Asterisk server
        _kill_flag = False #True when the core has shut down of its own accord
         
        def __init__(self):
            #The manager supports Python's native logging module and has optional features; see its
            #constructor's documentation for details.
            self._manager = pystrix.ami.Manager()

            #Before connecting to Asterisk, callback handlers should be registered to avoid missing
            #any events.
            self._register_callbacks()
            
            try:
                #Attempt to connect to Asterisk
                self._manager.connect(_HOST)
                
                #The first thing to be done is to ask the Asterisk server for a challenge token to
                #avoid sending the password in plain-text. This step is optional, however, and can
                #be bypassed by simply omitting the 'challenge' parameter in the Login action.
                challenge_response = self._manager.send_action(pystrix.ami.core.Challenge())
                #This command demonstrates the common case of constructing a request action and
                #sending it to Asterisk to await a response.
                
                if challenge_response and challenge_response.success:
                    #The response is either a named tuple or None, with the latter occuring in case
                    #the request timed out. Requests are blocking (expected to be near-instant), but
                    #thread-safe, so you can build complex threading logic if necessary.
                    action = pystrix.ami.core.Login(
                     _USERNAME, _PASSWORD, challenge=challenge_response.result['Challenge']
                    )
                    self._manager.send_action(action)
                    #As with the Challenge action before, a Login action is assembled and sent to
                    #Asterisk, only in two steps this time, for readability.
                    #The Login class has special response-processing logic attached to it that
                    #causes authentication failures to raise a ManagerAuthException error, caught
                    #below. It will still return the same named tuple if you need to extract
                    #additional information upon success, however.
                else:
                    self._kill_flag = True
                    raise ConnectionError(
                     "Asterisk did not provide an MD5 challenge token" +
                     (challenge_response is None and ': timed out' or '')
                    )
            except pystrix.ami.ManagerSocketError as e:
                self._kill_flag = True
                raise ConnectionError("Unable to connect to Asterisk server: %(error)s" % {
                 'error': str(e),
                })
            except pystrix.ami.core.ManagerAuthError as reason:
                self._kill_flag = True
                raise ConnectionError("Unable to authenticate to Asterisk server: %(reason)s" % {
                 'reason': reason,
                })
            except pystrix.ami.ManagerError as reason:
                self._kill_flag = True
                raise ConnectionError("An unexpected Asterisk error occurred: %(reason)s" % {
                 'reason': reason,
                })

            #Start a thread to make is_connected() fail if Asterisk dies.
            #This is not done automatically because it disallows the possibility of immediate
            #correction in applications that could gracefully replace their connection upon receipt
            #of a `ManagerSocketError`.
            self._manager.monitor_connection()

        def _register_callbacks(self):
            #This sets up some event callbacks so that interesting things, like calls being
            #established or torn down, are processed by the application's logic.

            #pystrix supports four callback patterns:
            #
            #  1. Exact string match — fires when the wire event name matches exactly.
            #  2. Class match — fires when the event has been typed to the given class.
            #     This works for all built-in classes and any class registered with
            #     pystrix.ami.register_event_class() (see below).
            #  3. Empty string '' — a catch-all that fires for every event, useful for
            #     logging or debugging.
            #  4. None — fires for responses not associated with any request, which
            #     typically indicates a glitch or a timed-out request.
            #
            #For events pystrix does not recognise, the event still arrives as a
            #generic _Event object with all headers intact. Register against its wire
            #name as a plain string to receive it.

            #Register 'FullyBooted' two ways to illustrate that string and class
            #matching are equivalent in performance and semantics.
            self._manager.register_callback('FullyBooted', self._handle_string_event)
            self._manager.register_callback(pystrix.ami.core_events.FullyBooted, self._handle_class_event)
            #Both handlers are invoked in registration order when 'FullyBooted' arrives.

            #Catch every event, regardless of type.
            self._manager.register_callback('', self._handle_event)

            #Catch orphaned responses (those with no matching request).
            self._manager.register_callback(None, self._handle_event)

            #Catch Asterisk's Shutdown signal using a plain string.
            self._manager.register_callback('Shutdown', self._handle_shutdown)

            #To use a custom typed class for an event that pystrix does not define
            #natively, register it before calling connect(). After registration,
            #both type-mutation on arrival and class-based callbacks work normally.
            #
            #  class MyQueueCallerJoin(pystrix.ami.ami._Event):
            #      pass
            #
            #  pystrix.ami.register_event_class(MyQueueCallerJoin)
            #  self._manager.register_callback(MyQueueCallerJoin, self._handle_queue_event)
            #
            #Supply name= when the wire event name differs from the class name:
            #
            #  pystrix.ami.register_event_class(MyClass, name='QueueCallerJoin')
            
        def _handle_shutdown(self, event, manager):
            self._kill_flag = True
            
        def _handle_event(self, event, manager):
            print("Received event: %s" % event.name)

        def _handle_string_event(self, event, manager):
            print("Received string event: %s" % event.name)

        def _handle_class_event(self, event, manager):
            print("Received class event: %s" % event.name)

        def is_alive(self):
            return not self._kill_flag
            
        def kill(self):
            self._manager.close()
            
            
    class Error(Exception):
        """
        The base class from which all exceptions native to this module inherit.
        """
        
    class ConnectionError(Error):
        """
        Indicates that a problem occurred while connecting to the Asterisk server
        or that the connection was severed unexpectedly.
        """

    if __name__ == '__main__':
        ami_core = AMICore()
        
        while ami_core.is_alive():
            #In a larger application, you'd probably do something useful in another non-daemon
            #thread or maybe run a parallel FastAGI server. The pystrix implementation has the AMI
            #threads run daemonically, however, so a block like this in the main thread is necessary
            time.sleep(1)
        ami_core.kill()
        
