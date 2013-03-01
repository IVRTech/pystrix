"""
pystrix.ami.app_meetme
======================

Provides classes meant to be fed to a `Manager` instance's `send_action()` function.

Specifically, this module provides implementations for features specific to the Meetme
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
http://www.asteriskdocs.org/ and https://wiki.asterisk.org/
"""
from ami import (_Request, ManagerError)
import app_meetme_events
import generic_transforms

class MeetmeList(_Request):
    """
    Lists all participants in all (or one) conferences.

    A series of 'MeetmeList' events follow, with one 'MeetmeListComplete' event at the end.

    Note that if no conferences are active, the response will indicate that it was not successful,
    per https://issues.asterisk.org/jira/browse/ASTERISK-16812
    """
    _aggregates = (app_meetme_events.MeetmeList_Aggregate,)
    _synchronous_events_list = (app_meetme_events.MeetmeList,)
    _synchronous_events_finalising = (app_meetme_events.MeetmeListComplete,)
    
    def __init__(self, conference=None):
        """
        `conference` is the optional identifier of the bridge.
        """
        _Request.__init__(self, 'MeetmeList')
        if not conference is None:
            self['Conference'] = conference
            
class MeetmeListRooms(_Request):
    """
    Lists all conferences.

    A series of 'MeetmeListRooms' events follow, with one 'MeetmeListRoomsComplete' event at the
    end.
    """
    _aggregates = (app_meetme_events.MeetmeListRooms_Aggregate,)
    _synchronous_events_list = (app_meetme_events.MeetmeListRooms,)
    _synchronous_events_finalising = (app_meetme_events.MeetmeListRoomsComplete,)
    
    def __init__(self):
        _Request.__init__(self, 'MeetmeListRooms')
        
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
        
