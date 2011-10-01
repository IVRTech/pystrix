"""
pystrix.agi.agi
===============

Provides a class that exposes methods for communicating with Asterisk from an
AGI (script) context.
  
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
import signal
import sys

from agi_core import *
from agi_core import _AGI

class AGI(_AGI):
    """
    An interface to Asterisk, exposing request-response functions for
    synchronous management of the call associated with this channel.
    """
    _got_sighup = False #True when a hangup signal has been received.
    
    def __init__(self, debug=False):
        """
        Binds the SIGHUP signal and associates I/O with stdin/stdout.

        `debug` should only be turned on for library development.
        """
        signal.signal(signal.SIGHUP, self._handle_sighup)
        self._rfile = sys.stdin
        self._wfile = sys.stdout
        
        _AGI.__init__(self, debug)
        
    def _handle_sighup(self, signum, frame):
        """
        Sets the has-hungup flag to trigger an exception when the next command
        is received.
        """
        self._got_sighup = True
        
    def _test_hangup(self):
        """
        If SIGHUP has been received, or another hangup flag has been set, an
        exception is raised; if not, this function is a no-op.
        
        Raises `AGISIGHUPHangup` if SIGHUP has been recieved, or any other exceptions
        normally raised by `_AGI`'s `_test_hangup()`.
        """
        if self._got_sighup:
            raise AGISIGHUPHangup("Received SIGHUP from Asterisk")
            
        _AGI._test_hangup(self)
        
class AGISIGHUPHangup(AGIHangup):
    """
    Indicates that the script's process received the SIGHUP signal, implying
    Asterisk has hung up the call. Specific to script-based instances.
    """
    
