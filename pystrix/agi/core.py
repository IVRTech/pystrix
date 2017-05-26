"""
pystrix.agi.core
================

All standard AGI actions as instantiable classes, suitable for passing to the
`execute()` function of an AGI interface.

Also includes constants to make programmatic interaction cleaner.
 
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
import time

from pystrix.agi.agi_core import (
    _Action,
    quote,
    _RESULT_KEY,
    AGIAppError,
)

CHANNEL_DOWN_AVAILABLE = 0  # Channel is down and available
CHANNEL_DOWN_RESERVED = 1  # Channel is down and reserved
CHANNEL_OFFHOOK = 2  # Channel is off-hook
CHANNEL_DIALED = 3  # A destination address has been specified
CHANNEL_ALERTING = 4  # The channel is locally ringing
CHANNEL_REMOTE_ALERTING = 5  # The channel is remotely ringing
CHANNEL_UP = 6  # The channel is connected
CHANNEL_BUSY = 7  # The channel is in a busy, non-conductive state

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


# Functions
###############################################################################
def _convert_to_char(value, items):
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


def _convert_to_int(items):
    """
    Extracts the offset-value from Asterisk's response, `items`, or returns -1 if the value
    can't be parsed.
    """
    offset = items.get('endpos')
    if offset and offset.data.isdigit():
        return int(offset.data)
    else:
        return -1


def _process_digit_list(digits):
    """
    Ensures that digit-lists are processed uniformly.
    """
    if type(digits) in (list, tuple, set, frozenset):
        digits = ''.join([str(d) for d in digits])
    return quote(digits)


# Classes
###############################################################################
class Answer(_Action):
    """
    Answers the call on the channel.
    
    If the channel has already been answered, this is a no-op.

    `AGIAppError` is raised on failure, most commonly because the connection
    could not be established.
    """

    def __init__(self):
        _Action.__init__(self, 'ANSWER')


class ChannelStatus(_Action):
    """
    Provides the current state of this channel or, if `channel` is set, that of the named
    channel.
    
    Returns one of the channel-state constants listed below:
    
    - CHANNEL_DOWN_AVAILABLE: Channel is down and available
    - CHANNEL_DOWN_RESERVED: Channel is down and reserved
    - CHANNEL_OFFHOOK: Channel is off-hook
    - CHANNEL_DIALED: A destination address has been specified
    - CHANNEL_ALERTING: The channel is locally ringing
    - CHANNEL_REMOTE_ALERTING: The channel is remotely ringing
    - CHANNEL_UP: The channel is connected
    - CHANNEL_BUSY: The channel is in a busy, non-conductive state

    The value returned is an integer in the range 0-7; values outside of
    that range were undefined at the time of writing, but will be returned
    verbatim. Applications unprepared to handle unknown states should
    raise an exception upon their receipt or otherwise handle the code
    gracefully.

    `AGIAppError` is raised on failure, most commonly because the channel is
    in a hung-up state.
    """

    def __init__(self, channel=None):
        _Action.__init__(self, 'CHANNEL STATUS', (channel and quote(channel)) or None)

    def process_response(self, response):
        result = response.items.get(_RESULT_KEY)
        try:
            return int(result.value)
        except ValueError:
            raise AGIAppError(
                "'%(result-key)s' key-value pair received from Asterisk contained a non-numeric value: %(value)r" % {
                    'result-key': _RESULT_KEY,
                    'value': result.value,
                }, response.items)


class ControlStreamFile(_Action):
    """
    See also `GetData`, `GetOption`, `StreamFile`.
    
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

    def __init__(self, filename, escape_digits='', sample_offset=0, forward='', rewind='', pause=''):
        escape_digits = _process_digit_list(escape_digits)
        _Action.__init__(self, 'CONTROL STREAM FILE', quote(filename),
                         quote(escape_digits), quote(sample_offset),
                         quote(forward), quote(rewind), quote(pause)
                         )

    def process_response(self, response):
        result = response.items.get(_RESULT_KEY)
        if not result.value == '0':
            return _convert_to_char(result.value, response.items)
        return None


class DatabaseDel(_Action):
    """
    Deletes the specified family/key entry from Asterisk's database.
    
    `AGIAppError` is raised on failure.
    
    `AGIDBError` is raised if the key could not be removed, which usually indicates that it
    didn't exist in the first place.
    """

    def __init__(self, family, key):
        _Action.__init__(self, 'DATABASE DEL', quote(family), quote(key))
        self.family = family
        self.key = key

    def process_response(self, response):
        result = response.items.get(_RESULT_KEY)
        if result.value == '0':
            raise AGIDBError("Unable to delete from database: family=%(family)r, key=%(key)r" % {
                'family': self.family,
                'key': self.key,
            }, response.items)


class DatabaseDeltree(_Action):
    """
    Deletes the specificed family (and optionally keytree) from Asterisk's database.

    `AGIAppError` is raised on failure.
    
    `AGIDBError` is raised if the family (or keytree) could not be removed, which usually
    indicates that it didn't exist in the first place.
    """

    def __init__(self, family, keytree=None):
        _Action.__init__(self,
                         'DATABASE DELTREE', quote(family), (keytree and quote(keytree) or None)
                         )
        self.family = family
        self.keytree = keytree

    def process_response(self, response):
        result = response.items.get(_RESULT_KEY)
        if result.value == '0':
            raise AGIDBError("Unable to delete family from database: family=%(family)r, keytree=%(keytree)r" % {
                'family': self.family,
                'keytree': self.keytree or '<unspecified>',
            }, response.items)


class DatabaseGet(_Action):
    """
    Retrieves the value of the specified family/key entry from Asterisk's database.
    
    `AGIAppError` is raised on failure.
    
    `AGIDBError` is raised if the key could not be found or if some other database problem
    occurs.
    """
    check_hangup = False

    def __init__(self, family, key):
        _Action.__init__(self, 'DATABASE GET', quote(family), quote(key))
        self.family = family
        self.key = key

    def process_response(self, response):
        result = response.items.get(_RESULT_KEY)
        if result.value == '0':
            raise AGIDBError("Key not found in database: family=%(family)r, key=%(key)r" % {
                'family': self.family,
                'key': self.key,
            }, response.items)
        elif result.value == '1':
            return result.data

        raise AGIDBError("Unable to query database: family=%(family)r, key=%(key)r, result=%(result)r" % {
            'family': self.family,
            'key': self.key,
            'result': result.value,
        }, response.items)


class DatabasePut(_Action):
    """
    Inserts or updates value of the specified family/key entry in Asterisk's database.
    
    `AGIAppError` is raised on failure.
    
    `AGIDBError` is raised if the key could not be inserted or if some other database problem
    occurs.
    """

    def __init__(self, family, key, value):
        _Action.__init__(self, 'DATABASE PUT', quote(family), quote(key), quote(value))
        self.family = family
        self.key = key
        self.value = value

    def process_response(self, response):
        result = response.items.get(_RESULT_KEY)
        if result.value == '0':
            raise AGIDBError("Unable to store value in database: family=%(family)r, key=%(key)r, value=%(value)r" % {
                'family': self.family,
                'key': self.key,
                'value': self.value,
            }, response.items)


class Exec(_Action):
    """
    Executes an arbitrary Asterisk `application` with the given `options`, returning that
    application's output.

    `options` is an optional sequence of arguments, with any double-quote characters or commas
    explicitly escaped.

    `AGIAppError` is raised if the application could not be executed.
    """
    check_hangup = False

    def __init__(self, application, options=()):
        self._application = application
        options = ','.join((str(o or '') for o in options))
        _Action.__init__(self, 'EXEC', self._application, (options and quote(options)) or '')

    def process_response(self, response):
        result = response.items.get(_RESULT_KEY)
        if result.value == '-2':
            raise AGIAppError("Unable to execute application '%(application)r'" % {
                'application': self._application,
            }, response.items)
        return response.raw[7:]  # Everything after 'result='


class GetData(_Action):
    """
    See also `ControlStreamFile`, `GetOption`, `StreamFile`.
    
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
    
    `AGIAppError` is raised on failure, most commonly because no keys, aside from '#', were
    entered.
    """

    def __init__(self, filename, timeout=2000, max_digits=255):
        _Action.__init__(self,
                         'GET DATA', quote(filename), quote(timeout), quote(max_digits)
                         )

    def process_response(self, response):
        result = response.items.get(_RESULT_KEY)
        return (result.value, result.data == 'timeout')


class GetFullVariable(_Action):
    """
    Returns a `variable` associated with this channel, with full expression-processing.
    
    The value of the requested variable is returned as a string. If the variable is
    undefined, `None` is returned.

    `AGIAppError` is raised on failure.
    """
    check_hangup = False

    def __init__(self, variable):
        _Action.__init__(self, 'GET FULL VARIABLE', quote(variable))

    def process_response(self, response):
        result = response.items.get(_RESULT_KEY)
        if result.value == '1':
            return result.data
        return None


class GetOption(_Action):
    """
    See also `ControlStreamFile`, `GetData`, `StreamFile`.

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

    def __init__(self, filename, escape_digits='', timeout=2000):
        escape_digits = _process_digit_list(escape_digits)
        _Action.__init__(self,
                         'GET OPTION', quote(filename),
                         quote(escape_digits), quote(timeout)
                         )

    def process_response(self, response):
        result = response.items.get(_RESULT_KEY)
        if not result.value == '0':
            dtmf_character = _convert_to_char(result.value, response.items)
            offset = _convert_to_int(response.items)
            return (dtmf_character, offset)
        return None


class GetVariable(_Action):
    """
    Returns a `variable` associated with this channel.
    
    The value of the requested variable is returned as a string. If the variable is
    undefined, `None` is returned.

    `AGIAppError` is raised on failure.
    """
    check_hangup = False

    def __init__(self, variable):
        _Action.__init__(self, 'GET VARIABLE', quote(variable))

    def process_response(self, response):
        result = response.items.get(_RESULT_KEY)
        if result.value == '1':
            return result.data
        return None


class Hangup(_Action):
    """
    Hangs up this channel or, if `channel` is set, the named channel.

    `AGIAppError` is raised on failure.
    """

    def __init__(self, channel=None):
        _Action.__init__(self, 'HANGUP', (channel and quote(channel) or None))


class Noop(_Action):
    """
    Does nothing.
    
    Good for testing the connection to the Asterisk server, like a ping, but
    not useful for much else. If you wish to log information through
    Asterisk, use the `verbose` method instead.
    
    `AGIAppError` is raised on failure.
    """

    def __init__(self):
        _Action.__init__(self, 'NOOP')


class ReceiveChar(_Action):
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

    def __init__(self, timeout=0):
        _Action.__init__(self, 'RECEIVE CHAR', quote(timeout))

    def process_response(self, response):
        result = response.items.get(_RESULT_KEY)
        if not result.value == '0':
            return (_convert_to_char(result.value, response.items), result.data == 'timeout')
        return None


class ReceiveText(_Action):
    """
    Receives a block of text from a supporting channel.

    `timeout` is the number of milliseconds to wait for text to be received, defaulting
    to infinite. Presumably, the first block received is immediately returned in full.

    The value returned is a string.

    `AGIAppError` is raised on failure.
    """

    def __init__(self, timeout=0):
        _Action.__init__(self, 'RECEIVE TEXT', quote(timeout))

    def process_response(self, response):
        result = response.items.get(_RESULT_KEY)
        return result.value


class RecordFile(_Action):
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
    - FORMAT_WAV: PCM16

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

    def __init__(self, filename, format=FORMAT_WAV, escape_digits='', timeout=-1, sample_offset=0, beep=True,
                 silence=None):
        escape_digits = _process_digit_list(escape_digits)
        _Action.__init__(self,
                         'RECORD FILE', quote(filename), quote(format),
                         quote(escape_digits), quote(timeout), quote(sample_offset),
                         (beep and quote('beep') or None),
                         (silence and quote('s=' + str(silence)) or None)
                         )

    def process_response(self, response):
        result = response.items.get(_RESULT_KEY)
        offset = _convert_to_int(response.items)

        if result.data == 'randomerror':
            raise AGIAppError("Unknown error occurred %(ms)i into recording: %(error)s" % {
                'ms': offset,
                'error': result.value,
            })
        elif result.data == 'timeout':
            return ('', offset, True)
        elif result.data == 'dtmf':
            return (_convert_to_char(result.value, response.items), offset, False)
        return ('', offset, True)  # Assume a timeout if any other result data is received.


class _SayAction(_Action):
    """
    A specialised subclass of `_Action` that provides behaviour common to several children.
    
    Synthesises speech on a channel. This abstracts the commonalities between the "SAY ?"
    subclasses.

    `say_type` is the type of command to be issued.

    `argument` is the argument to be synthesised.

    `escape_digits` may optionally be a list of DTMF digits, specified as a string or a sequence
    of possibly mixed ints and strings. Playback ends immediately when one is received.

    `AGIAppError` is raised on failure, most commonly because the channel was
    hung-up.
    """

    def __init__(self, say_type, argument, escape_digits, *args):
        escape_digits = _process_digit_list(escape_digits)
        _Action.__init__(self,
                         'SAY ' + say_type, quote(argument), quote(escape_digits), *args
                         )

    def process_response(self, response):
        result = response.items.get(_RESULT_KEY)

        if not result.value == '0':
            return _convert_to_char(result.value, response.items)
        return None


class SayAlpha(_SayAction):
    """
    Reads an alphabetic string of `characters`.

    `escape_digits` may optionally be a list of DTMF digits, specified as a string or a sequence
    of possibly mixed ints and strings. Playback ends immediately when one is received and it is
    returned. If nothing is recieved, `None` is returned.

    `AGIAppError` is raised on failure, most commonly because the channel was
    hung-up.
    """

    def __init__(self, characters, escape_digits=''):
        characters = _process_digit_list(characters)
        _SayAction.__init__(self, 'ALPHA', characters, escape_digits)


class SayDate(_SayAction):
    """
    Reads the date associated with `seconds` since the UNIX Epoch. If not given, the local time
    is used.
    
    `escape_digits` may optionally be a list of DTMF digits, specified as a string or a sequence
    of possibly mixed ints and strings. Playback ends immediately when one is received and it is
    returned. If nothing is recieved, `None` is returned.

    `AGIAppError` is raised on failure, most commonly because the channel was
    hung-up.
    """

    def __init__(self, seconds=None, escape_digits=''):
        if seconds is None:
            seconds = int(time.time())
        _SayAction.__init__(self, 'DATE', seconds, escape_digits)


class SayDatetime(_SayAction):
    """
    Reads the datetime associated with `seconds` since the UNIX Epoch. If not given, the local
    time is used.
    
    `escape_digits` may optionally be a list of DTMF digits, specified as a string or a sequence
    of possibly mixed ints and strings. Playback ends immediately when one is received and it is
    returned. If nothing is recieved, `None` is returned.

    `format` defaults to `"ABdY 'digits/at' IMp"`, but may be a string with any of the following
    meta-characters (or single-quote-escaped sound-file references):
    
    - A: Day of the week
    - B: Month (Full Text)
    - m: Month (Numeric)
    - d: Day of the month
    - Y: Year
    - I: Hour (12-hour format)
    - H: Hour (24-hour format)
    - M: Minutes
    - p: AM/PM
    - Q: Shorthand for Today, Yesterday or ABdY
    - R: Shorthand for HM
    - S: Seconds
    - T: Timezone

    `timezone` may be a string in standard UNIX form, like 'America/Edmonton'. If `format` is
    undefined, `timezone` is ignored and left to default to the system's local value.
    
    `AGIAppError` is raised on failure, most commonly because the channel was
    hung-up.
    """

    def __init__(self, seconds=None, escape_digits='', format=None, timezone=None):
        if seconds is None:
            seconds = int(time.time())
        if not format:
            timezone = None
        _SayAction.__init__(self,
                            'DATETIME', seconds, escape_digits,
                            (format and quote(format) or None), (timezone and quote(timezone) or None)
                            )


class SayDigits(_SayAction):
    """
    Reads a numeric string of `digits`.

    `escape_digits` may optionally be a list of DTMF digits, specified as a string or a sequence
    of possibly mixed ints and strings. Playback ends immediately when one is received and it is
    returned. If nothing is recieved, `None` is returned.

    `AGIAppError` is raised on failure, most commonly because the channel was
    hung-up.
    """

    def __init__(self, digits, escape_digits=''):
        digits = _process_digit_list(digits)
        _SayAction.__init__(self, 'DIGITS', digits, escape_digits)


class SayNumber(_SayAction):
    """
    Reads a `number` naturally.

    `escape_digits` may optionally be a list of DTMF digits, specified as a string or a sequence
    of possibly mixed ints and strings. Playback ends immediately when one is received and it is
    returned. If nothing is recieved, `None` is returned.

    `AGIAppError` is raised on failure, most commonly because the channel was
    hung-up.
    """

    def __init__(self, number, escape_digits=''):
        number = _process_digit_list(number)
        _SayAction.__init__(self, 'NUMBER', number, escape_digits)


class SayPhonetic(_SayAction):
    """
    Reads a phonetic string of `characters`.

    `escape_digits` may optionally be a list of DTMF digits, specified as a string or a sequence
    of possibly mixed ints and strings. Playback ends immediately when one is received and it is
    returned. If nothing is received, `None` is returned.

    `AGIAppError` is raised on failure, most commonly because the channel was
    hung-up.
    """

    def __init__(self, characters, escape_digits=''):
        characters = _process_digit_list(characters)
        _SayAction.__init__(self, 'PHONETIC', characters, escape_digits)


class SayTime(_SayAction):
    """
    Reads the time associated with `seconds` since the UNIX Epoch. If not given, the local
    time is used.
    
    `escape_digits` may optionally be a list of DTMF digits, specified as a string or a sequence
    of possibly mixed ints and strings. Playback ends immediately when one is received and it is
    returned. If nothing is received, `None` is returned.

    `AGIAppError` is raised on failure, most commonly because the channel was
    hung-up.
    """

    def __init__(self, seconds=None, escape_digits=''):
        if seconds is None:
            seconds = int(time.time())
        _SayAction.__init__(self, 'TIME', seconds, escape_digits)


class SendImage(_Action):
    """
    Sends the specified image, which is the `filename` of the file to be presented, either in
    an Asterisk-searched directory or as an absolute path, without extension. ('myfile.png'
    would be specified as 'myfile', to allow Asterisk to choose the most efficient encoding,
    based on extension, for the channel)

    `AGIAppError` is raised on failure.
    """

    def __init__(self, filename):
        _Action.__init__(self, 'SEND FILE', quote(filename))


class SendText(_Action):
    """
    Sends the specified `text` on a supporting channel.

    `AGIAppError` is raised on failure.
    """

    def __init__(self, text):
        _Action.__init__(self, 'SEND TEXT', quote(text))


class SetAutohangup(_Action):
    """
    Instructs Asterisk to hang up the channel after the given number of `seconds` have elapsed.

    Calling this function with `seconds` set to 0, the default, will disable auto-hangup.

    `AGIAppError` is raised on failure.
    """

    def __init__(self, seconds=0):
        _Action.__init__(self, 'SET AUTOHANGUP', quote(seconds))


class SetCallerid(_Action):
    """
    Sets the called ID (`number` and, optionally, `name`) of Asterisk on this channel.

    `AGIAppError` is raised on failure.
    """

    def __init__(self, number, name=None):
        if name:  # Escape it
            name = '\\"%(name)s\\"' % {
                'name': name,
            }
        else:  # Make sure it's the empty string
            name = ''
        number = "%(name)s<%(number)s>" % {
            'name': name,
            'number': number,
        }
        _Action.__init__(self, 'SET CALLERID', quote(number))


class SetContext(_Action):
    """
    Sets the context for Asterisk to use upon completion of this AGI instance.
    
    No context-validation is performed; specifying an invalid context will cause the call to
    terminate unexpectedly.
    
    `AGIAppError` is raised on failure.
    """

    def __init__(self, context):
        _Action.__init__(self, 'SET CONTEXT', quote(context))


class SetExtension(_Action):
    """
    Sets the extension for Asterisk to use upon completion of this AGI instance.
    
    No extension-validation is performed; specifying an invalid extension will cause the call to
    terminate unexpectedly.
    
    `AGIAppError` is raised on failure.
    """

    def __init__(self, extension):
        _Action.__init__(self, 'SET EXTENSION', quote(extension))


class SetMusic(_Action):
    """
    Enables or disables music-on-hold for this channel, per the state of the `on` argument.

    If specified, `moh_class` identifies the music-on-hold class to be used.
    
    `AGIAppError` is raised on failure.
    """

    def __init__(self, on, moh_class=None):
        _Action.__init__(self,
                         'SET MUSIC', quote(on and 'on' or 'off'),
                         (moh_class and quote(moh_class) or None)
                         )


class SetPriority(_Action):
    """
    Sets the priority for Asterisk to use upon completion of this AGI instance.
    
    No priority-validation is performed; specifying an invalid priority will cause the call to
    terminate unexpectedly.
    
    `AGIAppError` is raised on failure.
    """

    def __init__(self, priority):
        _Action.__init__(self, 'SET PRIORITY', quote(priority))


class SetVariable(_Action):
    """
    Sets the variable identified by `name` to `value` on the current channel.

    `AGIAppError` is raised on failure.
    """

    def __init__(self, name, value):
        _Action.__init__(self, 'SET VARIABLE', quote(name), quote(value))


class StreamFile(_Action):
    """
    See also `ControlStreamFile`, `GetData`, `GetOption`.

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

    def __init__(self, filename, escape_digits='', sample_offset=0):
        escape_digits = _process_digit_list(escape_digits)
        _Action.__init__(self,
                         'STREAM FILE', quote(filename),
                         quote(escape_digits), quote(sample_offset)
                         )

    def process_response(self, response):
        result = response.items.get(_RESULT_KEY)
        if not result.value == '0':
            dtmf_character = _convert_to_char(result.value, response.items)
            offset = _convert_to_int(response.items)
            return (dtmf_character, offset)
        return None


class TDDMode(_Action):
    """
    Sets the TDD transmission `mode` on supporting channels, one of the following:
    
    - TDD_ON
    - TDD_OFF
    - TDD_MATE
    
    `True` is returned if the mode is set, `False` if the channel isn't capable, and
    `AGIAppError` is raised if a problem occurs. According to documentation from 2006,
    all non-capable channels will cause an exception to occur.
    """

    def __init__(self, mode):
        _Action.__init__(self, 'TDD MODE', mode)

    def process_response(self, response):
        result = response.items.get(_RESULT_KEY)
        return result.value == '1'


class Verbose(_Action):
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

    def __init__(self, message, level=LOG_INFO):
        _Action.__init__(self, 'VERBOSE', quote(message), quote(level))


class WaitForDigit(_Action):
    """
    Waits for up to `timeout` milliseconds for a DTMF keypress to be received, returning that
    value. By default, this function blocks indefinitely.

    If no DTMF key is pressed, `None` is returned.
    
    `AGIAppError` is raised on failure, most commonly because the channel was
    hung-up.
    """

    def __init__(self, timeout=-1):
        _Action.__init__(self, 'WAIT FOR DIGIT', quote(timeout))

    def process_response(self, response):
        result = response.items.get(_RESULT_KEY)
        if not result.value == '0':
            return _convert_to_char(result.value, response.items)
        return None


# Exceptions
###############################################################################
class AGIDBError(AGIAppError):
    """
    Indicates that Asterisk encountered an error while interactive with its
    database.
    """
