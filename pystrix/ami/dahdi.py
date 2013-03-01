"""
pystrix.ami.dahdi
=================

Provides classes meant to be fed to a `Manager` instance's `send_action()` function.

Specifically, this module provides implementations for features specific to the DAHDI technology.
 
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

The requests implemented by this module follow the definitions provided by
https://wiki.asterisk.org/
"""
from ami import (_Request, ManagerError)
import dahdi_events
import generic_transforms

class DAHDIDNDoff(_Request):
    """
    Sets a DAHDI channel's DND status to off.
    """
    def __init__(self, dahdi_channel):
        """
        `dahdi_channel` is the channel to modify.
        """
        _Request.__init__(self, 'DAHDIDNDoff')
        self['DAHDIChannel'] = dahdi_channel

class DAHDIDNDon(_Request):
    """
    Sets a DAHDI channel's DND status to on.
    """
    def __init__(self, dahdi_channel):
        """
        `dahdi_channel` is the channel to modify.
        """
        _Request.__init__(self, 'DAHDIDNDon')
        self['DAHDIChannel'] = dahdi_channel
        
class DAHDIDialOffhook(_Request):
    """
    Dials a number on an off-hook DAHDI channel.
    """
    def __init__(self, dahdi_channel, number):
        """
        `dahdi_channel` is the channel to use and `number` is the number to dial.
        """
        _Request.__init__(self, 'DAHDIDialOffhook')
        self['DAHDIChannel'] = dahdi_channel
        self['Number'] = number

class DAHDIHangup(_Request):
    """
    Hangs up a DAHDI channel.
    """
    def __init__(self, dahdi_channel):
        """
        `dahdi_channel` is the channel to hang up.
        """
        _Request.__init__(self, 'DAHDIHangup')
        self['DAHDIChannel'] = dahdi_channel

class DAHDIRestart(_Request):
    """
    Fully restarts all DAHDI channels.
    """
    def __init__(self):
        _Request.__init__(self, 'DAHDIRestart')

class DAHDIShowChannels(_Request):
    """
    Provides the current status of all (or one) DAHDI channels through a series of
    'DAHDIShowChannels' events, ending with a 'DAHDIShowChannelsComplete' event.
    """
    _aggregates = (dahdi_events.DAHDIShowChannels_Aggregate,)
    _synchronous_events_list = (dahdi_events.DAHDIShowChannels,)
    _synchronous_events_finalising = (dahdi_events.DAHDIShowChannelsComplete,)
    
    def __init__(self, dahdi_channel=None):
        _Request.__init__(self, 'DAHDIShowChannels')
        if not dahdi_channel is None:
            self['DAHDIChannel'] = dahdi_channel
            
