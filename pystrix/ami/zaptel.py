"""
pystrix.ami.zaptel
==================

Provides classes meant to be fed to a `Manager` instance's `send_action()` function.

Specifically, this module provides implementations for features specific to the ConfBridge
application.

Support for Zaptel seems to have been deprecated in favour of DAHDI, so this module may disappear
in the future.

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
http://www.asteriskdocs.org/
"""
from ami import (_Request, ManagerError)

class ZapDNDoff(_Request):
    """
    Sets a Zap channel's DND status to off.
    """
    def __init__(self, zap_channel):
        """
        `zap_channel` is the channel to modify.
        """
        _Request.__init__(self, 'ZapDNDoff')
        self['ZapChannel'] = zap_channel

class ZapDNDon(_Request):
    """
    Sets a Zap channel's DND status to on.
    """
    def __init__(self, zap_channel):
        """
        `zap_channel` is the channel to modify.
        """
        _Request.__init__(self, 'ZapDNDon')
        self['ZapChannel'] = zap_channel
        
class ZapDialOffhook(_Request):
    """
    Dials a number on an off-hook Zap channel.
    """
    def __init__(self, zap_channel, number):
        """
        `zap_channel` is the channel to use and `number` is the number to dial.
        """
        _Request.__init__(self, 'ZapDialOffhook')
        self['ZapChannel'] = zap_channel
        self['Number'] = number

class ZapHangup(_Request):
    """
    Hangs up a Zap channel.
    """
    def __init__(self, zap_channel):
        """
        `zap_channel` is the channel to hang up.
        """
        _Request.__init__(self, 'ZapHangup')
        self['ZapChannel'] = zap_channel

class ZapRestart(_Request):
    """
    Fully restarts all Zap channels.
    """
    def __init__(self):
        _Request.__init__(self, 'ZapRestart')

class ZapShowChannels(_Request):
    """
    Provides the current status of all Zap channels through a series of 'ZapShowChannels' events,
    ending with a 'ZapShowChannelsComplete' event.
    """
    def __init__(self):
        _Request.__init__(self, 'ZapShowChannels')

