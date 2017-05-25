"""
pystrix.agi.fagi
================

Provides classes that expose methods for communicating with Asterisk from a
FastAGI (TCP socket) context.

Usage
-----

Usage of this module is provided in the examples directory of the source
distribution.

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
import cgi
import re
import socket
import threading
import types
from pystrix.agi.agi_core import *
from pystrix.agi.agi_core import _AGI

try:
	import socketserver
except:
	import SocketServer as socketserver




class _ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """
    Provides a variant of the TCPServer that spawns a new thread to handle each
    request.
    """
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socketserver.TCPServer.server_bind(self)
        
class _AGIClientHandler(socketserver.StreamRequestHandler):
    """
    Handles TCP connections.
    """
    def handle(self):
        """
        Creates an instance of an AGI-interface object and passes it to a pre-specified callable,
        selected by matching the request parameters against a series of regular expressions.
        """
        agi_instance = FastAGI(self.rfile, self.wfile, debug=self.server.debug)

        (path, kwargs) = self._extract_query_elements(agi_instance)
        args = self._extract_positional_args(agi_instance)
        
        (handler, match) = self.server.get_script_handler(path)
        if handler:
            handler(agi_instance, args, kwargs, match, path)

    def _extract_positional_args(self, agi_instance):
        """
        Pulls the 'agi_arg_x' values out of the AGI instance to make them easier to process, since
        the specification by which they're supplied may change in the future.
        """
        env = agi_instance.get_environment()
        keys = sorted((int(key[8:]) for key in env if key.startswith('agi_arg_')))
        return tuple((env['agi_arg_%i' % key] for key in keys))

    def _extract_query_elements(self, agi_instance):
        """
        Provides the path string and a dictionary of keyword arguments passed along with the AGI
        request. Arguments are supplied as a list, since the same parameter may be specified
        multiple times.
        """
        tokens = (agi_instance.get_environment().get('agi_network_script') or '/').split('?', 1)
        path = tokens[0]
        if len(tokens) == 1:
            return (path, {})
        return (path, cgi.urlparse.parse_qs(tokens[1]))

class FastAGIServer(_ThreadedTCPServer):
    """
    Provides a FastAGI TCP server to handle requests from Asterisk servers.
    """
    debug = False #Used to enable various printouts for library development
    _default_script_handler = None #A script-handler to use if nothing else matched
    _script_handlers = None #A list of regex/callable pairs to use when determining how to handle an AGI request
    _script_handlers_lock = None #A lock used to prevent race conditions on the handlers list
    
    def __init__(self, interface='127.0.0.1', port=4573, daemon_threads=True, debug=False):
        """
        Creates the server and binds the client-handler callable.
        
        `interface` is the address of the interface on which to listen; defaults
        to localhost, but may be any interface on the host or `'0.0.0.0'` for
        all. `port` is the TCP port on which to listen.
        
        `daemon_threads` indicates whether any threads spawned to handle
        requests should be killed if the main thread dies. (Generally a good
        idea to avoid hung calls keeping the process alive forever)

        `debug` should only be turned on for library development.
        """
        _ThreadedTCPServer.__init__(self, (interface, port), _AGIClientHandler)
        self.debug = debug
        self.daemon_threads = daemon_threads
        self._script_handlers = []
        self._script_handlers_lock = threading.Lock()

    def clear_script_handlers(self):
        """
        Empties the list of script handlers, allowing it to be repopulated. The default handler is
        not cleared by this action; to clear it, call `register_script_handler(None, None)`.
        """
        with self._script_handlers_lock:
            self._script_handlers = []

    def get_script_handler(self, script_path):
        """
        Provides the callable specified to handle requests received by this
        FastAGI server and the result of matching, as a tuple.

        `script_path` is the path received from Asterisk.
        """
        with self._script_handlers_lock:
            for (regex, handler) in self._script_handlers:
                match = None
                if isinstance(regex, str):
                    match = re.match(regex, script_path)
                else:
                    match = regex.match(script_path)
                if match:
                    return (handler, match)
                    
            return (self._default_script_handler, None)

    def register_script_handler(self, regex, handler):
        """
        Registers the given `handler`, which is a callable that accepts an AGI object used to
        communicate with the Asterisk channel, a tuple containing any positional arguments, a
        dictionary containing any keyword arguments (values are enumerated in a list), the match
        object (may be `None`), and the original script address as a string.

        Handlers are resolved by `regex`, which may be a regular expression object or a string,
        match in the order in which they were supplied, so provide more specific qualifiers first.

        The special `regex` value `None` sets the default handler, invoked when every comparison
        fails; this is preferable to adding a catch-all handler in case the list is changed at
        runtime. Setting the default handler to `None` disables the catch-all, which will typically
        make Asterisk just drop the call.
        """
        with self._script_handlers_lock:
            if regex is None:
                self._default_script_handler = handler
                return

            #Ensure that the regex hasn't been registered before
            for (old_regex, old_handler) in self._script_handlers:
                if old_regex == regex:
                    return

            #Add the handler to the end of the list
            self._script_handlers.append((regex, handler))

    def unregister_script_handler(self, regex):
        """
        Removes a specific script-handler from the list, given the same `regex` object used to
        register it initially.

        This function should only be used when a specific handler is no longer useful; if you want
        to re-introduce handlers, consider using `clear_script_handlers()` and re-adding all
        handlers in the desired order.
        """
        with self._script_handlers_lock:
            for (i, (old_regex, old_handler)) in enumerate(self._script_handlers):
                if old_regex == regex:
                    self._script_handlers.pop(i)
                    break

class FastAGI(_AGI):
    """
    An interface to Asterisk, exposing request-response functions for
    synchronous management of the call associated with this channel.
    """
    def __init__(self, rfile, wfile, debug=False):
        """
        Associates I/O with `rfile` and `wfile`.

        `debug` should only be turned on for library development.
        """
        self._rfile = rfile
        self._wfile = wfile
        
        _AGI.__init__(self, debug)
        
