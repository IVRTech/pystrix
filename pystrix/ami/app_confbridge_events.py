"""
pystrix.ami.app_confbridge_events
=================================

Provides defnitions and filtering rules for events that may be raised by Asterisk's ConfBridge
module.

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

The events implemented by this module follow the definitions provided by
http://www.asteriskdocs.org/ and https://wiki.asterisk.org/
"""
from ami import (_Aggregate, _Event)
import generic_transforms
    
class ConfbridgeEnd(_Event):
    """
    Indicates that a ConfBridge has ended.
    
    - 'Conference' : The room's identifier
    """
    
class ConfbridgeJoin(_Event):
    """
    Indicates that a participant has joined a ConfBridge room.
    
    `NameRecordingPath` blocks on <path>
    
    - 'CallerIDname' (optional) : The name, on supporting channels, of the participant
    - 'CallerIDnum' : The (often) numeric address of the participant
    - 'Channel' : The channel that joined
    - 'Conference' : The identifier of the room that was joined
    - 'NameRecordingPath' (optional) : The path at which the user's name-recording is kept
    - 'Uniqueid' : An Asterisk unique value
    """

class ConfbridgeLeave(_Event):
    """
    Indicates that a participant has left a ConfBridge room.
    
    - 'CallerIDname' (optional) : The name, on supporting channels, of the participant
    - 'CallerIDnum' : The (often) numeric address of the participant
    - 'Channel' : The channel that left
    - 'Conference' : The identifier of the room that was left
    - 'Uniqueid' : An Asterisk unique value
    """
    
class ConfbridgeList(_Event):
    """
    Describes a participant in a ConfBridge room.
    
    - 'Admin' : 'Yes' or 'No'
    - 'CallerIDNum' : The (often) numeric address of the participant
    - 'CallerIDName' (optional) : The name of the participant on supporting channels
    - 'Channel' : The Asterisk channel in use by the participant
    - 'Conference' : The room's identifier
    - 'MarkedUser' : 'Yes' or 'No'
    - 'NameRecordingPath' (optional) : The path at which the user's name-recording is kept
    """
    def process(self):
        """
        Translates the 'Admin' and 'MarkedUser' headers' values into bools.
        """
        (headers, data) = _Event.process(self)
        
        generic_transforms.to_bool(headers, ('Admin', 'MarkedUser',), truth_value='Yes')
            
        return (headers, data)

class ConfbridgeListComplete(_Event):
    """
    Indicates that all participants in a ConfBridge room have been enumerated.
    
    - 'ListItems' : The number of items returned prior to this event
    """
    def process(self):
        """
        Translates the 'ListItems' header's value into an int, or -1 on failure.
        """
        (headers, data) = _Event.process(self)
        
        generic_transforms.to_int(headers, ('ListItems',), -1)
        
        return (headers, data)
        
class ConfbridgeListRooms(_Event):
    """
    Describes a ConfBridge room.
    
    And, yes, it's plural in Asterisk, too.
    
    - 'Conference' : The room's identifier
    - 'Locked' : 'Yes' or 'No'
    - 'Marked' : The number of marked users
    - 'Parties' : The number of participants
    """
    def process(self):
        """
        Translates the 'Marked' and 'Parties' headers' values into ints, or -1 on failure.
        
        Translates the 'Locked' header's value into a bool.
        """
        (headers, data) = _Event.process(self)
        
        generic_transforms.to_bool(headers, ('Locked',), truth_value='Yes')
        generic_transforms.to_int(headers, ('Marked', 'Parties',), -1)
        
        return (headers, data)

class ConfbridgeListRoomsComplete(_Event):
    """
    Indicates that all ConfBridge rooms have been enumerated.
    
    - 'ListItems' : The number of items returned prior to this event
    """
    def process(self):
        """
        Translates the 'ListItems' header's value into an int, or -1 on failure.
        """
        (headers, data) = _Event.process(self)
        
        generic_transforms.to_int(headers, ('ListItems',), -1)
        
        return (headers, data)
        
class ConfbridgeStart(_Event):
    """
    Indicates that a ConfBridge has started.
    
    - 'Conference' : The room's identifier
    """

class ConfbridgeTalking(_Event):
    """
    Indicates that a participant has started or stopped talking.
    
    - 'Channel' : The Asterisk channel in use by the participant
    - 'Conference' : The room's identifier
    - 'TalkingStatus' : 'on' or 'off'
    - 'Uniqueid' : An Asterisk unique value
    """
    def process(self):
        """
        Translates the 'TalkingStatus' header's value into a bool.
        """
        (headers, data) = _Event.process(self)
        
        generic_transforms.to_bool(headers, ('TalkingStatus',), truth_value='on')
        
        return (headers, data)
        
        
#List-aggregation events
####################################################################################################
#These define non-Asterisk-native event-types that collect multiple events (cases where multiple
#events are generated in response to a single action) and emit the bundle as a single message.

class ConfbridgeList_Aggregate(_Aggregate):
    """
    Emitted after all conference participants have been received in response to a ConfbridgeList
    request.
    
    Its members consist of ConfbridgeList events.
    
    It is finalised by ConfbridgeListComplete.
    """
    _name = "ConfbridgeList_Aggregate"
    
    _aggregation_members = (ConfbridgeList,)
    _aggregation_finalisers = (ConfbridgeListComplete,)
    
    def _finalise(self, event):
        self._check_list_items_count(event, 'ListItems')
        return _Aggregate._finalise(self, event)
        
class ConfbridgeListRooms_Aggregate(_Aggregate):
    """
    Emitted after all conference rooms have been received in response to a ConfbridgeListRooms
    request.
    
    Its members consist of ConfbridgeListRooms events.
    
    It is finalised by ConfbridgeListRoomsComplete.
    """
    _name = "ConfbridgeListRooms_Aggregate"
    
    _aggregation_members = (ConfbridgeListRooms,)
    _aggregation_finalisers = (ConfbridgeListRoomsComplete,)
    
    def _finalise(self, event):
        self._check_list_items_count(event, 'ListItems')
        return _Aggregate._finalise(self, event)
        
