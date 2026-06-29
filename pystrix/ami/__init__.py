"""
pystrix.ami
===========

Provides a library suitable for interacting with an Asterisk server using the
Asterisk Management Interface (AMI) protocol.

Usage
-----

Importing this package is recommended over importing individual modules.

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
"""

# Register events
from pystrix.ami import (
    app_confbridge,
    app_confbridge_events,
    app_meetme,
    app_meetme_events,
    core,
    core_events,
    dahdi,
    dahdi_events,
)
from pystrix.ami.ami import (
    _EVENT_REGISTRY,
    _EVENT_REGISTRY_REV,
    EVENT_GENERIC,
    KEY_ACTION,
    KEY_ACTIONID,
    KEY_EVENT,
    KEY_RESPONSE,
    RESPONSE_GENERIC,
    Error,
    Manager,
    ManagerError,
    ManagerSocketError,
    _Aggregate,
    _Event,
    register_event_class,
    unregister_event_class,
)

for module in (
    core_events,
    dahdi_events,
    app_confbridge_events,
    app_meetme_events,
):
    for name in (e for e in dir(module) if not e.startswith("_")):
        class_object = getattr(module, name)
        if not (
            isinstance(class_object, type)
            and issubclass(class_object, (_Event, _Aggregate))
        ):
            continue
        _EVENT_REGISTRY[name] = class_object
        _EVENT_REGISTRY_REV[class_object] = name
del _EVENT_REGISTRY
del _EVENT_REGISTRY_REV
del _Event
del _Aggregate
