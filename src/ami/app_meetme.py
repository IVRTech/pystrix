"""

Event information
=================
 MeetmeJoin
 ----------
 Indicates that a user has joined a Meetme bridge.
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

class MeetmeList(_Request):
    """
    Lists all participants in all (or one) conferences.

    A series of 'MeetmeList' events follow, with one 'MeetmeListComplete' event at the end.

    Note that if no conferences are active, the response will indicate that it was not successful,
    per https://issues.asterisk.org/jira/browse/ASTERISK-16812
    """
    def __init__(self, conference=None):
        """
        `conference` is the optional identifier of the bridge.
        """
        _Request.__init__(self, 'MeetmeList')
        if not conference is None:
            self['Conference'] = conference
            
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
        
