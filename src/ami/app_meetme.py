"""

Event information
=================
 MeetmeJoin
 ----------
 - 'Channel' : The channel that was bridged
 - 'Meetme' : The ID of the Meetme bridge, typically a number formatted as a string
 - 'Uniqueid' : An Asterisk unique value (approximately the UNIX timestamp of the event)
 - 'Usernum' : The bridge-specific participant ID assigned to the channel
 
 MeetmeMute
 ----------
 Indicates that a user has been muted in a Meetme bridge.
 - 'Channel' : The channel that was muted
 - 'Meetme' : The ID of the Meetme bridge, typically a number formatted as a string
 - 'Status' : 'on' or 'off', depending on whether the user was muted or unmuted
 - 'Uniqueid' : An Asterisk unique value (approximately the UNIX timestamp of the event)
 - 'Usernum' : The participant ID of the user that was affected
"""

from ami import (_Request, ManagerError)

class MeetmeMute(_Request):
    """
    Mutes a participant in a Meetme bridge.
    
    Requires call
    """
    def __init__(self, meetme, usernum):
        """
        `meetme` is the identifier of the bridge and `usernum` is the participant ID of the user to
        be muted, which is associated with a channel by the 'MeetmeJoin' event. If successful, this
        request will trigger a 'MeetmeMute' event.
        """
        _Request.__init__(self, 'MeetmeMute')
        self['Meetme'] = meetme
        self['Usernum'] = usernum

class MeetmeUnmute(_Request):
    """
    Unmutes a participant in a Meetme bridge.
    
    Requires call
    """
    def __init__(self, meetme, usernum):
        """
        `meetme` is the identifier of the bridge and `usernum` is the participant ID of the user to
        be unmuted, which is associated with a channel by the 'MeetmeJoin' event. If successful,
        this request will trigger a 'MeetmeMute' event.
        """
        _Request.__init__(self, 'MeetmeUnmute')
        self['Meetme'] = meetme
        self['Usernum'] = usernum
        
