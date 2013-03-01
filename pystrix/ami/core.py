"""
pystrix.ami.core
================

Provides classes meant to be fed to a `Manager` instance's `send_action()` function.
 
Notes
-----

pystrix.ami.core_events contains event-definitions and processing rules for events raised by
actions in this module (and some others, since extensions can use built-in features).
 
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

The requests implemented by this module follow the definitions provided by
http://www.asteriskdocs.org/ and https://wiki.asterisk.org/
"""
import hashlib
import time
import types

from ami import (_Request, ManagerError)
import core_events
import generic_transforms

AUTHTYPE_MD5 = 'MD5' #Uses MD5 authentication when logging into AMI

#Constants for use with the `Events` action
EVENTMASK_ALL = 'on'
EVENTMASK_NONE = 'off'
EVENTMASK_CALL = 'call'
EVENTMASK_LOG = 'log'
EVENTMASK_SYSTEM = 'system'

#Audio format constants
FORMAT_SLN = 'sln'
FORMAT_G723 = 'g723'
FORMAT_G729 = 'g729'
FORMAT_GSM = 'gsm'
FORMAT_ALAW = 'alaw'
FORMAT_ULAW = 'ulaw'
FORMAT_VOX = 'vox'
FORMAT_WAV = 'wav'

#Originate result constants
ORIGINATE_RESULT_REJECT = 1 #Remote hangup
ORIGINATE_RESULT_RING_LOCAL = 2
ORIGINATE_RESULT_RING_REMOTE = 3
ORIGINATE_RESULT_ANSWERED = 4
ORIGINATE_RESULT_BUSY = 5
ORIGINATE_RESULT_CONGESTION = 8
ORIGINATE_RESULT_INCOMPLETE = 30 #Unable to resolve

class AbsoluteTimeout(_Request):
    """
    Causes Asterisk to hang up a channel after a given number of seconds.
    
    Requires call
    """
    def __init__(self, channel, seconds=0):
        """
        Causes the call on `channel` to be hung up after `seconds` have elapsed, defaulting to
        disabling auto-hangup.
        """
        _Request.__init__(self, 'AbsoluteTimeout')
        self['Channel'] = channel
        self['Timeout'] = str(int(seconds))

class AGI(_Request):
    """
    Causes Asterisk to execute an arbitrary AGI application in a call.

    Upon successful execution, an 'AsyncAGI' event is generated.
    
    Requires call
    """
    _synchronous_events_finalising = (core_events.AsyncAGI,)
    
    def __init__(self, channel, command, command_id=None):
        """
        `channel` is the call in which to execute `command`, the value passed to the AGI dialplan
        application. `command_id` is an optional value that will be present in the resulting event,
        and can reasonably be set to a sequential digit or UUID in your application for tracking
        purposes.
        """
        _Request.__init__(self, 'AGI')
        self['Channel'] = channel
        self['Command'] = command
        if not command_id is None:
            self['CommandID'] = str(command_id)

class Bridge(_Request):
    """
    Bridges two channels already connected to Asterisk.

    Requires call
    """
    def __init__(self, channel_1, channel_2, tone=False):
        """
        `channel_1` is the channel to which `channel_2` will be connected. `tone`, if `True`, will
        cause a sound to be played on `channel_2`.
        """
        _Request.__init__(self, "Bridge")
        self['Channel1'] = channel_1
        self['Channel2'] = channel_2
        self['Tone'] = tone and 'yes' or 'no'
        
class Challenge(_Request):
    """
    Asks the AMI server for a challenge token to be used to hash the login secret.
    
    The value provided under the returned response's 'Challenge' key must be passed as the
    'challenge' parameter of the `Login` object's constructor::

        login = Login(username='me', secret='password', challenge=response.get('Challenge'))
    """
    def __init__(self, authtype=AUTHTYPE_MD5):
        """
        `authtype` is used to specify the authentication type to be used.
        """
        _Request.__init__(self, 'Challenge')
        self['AuthType'] = authtype
        
class ChangeMonitor(_Request):
    """
    Changes the filename associated with the recording of a monitored channel. The channel must have
    previously been selected by the `Monitor` action.
    
    Requires call
    """
    def __init__(self, channel, filename):
        """
        `channel` is the channel to be affected and `filename` is the new target filename, without
        extension, as either an auto-resolved or absolute path.
        """
        _Request.__init__(self, 'ChangeMonitor')
        self['Channel'] = channel
        self['File'] = filename
        
class Command(_Request):
    """
    Sends an arbitrary shell command to Asterisk, returning its response as a series of lines in the
    'data' attribute.
    
    Requires command
    """
    def __init__(self, command):
        """
        `command` is the command to be executed.
        """
        _Request.__init__(self, 'Command')
        self['Command'] = command

class CoreShowChannels(_Request):
    """
    Asks Asterisk to list all active channels.
    
    Any number of 'CoreShowChannel' events may be generated in response to this request, followed by
    one 'CoreShowChannelsComplete'.

    Requires system
    """
    _aggregates = (core_events.CoreShowChannels_Aggregate,)
    _synchronous_events_list = (core_events.CoreShowChannel,)
    _synchronous_events_finalising = (core_events.CoreShowChannelsComplete,)
    
    def __init__(self):
        _Request.__init__(self, "CoreShowChannels")
        
class CreateConfig(_Request):
    """
    Creates an empty configuration file, intended for use before `UpdateConfig()`.

    Requires config
    """
    def __init__(self, filename):
        """
        `filename` is the name of the file, with extension, to be created.
        """
        _Request.__init__(self, "CreateConfig")
        self['Filename'] = filename

class DBDel(_Request):
    """
    Deletes a database value from Asterisk.
    
    Requires system
    """
    def __init__(self, family, key):
        """
        `family` and `key` are specifiers to select the value to remove.
        """
        _Request.__init__(self, 'DBDel')
        self['Family'] = family
        self['Key'] = key

class DBDelTree(_Request):
    """
    Deletes a database tree from Asterisk.
    
    Requires system
    """
    def __init__(self, family, key=None):
        """
        `family` and `key` (optional) are specifiers to select the values to remove.
        """
        _Request.__init__(self, 'DBDelTree')
        self['Family'] = family
        if not key is None:
            self['Key'] = key
            
class DBGet(_Request):
    """
    Requests a database value from Asterisk.
    
    A 'DBGetResponse' event will be generated upon success.
    
    Requires system
    """
    def __init__(self, family, key):
        """
        `family` and `key` are specifiers to select the value to retrieve.
        """
        _Request.__init__(self, 'DBGet')
        self['Family'] = family
        self['Key'] = key
        
class DBPut(_Request):
    """
    Stores a database value in Asterisk.
    
    Requires system
    """
    def __init__(self, family, key, value):
        """
        `family` and `key` are specifiers for where to place `value`.
        """
        _Request.__init__(self, 'DBPut')
        self['Family'] = family
        self['Key'] = key
        self['Val'] = value
        
class Events(_Request):
    """
    Changes the types of unsolicited events Asterisk sends to this manager connection.
    """
    def __init__(self, mask):
        """
        `Mask` is one of the following...
        
        * EVENTMASK_ALL
        * EVENTMASK_NONE
        
        ...or an iterable, like a tuple, with any combination of the following...
        
        * EVENTMASK_CALL
        * EVENTMASK_LOG
        * EVENTMASK_SYSTEM
        
        If an empty value is provided, EVENTMASK_NONE is assumed.
        """
        _Request.__init__(self, 'Events')
        if isinstance(mask, types.StringTypes):
            self['EventMask'] = mask
        else:
            if EVENTMASK_ALL in mask:
                self['EventMask'] = EVENTMASK_ALL
            else:
                self['EventMask'] = ','.join((m for m in mask if not m == EVENTMASK_NONE)) or EVENTMASK_NONE
                
    def process_response(self, response):
        """
        Indicates success if the response matches one of the valid patterns.
        """
        response = _Request.process_response(self, response)
        response.success = response.get('Response') in ('Events On', 'Events Off')
        return response
        
class ExtensionState(_Request):
    """
    Provides the state of an extension.
    
    If successful, a 'Status' key will be present, with one of the following values as a string:
    
    * -2: Extension removed
    * -1: Extension hint not found
    *  0: Idle
    *  1: In use
    *  2: Busy
    
    If non-negative, a 'Hint' key will be present, too, containing string data that can be helpful
    in discerning the current activity of the device.
    
    Requires call
    """
    def __init__(self, extension, context):
        """
        `extension` is the extension to be checked and `context` is the container in which it
        resides.
        """
        _Request.__init__(self, 'ExtensionState')
        self['Exten'] = extension
        self['Context'] = context
        
class GetConfig(_Request):
    """
    Gets the contents of an Asterisk configuration file.
    
    The result is recturned as a series of 'Line-XXXXXX-XXXXXX' keys that increment from 0
    sequentially, starting with 'Line-000000-000000'.
    
    A sequential generator is provided by the 'get_lines()' function on the response.
    
    Requires config
    """
    def __init__(self, filename):
        """
        `filename` is the name of the config file to be read, including extension.
        """
        _Request.__init__(self, 'GetConfig')
        self['Filename'] = filename
        
    def process_response(self, response):
        """
        Adds a 'get_lines' function that returns a generator that yields every line in order.
        """
        response = _Request.process_response(self, response)
        response.get_lines = lambda : (value for (key, value) in sorted(response.items()) if key.startswith('Line-'))
        return response
        
class Getvar(_Request):
    """
    Gets the value of a channel or global variable from Asterisk, returning the result under the
    'Value' key.
    
    Requires call
    """
    def __init__(self, variable, channel=None):
        """
        `variable` is the name of the variable to retrieve. `channel` is optional; if not specified,
        a global variable is retrieved.
        """
        _Request.__init__(self, 'Getvar')
        self['Variable'] = variable
        if not channel is None:
            self['Channel'] = channel
            
class Hangup(_Request):
    """
    Hangs up a channel.
    
    On success, a 'Hangup' event is generated.
    
    Requires call
    """
    _synchronous_events_finalising = (core_events.Hangup,)
    
    def __init__(self, channel):
        """
        `channel` is the ID of the channel to be hung up.
        """
        _Request.__init__(self, 'Hangup')
        self['Channel'] = channel
        
class ListCommands(_Request):
    """
    Provides a list of every command exposed by the Asterisk Management Interface, with synopsis,
    as a series of lines in the response's 'data' attribute.
    """
    def __init__(self):
        _Request.__init__(self, 'ListCommands')

class ListCategories(_Request):
    """
    Provides a list of every category in an Asterisk configuration file, as a series of lines in the
    response's 'data' attribute.

    Requires config
    """
    def __init__(self, filename):
        """
        `filename` is the name of the file, with extension, to be read.
        """
        _Request.__init__(self, 'ListCategories')
        self['Filename'] = filename
        

class LocalOptimizeAway(_Request):
    """
    Allows a bridged channel to be optimised in Asterisk's processing logic. This function should
    only be invoked after explicitly bridging.

    Requires call
    """
    def __init__(self, channel):
        """
        `channel` is the channel to be optimised.
        """
        _Request.__init__(self, 'LocalOptimizeAway')
        self['Channel'] = channel
        
class Login(_Request):
    """
    Authenticates to the AMI server.
    """
    def __init__(self, username, secret, events=True, challenge=None, authtype=AUTHTYPE_MD5):
        """
        `username` and `secret` are the credentials used to authenticate.
        
        `events` may be set to `False` to prevent unsolicited events from being received. This is
        normally not desireable, so leaving it `True` is usually a good idea.
        
        If given, `challenge` is a challenge string provided by Asterisk after sending a `Challenge`
        action, used with `authtype` to determine how to authenticate. `authtype` is ignored if the
        `challenge` parameter is unset.
        """
        _Request.__init__(self, 'Login')
        self['Username'] = username
        
        if not challenge is None and authtype:
            self['AuthType'] = authtype
            if authtype == AUTHTYPE_MD5:
                self['Key'] = hashlib.md5(challenge + secret).hexdigest()
            else:
                raise ManagerAuthError("Invalid AuthType specified: %(authtype)s" % {
                 'authtype': authtype,
                })
        else:
            self['Secret'] = secret
            
        if not events:
            self['Events'] = 'off'
            
    def process_response(self, response):
        """
        Raises `ManagerAuthError` if an error is received while attempting to authenticate.
        """
        if response.get('Response') == 'Error':
            raise ManagerAuthError(response.get('Message'))
        return _Request.process_response(self, response)
        
class Logoff(_Request):
    """
    Logs out of the current manager session, permitting reauthentication.
    """
    def __init__(self):
        _Request.__init__(self, 'Logoff')
        
class MailboxCount(_Request):
    """
    Provides the number of new and old messages in the specified mailbox, keyed under 'NewMessages'
    and 'OldMessages', which contain ints; -1 indicates a failure while parsing the value.
    """
    def __init__(self, mailbox):
        """
        `mailbox` is the mailbox to check.
        """
        _Request.__init__(self, 'MailboxCount')
        self['Mailbox'] = mailbox
        
    def process_response(self, response):
        """
        Converts the message-counts into integers.
        """
        response = _Request.process_response(self, response)
        generic_transforms.to_int(response, ('NewMessages', 'OldMessages',), -1)
        return response
        
class MailboxStatus(_Request):
    """
    Provides the number of waiting messages in the specified mailbox, keyed under 'Waiting', which
    contains an int; -1 indicates a failure while parsing the value.
    """
    def __init__(self, mailbox):
        """
        `mailbox` is the mailbox to check.
        """
        _Request.__init__(self, 'MailboxStatus')
        self['Mailbox'] = mailbox

    def process_response(self, response):
        """
        Converts the waiting-message-count into an integer.
        """
        response = _Request.process_response(self, response)
        generic_transforms.to_int(response, ('Waiting',), -1)
        return response

class MixMonitorMute(_Request):
    """
    Mutes or unmutes one or both channels being monitored (recorded).

    Requires call
    """
    def __init__(self, channel, direction, mute):
        """
        `channel` is the channel to operate on.

        `direction` is one of the following:
        
        * 'read': voice originating on the `channel`
        * 'write': voice delivered to the `channel`
        * 'both': all audio on the `channel`

        `mute` is `True` to muste the audio.
        """
        _Request.__init__(self, 'MixMonitorMute')
        self['Channel'] = channel
        self['Direction'] = direction
        self['State'] = mute and '1' or '0'

class ModuleCheck(_Request):
    """
    Indicates whether a module has been loaded.

    If the module was loaded, its version is present in the response.
    """
    def __init__(self, module):
        """
        `module` is the name of the module, without extension.
        """
        _Request.__init__(self, 'ModuleCheck')
        self['Module'] = module

class ModuleLoad(_Request):
    """
    Loads, unloads, or reloads modules.

    Requires system
    """
    def __init__(self, load_type, module=None):
        """
        `load_type` is one of the following:
        
        * 'load'
        * 'unload'
        * 'reload': if `module` is undefined, all modules are reloaded
        
        `module` is optionally the name of the module, with extension, or one of the following for
        a built-in subsystem:
        
        * 'cdr'
        * 'dnsmgr'
        * 'enum'
        * 'extconfig'
        * 'http'
        * 'manager'
        * 'rtp'
        """
        _Request.__init__(self, 'ModuleLoad')
        self['LoadType'] = load_type
        if not module is None:
            self['Module'] = module
            
class Monitor(_Request):
    """
    Starts monitoring (recording) a channel.
    
    Requires call
    """
    def __init__(self, channel, filename, format='wav', mix=True):
        """
        `channel` is the channel to be affected and `filename` is the new target filename, without
        extension, as either an auto-resolved or absolute path.

        `format` may be any format Asterisk understands, defaulting to FORMAT_WAV:
        
        * FORMAT_SLN
        * FORMAT_G723
        * FORMAT_G729
        * FORMAT_GSM
        * FORMAT_ALAW
        * FORMAT_ULAW
        * FORMAT_VOX
        * FORMAT_WAV: PCM16

        `mix`, defaulting to `True`, muxes both audio streams associated with the channel after
        recording is complete, with the alternative leaving the two streams separate.
        """
        _Request.__init__(self, 'Monitor')
        self['Channel'] = channel
        self['File'] = filename
        self['Format'] = format
        self['Mix'] = mix and 'true' or 'false'

class MuteAudio(_Request):
    """
    Starts or stops muting audio on a channel.

    Either (or both) directions can be silenced.
    
    Requires system
    """
    def __init__(self, channel, input=False, output=False, muted=False):
        """
        `channel` is the channel to be affected and `muted` indicates whether audio is being turned
        on or off. `input` (from the channel) and `output` (to the channel) indicate the subchannels
        to be adjusted.
        """
        _Request.__init__(self, 'MuteAudio')
        self['Channel'] = channel
        if input and output:
            self['Direction'] = 'all'
        elif input:
            self['Direction'] = 'in'
        elif output:
            self['Direction'] = 'out'
        else:
            raise ValueError("Unable to construct request that affects no audio subchannels")
        self['State'] = muted and 'on' or 'off'

class _Originate(_Request):
    """
    Provides the common base for originated calls.
    
    Requires call
    """
    def __init__(self, channel, timeout=None, callerid=None, variables={}, account=None, async=True):
        """
        Sets common parameters for originated calls.

        `channel` is the destination to be called, expressed as a fully qualified Asterisk channel,
        like "SIP/test-account@example.org".

        `timeout`, if given, is the number of milliseconds to wait before dropping an unanwsered
        call. If set, the request's timeout value will be set to this number + 2 seconds, removing
        the need to set both variables. If not set, the request's timeout value will be set to ten
        minutes.

        `callerid` is an optinal string of the form "name"<number>, where 'name' is the name to be
        displayed (on supporting channels) and 'number' is the source identifier, typically a string
        of digits on most channels that may interact with the PSTN.

        `variables` is an oprional dictionary of key-value variable pairs to be set as part of the
        channel's namespace.

        `account` is an optional account code to be associated with the channel, useful for tracking
        billing information.

        `async` should always be `True`. If not, only one unanswered call can be active at a time.
        """
        _Request.__init__(self, "Originate")
        self['Channel'] = channel
        self['Async'] = async and 'true' or 'false'
        
        if timeout and timeout > 0:
            self['Timeout'] = str(timeout)
            self.timeout = timeout + 2000 #Timeout + 2s
        else:
            self.timeout = 10 * 60 * 1000 #Ten minutes

        if callerid:
            self['CallerID'] = callerid

        if variables:
            self['Variable'] = tuple(['%(key)s=%(value)s' % {'key': key, 'value': value,} for (key, value) in variables.items()])

        if account:
            self['Account'] = account
            
class Originate_Application(_Originate):
    """
    Initiates a call that answers, executes an arbitrary dialplan application, and hangs up.
    
    Requires call
    """
    def __init__(self, channel, application, data=(), timeout=None, callerid=None, variables={}, account=None, async=True):
        """
        `channel` is the destination to be called, expressed as a fully qualified Asterisk channel,
        like "SIP/test-account@example.org".

        `application` is the name of the application to be executed, and `data` is optionally any
        parameters to pass to the application, as an ordered sequence (list or tuple) of strings,
        escaped as necessary (the ',' character is special).

        `timeout`, if given, is the number of milliseconds to wait before dropping an unanwsered
        call. If set, the request's timeout value will be set to this number + 2 seconds, removing
        the need to set both variables. If not set, the request's timeout value will be set to ten
        minutes.

        `callerid` is an optinal string of the form "name"<number>, where 'name' is the name to be
        displayed (on supporting channels) and 'number' is the source identifier, typically a string
        of digits on most channels that may interact with the PSTN.

        `variables` is an oprional dictionary of key-value variable pairs to be set as part of the
        channel's namespace.

        `account` is an optional account code to be associated with the channel, useful for tracking
        billing information.

        `async` should always be `True`. If not, only one unanswered call can be active at a time.
        """
        _Originate.__init__(self, channel, timeout, callerid, variables, account, async)
        self['Application'] = application
        if data:
            self['Data'] = ','.join((str(d) for d in data))
            
class Originate_Context(_Originate):
    """
    Initiates a call with instructions derived from an arbitrary context/extension/priority.
    
    Requires call
    """
    def __init__(self, channel, context, extension, priority, timeout=None, callerid=None, variables={}, account=None, async=True):
        """
        `channel` is the destination to be called, expressed as a fully qualified Asterisk channel,
        like "SIP/test-account@example.org".

        `context`, `extension`, and `priority`, must match a triple known to Asterisk internally. No
        validation is performed, so specifying an invalid target will terminate the call
        immediately.

        `timeout`, if given, is the number of milliseconds to wait before dropping an unanwsered
        call. If set, the request's timeout value will be set to this number + 2 seconds, removing
        the need to set both variables. If not set, the request's timeout value will be set to ten
        minutes.

        `callerid` is an optinal string of the form "name"<number>, where 'name' is the name to be
        displayed (on supporting channels) and 'number' is the source identifier, typically a string
        of digits on most channels that may interact with the PSTN.

        `variables` is an oprional dictionary of key-value variable pairs to be set as part of the
        channel's namespace.

        `account` is an optional account code to be associated with the channel, useful for tracking
        billing information.

        `async` should always be `True`. If not, only one unanswered call can be active at a time.
        """
        _Originate.__init__(self, channel, timeout, callerid, variables, account, async)
        self['Context'] = context
        self['Exten'] = extension
        self['Priority'] = priority
        
class Park(_Request):
    """
    Parks a call for later retrieval.

    Requires call
    """
    def __init__(self, channel, channel_callback, timeout=None):
        """
        `channel` is the channel to be parked and `channel_callback` is the channel to which parking
        information is announced.

        If `timeout`, a number of milliseconds, is given, then `channel_callback` is given `channel`
        if the call was not previously retrieved.
        """
        _Request.__init__(self, "Park")
        self['Channel'] = channel
        self['Channel2'] = channel_callback
        if timeout:
            self['Timeout'] = str(timeout)

class ParkedCalls(_Request):
    """
    Lists all parked calls.

    Any number of 'ParkedCall' events may be generated in response to this request, followed by one
    'ParkedCallsComplete'.
    """
    _aggregates = (core_events.ParkedCalls_Aggregate,)
    _synchronous_events_list = (core_events.ParkedCall,)
    _synchronous_events_finalising = (core_events.ParkedCallsComplete,)
    
    def __init__(self):
        _Request.__init__(self, "ParkedCalls")

class PauseMonitor(_Request):
    """
    Pauses the recording of a monitored channel. The channel must have previously been selected by
    the `Monitor` action.
    
    Requires call
    """
    def __init__(self, channel):
        """
        `channel` is the channel to be affected.
        """
        _Request.__init__(self, 'PauseMonitor')
        self['Channel'] = channel
        
class Ping(_Request):
    """
    Pings the AMI server. The response value has a 'RTT' attribute, which is the number of seconds
    the trip took, as a floating-point number, or -1 in case of failure.
    """
    _start_time = None #The time at which the ping message was built
    
    def __init__(self):
        _Request.__init__(self, 'Ping')
        
    def build_request(self, action_id, id_generator, **kwargs):
        """
        Records the time at which the request was assembled, to provide a latency value.
        """
        request = _Request.build_request(self, action_id, id_generator, **kwargs)
        self._start_time = time.time()
        return request
        
    def process_response(self, response):
        """
        Adds the number of seconds elapsed since the message was prepared for transmission under
        the 'RTT' key or sets it to -1 in case the server didn't respond as expected.
        """
        response = _Request.process_response(self, response)
        if response.get('Response') == 'Pong':
            response['RTT'] = time.time() - self._start_time
        else:
            response['RTT'] = -1
        return response
        
class PlayDTMF(_Request):
    """
    Plays a DTMF tone on a channel.
    
    Requires call
    """
    def __init__(self, channel, digit):
        """
        `channel` is the channel to be affected, and `digit` is the tone to play.
        """
        _Request.__init__(self, 'PlayDTMF')
        self['Channel'] = channel
        self['Digit'] = str(digit)

class QueueAdd(_Request):
    """
    Adds a member to a queue.

    Upon success, a 'QueueMemberAdded' event will be generated.

    Requires agent
    """
    _synchronous_events_finalising = (core_events.QueueMemberAdded,)
    
    def __init__(self, interface, queue, membername=None, penalty=0, paused=False):
        """
        Adds the device identified by `interface` to the given `queue`.

        `membername` optionally provides a friendly name for logging purposes, `penalty` establishes
        a priority structure (lower priorities first, defaulintg to 0) for call escalation, and
        `paused` optinally allows the interface to start in a disabled state.
        """
        _Request.__init__(self, "QueueAdd")
        self['Queue'] = queue
        self['Interface'] = interface
        self['Penalty'] = str(penalty)
        self['Paused'] = paused and 'yes' or 'no'
        if membername:
            self['MemberName'] = membername

class QueueLog(_Request):
    """
    Adds an arbitrary record to the queue log.

    Requires agent
    """
    def __init__(self, queue, event, interface=None, uniqueid=None, message=None):
        """
        `queue` is the queue to which the `event` is to be attached.

        `interface` optionally allows the event to be associated with a specific queue member.

        `uniqueid`'s purpose is presently unknown.

        `message`'s purpose is presently unknown.
        """
        _Request.__init__(self, "QueueLog")
        self['Queue'] = queue
        self['Event'] = event
        if not uniqueid is None:
            self['Uniqueid'] = uniqueid
        if not interface is None:
            self['Interface'] = interface
        if not message is None:
            self['Message'] = message

class QueuePause(_Request):
    """
    Pauses or unpauses a member in one or all queues.

    Upon success, a 'QueueMemberPaused' event will be generated for all affected queues.

    Requires agent
    """
    def __init__(self, interface, paused, queue=None):
        """
        `interface` is the device to be affected, and `queue` optionally limits the scope to a
        single queue. `paused` must be `True` or `False`, to control the action being taken.
        """
        _Request.__init__(self, "QueuePause")
        self['Interface'] = interface
        self['Paused'] = paused and 'true' or 'false'
        if not queue is None:
            self['Queue'] = queue

class QueuePenalty(_Request):
    """
    Changes the penalty value associated with a queue member, in one or all queues.

    Requires agent
    """
    def __init__(self, interface, penalty, queue=None):
        """
        Changes the `penalty` value associated with `interface` in all queues, unless `queue` is
        defined, limiting it to one.
        """
        _Request.__init__(self, "QueuePenalty")
        self['Interface'] = interface
        self['Penalty'] = str(penalty)
        if not queue is None:
            self['Queue'] = queue

class QueueReload(_Request):
    """
    Reloads properties from config files for one or all queues.

    Requires agent
    """
    def __init__(self, queue=None, members='yes', rules='yes', parameters='yes'):
        """
        Reloads parameters for all queues, unless `queue` is defined, limiting it to one.

        `members` is 'yes' (default) or 'no', indicating whether the member-list should be reloaded.
        
        `rules` is 'yes' (default) or 'no', indicating whether the rule-list should be reloaded.

        `parameters` is 'yes' (default) or 'no', indicating whether the parameter-list should be
        reloaded.
        """
        _Request.__init__(self, "QueueReload")
        self['Members'] = members
        self['Rules'] = rules
        self['Parameters'] = parameters
        if not queue is None:
            self['Queue'] = queue
            
class QueueRemove(_Request):
    """
    Removes a member from a queue.

    Upon success, a 'QueueMemberRemoved' event will be generated.

    Requires agent
    """
    _synchronous_events_finalising = (core_events.QueueMemberRemoved,)
    
    def __init__(self, interface, queue):
        """
        Removes the device identified by `interface` from the given `queue`.
        """
        _Request.__init__(self, "QueueRemove")
        self['Queue'] = queue
        self['Interface'] = interface

class QueueStatus(_Request):
    """
    Describes the status of one (or all) queues.

    Upon success, 'QueueParams', 'QueueMember', and 'QueueEntry' events will be generated, ending
    with 'QueueStatusComplete'.
    """
    _aggregates = (core_events.QueueStatus_Aggregate,)
    _synchronous_events_list = (core_events.QueueParams, core_events.QueueMember, core_events.QueueEntry,)
    _synchronous_events_finalising = (core_events.QueueStatusComplete,)
    
    def __init__(self, queue=None):
        """
        Describes all queues in the system, unless `queue` is given, which limits the scope to one.
        """
        _Request.__init__(self, "QueueStatus")
        if not queue is None:
            self['Queue'] = queue

class Redirect(_Request):
    """
    Redirects a call to an arbitrary context/extension/priority.
    
    Requires call
    """
    def __init__(self, channel, context, extension, priority):
        """
        `channel` is the destination to be redirected.

        `context`, `extension`, and `priority`, must match a triple known to Asterisk internally. No
        validation is performed, so specifying an invalid target will terminate the call
        immediately.
        """
        _Request.__init__(self, "Redirect")
        self['Channel'] = channel
        self['Context'] = context
        self['Exten'] = extension
        self['Priority'] = priority

class Reload(_Request):
    """
    Reloads Asterisk's configuration globally or for a specific module.
    
    Requires call
    """
    def __init__(self, module=None):
        """
        If given, `module` limits the scope of the reload to a specific module, named without
        extension.
        """
        _Request.__init__(self, "Reload")
        if not module is None:
            self['Module'] = module

class SendText(_Request):
    """
    Sends text along a supporting channel.
    
    Requires call
    """
    def __init__(self, channel, message):
        """
        `channel` is the channel along which to send `message`.
        """
        _Request.__init__(self, "SendText")
        self['Channel'] = channel
        self['Message'] = message
        
class SetCDRUserField(_Request):
    """
    Sets the user-field attribute for the CDR associated with a channel.
    
    Requires call
    """
    def __init__(self, channel, user_field):
        """
        `channel` is the channel to be affected, and `user_field` is the value to set.
        """
        _Request.__init__(self, 'SetCDRUserField')
        self['Channel'] = channel
        self['UserField'] = user_field
        
class Setvar(_Request):
    """
    Sets a channel-level or global variable.
    
    Requires call
    """
    def __init__(self, variable, value, channel=None):
        """
        `value` is the value to be set under `variable`.
        
        `channel` is the channel to be affected, or `None`, the default, if the variable is global.
        """
        _Request.__init__(self, 'Setvar')
        if channel:
            self['Channel'] = channel
        self['Variable'] = variable
        self['Value'] = value

class SIPnotify(_Request):
    """
    Sends a SIP NOTIFY to the remote party on a channel.

    Requires call
    """
    def __init__(self, channel, headers={}):
        """
        `channel` is the channel along which to send the NOTIFY.

        `headers` is a dictionary of key-value pairs to be inserted as SIP headers.
        """
        _Request.__init__(self, "SIPnotify")
        self['Channel'] = channel
        if headers:
            self['Variable'] = tuple(['%(key)s=%(value)s' % {'key': key, 'value': value,} for (key, value) in headers.items()])

class SIPpeers(_Request):
    """
    Lists all SIP peers.

    Any number of 'PeerEntry' events may be generated in response to this request, followed by one
    'PeerlistComplete'.

    Requires system
    """
    _aggregates = (core_events.SIPpeers_Aggregate,)
    _synchronous_events_list = (core_events.PeerEntry,)
    _synchronous_events_finalising = (core_events.PeerlistComplete,)
    
    def __init__(self):
        _Request.__init__(self, "SIPpeers")

class SIPqualify(_Request):
    """
    Sends a SIP OPTIONS to the specified peer, mostly to ensure its presence.

    Some events are likely raised by this, but they're unknown at the moment.

    Requires system
    """
    def __init__(self, peer):
        """
        `peer` is the peer to ping.
        """
        _Request.__init__(self, "SIPqualify")
        self['Peer'] = peer

class SIPshowpeer(_Request):
    """
    Provides detailed information about a SIP peer.

    The response has the following key-value pairs:
    
    * 'ACL': True or False
    * 'Address-IP': The IP of the peer
    * 'Address-Port': The port of the peer, as an integer
    * 'AMAflags': "Unknown"
    * 'Callgroup': ?
    * 'Callerid': "Linksys #2" <555>
    * 'Call-limit': ?
    * 'Channeltype': "SIP"
    * 'ChanObjectType': "peer"
    * 'CID-CallingPres': ?
    * 'Context': The context associated with the peer
    
     * 'CodecOrder': The order in which codecs are tried
     * 'Codecs': A list of supported codecs
     
    * 'Default-addr-IP': ?
    * 'Default-addr-port': ?
    * 'Default-Username': ?
    * 'Dynamic': True or False, depending on whether the peer is resolved by static IP or
      authentication
    * 'Language': The language preference (may be empty) of this peer
    * 'LastMsgsSent': ?
    * 'MaxCallBR': The maximum bitrate in kbps supported by the peer, as an integer
    * 'MD5SecretExist': True or False, depending on whether an MD5 secret is defined
    * 'ObjectName': The internal name of the peer
    * 'Pickupgroup': ?
    * 'Reg-Contact': The registration contact address for this peer
    * 'RegExpire': Time in seconds until SIP registration expires, as an integer
    * 'RegExtension': ?
    * 'SecretExist': True or False, depending on whether a secret is defined.
    * 'SIP-AuthInsecure': True or False
    * 'SIP-CanReinvite': True or False, depending on whether the peer supports REINVITE
    * 'SIP-DTMFmode': The DTMF transport mode to use with this peer, "rfc2833" or ?
    * 'SIP-NatSupport': The NATting workarounds supported by this peer, "RFC3581" or ?
    * 'SIP-PromiscRedir': True or False, depending on whether this peer is allowed to arbitrarily
      redirect calls
    * 'SIP-Useragent': The User-Agent of the peer
    * 'SIP-UserPhone': True or False, (presumably) depending on whether this peer is a terminal
      device
    * 'SIP-VideoSupport': True or False
    * 'SIPLastMsg': ?
    * 'Status': 'Unmonitored', 'OK (\d+ ms)'
    * 'ToHost': ?
    * 'TransferMode': "open"
    * 'VoiceMailbox': The mailbox associated with the peer; may be null
    
    Requires system
    """
    def __init__(self, peer):
        """
        `peer` is the identifier of the peer for which information is to be retrieved.
        """
        _Request.__init__(self, "SIPshowpeer")
        self['Peer'] = peer
        
    def process_response(self, response):
        """
        Sets the 'ACL', 'Dynamic', 'MD5SecretExist', 'SecretExist', 'SIP-CanReinvite',
        'SIP-PromiscRedir', 'SIP-UserPhone', 'SIP-VideoSupport', and 'SIP-AuthInsecure' headers'
        values to booleans.
        
        Sets the 'Address-Port', 'MaxCallBR', and 'RegExpire' headers' values to ints, with -1
        indicating failure.
        """
        response = _Request.process_response(self, response)
        
        generic_transforms.to_bool(response, (
         'ACL', 'Dynamic', 'MD5SecretExist', 'SecretExist', 'SIP-CanReinvite', 'SIP-PromiscRedir',
         'SIP-UserPhone', 'SIP-VideoSupport',
        ), truth_value='Y')
        generic_transforms.to_bool(response, ('SIP-AuthInsecure',), truth_value='yes')
        generic_transforms.to_int(response, ('Address-Port',), -1)
        generic_transforms.to_int(response, ('MaxCallBR', 'RegExpire'), -1, preprocess=(lambda x:x.split()[0]))
        
        return response
        
class SIPshowregistry(_Request):
    """
    Lists all SIP registrations.

    Any number of 'RegistryEntry' events may be generated in response to this request, followed by
    one 'RegistrationsComplete'.

    Requires system
    """
    _aggregates = (core_events.SIPshowregistry_Aggregate,)
    _synchronous_events_list = (core_events.RegistryEntry,)
    _synchronous_events_finalising = (core_events.RegistrationsComplete,)
    
    def __init__(self):
        _Request.__init__(self, "SIPshowregistry")
        
class Status(_Request):
    """
    Lists the status of an active channel.

    Zero or one 'Status' events are generated, followed by a 'StatusComplete' event.

    Requires call
    """
    _aggregates = (core_events.Status_Aggregate,)
    _synchronous_events_list = (core_events.Status,)
    _synchronous_events_finalising = (core_events.StatusComplete,)
    
    def __init__(self, channel):
        """
        `channel` is the channel for which status information is to be retrieved.
        """
        _Request.__init__(self, "Status")
        self['channel'] = channel

class StopMonitor(_Request):
    """
    Stops recording a monitored channel. The channel must have previously been selected by
    the `Monitor` action.
    
    Requires call
    """
    def __init__(self, channel):
        """
        `channel` is the channel to be affected.
        """
        _Request.__init__(self, 'StopMonitor')
        self['Channel'] = channel

class UnpauseMonitor(_Request):
    """
    Unpauses recording on a monitored channel. The channel must have previously been selected by
    the `Monitor` action.
    
    Requires call
    """
    def __init__(self, channel):
        """
        `channel` is the channel to be affected.
        """
        _Request.__init__(self, 'UnpauseMonitor')
        self['Channel'] = channel

class UpdateConfig(_Request):
    """
    Updates any number of values in an Asterisk configuration file.

    Requires config
    """
    def __init__(self, src_filename, dst_filename, changes, reload=True):
        """
        Reads from `src_filename`, performing all `changes`, and writing to `dst_filename`.

        If `reload` is `True`, the changes take effect immediately. If `reload` is the name of a
        module, that module is reloaded.

        `changes` may be any iterable object countaining quintuples with the following items:
        
        #. One of the following:
        
         * 'NewCat': creates a new category
         * 'RenameCat': renames a category
         * 'DelCat': deletes a category
         * 'Update': changes a value
         * 'Delete': removes a value
         * 'Append': adds a value
         
        2. The name of the category to operate on
        #. `None` or the name of the variable to operate on
        #. `None` or the value to be set/added (has no effect with 'Delete')
        #. `None` or a string that needs to be matched in the line to serve as a qualifier
        """
        _Request.__init__(self, "UpdateConfig")
        self['SrcFilename'] = src_filename
        self['DstFilename'] = dst_filename
        self['Reload'] = type(reload) == bool and (reload and 'true' or 'false') or reload

        for (i, (action, category, variable, value, match)) in enumerate(changes):
            index = '%(index)06i' % {
             'index': i,
            }
            self['Action-' + index] = action
            self['Cat-' + index] = category
            if not variable is None:
                self['Var-' + index] = variable
            if not value is None:
                self['Value-' + index] = value
            if not match is None:
                self['Match-' + index] = match

class UserEvent(_Request):
    """
    Causes a 'UserEvent' event to be generated.
    
    Requires user
    """
    _synchronous_events_finalising = (core_events.UserEvent,)
    
    def __init__(self, **kwargs):
        """
        Any keyword-arguments passed will be present in the generated event, making this usable as a
        crude form of message-passing between AMI clients.
        """
        _Request.__init__(self, 'UserEvent')
        for (key, value) in kwargs.items():
            self[key] = value

class VoicemailUsersList(_Request):
    """
    Lists all voicemail information.
    
    Any number of 'VoicemailUserEntry' events may be generated in response to this request, followed
    by one 'VoicemailUserEntryComplete'.
    
    Requires system (probably)
    """
    _aggregates = (core_events.VoicemailUsersList_Aggregate,)
    _synchronous_events_list = (core_events.VoicemailUserEntry,)
    _synchronous_events_finalising = (core_events.VoicemailUserEntryComplete,)
    
    def __init__(self):
        _Request.__init__(self, 'VoicemailUsersList')


#Exceptions
###############################################################################
class ManagerAuthError(ManagerError):
    """
    Indicates that a problem occurred while authenticating 
    """
    
