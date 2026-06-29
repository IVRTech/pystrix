Fast Asterisk Gateway Interface (FastAGI)
=========================================

A simple FastAGI implementation is provided below, demonstrating how to listen for and handle
requests from Asterisk, like, as illustrated, answering a call, playing a message, and hanging
up::

    import re
    import threading
    import time

    import pystrix
    
    class FastAGIServer(threading.Thread):
        """
        A simple thread that runs a FastAGI server forever.
        """
        _fagi_server = None #The FastAGI server controlled by this thread
        
        def __init__(self):
            threading.Thread.__init__(self)
            self.daemon = True
            
            self._fagi_server = pystrix.agi.FastAGIServer()
            
            self._fagi_server.register_script_handler(re.compile('demo'), self._demo_handler)
            self._fagi_server.register_script_handler(None, self._noop_handler)
            
        def _demo_handler(self, agi, args, kwargs, match, path):
            """
            `agi` is the AGI instance used to process events related to the channel, `args` is a
            collection of positional arguments provided with the script as a tuple, `kwargs` is a
            dictionary of keyword arguments supplied with the script (values are enumerated in a list),
            `match` is the regex match object (None if the fallback handler), and `path` is the string
            path supplied by Asterisk, in case special processing is needed.

            The directives issued in this function can all raise Hangup exceptions, which should be
            caught if doing anything complex, but an uncaught exception will simply cause a warning to
            be raised, making AGI scripts very easy to write.
            """
            agi.execute(pystrix.agi.core.Answer()) #Answer the call
            
            response = agi.execute(pystrix.agi.core.StreamFile('demo-thanks', escape_digits=('1', '2'))) #Play a file; allow DTMF '1' or '2' to interrupt
            if response: #Playback was interrupted; if you don't care, you don't need to catch this
                (dtmf_character, offset) = response #The key pressed by the user and the playback time
                
            agi.execute(pystrix.agi.core.Hangup()) #Hang up the call

        def _noop_handler(self, agi, args, kwargs, match, path):
            """
            Does nothing, causing control to return to Asterisk's dialplan immediately; provided just
            to demonstrate the fallback handler.
            """
            
        def kill(self):
            self._fagi_server.shutdown()
            
        def run(self):
            self._fagi_server.serve_forever()



    if __name__ == '__main__':
        fastagi_core = FastAGIServer()
        fastagi_core.start()
        
        while fastagi_core.is_alive():
            #In a larger application, you'd probably do something useful in another non-daemon
            #thread or maybe run a parallel AMI server
            time.sleep(1)
        fastagi_core.kill()
        

Hangup signaling
----------------

Asterisk sends FastAGI hangup notifications over the same network connection used for command
responses. If ``HANGUP`` arrives while pystrix is waiting for a command response, pystrix consumes
that notification and continues reading the actual response from Asterisk.

If a channel hangs up while a long-running application such as ``Dial`` is active, Asterisk may also
send a final ``HANGUP`` after the FastAGI handler has already returned and the socket has been
closed. On some Asterisk versions this can appear in the Asterisk console as an
``ast_carefulwrite`` ``Broken pipe`` error even though the FastAGI handler completed normally.

Set ``AGISIGHUP`` before entering FastAGI if Asterisk should not send those hangup notifications::

    exten => 97153654,1,Progress()
    same => n,Set(AGISIGHUP=no)
    same => n,AGI(agi://127.0.0.1/router)

If Asterisk should instead stop AGI processing as soon as it detects the hangup, set
``AGIEXITONHANGUP`` before entering FastAGI; Asterisk closes the AGI connection itself in this
case::

    exten => 97153654,1,Progress()
    same => n,Set(AGIEXITONHANGUP=yes)
    same => n,AGI(agi://127.0.0.1/router)

A closed FastAGI connection is reported to pystrix as :class:`agi.AGISIGPIPEHangup`.
