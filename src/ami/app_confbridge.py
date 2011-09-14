"""

Event information
=================
 ConfbridgeEnd
 -------------
 Indicates that a ConfBridge has ended.
 - 'Conference' : The room's identifier
 
 ConfbridgeJoin
 --------------
 Indicates that a participant has joined a ConfBridge room.
 - 'CallerIDname' (optional) : The name, on supporting channels, of the participant
 - 'CallerIDnum' : The (often) numeric address of the participant
 - 'Channel' : The channel that joined
 - 'Conference' : The identifier of the room that was joined
 - 'Uniqueid' : An Asterisk unique value (approximately the UNIX timestamp of the event)

 ConfbridgeLeave
 --------------
 Indicates that a participant has left a ConfBridge room.
 - 'CallerIDname' (optional) : The name, on supporting channels, of the participant
 - 'CallerIDnum' : The (often) numeric address of the participant
 - 'Channel' : The channel that left
 - 'Conference' : The identifier of the room that was left
 - 'Uniqueid' : An Asterisk unique value (approximately the UNIX timestamp of the event)

 ConfbridgeList
 --------------
 Describes a participant in a ConfBridge room.
 - 'Admin' : 'Yes' or 'No'
 - 'CallerIDNum' : The (often) numeric address of the participant
 - 'CallerIDName' (optional) : The name of the participant on supporting channels
 - 'Channel' : The Asterisk channel in use by the participant
 - 'Conference' : The room's identifier
 - 'MarkedUser' : 'Yes' or 'No'

 ConfbridgeListComplete
 ----------------------
 Indicates that all participants in a ConfBridge room have been enumerated.
 - 'ListItems' : The number of items returned prior to this event

 ConfbridgeListRooms
 -------------------
 Describes a ConfBridge room.
 - 'Conference' : The room's identifier
 - 'Locked' : 'Yes' or 'No'
 - 'Marked' : The number of marked users
 - 'Parties' : The number of participants

 ConfbridgeListRoomsComplete
 ---------------------------
 Indicates that all ConfBridge rooms have been enumerated.
 - 'ListItems' : The number of items returned prior to this event

 ConfbridgeStart
 ---------------
 Indicates that a ConfBridge has started.
 - 'Conference' : The room's identifier

 ConfbridgeTalking
 -----------------
 Indicates that a participant has started or stopped talking.
 - 'Channel' : The Asterisk channel in use by the participant
 - 'Conference' : The room's identifier
 - 'TalkingStatus' : 'on' or 'off'
 - 'Uniqueid' : An Asterisk unique value (approximately the UNIX timestamp of the event)
"""

from ami import (_Request, ManagerError)

class ConfbridgeKick(_Request):
    """
    Kicks a participant from a ConfBridge room.
    """
    def __init__(self, conference, channel):
        """
        `channel` is the channel to be kicked from `conference`.
        """
        _Request.__init__(self, 'ConfbridgeKick')
        self['Conference'] = conference
        self['Channel'] = channel
        
class ConfbridgeList(_Request):
    """
    Lists all participants in a ConfBridge room.

    A series of 'ConfbridgeList' events follow, with one 'ConfbridgeListComplete' event at the end.
    """
    def __init__(self, conference):
        """
        `conference` is the identifier of the bridge.
        """
        _Request.__init__(self, 'ConfbridgeList')
        self['Conference'] = conference

class ConfbridgeListRooms(_Request):
    """
    Lists all ConfBridge rooms.

    A series of 'ConfbridgeListRooms' events follow, with one 'ConfbridgeListRoomsComplete' event at
    the end.
    """
    def __init__(self):
        _Request.__init__(self, 'ConfbridgeListRooms')

class ConfbridgeLock(_Request):
    """
    Locks a ConfBridge room, disallowing access to non-administrators.
    """
    def __init__(self, conference):
        """
        `conference` is the identifier of the bridge.
        """
        _Request.__init__(self, 'ConfbridgeLock')
        self['Conference'] = conference

class ConfbridgeUnlock(_Request):
    """
    Unlocks a ConfBridge room, allowing access to non-administrators.
    """
    def __init__(self, conference):
        """
        `conference` is the identifier of the bridge.
        """
        _Request.__init__(self, 'ConfbridgeUnlock')
        self['Conference'] = conference

class ConfbridgeMute(_Request):
    """
    Mutes a participant in a ConfBridge room.
    """
    def __init__(self, conference, channel):
        """
        `channel` is the channel to be muted in `conference`.
        """
        _Request.__init__(self, 'ConfbridgeMute')
        self['Conference'] = conference
        self['Channel'] = channel

class ConfbridgeUnmute(_Request):
    """
    Unmutes a participant in a ConfBridge room.
    """
    def __init__(self, conference, channel):
        """
        `channel` is the channel to be unmuted in `conference`.
        """
        _Request.__init__(self, 'ConfbridgeUnmute')
        self['Conference'] = conference
        self['Channel'] = channel

class ConfbridgeStartRecord(_Request):
    """
    Starts recording a ConfBridge conference.

    A 'VarSet' event will be generated to indicate the absolute path of the recording. To identify
    it, match its 'Channel' key against "ConfBridgeRecorder/conf-?-...", where "..." is
    Asterisk-generated identification data that can be discarded and "?" is the room ID. The
    'Variable' key must be "MIXMONITOR_FILENAME", with the 'Value' key holding the file's path.
    """
    def __init__(self, conference, filename=None):
        """
        `conference` is the room to be recorded, and `filename`, optional, is the path,
        Asterisk-resolved or absolute, of the file to write.
        """
        _Request.__init__(self, 'ConfbridgeStartRecord')
        self['Conference'] = conference
        if filename:
            self['RecordFile'] = filename

class ConfbridgeStopRecord(_Request):
    """
    Stops recording a ConfBridge conference.

    A 'Hangup' event will be generated when the recorder detaches from the conference. To identify
    it, match its 'Channel' key against "ConfBridgeRecorder/conf-?-...", where "..." is
    Asterisk-generated identification data that can be discarded and "?" is the room ID.
    """
    def __init__(self, conference):
        """
        `conference` is the room being recorded.
        """
        _Request.__init__(self, 'ConfbridgeStopRecord')
        self['Conference'] = conference

class ConfbridgeSetSingleVideoSrc(_Request):
    """
    Sets the video source for the conference to a single channel's stream.
    """
    def __init__(self, conference, channel):
        """
        `channel` is the video source in `conference`.
        """
        _Request.__init__(self, 'ConfbridgeSetSingleVideoSource')
        self['Conference'] = conference
        self['Channel'] = channel

