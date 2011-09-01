import time

from ami import _ManagerRequest

class Hangup(_ManagerRequest):
    """
    Hangs up a channel.
    """
    def __init__(self, channel):
        """
        `channel` is the ID of the channel to be hung up.
        """
        _ManagerRequest.__init__('Hangup')
        self['Channel'] = channel
        
class Login(_ManagerRequest):
    """
    Authenticates to the AMI server.
    """
    def __init__(self, username, secret):
        """
        `username` and `secret` are the credentials used to authenticate.
        """
        _ManagerRequest.__init__('Login')
        self['Username'] = username
        self['Secret'] = secret
        
    def process_response(self, response):
        """
        Raises `ManagerAuthException` if an error is received while attempting to authenticate.
        """
        if response.get_header('Response') == 'Error':
            raise ManagerAuthException(response.get_header('Message'))
        return response
        
class Ping(_ManagerRequest):
    """
    Pings the AMI server.
    """
    _start_time = None #The time at which the ping message was built
    
    def __init__(self):
        _ManagerRequest.__init__('Ping')
        
    def build_request(self, id_generator, **kwargs):
        """
        Records the time at which the request was assembled, to provide a latency value.
        """
        request = _ManagerRequest.build_request(self, id_generator, kwargs)
        self._start_time = time.time()
        return request
        
    def process_response(self, response):
        """
        Responds with the number of seconds elapsed since the message was prepared for transmission
        or -1 in case the server didn't respond as expected.
        """
        if response.get_header('Response') == 'Pong':
            return time.time() - self._start_time
        return -1
        




    def logoff(self):
        """Logoff from the manager"""

        cdict = {'Action':'Logoff'}
        response = self.send_action(cdict)
        
        return response

    

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

    def mailbox_status(self, mailbox):
        """Get the status of the specfied mailbox"""
     
        cdict = {'Action':'MailboxStatus'}
        cdict['Mailbox'] = mailbox
        response = self.send_action(cdict)
        
        return response

    def command(self, command):
        """Execute a command"""

        cdict = {'Action':'Command'}
        cdict['Command'] = command
        response = self.send_action(cdict)
        
        return response

    def extension_state(self, exten, context):
        """Get the state of an extension"""

        cdict = {'Action':'ExtensionState'}
        cdict['Exten'] = exten
        cdict['Context'] = context
        response = self.send_action(cdict)
        
        return response

    def playdtmf (self, channel, digit) :
        """Plays a dtmf digit on the specified channel"""
        cdict = {'Action':'PlayDTMF'}
        cdict['Channel'] = channel
        cdict['Digit'] = digit
        response = self.send_action(cdict)

        return response

    def absolute_timeout(self, channel, timeout):
        """Set an absolute timeout on a channel"""
        
        cdict = {'Action':'AbsoluteTimeout'}
        cdict['Channel'] = channel
        cdict['Timeout'] = timeout
        response = self.send_action(cdict)

        return response

    def mailbox_count(self, mailbox):
        cdict = {'Action':'MailboxCount'}
        cdict['Mailbox'] = mailbox
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
        
        
class ManagerAuthException(ManagerException):
    pass
    
