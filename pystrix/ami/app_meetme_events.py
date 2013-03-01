"""
pystrix.ami.app_meetme_events
=============================

Provides defnitions and filtering rules for events that may be raised by Asterisk's Meetme module.

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

class MeetmeJoin(_Event):
    """
    Indicates that a user has joined a Meetme bridge.
    
    - 'Channel' : The channel that was bridged
    - 'Meetme' : The ID of the Meetme bridge, typically a number formatted as a string
    - 'Uniqueid' : An Asterisk unique value
    - 'Usernum' : The bridge-specific participant ID assigned to the channel
    """

class MeetmeList(_Event):
    """
    Describes a participant in a Meetme room.
    
    - 'Admin' : 'Yes' or 'No'
    - 'CallerIDNum' : The (often) numeric address of the participant
    - 'CallerIDName' (optional) : The name of the participant on supporting channels
    - 'Channel' : The Asterisk channel in use by the participant
    - 'Conference' : The room's identifier
    - 'ConnectedLineNum' : unknown
    - 'ConnectedLineName' : unknown
    - 'MarkedUser' : 'Yes' or 'No'
    - 'Muted' : "By admin", "By self", "No"
    - 'Role' : "Listen only", "Talk only", "Talk and listen"
    - 'Talking' : 'Yes', 'No', or 'Not monitored'
    - 'UserNumber' : The ID of the participant in the conference
    """
    def process(self):
        """
        Translates the 'Admin' and 'MarkedUser' headers' values into bools.
        
        Translates the 'Talking' header's value into a bool, or `None` if not monitored.
        
        Translates the 'UserNumber' header's value into an int, or -1 on failure.
        """
        (headers, data) = _Event.process(self)
        
        talking = headers.get('Talking')
        if talking == 'Yes':
            headers['Talking'] = True
        elif talking == 'No':
            headers['Talking'] = False
        else:
            headers['Talking'] = None
        
        generic_transforms.to_bool(headers, ('Admin', 'MarkedUser',), truth_value='Yes')
        generic_transforms.to_int(headers, ('UserNumber',), -1)
            
        return (headers, data)

class MeetmeListComplete(_Event):
    """
    Indicates that all participants in a Meetme query have been enumerated.
    
    - 'ListItems' : The number of items returned prior to this event
    """
    def process(self):
        """
        Translates the 'ListItems' header's value into an int, or -1 on failure.
        """
        (headers, data) = _Event.process(self)
        
        generic_transforms.to_int(headers, ('ListItems',), -1)
        
        return (headers, data)

class MeetmeListRooms(_Event):
    """
    Describes a Meetme room.
    
    And, yes, it's plural in Asterisk, too.
    
    - 'Activity' : The duration of the conference
    - 'Conference' : The room's identifier
    - 'Creation' : 'Dynamic' or 'Static'
    - 'Locked' : 'Yes' or 'No'
    - 'Marked' : The number of marked users, but not as an integer: 'N/A' or %.4d
    - 'Parties' : The number of participants
    """
    def process(self):
        """
        Translates the 'Parties' header's value into an int, or -1 on failure.
        
        Translates the 'Locked' header's value into a bool.
        """
        (headers, data) = _Event.process(self)
        
        generic_transforms.to_bool(headers, ('Locked',), truth_value='Yes')
        generic_transforms.to_int(headers, ('Parties',), -1)
        
        return (headers, data)

class MeetmeListRoomsComplete(_Event):
    """
    Indicates that all Meetme rooms have been enumerated.
    
    - 'ListItems' : The number of items returned prior to this event
    """
    def process(self):
        """
        Translates the 'ListItems' header's value into an int, or -1 on failure.
        """
        (headers, data) = _Event.process(self)
        
        generic_transforms.to_int(headers, ('ListItems',), -1)
        
        return (headers, data)

class MeetmeMute(_Event):
    """
    Indicates that a user has been muted in a Meetme bridge.
    
    - 'Channel' : The channel that was muted
    - 'Meetme' : The ID of the Meetme bridge, typically a number formatted as a string
    - 'Status' : 'on' or 'off', depending on whether the user was muted or unmuted
    - 'Uniqueid' : An Asterisk unique value
    - 'Usernum' : The participant ID of the user that was affected
    """
    def process(self):
        """
        Translates the 'Status' header's value into a bool.
        """
        (headers, data) = _Event.process(self)
        
        generic_transforms.to_bool(headers, ('Status',), truth_value='on')
        
        return (headers, data)
        
        
#List-aggregation events
####################################################################################################
#These define non-Asterisk-native event-types that collect multiple events (cases where multiple
#events are generated in response to a single action) and emit the bundle as a single message.

class MeetmeList_Aggregate(_Aggregate):
    """
    Emitted after all participants have been received in response to a MeetmeList request.
    
    Its members consist of MeetmeList events.
    
    It is finalised by MeetmeListComplete.
    """
    _name = "MeetmeList_Aggregate"
    
    _aggregation_members = (MeetmeList,)
    _aggregation_finalisers = (MeetmeListComplete,)
    
    def _finalise(self, event):
        self._check_list_items_count(event, 'ListItems')
        return _Aggregate._finalise(self, event)
        
class MeetmeListRooms_Aggregate(_Aggregate):
    """
    Emitted after all participants have been received in response to a MeetmeListRooms request.
    
    Its members consist of MeetmeListRooms events.
    
    It is finalised by MeetmeListRoomsComplete.
    """
    _name = "MeetmeListRooms_Aggregate"
    
    _aggregation_members = (MeetmeListRooms,)
    _aggregation_finalisers = (MeetmeListRoomsComplete,)
    
    def _finalise(self, event):
        self._check_list_items_count(event, 'ListItems')
        return _Aggregate._finalise(self, event)
        
