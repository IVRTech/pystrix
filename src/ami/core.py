"""

The requests and events implemented by this module follow the definitions provided by
http://www.asteriskdocs.org/

Event information
=================
 DBGetResponse
 -------------
 Provides the value requested from the database.
 - 'Family' : The family of the value being provided
 - 'Key' : The key of the value being provided
 - 'Val' : The value being provided, represented as a string
 
 Hangup
 ------
 Indicates that a channel has been hung up.
 - 'Cause' : One of the following numeric values, as a string:
  - 0 : Channel cleared normally
 - 'Cause-txt' : Additional information related to the hangup
 - 'Channel' : The channel hung up
 - 'Uniqueid' : An Asterisk unique value (approximately the UNIX timestamp of the event)

 ParkedCall
 ----------
 Describes a parked call.
 - 'ActionID' : The ID associated with the original request
 - 'CallerID' : The ID of the caller, ".+?" <.+?>
 - 'CallerIDName' (optional) : The name of the caller, on supporting channels
 - 'Channel' : The channel of the parked call
 - 'Exten' : The extension associated with the parked call
 - 'From' : The callback channel associated with the call
 - 'Timeout' (optional) : The time remaining before the call is reconnected with the callback
                          channel

 ParkedCallsComplete
 -------------------
 Indicates that all parked calls have been listed.
 - 'ActionID' : The ID associated with the original request

 PeerEntry
 ---------
 Describes a peer.
 - 'ActionID' : The ID associated with the original request
 - 'ChannelType' : The type of channel being described.
  - 'SIP'
 - 'ObjectName' : The internal name by which this peer is known
 - 'ChanObjectType': The type of object
  - 'peer'
 - 'IPaddress' (optional) : The IP of the peer
 - 'IPport' (optional) : The port of the peer
 - 'Dynamic' : 'yes' or 'no', depending on whether the peer is resolved by IP or authentication
 - 'Natsupport' : 'yes' or 'no', depending on whether the peer's messages' content should be trusted
                  for routing purposes. If not, packets are sent back to the last hop
 - 'VideoSupport' : 'yes' or 'no'
 - 'ACL' : 'yes' or 'no'
 - 'Status' : 'Unmonitored', 'OK (\d+ ms)'
 - 'RealtimeDevice' : 'yes' or 'no'

 PeerlistComplete
 ----------------
 Indicates that all peers have been listed.
 - 'ActionID' : The ID associated with the original request

 QueueEntry
 ----------
 Indicates that a call is waiting to be answered.
 - 'ActionID' (optional) : The ID associated with the original request, if a response
 - 'Channel' : The channel of the inbound call
 - 'CallerID' : The (often) numeric ID of the caller
 - 'CallerIDName' (optional) : The friendly name of the caller on supporting channels
 - 'Position' : The numeric position of the caller in the queue
 - 'Queue' : The queue in which the caller is waiting
 - 'Wait' : The number of seconds the caller has been waiting

 QueueMember
 -----------
 Describes a member of a queue.
 - 'ActionID' (optional) : The ID associated with the original request, if a response
 - 'CallsTaken' : The number of calls received by this member
 - 'LastCall' : The UNIX timestamp of the last call taken, or 0 if none
 - 'Location' : The interface in the queue
 - 'MemberName' (optional) : The friendly name of the member
 - 'Membership' : "dynamic" ("static", too?)
 - 'Paused' : '1' or '0' for 'true' and 'false', respectively
 - 'Penalty' : The selection penalty to apply to this member (higher numbers mean later selection)
 - 'Queue' : The queue to which the member belongs
 - 'Status' : One of the following:
  - 0 : Idle
  - 1 : In use
  - 2 : Busy

 QueueMemberAdded
 ----------------
 Indicates that a member was added to a queue.
 - 'CallsTaken' : The number of calls received by this member
 - 'LastCall' : The UNIX timestamp of the last call taken, or 0 if none
 - 'Location' : The interface added to the queue
 - 'MemberName' (optional) : The friendly name of the member
 - 'Membership' : "dynamic" ("static", too?)
 - 'Paused' : '1' or '0' for 'true' and 'false', respectively
 - 'Penalty' : The selection penalty to apply to this member (higher numbers mean later selection)
 - 'Queue' : The queue to which the member was added
 - 'Status' : One of the following:
  - 0 : Idle
  - 1 : In use
  - 2 : Busy

 QueueMemberPaused
 -----------------
 Indicates that the pause-state of a queue member was changed
 - 'Location' : The interface added to the queue
 - 'MemberName' (optional) : The friendly name of the member
 - 'Paused' : '1' or '0' for 'true' and 'false', respectively
 - 'Queue' : The queue in which the member was paused

 QueueMemberRemoved
 ------------------
 Indicates that a member was removed from a queue.
 - 'Location' : The interface removed from the queue
 - 'MemberName' (optional) : The friendly name of the member
 - 'Queue' : The queue from which the member was removed

 QueueParams
 -----------
 Describes the attributes of a queue.
 - 'Abandoned' : The number of calls that have gone unanswered
 - 'ActionID' (optional) : The ID associated with the original request, if a response
 - 'Calls' : The number of current calls in the queue
 - 'Completed' : The number of completed calls
 - 'Holdtime' : ?
 - 'Max' : ?
 - 'Queue' : The queue being described
 - 'ServiceLevel' : ?
 - 'ServicelevelPerf' : ?
 - 'Weight' : ?

 QueueStatusComplete
 -------------------
 Indicates that a QueueStatus request has completed.
 - 'ActionID' : The ID associated with the original request

 Status
 ------
 Describes the current status of a channel.
 - 'Account' : The billing account associated with the channel; may be empty
 - 'ActionID' : The ID associated with the original request
 - 'Channel' : The channel being described
 - 'CallerID' : The ID of the caller, ".+?" <.+?>
 - 'CallerIDNum' : The (often) numeric component of the CallerID
 - 'CallerIDName' (optional) : The, on suporting channels, name of the caller, enclosed in quotes
 - 'Context' : The context of the directive the channel is executing
 - 'Extension' : The extension of the directive the channel is executing
 - 'Link' : ?
 - 'Priority' : The priority of the directive the channel is executing
 - 'Seconds' : The number of seconds the channel has been active
 - 'State' : "Up"
 - 'Uniqueid' : An Asterisk unique value (approximately the UNIX timestamp of the event)

 StatusComplete
 --------------
 Indicates that all requested channel information has been provided.
 - 'ActionID' : The ID associated with the original request

 UserEvent
 ---------
 Generated in response to the UserEvent request.
 - 'ActionID' : The ID associated with the original request
 - * : Any keys supplied with the request
"""
import hashlib
import time
import types

from ami import (_Request, ManagerError)

AUTHTYPE_MD5 = 'MD5' #Uses MD5 authentication when logging into AMI

#Constants for use with the `Events` action
EVENTMASK_ALL = 'on'
EVENTMASK_NONE = 'off'
EVENTMASK_CALL = 'call'
EVENTMASK_LOG = 'log'
EVENTMASK_SYSTEM = 'system'

FORMAT_SLN = 'sln'
FORMAT_G723 = 'g723'
FORMAT_G729 = 'g729'
FORMAT_GSM = 'gsm'
FORMAT_ALAW = 'alaw'
FORMAT_ULAW = 'ulaw'
FORMAT_VOX = 'vox'
FORMAT_WAV = 'wav'

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
        
class Challenge(_Request):
    """
    Asks the AMI server for a challenge token to be used to hash the login secret.
    
    The value provided under the returned response's 'Challenge' key must be passed as the
    'challenge' parameter of the `Login` object's constructor:
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
        - EVENTMASK_ALL
        - EVENTMASK_NONE
        ...or an iterable, like a tuple, of any of the following...
        - EVENTMASK_CALL
        - EVENTMASK_LOG
        - EVENTMASK_SYSTEM
        
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
    
    If successful, a 'Status' key will be present, with one of the following values:
    - -2 : Extension removed
    - -1 : Extension hint not found
    -  0 : Idle
    -  1 : In use
    -  2 : Busy
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
        Adds a 'lines' attribute as a generator that produces every line in order.
        """
        response = _Request.process_response(self, response)
        response.get_lines = lambda : (value for (key, value) in sorted(response.items()) if key.startswith('Line-'))
        return response
        
def GetVar(_Request):
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
        _Request.__init__(self, 'GetVar')
        self['Variable'] = variable
        if not channel is None:
            self['Channel'] = channel
            
class Hangup(_Request):
    """
    Hangs up a channel.
    
    On success, a 'Hangup' event is generated.
    
    Requires call
    """
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
        for messages in ('NewMessages', 'OldMessages'):
            msgs = self.get(messages)
            if msgs is not None and msgs.isdigit():
                self[messages] = int(msgs)
            else:
                self[messages] = -1
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
        messages = self.get('Waiting')
        if messages is not None and messages.isdigit():
            self['Waiting'] = int(messages)
        else:
            self['Waiting'] = -1
        return response
        
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
        - FORMAT_SLN
        - FORMAT_G723
        - FORMAT_G729
        - FORMAT_GSM
        - FORMAT_ALAW
        - FORMAT_ULAW
        - FORMAT_VOX
        - FORMAT_WAV : PCM16

        `mix`, defaulting to `True`, muxes both audio streams associated with the channel, with the
        alternative recording only audio produced by the channel.
        """
        _Request.__init__(self, 'Monitor')
        self['Channel'] = channel
        self['File'] = filename
        self['Format'] = format
        self['Mix'] = mix and 'true' or 'false'

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
        self.__init__(self, "Originate")
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

    The application could be an AGI directive to allow for fully dynamic logic.
    
    Requires call
    """
    def __init__(self, channel, application, data=(), timeout=None, callerid=None, variables={}, account=None, async=True):
        """
        `channel` is the destination to be called, expressed as a fully qualified Asterisk channel,
        like "SIP/test-account@example.org".

        `application` is the name of the application to be executed, and `data` is optionally any
        parameters to pass to the application, as an ordered sequence (list or tuple) of strings,
        escaped as necessary (the '|' character is special).

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
            self['Data'] = '|'.join((str(d) for d in data))
            
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
    Pings the AMI server. The response value is the number of seconds the trip took, or -1 in case
    of failure.
    """
    _start_time = None #The time at which the ping message was built
    
    def __init__(self):
        _Request.__init__(self, 'Ping')
        
    def build_request(self, id_generator, **kwargs):
        """
        Records the time at which the request was assembled, to provide a latency value.
        """
        request = _Request.build_request(self, id_generator, kwargs)
        self._start_time = time.time()
        return request
        
    def process_response(self, response):
        """
        Responds with the number of seconds elapsed since the message was prepared for transmission
        or -1 in case the server didn't respond as expected.
        """
        if response.get('Response') == 'Pong':
            return time.time() - self._start_time
        return -1
        
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

class QueueRemove(_Request):
    """
    Removes a member from a queue.

    Upon success, a 'QueueMemberRemoved' event will be generated.

    Requires agent
    """
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
    def __init__(self, queue=None):
        """
        Describes all queues in the system, unless `queue` is given, which limits the scope to one.
        """
        _Request.__init__(self, "QueueStatus")
        if not queue is None:
            self['Queue'] = queue
            
class Redirect(_Request):
    """
    Redirects a call with to an arbitrary context/extension/priority.
    
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
        
class SetVar(_Request):
    """
    Sets a channel-level or global variable.
    
    Requires call
    """
    def __init__(self, variable, value, channel=None):
        """
        `value` is the value to be set under `variable`.
        
        `channel` is the channel to be affected, or `None`, the default, if the variable is global.
        """
        _Request.__init__(self, 'SetVar')
        if channel:
            self['Channel'] = channel
        self['Variable'] = variable
        self['Value'] = value

class SIPPeers(_Request):
    """
    Lists all SIP peers.

    Any number of 'PeerEntry' events may be generated in response to this request, followed by one
    'PeerlistComplete'.

    Requires system
    """
    def __init__(self):
        _Request.__init__(self, "SIPPeers")

class SIPShowPeer(_Request):
    """
    Provides detailed information about a SIP peer.

    The response has the following key-value pairs:
    - 'ACL' : 'Y' or 'N'
    - 'Address-IP' : The IP of the peer
    - 'Address-Port' : The port of the peer
    - 'AMAflags' : "Unknown"
    - 'Callgroup' : ?
    - 'Callerid' : "Linksys #2" <555>
    - 'Call-limit' : ?
    - 'Channeltype' : "SIP"
    - 'ChanObjectType' : "peer"
    - 'CID-CallingPres' : ?
    - 'Context' : The context associated with the peer
       - 'CodecOrder' : The order in which codecs are tried
       - 'Codecs': A list of supported codecs
       - 'Default-addr-IP' : ?
    - 'Default-addr-port' : ?
    - 'Default-Username' : ?
    - 'Dynamic' : 'Y' or 'N', depending on whether the peer is resolved by static IP or
                  authentication
    - 'Language' : The language preference (may be empty) of this peer
    - 'LastMsgsSent' : ?
    - 'MaxCallBR' : The maximum bitrate supported by the peer, "\d+ kbps"
    - 'MD5SecretExist' : 'Y' or 'N', depending on whether an MD5 secret is defined
    - 'ObjectName' : The internal name of the peer
    - 'Pickupgroup' : ?
    - 'Reg-Contact' : The registration contact address for this peer
    - 'RegExpire': Time until SIP registration expires, "\d+ seconds?"
    - 'RegExtension' : ?
    - 'SecretExist' : 'Y' or 'N', depending on whether a secret is defined.
    - 'SIP-AuthInsecure' : 'yes' or 'no'
    - 'SIP-CanReinvite' : 'Y' or 'N', depending on whether the peer supports REINVITE
    - 'SIP-DTMFmode' : The DTMF transport mode to use with this peer, "rfc2833" or ?
    - 'SIP-NatSupport' : The NATting workarounds supported by this peer, "RFC3581" or ?
    - 'SIP-PromiscRedir' : 'Y' or 'N', depending on whether this peer is allowed to arbitrarily
                           redirect calls
    - 'SIP-Useragent' : The User-Agent of the peer
    - 'SIP-UserPhone' : 'Y' or 'N', (presumably) depending on whether this peer is a terminal device
    - 'SIP-VideoSupport' : 'Y' or 'N'
    - 'SIPLastMsg' : ?
    - 'Status' : 'Unmonitored', 'OK (\d+ ms)'
    - 'ToHost' : ?
    - 'TransferMode' : "open"
    - 'VoiceMailbox' : The mailbox associated with the peer
    
    Requires system
    """
    def __init__(self, peer):
        """
        `peer` is the identifier of the peer for which information is to be retrieved.
        """
        _Request.__init__(self, "SIPShowPeer)
        self['Peer'] = peer
        
class Status(_Request):
    """
    Lists the status of an active channel.

    Zero or one 'Status' events are generated, followed by a 'StatusComplete' event.

    Requires call
    """
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
        - One of the following:
         - 'NewCat' : creates a new category
         - 'RenameCat' : renames a category
         - 'DelCat' : deletes a category
         - 'Update' : changes a value
         - 'Delete' : removes a value
         - 'Append' : adds a value
        - The name of the category to operate on
        - `None` or the name of the variable to operate on
        - `None` or the value to be set/added (has no effect with 'Delete')
        - `None` or a string that needs to be matched in the line to serve as a qualifier
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
    class UnpauseMonitor(_Request):
    """
    Causes a 'UserEvent' event to be generated.
    
    Requires user
    """
    def __init__(self, **kwargs):
        """
        Any keyword-arguments passed will be present in the generated event, making this a crude
        form of message-passing.
        """
        _Request.__init__(self, 'UserEvent')
        for (key, value) in kwargs.items():
            self[key] = value
            
class ManagerAuthError(ManagerError):
    """
    Indicates that a problem occurred while authenticating 
    """
    
