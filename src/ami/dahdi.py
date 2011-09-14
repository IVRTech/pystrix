"""

Event information
=================
 DAHDIShowChannels
 ---------------
 Describes the current state of a DAHDI channel.
 - 'ActionID' : The ID associated with the original request
 #- 'Alarm' : "No Alarm"
 - 'Channel' : The channel being described
 - 'Context' : The context associated with the channel
 - 'DND' : 'Disabled' or 'Enabled'
 #- 'Signalling' : "FXO Kewlstart", "FXS Kewlstart"
 
 DAHDIShowChannelsComplete
 -----------------------
 Indicates that all DAHDI channels have been described.
 - 'ActionID' : The ID associated with the original request
"""

from ami import (_Request, ManagerError)

class DAHDIDNDoff(_Request):
    """
    Sets a DAHDI channel's DND status to off.
    """
    def __init__(self, dahdi_channel):
        """
        `dahdi_channel` is the channel to modify.
        """
        _Request.__init__(self, 'DAHDIDNDoff')
        self['DAHDIChannel'] = dahdi_channel

class DAHDIDNDon(_Request):
    """
    Sets a DAHDI channel's DND status to on.
    """
    def __init__(self, dahdi_channel):
        """
        `dahdi_channel` is the channel to modify.
        """
        _Request.__init__(self, 'DAHDIDNDon')
        self['DAHDIChannel'] = dahdi_channel
        
class DAHDIDialOffhook(_Request):
    """
    Dials a number on an off-hook DAHDI channel.
    """
    def __init__(self, dahdi_channel, number):
        """
        `dahdi_channel` is the channel to use and `number` is the number to dial.
        """
        _Request.__init__(self, 'DAHDIDialOffhook')
        self['DAHDIChannel'] = dahdi_channel
        self['Number'] = number

class DAHDIHangup(_Request):
    """
    Hangs up a DAHDI channel.
    """
    def __init__(self, dahdi_channel):
        """
        `dahdi_channel` is the channel to hang up.
        """
        _Request.__init__(self, 'DAHDIHangup')
        self['DAHDIChannel'] = dahdi_channel

class DAHDIRestart(_Request):
    """
    Fully restarts all DAHDI channels.
    """
    def __init__(self):
        _Request.__init__(self, 'DAHDIRestart')

class DAHDIShowChannels(_Request):
    """
    Provides the current status of all (or one) DAHDI channels through a series of
    'DAHDIShowChannels' events, ending with a 'DAHDIShowChannelsComplete' event.
    """
    def __init__(self, dahdi_channel=None):
        _Request.__init__(self, 'DAHDIShowChannels')
        if not dahdi_channel is None:
            self['DAHDIChannel'] = dahdi_channel
            
