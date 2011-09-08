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
    
    An unsolicited 'DBGetResponse' event will be generated upon success, with 'Family', 'Key', and
    'Val' headers; 'Family' and 'Key' correspond to the parameters requested, and 'Val' is the
    result.
    
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
    
    A sequential generator is provided in the 'lines' attribute.
    
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
        response.lines = (value for (key, value) in sorted(response.items()) if key.startswith('Line-'))
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
    
    This function will produce an unsolicited 'Hangup' event, which has the following keys:
    - 'Cause' : One of the following numeric values, as a string:
                -  0 : Channel cleared normally
    - 'Cause-txt' : Additional information related to the hangup
    - 'Channel' : The channel hung up
    - 'Uniqueid' : An Asterisk unique value (approximately the UNIX timestamp of the event)
    
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
        _Request.__init__(self, 'MailboxCount)
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
        

#Cleared up to MeetMe, which probably belongs in its own modle
#http://www.asteriskdocs.org/html/re270.html






































    

    

    def status(self, channel = ''):
        """Get a status message from asterisk"""

        cdict = {'Action':'Status'}
        cdict['Channel'] = channel
        response = self.send_action(cdict)
        
        return response

    def redirect(self, channel, exten, priority='1', extra_channel='', context=''):
        """Redirect a channel"""
    
        cdict = {'Action':'Redirect'}
        cdict['Channel'] = channel
        cdict['Exten'] = exten
        cdict['Priority'] = priority
        if context:   cdict['Context']  = context
        if extra_channel: cdict['ExtraChannel'] = extra_channel
        response = self.send_action(cdict)
        
        return response

    def originate(self, channel, exten, context='', priority='', timeout='', caller_id='', async=False, account='', variables={}):
        """Originate a call"""

        cdict = {'Action':'Originate'}
        cdict['Channel'] = channel
        cdict['Exten'] = exten
        if context:   cdict['Context']  = context
        if priority:  cdict['Priority'] = priority
        if timeout:   cdict['Timeout']  = timeout
        if caller_id: cdict['CallerID'] = caller_id
        if async:     cdict['Async']    = 'yes'
        if account:   cdict['Account']  = account
        # join dict of vairables together in a string in the form of 'key=val|key=val'
        # with the latest CVS HEAD this is no longer necessary
        # if variables: cdict['Variable'] = '|'.join(['='.join((str(key), str(value))) for key, value in variables.items()])
        if variables: cdict['Variable'] = ['='.join((str(key), str(value))) for key, value in variables.items()]
              
        response = self.send_action(cdict)
        
        return response
    

    def playdtmf (self, channel, digit) :
        """Plays a dtmf digit on the specified channel"""
        cdict = {'Action':'PlayDTMF'}
        cdict['Channel'] = channel
        cdict['Digit'] = digit
        response = self.send_action(cdict)

        return response

    
    def sippeers(self):
        cdict = {'Action' : 'Sippeers'}
        response = self.send_action(cdict)
        return response

    def sipshowpeer(self, peer):
        cdict = {'Action' : 'SIPshowpeer'}
        cdict['Peer'] = peer
        response = self.send_action(cdict)
        return response
        
        
class ManagerAuthError(ManagerError):
    pass
    
