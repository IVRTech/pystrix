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
            #This sets up some event callbacks, so that interesting things, like calls being
            #established or torn down, will be processed by your application's logic. Of course,
            #since this is just an example, the same event will be registered using two different
            #methods.

            #The event that will be registered is 'FullyBooted', sent by Asterisk immediately after
            #connecting, to indicate that everything is online. What the following code does is
            #register two different callback-handlers for this event using two different
            #match-methods: string comparison and class-match. String-matching and class-resolution
            #are equal in performance, so choose whichever you think looks better.
            self._manager.register_callback('FullyBooted', self._handle_string_event)
            self._manager.register_callback(pystrix.ami.core_events.FullyBooted, self._handle_class_event)
            #Now, when 'FullyBooted' is received, both handlers will be invoked in the order in
            #which they were registered.

            #A catch-all-handler can be set using the empty string as a qualifier, causing it to
            #receive every event emitted by Asterisk, which may be useful for debugging purposes.
            self._manager.register_callback('', self._handle_event)

            #Additionally, an orphan-handler may be provided using the special qualifier None,
            #causing any responses not associated with a request to be received. This should only
            #apply to glitches in pre-production versions of Asterisk or requests that timed out
            #while waiting for a response, which is also indicative of glitchy behaviour. This
            #handler could be used to process the orphaned response in special cases, but is likely
            #best relegated to a logging role.
            self._manager.register_callback(None, self._handle_event)

            #And here's another example of a registered event, this time catching Asterisk's
            #Shutdown signal, emitted when the system is shutting down.
            self._manager.register_callback('Shutdown', self._handle_shutdown)
            
        def _handle_shutdown(self, event, manager):
            self._kill_flag = True
            
        def _handle_event(self, event, manager):
            print("Recieved event: %s" % event.name)

        def _handle_string_event(self, event, manager):
            print("Recieved string event: %s" % event.name)

        def _handle_class_event(self, event, manager):
            print("Recieved class event: %s" % event.name)

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
        
