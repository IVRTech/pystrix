"""

Support for Zaptel seems to have been deprecated in favour of DAHDI, so this module may disappear in
the future.

Event information
=================
 ZapShowChannels
 ---------------
 Describes the current state of a Zaptel channel.
 - 'ActionID' : The ID associated with the original request
 - 'Alarm' : "No Alarm"
 - 'Channel' : The channel being described
 - 'Context' : The context associated with the channel
 - 'DND' : 'Disabled' or 'Enabled'
 - 'Signalling' : "FXO Kewlstart", "FXS Kewlstart"
 
 ZapShowChannelsComplete
 -----------------------
 Indicates that all Zaptel channels have been described.
 - 'ActionID' : The ID associated with the original request
"""

from ami import (_Request, ManagerError)

class ZapDNDoff(_Request):
    """
    Sets a Zap channel's DND status to off.
    """
    def __init__(self, zap_channel):
        """
        `zap_channel` is the channel to modify.
        """
        _Request.__init__(self, 'ZapDNDoff')
        self['ZapChannel'] = zap_channel

class ZapDNDon(_Request):
    """
    Sets a Zap channel's DND status to on.
    """
    def __init__(self, zap_channel):
        """
        `zap_channel` is the channel to modify.
        """
        _Request.__init__(self, 'ZapDNDon')
        self['ZapChannel'] = zap_channel
        
class ZapDialOffhook(_Request):
    """
    Dials a number on an off-hook Zap channel.
    """
    def __init__(self, zap_channel, number):
        """
        `zap_channel` is the channel to use and `number` is the number to dial.
        """
        _Request.__init__(self, 'ZapDialOffhook')
        self['ZapChannel'] = zap_channel
        self['Number'] = number

class ZapHangup(_Request):
    """
    Hangs up a Zap channel.
    """
    def __init__(self, zap_channel):
        """
        `zap_channel` is the channel to hang up.
        """
        _Request.__init__(self, 'ZapHangup')
        self['ZapChannel'] = zap_channel

class ZapRestart(_Request):
    """
    Fully restarts all Zap channels.
    """
    def __init__(self):
        _Request.__init__(self, 'ZapRestart')

class ZapShowChannels(_Request):
    """
    Provides the current status of all Zap channels through a series of 'ZapShowChannels' events,
    ending with a 'ZapShowChannelsComplete' event.
    """
    def __init__(self):
        _Request.__init__(self, 'ZapShowChannels')

