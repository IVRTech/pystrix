"""
pystrix.ami.app_confbridge
==========================

Provides classes meant to be fed to a `Manager` instance's `send_action()` function.

Specifically, this module provides implementations for features specific to the ConfBridge
application.
 
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

The requests and events implemented by this module follow the definitions provided by
https://wiki.asterisk.org/
"""
from ami import (_Request, ManagerError)
import core_events
import app_confbridge_events
import generic_transforms

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
    _aggregates = (app_confbridge_events.ConfbridgeList_Aggregate,)
    _synchronous_events_list = (app_confbridge_events.ConfbridgeList,)
    _synchronous_events_finalising = (app_confbridge_events.ConfbridgeListComplete,)
    
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
    _aggregates = (app_confbridge_events.ConfbridgeListRooms_Aggregate,)
    _synchronous_events_list = (app_confbridge_events.ConfbridgeListRooms,)
    _synchronous_events_finalising = (app_confbridge_events.ConfbridgeListRoomsComplete,)
    
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

class ConfbridgeMoHOn(_Request):
    """
    Forces MoH to a participant in a ConfBridge room.
    
    This action does not mute audio coming from the participant.
    
    Depends on <path>.
    """
    def __init__(self, conference, channel):
        """
        `channel` is the channel to which MoH should be started in `conference`.
        """
        _Request.__init__(self, 'ConfbridgeMoHOn')
        self['Conference'] = conference
        self['Channel'] = channel

class ConfbridgeMoHOff(_Request):
    """
    Stops forcing MoH to a participant in a ConfBridge room.
    
    This action does not unmute audio coming from the participant.
    
    Depends on <path>.
    """
    def __init__(self, conference, channel):
        """
        `channel` is the channel to which MoH should be stopped in `conference`.
        """
        _Request.__init__(self, 'ConfbridgeMoHOff')
        self['Conference'] = conference
        self['Channel'] = channel

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

class ConfbridgePlayFile(_Request):
    """
    Plays a file to individuals or an entire conference.
    
    Note: This implementation is built upon the not-yet-accepted patch under
    https://issues.asterisk.org/jira/browse/ASTERISK-19571
    """
    def __init__(self, file, conference, channel=None):
        """
        `file`, resolved like other Asterisk media, is played to `conference`
        or, if specified, a specific `channel` therein.
        """
        _Request.__init__(self, 'ConfbridgePlayFile')
        self['Conference'] = conference
        if channel:
            self['Channel'] = channel
        self['File'] = file
        
class ConfbridgeStartRecord(_Request):
    """
    Starts recording a ConfBridge conference.

    A 'VarSet' event will be generated to indicate the absolute path of the recording. To identify
    it, match its 'Channel' key against "ConfBridgeRecorder/conf-?-...", where "..." is
    Asterisk-generated identification data that can be discarded and "?" is the room ID. The
    'Variable' key must be "MIXMONITOR_FILENAME", with the 'Value' key holding the file's path.
    """
    _synchronous_events_finalising = (core_events.VarSet,)
    
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
    _synchronous_events_finalising = (core_events.Hangup,)
    
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

