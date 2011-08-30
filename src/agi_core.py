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

_ValueData = collections.namedtuple('ValueData', ('value', 'data', 'raw'))

_RE_CODE = re.compile(r'(^\d*)\s*(.*)') #Matches Asterisk's response-code lines
_RE_KV = re.compile(r'(?P<key>\w+)=(?P<raw>.*)') #Matches Asterisk's key-value response-pairs
_RE_VD = re.compile(r'(?P<value>[^\s]+)(?:\s+\((?P<data>.*)\))?') #Matches Asterisk's value-data response-pairs

CHANNEL_DOWN_AVAILABLE = 0 #Channel is down and available
CHANNEL_DOWN_RESERVED = 1 #Channel is down and reserved
CHANNEL_OFFHOOK = 2 #Channel is off-hook
CHANNEL_DIALED = 3 #A destination address has been specified
CHANNEL_ALERTING = 4 #The channel is locally ringing
CHANNEL_REMOTE_ALERTING = 5 #The channel is remotely ringing
CHANNEL_UP = 6 #The channel is connected
CHANNEL_BUSY = 7 #The channel is in a busy, non-conductive state

class _AGI(object):
    """
    This class encapsulates communication between Asterisk an a python script.
    It handles encoding commands to Asterisk and parsing responses from
    Asterisk. 
    """
    _environment = None #The environment variables received from Asterisk for this channel
    _rfile = None #The input file-object
    _wfile = None #The output file-object
    
    def __init__(self):
        """
        Sets up variables required to process an AGI session.
        """
        self._environment = {}
        self._parse_agi_environment()
        
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
                    
    def _quote(self, value):
        """
        Encapsulates `value` in double-quotes and coerces it into a string, if
        necessary.
        """
        return '"%(string)s"' % {
         'string': str(string),
        }
        
    def _test_hangup(self):
        """
        Tests to see if the channel has been hung up.
        
        At present, this is a no-op because no generic hang-up conditions are
        known, but subclasses may have specific scenarios to test for.
        """
        return
        
    def agi_get_environment(self):
        """
        Returns Asterisk's initial environment values.
        
        Note that this function returns a copy of the values, so repeated calls
        are less favourable than storing the returned value locally and
        dissecting it there.
        """
        return self._environment.copy()
        
    def answer(self):
        """
        Answers the call on the channel.
        
        If the channel has already been answered, this is a no-op.

        `AGIAppError` is raised on failure, most commonly because the connection
        could not be established.
        """
        self.execute('ANSWER')
        
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
        response = self.execute('EXEC', application, (options and self._quote(options)) or '')
        result = response.get('result')
        if result:
            if result.value == '-2':
                raise AGIAppError("Unable to execute application '%(application)s'" % {
                 'application': application,
                })
            return result.raw
        raise AGIAppError("No response received after executing application '%(application)s'" % {
         'application': application,
        })
        
    def channel_status(self, channel=''):
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
        response = self.execute('CHANNEL STATUS', (channel and self._quote(channel)) or '')
        result = response.get('result')
        if not result:
            raise AGIAppError("'result' key-value pair not received from Asterisk")

        try:
            return int(result.value)
        except ValueError:
            raise AGIAppError("'result' key-value pair received from Asterisk contained a non-numeric value: %(value)s" % {
             'value': result.value,
            })
            
    def control_stream_file(self, filename, escape_digits='', skipms=0, forward='', rewind='', pause=''):
        """
        Plays back the specified file, which is the `filename` of the file to be played, either in
        an Asterisk-searched directory or as an absolute path, without extension. ('myfile.wav'
        would be specified as 'myfile', to allow Asterisk to choose the most efficient encoding,
        based on extension, for the channel)
        
        `escape_digits` must be a list of DTMF digits, specified as a string or a sequence of
        possibly mixed ints and strings. Playback ends immediately when one is received.

        `skipms` may be used to jump an arbitrary number of milliseconds into the audio data.

        If specified, `forward`, `rewind`, and `pause` are DTMF characters that will seek forwards
        and backwards in the audio stream or pause it temporarily; by default, these features are
        disabled.

        If a DTMF key is received, it is returned as a string. If nothing is received or the file
        could not be played back (see Asterisk logs), '0' is returned. None is returned if the
        'result' key isn't received.
        
        `AGIAppError` is raised on failure, most commonly because the channel was
        hung-up.
        """
        escape_digits = self._process_digit_list(escape_digits)
        response = self.execute(
         'CONTROL STREAM FILE', self._quote(filename),
         self._quote(escape_digits), self._quote(skipms),
         self._quote(fwd), self._quote(rew), self._quote(pause)
        )
        result = response.get('result')
        if result:
            return result.value
            
    def database_del(self, family, key):
        """
        Deletes the specified family/key entry from Asterisk's database.
        
        `AGIAppError` is raised on failure.
        
        `AGIDBError` is raised if the key could not be removed, which usually indicates that it
        didn't exist in the first place.
        """
        response = self.execute('DATABASE DEL', self._quote(family), self._quote(key))
        result = response.get('result')
        if result and result.value == '0':
            raise AGIDBError("Unable to delete from database: family=%(family)s, key=%(key)s" % {
             'family': family,
             'key': key,
            })
            
    def database_deltree(self, family, keytree=''):
        """
        Deletes the specificed family (and optinally keytree) from Asterisk's database.

        `AGIAppError` is raised on failure.
        
        `AGIDBError` is raised if the family (or keytree) could not be removed, which usually
        indicates that it didn't exist in the first place.
        """
        response = self.execute('DATABASE DELTREE', self._quote(family), self._quote(key))
        result = response.get('result')
        if result and result.value == '0':
            raise AGIDBError("Unable to delete family from database: family=%(family)s, keytree=%(keytree)s" % {
             'family': family,
             'keytree': keytree or '<unspecified>',
            })
            
    def database_get(self, family, key):
        """
        Retrieves the value of the specified family/key entry from Asterisk's database.
        
        `AGIAppError` is raised on failure.
        
        `AGIDBError` is raised if the key could not be found or if some other database problem
        occurs.
        """
        response = self.execute('DATABASE GET', self._quote(family), self._quote(key))
        result = response.get('result')
        if result:
            if result.value == '0':
                raise AGIDBError("Key not found in database: family=%(family)s, key=%(key)s" % {
                 'family': family,
                 'key': key,
                })
            elif result.value == '1':
                return result.data
        raise AGIDBError("Unable to query database: family=%(family)s, key=%(key)s, result=%(result)s" % {
         'family': family,
         'key': key,
         'result': (result and result.value) or '<no-result>',
        })
        
    def database_put(self, family, key, value):
        """
        Inserts or updates value of the specified family/key entry in Asterisk's database.
        
        `AGIAppError` is raised on failure.
        
        `AGIDBError` is raised if the key could not be inserted or if some other database problem
        occurs.
        """
        response = self.execute('DATABASE PUT', self._quote(family), self._quote(key), self._quote(value))
        result = response.get('result')
        if not result or result.value == '0':
            raise AGIDBError("Unable to store value in database: family=%(family)s, key=%(key)s, value=%(value)s" % {
             'family': family,
             'key': key,
             'value': value,
            })
            
    def noop(self):
        """
        Does nothing.
        
        Good for testing the connection to the Asterisk server, like a ping, but
        not useful for much else. If you wish to log information through
        Asterisk, use the `verbose` method instead.
        
        `AGIAppError` is raised on failure.
        """
        self.execute('NOOP')
        
    def verbose(self, message, level=1):
        """
        Causes Asterisk to process `message`, logging it to console or disk,
        depending on whether `level` is greater-than-or-equal-to Asterisk's
        corresponding verbosity threshold.
        
        `level` defaults to 1, which is nominally akin to 'INFO', with 0 being
        'DEBUG', 2, being 'WARN', 3 being 'ERROR', and 4 being 'CRITICAL'.
        
        `AGIAppError` is raised on failure.
        """
        self.execute('VERBOSE', self._quote(message), self._quote(level))
        
        
        
        
        
        
    def execute(self, command, *args):
        self._test_hangup()
        
        self._send_command(command, *args)
        return self._get_result()
        
    def _send_command(self, command, *args):
        """Send a command to Asterisk"""
        command = ('%s %s' % (command.strip(), ' '.join(map(str,args)))).strip()
        if command[-1] != '\n':
            command += '\n'
            
        try:
            self._wfile.write(command)
            self._wfile.flush()
        except Exception as e:
            raise AGISIGPIPEHangup("Socket link broken: %(error)s" % {
             'error': str(e),
            })
            
    def _get_result(self):
        """Read the result of a command from Asterisk"""
        code = 0
        result = {'result':('','')}
        line = self._read_line()
        m = _RE_CODE.search(line)
        if m:
            code = int(m.group(1))
            
        if code == 200:
            for (key, raw) in _RE_KV.findall(m.group(2)):
                value = raw
                data = None
                kd_m = _RE_KD.match(raw)
                if kd_m:
                    value = kd_m.group('value')
                    data = kd_m.group('data')
                result[key] = _ValueData(value, data, raw)
                
                # If user hangs up... we get 'hangup' in the data
                if data == 'hangup':
                    raise AGIResultHangup("User hung up during execution")
                elif key == 'result' and value == '-1':
                    raise AGIAppError("Error executing application or the channel was hung up")
                    
            return result
        elif code == 510:
            raise AGIInvalidCommandError(response)
        elif code == 511:
            raise AGIDeadChannelError(response)
        elif code == 520:
            usage = [line]
            line = self._read_line()
            while line[:3] != '520':
                usage.append(line)
                line = self._read_line()
            usage.append(line)
            usage = '%s\n' % '\n'.join(usage)
            raise AGIUsageError(usage)
        else:
            raise AGIUnknownError(code, 'Unhandled code or undefined response')

    def _read_line(self):
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
            
    def _process_digit_list(self, digits):
        if type(digits) in (list, tuple):
            digits = ''.join(map(str, digits))
        return self._quote(digits)

    
    
        
    def wait_for_digit(self, timeout=-1):
        """agi.wait_for_digit(timeout=-1) --> digit
        Waits for up to 'timeout' milliseconds for a channel to receive a DTMF
        digit.  Returns digit dialed
        Throws AGIError on channel falure
        """
        res = self.execute('WAIT FOR DIGIT', timeout)['result'][0]
        if res == '0':
            return ''
        else:
            try:
                return chr(int(res))
            except ValueError:
                raise AGIError('Unable to convert result to digit: %s' % res)

    def send_text(self, text=''):
        """agi.send_text(text='') --> None
        Sends the given text on a channel.  Most channels do not support the
        transmission of text.
        Throws AGIError on error/hangup
        """
        self.execute('SEND TEXT', self._quote(text))['result'][0]

    def receive_char(self, timeout=0):
        """agi.receive_char(timeout=0) --> chr
        Receives a character of text on a channel.  Specify timeout to be the
        maximum time to wait for input in milliseconds, or 0 for infinite. Most channels
        do not support the reception of text.
        """
        res = self.execute('RECEIVE CHAR', timeout)['result'][0]

        if res == '0':
            return ''
        else:
            try:
                return chr(int(res))
            except:
                raise AGIError('Unable to convert result to char: %s' % res)

    def tdd_mode(self, mode='off'):
        """agi.tdd_mode(mode='on'|'off') --> None
        Enable/Disable TDD transmission/reception on a channel. 
        Throws AGIAppError if channel is not TDD-capable.
        """
        res = self.execute('TDD MODE', mode)['result'][0]
        if res == '0':
            raise AGIAppError('Channel is not TDD-capable')
            
    def stream_file(self, filename, escape_digits='', sample_offset=0):
        """agi.stream_file(filename, escape_digits='', sample_offset=0) --> digit
        Send the given file, allowing playback to be interrupted by the given
        digits, if any.  escape_digits is a string '12345' or a list  of 
        ints [1,2,3,4,5] or strings ['1','2','3'] or mixed [1,'2',3,'4']
        If sample offset is provided then the audio will seek to sample
        offset before play starts.  Returns  digit if one was pressed.
        Throws AGIError if the channel was disconnected.  Remember, the file
        extension must not be included in the filename.
        """
        escape_digits = self._process_digit_list(escape_digits)
        response = self.execute('STREAM FILE', filename, escape_digits, sample_offset)
        res = response['result'][0]
        if res == '0':
            return ''
        else:
            try:
                return chr(int(res))
            except:
                raise AGIError('Unable to convert result to char: %s' % res)
    
    

    def send_image(self, filename):
        """agi.send_image(filename) --> None
        Sends the given image on a channel.  Most channels do not support the
        transmission of images.   Image names should not include extensions.
        Throws AGIError on channel failure
        """
        res = self.execute('SEND IMAGE', filename)['result'][0]
        if res != '0':
            raise AGIAppError('Channel falure on channel %s' % self.env.get('agi_channel','UNKNOWN'))

    def say_digits(self, digits, escape_digits=''):
        """agi.say_digits(digits, escape_digits='') --> digit
        Say a given digit string, returning early if any of the given DTMF digits
        are received on the channel.  
        Throws AGIError on channel failure
        """
        digits = self._process_digit_list(digits)
        escape_digits = self._process_digit_list(escape_digits)
        res = self.execute('SAY DIGITS', digits, escape_digits)['result'][0]
        if res == '0':
            return ''
        else:
            try:
                return chr(int(res))
            except:
                raise AGIError('Unable to convert result to char: %s' % res)

    def say_number(self, number, escape_digits=''):
        """agi.say_number(number, escape_digits='') --> digit
        Say a given digit string, returning early if any of the given DTMF digits
        are received on the channel.  
        Throws AGIError on channel failure
        """
        number = self._process_digit_list(number)
        escape_digits = self._process_digit_list(escape_digits)
        res = self.execute('SAY NUMBER', number, escape_digits)['result'][0]
        if res == '0':
            return ''
        else:
            try:
                return chr(int(res))
            except:
                raise AGIError('Unable to convert result to char: %s' % res)

    def say_alpha(self, characters, escape_digits=''):
        """agi.say_alpha(string, escape_digits='') --> digit
        Say a given character string, returning early if any of the given DTMF
        digits are received on the channel.  
        Throws AGIError on channel failure
        """
        characters = self._process_digit_list(characters)
        escape_digits = self._process_digit_list(escape_digits)
        res = self.execute('SAY ALPHA', characters, escape_digits)['result'][0]
        if res == '0':
            return ''
        else:
            try:
                return chr(int(res))
            except:
                raise AGIError('Unable to convert result to char: %s' % res)

    def say_phonetic(self, characters, escape_digits=''):
        """agi.say_phonetic(string, escape_digits='') --> digit
        Phonetically say a given character string, returning early if any of
        the given DTMF digits are received on the channel.  
        Throws AGIError on channel failure
        """
        characters = self._process_digit_list(characters)
        escape_digits = self._process_digit_list(escape_digits)
        res = self.execute('SAY PHONETIC', characters, escape_digits)['result'][0]
        if res == '0':
            return ''
        else:
            try:
                return chr(int(res))
            except:
                raise AGIError('Unable to convert result to char: %s' % res)

    def say_date(self, seconds, escape_digits=''):
        """agi.say_date(seconds, escape_digits='') --> digit
        Say a given date, returning early if any of the given DTMF digits are
        pressed.  The date should be in seconds since the UNIX Epoch (Jan 1, 1970 00:00:00)
        """
        escape_digits = self._process_digit_list(escape_digits)
        res = self.execute('SAY DATE', seconds, escape_digits)['result'][0]
        if res == '0':
            return ''
        else:
            try:
                return chr(int(res))
            except:
                raise AGIError('Unable to convert result to char: %s' % res)

    def say_time(self, seconds, escape_digits=''):
        """agi.say_time(seconds, escape_digits='') --> digit
        Say a given time, returning early if any of the given DTMF digits are
        pressed.  The time should be in seconds since the UNIX Epoch (Jan 1, 1970 00:00:00)
        """
        escape_digits = self._process_digit_list(escape_digits)
        res = self.execute('SAY TIME', seconds, escape_digits)['result'][0]
        if res == '0':
            return ''
        else:
            try:
                return chr(int(res))
            except:
                raise AGIError('Unable to convert result to char: %s' % res)
    
    def say_datetime(self, seconds, escape_digits='', format='', zone=''):
        """agi.say_datetime(seconds, escape_digits='', format='', zone='') --> digit
        Say a given date in the format specfied (see voicemail.conf), returning
        early if any of the given DTMF digits are pressed.  The date should be
        in seconds since the UNIX Epoch (Jan 1, 1970 00:00:00).
        """
        escape_digits = self._process_digit_list(escape_digits)
        if format: format = self._quote(format)
        res = self.execute('SAY DATETIME', seconds, escape_digits, format, zone)['result'][0]
        if res == '0':
            return ''
        else:
            try:
                return chr(int(res))
            except:
                raise AGIError('Unable to convert result to char: %s' % res)

    def get_data(self, filename, timeout=0, max_digits=255):
        """agi.get_data(filename, timeout=0, max_digits=255) --> digits
        Stream the given file and receive dialed digits
        """
        result = self.execute('GET DATA', filename, timeout, max_digits)
        res, value = result['result']
        return res
    
    def get_option(self, filename, escape_digits='', timeout=0):
        """agi.get_option(filename, escape_digits='', timeout=0) --> digit
        Send the given file, allowing playback to be interrupted by the given
        digits, if any.  escape_digits is a string '12345' or a list  of 
        ints [1,2,3,4,5] or strings ['1','2','3'] or mixed [1,'2',3,'4']
        Returns  digit if one was pressed.
        Throws AGIError if the channel was disconnected.  Remember, the file
        extension must not be included in the filename.
        """
        escape_digits = self._process_digit_list(escape_digits)
        if timeout:
            response = self.execute('GET OPTION', filename, escape_digits, timeout)
        else:
            response = self.execute('GET OPTION', filename, escape_digits)

        res = response['result'][0]
        if res == '0':
            return ''
        else:
            try:
                return chr(int(res))
            except:
                raise AGIError('Unable to convert result to char: %s' % res)

    def set_context(self, context):
        """agi.set_context(context)
        Sets the context for continuation upon exiting the application.
        No error appears to be produced.  Does not set exten or priority
        Use at your own risk.  Ensure that you specify a valid context.
        """
        self.execute('SET CONTEXT', context)

    def set_extension(self, extension):
        """agi.set_extension(extension)
        Sets the extension for continuation upon exiting the application.
        No error appears to be produced.  Does not set context or priority
        Use at your own risk.  Ensure that you specify a valid extension.
        """
        self.execute('SET EXTENSION', extension)

    def set_priority(self, priority):
        """agi.set_priority(priority)
        Sets the priority for continuation upon exiting the application.
        No error appears to be produced.  Does not set exten or context
        Use at your own risk.  Ensure that you specify a valid priority.
        """
        self.execute('set priority', priority)

    def goto_on_exit(self, context='', extension='', priority=''):
        context = context or self.env['agi_context']
        extension = extension or self.env['agi_extension']
        priority = priority or self.env['agi_priority']
        self.set_context(context)
        self.set_extension(extension)
        self.set_priority(priority)

    def record_file(self, filename, format='gsm', escape_digits='#', timeout=-1, offset=0, beep='beep'):
        """agi.record_file(filename, format, escape_digits, timeout=-1, offset=0, beep='beep') --> None
        Record to a file until a given dtmf digit in the sequence is received
        The format will specify what kind of file will be recorded.  The timeout 
        is the maximum record time in milliseconds, or -1 for no timeout. Offset 
        samples is optional, and if provided will seek to the offset without 
        exceeding the end of the file
        """
        escape_digits = self._process_digit_list(escape_digits)
        res = self.execute('RECORD FILE', self._quote(filename), format, escape_digits, timeout, offset, beep)['result'][0]
        try:
            return chr(int(res))
        except:
            raise AGIError('Unable to convert result to digit: %s' % res)

    def set_autohangup(self, secs):
        """agi.set_autohangup(secs) --> None
        Cause the channel to automatically hangup at <secs> seconds in the
        future.  Of course it can be hungup before then as well.   Setting to
        0 will cause the autohangup feature to be disabled on this channel.
        """
        self.execute('SET AUTOHANGUP', secs)

    def hangup(self, channel=''):
        """agi.hangup(channel='')
        Hangs up the specified channel.
        If no channel name is given, hangs up the current channel
        """
        self.execute('HANGUP', channel)

    

    def set_callerid(self, number):
        """agi.set_callerid(number) --> None
        Changes the callerid of the current channel.
        """
        self.execute('SET CALLERID', number)

    

    def set_variable(self, name, value):
        """Set a channel variable.
        """
        self.execute('SET VARIABLE', self._quote(name), self._quote(value))

    def get_variable(self, name):
        """Get a channel variable.

        This function returns the value of the indicated channel variable.  If
        the variable is not set, an empty string is returned.
        """
        try:
           result = self.execute('GET VARIABLE', self._quote(name))
        except AGIResultHangup:
           result = {'result': ('1', 'hangup')}

        res, value = result['result']
        return value

    def get_full_variable(self, name, channel = None):
        """Get a channel variable.

        This function returns the value of the indicated channel variable.  If
        the variable is not set, an empty string is returned.
        """
        try:
           if channel:
              result = self.execute('GET FULL VARIABLE', self._quote(name), self._quote(channel))
           else:
              result = self.execute('GET FULL VARIABLE', self._quote(name))

        except AGIResultHangup:
           result = {'result': ('1', 'hangup')}

        res, value = result['result']
        return value

    

    
        
        
class AGIException(Exception):
    """
    The base exception from which all exceptions native to this module inherit.
    """
    
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
    
