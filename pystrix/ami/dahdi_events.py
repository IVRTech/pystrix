"""
pystrix.ami.dahdi_events
========================

Provides defnitions and filtering rules for events that may be raised by Asterisk's DAHDI module.

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
from pystrix.ami.ami import (_Aggregate, _Event)
from pystrix.ami import generic_transforms

class DAHDIShowChannels(_Event):
    """
    Describes the current state of a DAHDI channel.
    
    Yes, the event's name is pluralised.
    
    - 'AccountCode': unknown (not present if the DAHDI channel is down)
    - 'Alarm': unknown
    - 'Channel': The channel being described (not present if the DAHDI channel is down)
    - 'Context': The Asterisk context associated with the channel
    - 'DAHDIChannel': The ID of the DAHDI channel
    - 'Description': unknown
    - 'DND': 'Disabled' or 'Enabled'
    - 'Signalling': A lexical description of the current signalling state
    - 'SignallingCode': A numeric description of the current signalling state
    - 'Uniqueid': unknown (not present if the DAHDI channel is down)
    """
    def process(self):
        """
        Translates the 'DND' header's value into a bool.
        
        Translates the 'DAHDIChannel' and 'SignallingCode' headers' values into ints, or -1 on
        failure.
        """
        (headers, data) = _Event.process(self)
        
        generic_transforms.to_bool(headers, ('DND',), truth_value='Enabled')
        generic_transforms.to_int(headers, ('DAHDIChannel', 'SignallingCode',), -1)
                
        return (headers, data)

class DAHDIShowChannelsComplete(_Event):
    """
    Indicates that all DAHDI channels have been described.
    
    - 'Items': The number of items returned prior to this event
    """
    def process(self):
        """
        Translates the 'Items' header's value into an int, or -1 on failure.
        """
        (headers, data) = _Event.process(self)
        
        generic_transforms.to_int(headers, ('Items',), -1)
        
        return (headers, data)
        
        
#List-aggregation events
####################################################################################################
#These define non-Asterisk-native event-types that collect multiple events (cases where multiple
#events are generated in response to a single action) and emit the bundle as a single message.

class DAHDIShowChannels_Aggregate(_Aggregate):
    """
    Emitted after all DAHDI channels have been enumerated in response to a DAHDIShowChannels
    request.
    
    Its members consist of DAHDIShowChannels events.
    
    It is finalised by DAHDIShowChannelsComplete.
    """
    _name = "DAHDIShowChannels_Aggregate"
    
    _aggregation_members = (DAHDIShowChannels,)
    _aggregation_finalisers = (DAHDIShowChannelsComplete,)
    
    def _finalise(self, event):
        self._check_list_items_count(event, 'Items')
        return _Aggregate._finalise(self, event)
        
