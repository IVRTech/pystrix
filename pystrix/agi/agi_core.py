"""
pystrix.agi.agi_core
====================

The core framework needed for an AGI session, regardless of interface.

Usage
-----

This module should not be used directly; instead, import one of `agi`
or `fastagi`.

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
import re
import time

_Response = collections.namedtuple('Response', ('items', 'code', 'raw'))
_ValueData = collections.namedtuple('ValueData', ('value', 'data'))

_RE_CODE = re.compile(r'(^\d+)\s*(.+)') #Matches Asterisk's response-code lines
_RE_KV = re.compile(r'(?P<key>\w+)=(?P<value>[^\s]+)?(?:\s+\((?P<data>.*)\))?') #Matches Asterisk's key-value response-pairs

_RESULT_KEY = 'result'


#Functions
###############################################################################
def quote(value):
    """
    Encapsulates `value` in double-quotes and coerces it into a string, if
    necessary.
    """
    return '"%(value)s"' % {
     'value': str(value),
    }


#Classes
###############################################################################
class _AGI(object):
    """
    This class encapsulates communication between Asterisk an a python script.
    It handles encoding commands to Asterisk and parsing responses from
    Asterisk. 
    """
    _environment = None #The environment variables received from Asterisk for this channel
    _debug = False #If True, development information is printed to console
    _rfile = None #The input file-like-object
    _wfile = None #The output file-like-object
    
    def __init__(self, debug=False):
        """
        Sets up variables required to process an AGI session.

        `debug` should only be turned on for library development.
        """
        self._debug = debug
        
        self._environment = {}
        self._parse_agi_environment()

    def execute(self, action):
        """
        Sends a request to Asterisk and waits for a response before returning control to the caller.

        The given `_Action` object, `action`, carries the command, arguments, and result-processing
        logic used to communicate with Asterisk.

        The state of the channel is verified with each call to this function, to ensure that it is
        still connected. An instance of `AGIHangup` is raised if it is not.
        """
        self._test_hangup()
        
        self._send_command(action.command)
        return action.process_response(self._get_result(action.check_hangup))

    def get_environment(self):
        """
        Returns Asterisk's initial environment variables as a dictionary.
        
        Note that this function returns a copy of the values, so repeated calls
        are less favourable than storing the returned value locally and
        dissecting it there.
        """
        return self._environment.copy()

    def _get_result(self, check_hangup=True):
        """
        Waits for a response from Asterisk, parses it, validates its contents, and returns it as a
        named tuple with 'items', 'code', and 'raw' attributes, where 'items' is a dictionary of
        Asterisk response-keys and value/data pairs, themselves in named tupled with 'value' and
        'data' attributes, 'code' is the numeric code received from Asterisk, and 'raw' is the line
        received, excluding the code.

        `check_hangup`, if `True`, the default, will cause `AGIResultHangup` to be raised if the
        'data' attribute of the 'result' key is 'hangup'.

        If the result indicates failure, `AGIAppError` is raised.

        If no 'result' key is provided, `AGIError` is raised.

        `AGIInvalidCommandError` is raised if the given command is unrecognised, either because the
        requested function isn't implemented in the current version of Asterisk or because the
        `execute()` function was invoked incorrectly.
        
        `AGIUsageError` is emitted if the arguments provided for a command are invalid.
        
        `AGIDeadChannelError` occurs if a command is attempted on a dead channel.

        `AGIUnknownError` covers any unrecognised Asterisk response code.
        """
        code = 0
        response = {}
        
        line = self._read_line()
        m = _RE_CODE.search(line)
        if m:
            code = int(m.group(1))
            
        if code == 200:
            raw = m.group(2) #The entire line, excluding the code
            for (key, value, data) in _RE_KV.findall(m.group(2)):
                response[key] = _ValueData(value or '', data)
                
            if not _RESULT_KEY in response: #Must always be present.
                raise AGINoResultError("Asterisk did not provide a '%(result-key)s' key-value pair" % {
                 'result-key': _RESULT_KEY,
                }, response)

            result = response.get(_RESULT_KEY)
            if result.value == '-1': #A result of -1 always indicates failure
                raise AGIAppError("Error executing application or the channel was hung up", response)
            if check_hangup and result.data == 'hangup': #A 'hangup' response usually indicates that the channel was hungup, but it is a legal variable value
                raise AGIResultHangup("User hung up during execution", response)
                
            return _Response(response, code, raw)
        elif code == 0:
            raise AGIResultHangup("Call hung up")
        elif code == 510:
            raise AGIInvalidCommandError(response)
        elif code == 511:
            raise AGIDeadChannelError(response)
        elif code == 520:
            usage = [line]
            while True:
                line = self._read_line()
                usage.append(line)
                if line.startswith('520'):
                    break
            raise AGIUsageError('\n'.join(usage + ['']))
        else:
            raise AGIUnknownError("Unhandled code or undefined response: %(code)i : %(line)s" % {
             'code': code,
             'line': repr(line),
            })
            
    def _parse_agi_environment(self):
        """
        Reads all of Asterisk's environment variables and stores them in memory.
        """
        while True:
            line = self._read_line()
            if line == '': #Blank line signals end
                break
                
            if ':' in line:
                (key, data) = line.split(':', 1)
                key = key.strip()
                data = data.strip()
                if key:
                    self._environment[key] = data
                    
    def _read_line(self):
        """
        Reads and returns a line from the Asterisk pipe, blocking until a complete line is
        assembled.
        
        If the pipe is closed before this happens, `AGISIGPIPEHangup` is raised.
        """
        try:
            line = self._rfile.readline()
            if not line: #EOF encountered
                raise AGISIGPIPEHangup("Process input pipe closed")
            elif not line.endswith('\n'): #Fragment encountered
                #Recursively append to the current fragment until the line is
                #complete or the socket dies.
                line += self._read_line()
            return line.strip()
        except IOError as e:
            raise AGISIGPIPEHangup("Process input pipe broken: %(error)s" % {
             'error': str(e),
            })
            
    def _send_command(self, command, *args):
        """
        Formats a `command` and sends it to Asterisk.

        The formatted command is constructed by joining the action verb component with every
        following argument, discarding those that are `None`.

        If the connection to Asterisk is broken, `AGISIGPIPEHangup` is raised.
        """
        try:
            self._wfile.write(command)
            self._wfile.flush()
        except Exception as e:
            raise AGISIGPIPEHangup("Socket link broken: %(error)s" % {
             'error': str(e),
            })
            
    def _test_hangup(self):
        """
        Tests to see if the channel has been hung up.
        
        At present, this is a no-op because no generic hang-up conditions are
        known, but subclasses may have specific scenarios to test for.
        """
        return

class _Action(object):
    """
    Provides the basis for assembling and issuing an action via AGI.
    """
    _command = None #The command that drives this action
    _arguments = None #A tuple of arguments to qualify the command
    check_hangup = True #True if the output of this action is sure to be hangup-detection-safe
    
    def __init__(self, command, *arguments):
        self._command = command
        self._arguments = arguments

    @property
    def command(self):
        command = ' '.join([self._command.strip()] + [str(arg) for arg in self._arguments if not arg is None]).strip()
        if not command.endswith('\n'):
            command += '\n'
        return command
        
    def process_response(self, response):
        """
        Just returns the `response` from Asterisk verbatim. May be overridden to allow for
        sophisticated processing.
        """
        return response


#Exceptions
###############################################################################
class AGIException(Exception):
    """
    The base exception from which all exceptions native to this module inherit.
    """
    items = None #Any items received from Asterisk, as a dictionary.

    def __init__(self, message, items={}):
        Exception.__init__(self, message)
        self.items = items
        
class AGIError(AGIException):
    """
    The base error from which all errors native to this module inherit.
    """
    
class AGINoResultError(AGIException):
    """
    Indicates that Asterisk did not return a 'result' parameter in a 200 response.
    """
    
class AGIUnknownError(AGIError):
    """
    An error raised when an unknown response is received from Asterisk.
    """
    
class AGIAppError(AGIError):
    """
    An error raised when an attempt to make use of an Asterisk application
    fails.
    """
    
class AGIDeadChannelError(AGIError):
    """
    Indicates that a command was issued on a channel that can no longer process
    it.
    """
    
class AGIInvalidCommandError(AGIError):
    """
    Indicates that a request made to Asterisk was not understood.
    """
    
class AGIUsageError(AGIError):
    """
    Indicates that a request made to Asterisk was sent with invalid syntax.
    """
    
class AGIHangup(AGIException):
    """
    The base exception used to indicate that the call has been completed or
    abandoned.
    """
    
class AGISIGPIPEHangup(AGIHangup):
    """
    Indicates that the communications pipe to Asterisk has been severed.
    """
    
class AGIResultHangup(AGIHangup):
    """
    Indicates that Asterisk received a clean hangup event.
    """
    
