"""
pystrix.agi_core

Purpose
=======
 The core logic needed for an AGI session, regardless of interface.
 
 All AGI actions are exposed by the _AGI class in this module, targeting
 Asterisk version 1.10.
 
Usage
=====
 This module should not be used directly; instead, import one of `agi`
 or `fagi`.
 
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
import collections
import re
import time

_Response = collections.namedtuple('Response', ('items', 'code', 'raw'))
_ValueData = collections.namedtuple('ValueData', ('value', 'data'))

_RE_CODE = re.compile(r'(^\d*)\s*(.*)') #Matches Asterisk's response-code lines
_RE_KV = re.compile(r'(?P<key>\w+)=(?P<value>[^\s]+)(?:\s+\((?P<data>.*)\))?') #Matches Asterisk's key-value response-pairs

_RESULT_KEY = 'result'

CHANNEL_DOWN_AVAILABLE = 0 #Channel is down and available
CHANNEL_DOWN_RESERVED = 1 #Channel is down and reserved
CHANNEL_OFFHOOK = 2 #Channel is off-hook
CHANNEL_DIALED = 3 #A destination address has been specified
CHANNEL_ALERTING = 4 #The channel is locally ringing
CHANNEL_REMOTE_ALERTING = 5 #The channel is remotely ringing
CHANNEL_UP = 6 #The channel is connected
CHANNEL_BUSY = 7 #The channel is in a busy, non-conductive state

FORMAT_SLN = 'sln'
FORMAT_G723 = 'g723'
FORMAT_G729 = 'g729'
FORMAT_GSM = 'gsm'
FORMAT_ALAW = 'alaw'
FORMAT_ULAW = 'ulaw'
FORMAT_VOX = 'vox'
FORMAT_WAV = 'wav'

LOG_DEBUG = 0
LOG_INFO = 1
LOG_WARN = 2
LOG_ERROR = 3
LOG_CRITICAL = 4

TDD_ON = 'on'
TDD_OFF = 'off'
TDD_MATE = 'mate'

class _AGI(object):
    """
    This class encapsulates communication between Asterisk an a python script.
    It handles encoding commands to Asterisk and parsing responses from
    Asterisk. 
    """
    _environment = None #The environment variables received from Asterisk for this channel
    _rfile = None #The input file-like-object
    _wfile = None #The output file-like-object
    
    def __init__(self):
        """
        Sets up variables required to process an AGI session.
        """
        self._environment = {}
        self._parse_agi_environment()

    def agi_get_environment(self):
        """
        Returns Asterisk's initial environment values.
        
        Note that this function returns a copy of the values, so repeated calls
        are less favourable than storing the returned value locally and
        dissecting it there.
        """
        return self._environment.copy()

    def execute(self, command, check_hangup, *args):
        """
        Sends a request to Asterisk and waits for a response before returning control to the caller.

        The request type is specified in `command`, `check_hangup` indicates whether the response
        should be parsed to look for patterns associated with hangups (must be optional, since the
        patterns can be legal responses for some instant-returning requests), and `*args` contains
        every argument associated with the request.
        
        The state of the channel is verified with each call to this function, to ensure that it is
        still connected. An instance of `AGIHangup` is raised if it is not.

        This function is intended for internal use only, but is exposed for purposes of
        extendability. For details on how it works, see `_send_command()` and `_get_result()`.
        """
        self._test_hangup()
        
        self._send_command(command, *args)
        return self._get_result(check_hangup)
        
    def _convert_to_char(self, value, items):
        """
        Converts the given value into an ASCII character or raises `AGIAppError` with `items` as the
        payload.
        """
        try:
            return chr(int(value))
        except ValueError:
            raise AGIAppError("Unable to convert Asterisk result to DTMF character: %(value)r" % {
             'value': value,
            }, items)

    def _convert_to_int(self, items):
        """
        Extracts the offset-value from Asterisk's response, `items`, or returns -1 if the value
        can't be parsed.
        """
        offset = items.get('endpos')
        if offset and offset.data.isdigit():
            return int(offset.data)
        else:
            return -1

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
                response[key] = _ValueData(value, data)
                
            if not _RESULT_KEY in response: #Must always be present.
                raise AGIError("Asterisk did not provide a '%(result-key)s' key-value pair" % {
                 'result-key': _RESULT_KEY,
                }, response)

            with response.get(_RESULT_KEY) as result:
                if result.value == '-1': #A result of -1 always indicates failure
                    raise AGIAppError("Error executing application or the channel was hung up", response)
                if check_hangup and result.data == 'hangup': #A 'hangup' response usually indicates that the channel was hungup, but it is a legal variable value
                    raise AGIResultHangup("User hung up during execution", response)
                    
            return _Response(response, code, raw)
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
            raise AGIUnknownError("Unhandled code or undefined response: %(code)i" % {
             'code': code,
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

    def _process_digit_list(self, digits):
        """
        Ensures that digit-lists are processed uniformly.
        """
        if type(digits) in (list, tuple, set, frozenset):
            digits = ''.join([str(d) for d in digits])
        return self._quote(digits)
        
    def _quote(self, value):
        """
        Encapsulates `value` in double-quotes and coerces it into a string, if
        necessary.
        """
        return '"%(string)s"' % {
         'string': str(string),
        }

    def _read_line(self):
        """
        Reads and returns a line from the Asterisk pipe, blocking until a complete line is
        assembled.
        
        If the pipe is closed before this happens, `AGISIGPIPEHangup` is raised.
        """
        try:
            line = self._rfile.readline()
            if not line: #EOF encountered
                raise AGISIGPIPEHangup("Process input pipe closed: %(error)s" % {
                 'error': str(e),
                })
            elif not line.endswith('\n'): #Fragment encountered
                #Recursively append to the current fragment until the line is
                #complete or the socket dies.
                line += self._read_line()
            return line.strip()
        except IOError as e:
            raise AGISIGPIPEHangup("Process input pipe broken: %(error)s" % {
             'error': str(e),
            })
            
    def _say(self, say_type, argument, escape_digits, *args):
        """
        Synthesises speech on a channel. This abstracts the commonalities between the "SAY ?"
        functions.

        `say_type` is the type of command to be issued.

        `argument` is the argument to be synthesised.

        `escape_digits` may optionally be a list of DTMF digits, specified as a string or a sequence
        of possibly mixed ints and strings. Playback ends immediately when one is received.

        `AGIAppError` is raised on failure, most commonly because the channel was
        hung-up.
        """
        escape_digits = self._process_digit_list(escape_digits)
        response = self.execute('SAY ' + say_type, self._quote(argument), self._quote(escape_digits), *args)
        result = response.get(_RESULT_KEY)

        if not result.value == '0':
            return self._convert_to_char(result.value, response.items)
        return None
        
    def _send_command(self, command, *args):
        """
        Formats a `command` and sends it to Asterisk.

        The formatted command is constructed by joining the action verb component with every
        following argument, discarding those that are `None`.

        If the connection to Asterisk is broken, `AGISIGPIPEHangup` is raised.
        """
        command = ' '.join([command.strip()] + [str(arg) for arg in args if not arg is None]))).strip()
        if not command.endswith('\n'):
            command += '\n'
            
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
        
    #Core Asterisk functions
    ###########################################################################
    def answer(self):
        """
        Answers the call on the channel.
        
        If the channel has already been answered, this is a no-op.

        `AGIAppError` is raised on failure, most commonly because the connection
        could not be established.
        """
        self.execute('ANSWER', True)
        
    def appexec(self, application, options=()):
        """
        Executes an arbitrary Asterisk `application` with the given `options`, returning that
        application's output.

        `options` is an optional sequence of arguments, with any double-quote characters or pipes
        explicitly escaped.

        `AGIAppError is raised if the application could not be executed.
        """
        """agi.appexec(application, options='')
        Executes <application> with given <options>.
        Returns whatever the application returns, or -2 on failure to find
        application
        """
        options = '|'.join(options)
        response = self.execute('EXEC', False, application, (options and self._quote(options)) or '')
        result = response.items.get(_RESULT_KEY)
        if result.value == '-2':
            raise AGIAppError("Unable to execute application '%(application)r'" % {
             'application': application,
            }, response.items)
        return response.raw[7:] #Everything after 'result='
        
    def channel_status(self, channel=None):
        """
        Provides the current state of this channel or, if `channel` is set, that of the named
        channel.
        
        Returns one of the channel-state constants listed below:
        - CHANNEL_DOWN_AVAILABLE : Channel is down and available
        - CHANNEL_DOWN_RESERVED : Channel is down and reserved
        - CHANNEL_OFFHOOK : Channel is off-hook
        - CHANNEL_DIALED : A destination address has been specified
        - CHANNEL_ALERTING : The channel is locally ringing
        - CHANNEL_REMOTE_ALERTING : The channel is remotely ringing
        - CHANNEL_UP : The channel is connected
        - CHANNEL_BUSY : The channel is in a busy, non-conductive state

        The value returned is an integer in the range 0-7, values outside of
        that range were undefined at the time of writing, but will be returned
        verbatim. Applications unprepared to handle unknown states should
        raise an exception upon their receipt or otherwise handle the code
        gracefully.

        `AGIAppError` is raised on failure, most commonly because the channel is
        in a hung-up state.
        """
        response = self.execute('CHANNEL STATUS', True, (channel and self._quote(channel)) or None)
        result = response.items.get(_RESULT_KEY)
        try:
            return int(result.value)
        except ValueError:
            raise AGIAppError("'%(result-key)s' key-value pair received from Asterisk contained a non-numeric value: %(value)r" % {
             'result-key': _RESULT_KEY,
             'value': result.value,
            }, response.items)
            
    def control_stream_file(self, filename, escape_digits='', sample_offset=0, forward='', rewind='', pause=''):
        """
        See also `get_data`, `get_option`, `stream_file`.
        
        Plays back the specified file, which is the `filename` of the file to be played, either in
        an Asterisk-searched directory or as an absolute path, without extension. ('myfile.wav'
        would be specified as 'myfile', to allow Asterisk to choose the most efficient encoding,
        based on extension, for the channel)
        
        `escape_digits` may optionally be a list of DTMF digits, specified as a string or a sequence
        of possibly mixed ints and strings. Playback ends immediately when one is received.
        
        `sample_offset` may be used to jump an arbitrary number of milliseconds into the audio data.

        If specified, `forward`, `rewind`, and `pause` are DTMF characters that will seek forwards
        and backwards in the audio stream or pause it temporarily; by default, these features are
        disabled.

        If a DTMF key is received, it is returned as a string. If nothing is received or the file
        could not be played back (see Asterisk logs), None is returned.
        
        `AGIAppError` is raised on failure, most commonly because the channel was
        hung-up.
        """
        escape_digits = self._process_digit_list(escape_digits)
        response = self.execute(
         'CONTROL STREAM FILE', True, self._quote(filename),
         self._quote(escape_digits), self._quote(sample_offset),
         self._quote(forward), self._quote(rewind), self._quote(pause)
        )
        result = response.items.get(_RESULT_KEY)
        if not result.value == '0':
            return self._convert_to_char(result.value, response.items)
        return None
        
    def database_del(self, family, key):
        """
        Deletes the specified family/key entry from Asterisk's database.
        
        `AGIAppError` is raised on failure.
        
        `AGIDBError` is raised if the key could not be removed, which usually indicates that it
        didn't exist in the first place.
        """
        response = self.execute('DATABASE DEL', True, self._quote(family), self._quote(key))
        result = response.items.get(_RESULT_KEY)
        if result.value == '0':
            raise AGIDBError("Unable to delete from database: family=%(family)r, key=%(key)r" % {
             'family': family,
             'key': key,
            }, response.items)
            
    def database_deltree(self, family, keytree=None):
        """
        Deletes the specificed family (and optinally keytree) from Asterisk's database.

        `AGIAppError` is raised on failure.
        
        `AGIDBError` is raised if the family (or keytree) could not be removed, which usually
        indicates that it didn't exist in the first place.
        """
        response = self.execute(
         'DATABASE DELTREE', True, self._quote(family), (keytree and self._quote(keytree) or None)
        )
        result = response.items.get(_RESULT_KEY)
        if result.value == '0':
            raise AGIDBError("Unable to delete family from database: family=%(family)r, keytree=%(keytree)r" % {
             'family': family,
             'keytree': keytree or '<unspecified>',
            }, response.items)
            
    def database_get(self, family, key):
        """
        Retrieves the value of the specified family/key entry from Asterisk's database.
        
        `AGIAppError` is raised on failure.
        
        `AGIDBError` is raised if the key could not be found or if some other database problem
        occurs.
        """
        response = self.execute('DATABASE GET', False, self._quote(family), self._quote(key))
        result = response.items.get(_RESULT_KEY)
        if result.value == '0':
            raise AGIDBError("Key not found in database: family=%(family)r, key=%(key)r" % {
             'family': family,
             'key': key,
            }, response.items)
        elif result.value == '1':
            return result.data
            
        raise AGIDBError("Unable to query database: family=%(family)r, key=%(key)r, result=%(result)r" % {
         'family': family,
         'key': key,
         'result': result.value,
        }, response.items)
        
    def database_put(self, family, key, value):
        """
        Inserts or updates value of the specified family/key entry in Asterisk's database.
        
        `AGIAppError` is raised on failure.
        
        `AGIDBError` is raised if the key could not be inserted or if some other database problem
        occurs.
        """
        response = self.execute('DATABASE PUT', True self._quote(family), self._quote(key), self._quote(value))
        result = response.items.get(_RESULT_KEY)
        if result.value == '0':
            raise AGIDBError("Unable to store value in database: family=%(family)r, key=%(key)r, value=%(value)r" % {
             'family': family,
             'key': key,
             'value': value,
            }, response.items)
            
    def get_data(self, filename, timeout=2000, max_digits=255):
        """
        See also `control_stream_file`, `get_option`, `stream_file`.
        
        Plays back the specified file, which is the `filename` of the file to be played, either in
        an Asterisk-searched directory or as an absolute path, without extension. ('myfile.wav'
        would be specified as 'myfile', to allow Asterisk to choose the most efficient encoding,
        based on extension, for the channel)
        
        `timeout` is the number of milliseconds to wait between DTMF presses or following the end
        of playback if no keys were pressed to interrupt playback prior to that point. It defaults
        to 2000.

        `max_digits` is the number of DTMF keypresses that will be accepted. It defaults to 255.

        The value returned is a tuple consisting of (dtmf_keys:str, timeout:bool). '#' is always
        interpreted as an end-of-event character and will never be present in the output.
        
        `AGIAppError` is raised on failure, most commonly because the channel was
        hung-up.
        """
        response = self.execute('GET DATA', True, self._quote(filename), self._quote(timeout), self._quote(max_digits))
        result = response.items.get(_RESULT_KEY)
        return (result.value, result.data == 'timeout')
        
    def get_full_variable(self, variable):
        """
        Returns a `variable` associated with this channel, with full expression-processing.
        
        The value of the requested variable is returned as a string. If the variable is
        undefined, `None` is returned.

        `AGIAppError` is raised on failure.
        """
        response = self.execute('GET FULL VARIABLE', False, self._quote(variable))
        result = response.items.get(_RESULT_KEY)
        if result.value == '1':
            return result.data
        return None

    def get_option(self, filename, escape_digits='', timeout=2000):
        """
        See also `control_stream_file`, `get_data`, `stream_file`.

        Plays back the specified file, which is the `filename` of the file to be played, either in
        an Asterisk-searched directory or as an absolute path, without extension. ('myfile.wav'
        would be specified as 'myfile', to allow Asterisk to choose the most efficient encoding,
        based on extension, for the channel)
        
        `escape_digits` may optionally be a list of DTMF digits, specified as a string or a sequence
        of possibly mixed ints and strings. Playback ends immediately when one is received.
        
        `timeout` is the number of milliseconds to wait following the end of playback if no keys
        were pressed to interrupt playback prior to that point. It defaults to 2000.
        
        The value returned is a tuple consisting of (dtmf_key:str, offset:int), where the offset is
        the number of milliseconds that elapsed since the start of playback, or None if playback
        completed successfully or the sample could not be opened.
        
        `AGIAppError` is raised on failure, most commonly because the channel was
        hung-up.
        """
        escape_digits = self._process_digit_list(escape_digits)
        response = self.execute(
         'GET OPTION', True, self._quote(filename),
         self._quote(escape_digits), self._quote(timeout)
        )
        result = response.items.get(_RESULT_KEY)
        if not result.value == '0':
            dtmf_character = self._convert_to_char(result.value, response.items)
            offset = self._convert_to_int(response.items)
            return (dtmf_character, offset)
        return None
        
    def get_variable(self, name):
        """
        Returns a `variable` associated with this channel.
        
        The value of the requested variable is returned as a string. If the variable is
        undefined, `None` is returned.

        `AGIAppError` is raised on failure.
        """
        response = self.execute(
         'GET VARIABLE', False, self._quote(variable))
        )
        result = response.items.get(_RESULT_KEY)
        if result.value == '1':
            return result.data
        return None
        
    def hangup(self, channel=None):
        """
        Hangs up this channel or, if `channel` is set, the named channel.

        `AGIAppError` is raised on failure.
        """
        self.execute('HANGUP', True, (channel and self._quote(channel) or None))
        
    def noop(self):
        """
        Does nothing.
        
        Good for testing the connection to the Asterisk server, like a ping, but
        not useful for much else. If you wish to log information through
        Asterisk, use the `verbose` method instead.
        
        `AGIAppError` is raised on failure.
        """
        self.execute('NOOP', True)

    def receive_char(self, timeout=0):
        """
        Receives a single character of text from a supporting channel, discarding anything else in
        the character buffer.

        `timeout` is the number of milliseconds to wait for a character to be received, defaulting
        to infinite.

        The value returned is a tuple of the form (char:str, timeout:bool), with the timeout element
        indicating whether the function returned because of a timeout, which may result in an empty
        string. `None` is returned if the channel does not support text.

        `AGIAppError` is raised on failure.
        """
        response = self.execute('RECEIVE CHAR', True, self._quote(timeout))
        result = response.items.get(_RESULT_KEY)
        if not result.value == '0':
            return (self._convert_to_char(result.value, response.items), result.data == 'timeout')
        return None

    def receive_text(self, timeout=0):
        """
        Receives a block of text from a supporting channel.

        `timeout` is the number of milliseconds to wait for text to be received, defaulting
        to infinite. Presumably, the first block received is immediately returned in full.

        The value returned is a string.

        `AGIAppError` is raised on failure.
        """
        response = self.execute('RECEIVE TEXT', True, self._quote(timeout))
        result = response.items.get(_RESULT_KEY)
        return result.value
        
    def record_file(self, filename, format=FORMAT_WAV, escape_digits='', timeout=-1, sample_offset=0, beep=True, silence=None):
        """
        Records audio to the specified file, which is the `filename` of the file to be written,
        defaulting to Asterisk's sounds path or an absolute path, without extension. ('myfile.wav'
        would be specified as 'myfile') `format` is one of the following, which sets the extension
        and encoding, with WAV being the default:
        - FORMAT_SLN
        - FORMAT_G723
        - FORMAT_G729
        - FORMAT_GSM
        - FORMAT_ALAW
        - FORMAT_ULAW
        - FORMAT_VOX
        - FORMAT_WAV : PCM16

        The filename may also contain the special string '%d', which Asterisk will replace with an
        auto-incrementing number, with the resulting filename appearing in the 'RECORDED_FILE'
        channel variable.
        
        `escape_digits` may optionally be a list of DTMF digits, specified as a string or a sequence
        of possibly mixed ints and strings. Playback ends immediately when one is received.
        
        `timeout` is the number of milliseconds to wait following the end of playback if no keys
        were pressed to end recording prior to that point. By default, it waits forever.

        `sample_offset` may be used to jump an arbitrary number of milliseconds into the audio data.

        `beep`, if `True`, the default, causes an audible beep to be heard when recording begins.

        `silence`, if given, is the number of seconds of silence to allow before terminating
        recording early.
        
        The value returned is a tuple consisting of (dtmf_key:str, offset:int, timeout:bool), where
        the offset is the number of milliseconds that elapsed since the start of playback dtmf_key
        may be the empty string if no key was pressed, and timeout is `False` if recording ended due
        to another condition (DTMF or silence).
        
        The raising of `AGIResultHangup` is another condition that signals a successful recording,
        though it also means the user hung up.
        
        `AGIAppError` is raised on failure, most commonly because the destination file isn't
        writable.
        """
        escape_digits = self._process_digit_list(escape_digits)
        response = self.execute(
         'RECORD FILE', True, self._quote(filename), self._quote(format),
         self._quote(escape_digits), self._quote(timeout), self._quote(sample_offset),
         (beep and self._quote('beep') or None),
         (silence and self._quote('s=' + str(silence)) or None)
        )
        result = response.items.get(_RESULT_KEY)

        offset = self._convert_to_int(response.items)
        
        if result.data == 'randomerror':
            raise AGIAppError("Unknown error occurred %(ms)i into recording: %(error)s" % {
             'ms': offset,
             'error': result.value,
            })
        elif result.data == 'timeout':
            return ('', offset, True)
        elif result.data == 'dtmf':
            return (self._convert_to_char(result.value, response.items), offset, False)
        return ('', offset, True) #Assume a timeout if any other result data is received.
        
    def say_alpha(self, characters, escape_digits=''):
        """
        Reads an alphabetic string of `characters`.

        `escape_digits` may optionally be a list of DTMF digits, specified as a string or a sequence
        of possibly mixed ints and strings. Playback ends immediately when one is received and it is
        returned. If nothing is recieved, `None` is returned.

        `AGIAppError` is raised on failure, most commonly because the channel was
        hung-up.
        """
        characters = self._process_digit_list(characters)
        return self._say('ALPHA', characters, escape_digits)
        
    def say_date(self, seconds=None, escape_digits=''):
        """
        Reads the date associated with `seconds` since the UNIX Epoch. If not given, the local time
        is used.
        
        `escape_digits` may optionally be a list of DTMF digits, specified as a string or a sequence
        of possibly mixed ints and strings. Playback ends immediately when one is received and it is
        returned. If nothing is recieved, `None` is returned.

        `AGIAppError` is raised on failure, most commonly because the channel was
        hung-up.
        """
        if seconds is None:
            seconds = int(time.time())
        return self._say('DATE', seconds, escape_digits)

    def say_datetime(self, seconds=None, escape_digits='', format=None, timezone=None):
        """
        Reads the datetime associated with `seconds` since the UNIX Epoch. If not given, the local
        time is used.
        
        `escape_digits` may optionally be a list of DTMF digits, specified as a string or a sequence
        of possibly mixed ints and strings. Playback ends immediately when one is received and it is
        returned. If nothing is recieved, `None` is returned.

        `format` defaults to "ABdY 'digits/at' IMp", but may be a string with any of the following
        meta-characters:
        - A : Day of the week
        - B : Month (Full Text)
        - m : Month (Numeric)
        - d : Day of the month
        - Y : Year
        - I : Hour (12-hour format)
        - H : Hour (24-hour format)
        - M : Minutes
        - P : AM/PM
        - Q : Shorthand for Today, Yesterday or ABdY
        - R : Shorthand for HM
        - S : Seconds
        - T : Timezone

        `timezone` may be a string in standard UNIX form, like 'America/Edmonton'. If `format` is
        undefined, `timezone` is ignored and left to default to the system's local value.
        
        `AGIAppError` is raised on failure, most commonly because the channel was
        hung-up.
        """
        if seconds is None:
            seconds = int(time.time())
        if not format:
            timezone = None
        return self._say(
         'DATETIME', seconds, escape_digits,
         (format and self._quote(format) or None), (timezone and self._quote(timezone) or None)
        )
        
    def say_digits(self, digits, escape_digits=''):
        """
        Reads a numeric string of `digits`.

        `escape_digits` may optionally be a list of DTMF digits, specified as a string or a sequence
        of possibly mixed ints and strings. Playback ends immediately when one is received and it is
        returned. If nothing is recieved, `None` is returned.

        `AGIAppError` is raised on failure, most commonly because the channel was
        hung-up.
        """
        digits = self._process_digit_list(digits)
        return self._say('DIGITS', digits, escape_digits)
        
    def say_number(self, number, escape_digits=''):
        """
        Reads a `number` naturally.

        `escape_digits` may optionally be a list of DTMF digits, specified as a string or a sequence
        of possibly mixed ints and strings. Playback ends immediately when one is received and it is
        returned. If nothing is recieved, `None` is returned.

        `AGIAppError` is raised on failure, most commonly because the channel was
        hung-up.
        """
        number = self._process_digit_list(number)
        return self._say('DIGITS', number, escape_digits)
        
    def say_phonetic(self, characters, escape_digits=''):
        """
        Reads a phonetic string of `characters`.

        `escape_digits` may optionally be a list of DTMF digits, specified as a string or a sequence
        of possibly mixed ints and strings. Playback ends immediately when one is received and it is
        returned. If nothing is recieved, `None` is returned.

        `AGIAppError` is raised on failure, most commonly because the channel was
        hung-up.
        """
        characters = self._process_digit_list(characters)
        return self._say('ALPHA', characters, escape_digits)
        
    def say_time(self, seconds=None, escape_digits=''):
        """
        Reads the datetime associated with `seconds` since the UNIX Epoch. If not given, the local
        time is used.
        
        `escape_digits` may optionally be a list of DTMF digits, specified as a string or a sequence
        of possibly mixed ints and strings. Playback ends immediately when one is received and it is
        returned. If nothing is recieved, `None` is returned.

        `AGIAppError` is raised on failure, most commonly because the channel was
        hung-up.
        """
        if seconds is None:
            seconds = int(time.time())
        return self._say('TIME', seconds, escape_digits)
        
    def send_image(self, filename):
        """
        Sends the specified image, which is the `filename` of the file to be presented, either in
        an Asterisk-searched directory or as an absolute path, without extension. ('myfile.png'
        would be specified as 'myfile', to allow Asterisk to choose the most efficient encoding,
        based on extension, for the channel)

        `AGIAppError` is raised on failure.
        """
        self.execute('SEND FILE', True, self._quote(filename))
        
    def send_text(self, text):
        """
        Sends the specified `text` on a supporting channel.

        `AGIAppError` is raised on failure.
        """
        self.execute('SEND TEXT', True, self._quote(text))

    def set_autohangup(self, seconds=0):
        """
        Instructs Asterisk to hang up the channel after the given number of `seconds` have elapsed.

        Calling this function with `seconds` set to 0, the default, will disable auto-hangup.

        `AGIAppError` is raised on failure.
        """
        self.execute('SET AUTOHANGUP', True, self._quote(seconds))
        
    def set_callerid(self, number, name=None):
        """
        Sets the called ID (`number` and, optionally, `name`) of Asterisk on this channel.

        `AGIAppError` is raised on failure.
        """
        if name:
            name = '\\"%(name)s\\"' % {
             'name': name,
            }
        else:
            name = ''
        number = "%(name)s<%(number)s>" % {
         'name': name,
         'number': number,
        }
        self.execute('SET CALLERID', True, self._quote(number))
        
    def set_context(self, context):
        """
        Sets the context for Asterisk to use upon completion of this AGI instance.
        
        No context-validation is performed; specifying an invalid context will cause the call to
        terminate unexpectedly.
        
        `AGIAppError` is raised on failure.
        """
        self.execute('SET CONTEXT', True, self._quote(context))

    def set_extension(self, extension):
        """
        Sets the extension for Asterisk to use upon completion of this AGI instance.
        
        No extension-validation is performed; specifying an invalid extension will cause the call to
        terminate unexpectedly.
        
        `AGIAppError` is raised on failure.
        """
        self.execute('SET EXTENSION', True, self._quote(extension))
        
    def set_music_on_hold(self, on, moh_class=None):
        """
        Enables or disables music-on-hold for this channel, per the state of the `on` argument.

        If specified, `moh_class` identifies the music-on-hold class to be used.
        
        `AGIAppError` is raised on failure.
        """
        self.execute(
         'SET MUSIC', True, self._quote(on and 'on' or 'off'),
         (moh_class and self._quote(moh_class) or None)
        )
        
    def set_priority(self, priority):
        """
        Sets the priority for Asterisk to use upon completion of this AGI instance.
        
        No priority-validation is performed; specifying an invalid priority will cause the call to
        terminate unexpectedly.
        
        `AGIAppError` is raised on failure.
        """
        self.execute('SET PRIORITY', True, self._quote(priority))
        
    def set_variable(self, name, value):
        """
        Sets the variable identified by `name` to `value` on the current channel.

        `AGIAppError` is raised on failure.
        """
        self.execute('SET VARIABLE', True, self._quote(name), self._quote(value))
        
    def stream_file(self, filename, escape_digits='', sample_offset=0):
        """
        See also `control_stream_file`, `get_data`, `get_option`.

        Plays back the specified file, which is the `filename` of the file to be played, either in
        an Asterisk-searched directory or as an absolute path, without extension. ('myfile.wav'
        would be specified as 'myfile', to allow Asterisk to choose the most efficient encoding,
        based on extension, for the channel)
        
        `escape_digits` may optionally be a list of DTMF digits, specified as a string or a sequence
        of possibly mixed ints and strings. Playback ends immediately when one is received.
        
        `sample_offset` may be used to jump an arbitrary number of milliseconds into the audio data.
        
        The value returned is a tuple consisting of (dtmf_key:str, offset:int), where the offset is
        the number of milliseconds that elapsed since the start of playback, or None if playback
        completed successfully or the sample could not be opened.
        
        `AGIAppError` is raised on failure, most commonly because the channel was
        hung-up.
        """
        escape_digits = self._process_digit_list(escape_digits)
        response = self.execute(
         'STREAM FILE', True, self._quote(filename),
         self._quote(escape_digits), self._quote(sample_offset)
        )
        result = response.items.get(_RESULT_KEY)
        if not result.value == '0':
            dtmf_character = self._convert_to_char(result.value, response.items)
            offset = self._convert_to_int(response.items)
            return (dtmf_character, offset)
        return None
        
    def tdd_mode(self, mode):
        """
        Sets the TDD transmission `mode` on supporting channels, one of the following:
        - TDD_ON
        - TDD_OFF
        - TDD_MATE
        
        `True` is returned if the mode is set, `False` if the channel isn't capable, and
        `AGIAppError` is raised if a problem occurs. According to documentation from 2006,
        all non-capable channels will cause an exception to occur.
        """
        response = self.execute('TDD MODE', True, mode)
        result = response.items.get(_RESULT_KEY)
        return result.value == '1'
        
    def verbose(self, message, level=LOG_INFO):
        """
        Causes Asterisk to process `message`, logging it to console or disk,
        depending on whether `level` is greater-than-or-equal-to Asterisk's
        corresponding verbosity threshold.
        
        `level` is one of the following, defaulting to LOG_INFO:
        - LOG_DEBUG
        - LOG_INFO
        - LOG_WARN
        - LOG_ERROR
        - LOG_CRITICAL
        
        `AGIAppError` is raised on failure.
        """
        self.execute('VERBOSE', True, self._quote(message), self._quote(level))
        
    def wait_for_digit(self, timeout=-1):
        """
        Waits for up to `timeout` milliseconds for a DTMF keypress to be received, returning that
        value. By default, this function blocks indefinitely.

        If no DTMF key is pressed, `None` is returned.
        
        `AGIAppError` is raised on failure, most commonly because the channel was
        hung-up.
        """
        response = self.execute('WAIT FOR DIGIT', True, self._quote(timeout))
        result = response.items.get(_RESULT_KEY)
        if not result.value == '0':
            return self._convert_to_char(result.value, response.items)
        return None
        

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
    
class AGIUnknownError(AGIError):
    """
    An error raised when an unknown response is received from Asterisk.
    """
    
class AGIAppError(AGIError):
    """
    An error raised when an attempt to make use of an Asterisk application
    fails.
    """
    
class AGIDBError(AGIAppError):
    """
    Indicates that Asterisk encountered an error while interactive with its
    database.
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
    
