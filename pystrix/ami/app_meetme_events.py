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
from ami import _Message

class MeetmeJoin(_Message):
    """
    Indicates that a user has joined a Meetme bridge.
    
    - 'Channel' : The channel that was bridged
    - 'Meetme' : The ID of the Meetme bridge, typically a number formatted as a string
    - 'Uniqueid' : An Asterisk unique value
    - 'Usernum' : The bridge-specific participant ID assigned to the channel
    """

class MeetmeMute(_Message):
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
        (headers, data) = _Message.process(self)
        
        headers['Status'] = headers.get('Status') == 'on'
        
        return (headers, data)
        
