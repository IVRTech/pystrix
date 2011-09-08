"""
pystrix.agi.fagi

Purpose
=======
 Provides classes that expose methods for communicating with Asterisk from a
 FastAGI (TCP socket) context.
 
Usage
=====
 Usage of this module is provided in the examples directory of the source
 distribution.
 
Legal
=====
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
import SocketServer

from agi_core import *
from agi_core import _AGI

class _ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    """
    Provides a variant of the TCPServer that spawns a new thread to handle each
    request.
    """
    
class _AGIClientHandler(SocketServer.StreamRequestHandler):
    """
    Handles TCP connections.
    """
    def handle(self):
        """
        Creates an instance of an AGI-interface object and passes it to a
        pre-specified callable.
        """
        agi_instance = FastAGI(self.rfile, self.wfile)
        
        handler = self.server.get_client_handler()
        handler(agi_instance)
        
class FastAGIServer(_ThreadedTCPServer):
    """
    Provides a FastAGI TCP server to handle requests from Asterisk servers.
    """
    _client_handler = None #The callable to be invoked to handle the AGI client.
    
    def __init__(self, handler, interface='127.0.0.1', port=4573, daemon_threads=True):
        """
        Creates the server and binds the client-handler callable.
        
        `interface` is the address of the interface on which to listen; defaults
        to localhost, but may be any interface on the host or `'0.0.0.0'` for
        all. `port` is the TCP port on which to listen.
        
        `daemon_threads` indicates whether any threads spawned to handle
        requests should be killed if the main thread dies. (Generally a good
        idea to avoid hung calls keeping the process alive forever)
        """
        _ThreadingTCPServer.__init__(self, (interface, port), _AGIClientHandler)
        self.daemon_threads = daemon_threads
        self._client_handler = handler
        
    def get_client_handler(self):
        """
        Provides the callable specified to handle requests received by this
        Fast AGI server.
        """
        return self._client_handler
        
class FastAGI(_AGI):
    """
    An interface to Asterisk, exposing request-response functions for
    synchronous management of the call associated with this channel.
    """
    def __init__(self, rfile, wfile):
        """
        Associates I/O with `rfile` and `wfile`.
        """
        self._rfile = rfile
        self._wfile = wfile
        
        _AGI.__init__(self)
        
