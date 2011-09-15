"""
pystrix.ami.dahdi_events

Purpose
=======
 Provides defnitions and filtering rules for events that may be raised by Asterisk's DAHDI module.
 
Usage
=====
 This module should never be used directly by user code. Rather, it is a pre-processing resource to
 simplify event-interpretation and a reference for application authors.
 
Legal
=====
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
from ami import _Message

class DAHDIShowChannels(_Message):
    """
    Describes the current state of a DAHDI channel.
    - 'ActionID' : The ID associated with the original request
    - 'Channel' : The channel being described
    - 'Context' : The context associated with the channel
    - 'DND' : 'Disabled' or 'Enabled'
    """
    def process(self):
        """
        Translates the 'DND' header's value into a bool.
        """
        (headers, data) = _Message.process(self)
        headers['DND'] = headers.get('DND') == 'Enabled'
        return (headers, data)

class DAHDIShowChannelsComplete(_Message):
    """
    Indicates that all DAHDI channels have been described.
    - 'ActionID' : The ID associated with the original request
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
 
