"""
pystrix.agi
===========

Provides a library suitable for interacting with an Asterisk server using the
Asterisk Gateway Interface (AGI) protocol.
 
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
from agi_core import (
 AGIException, AGIError, AGINoResultError, AGIUnknownError, AGIAppError,
 AGIHangup, AGISIGPIPEHangup, AGIResultHangup,
 AGIDeadChannelError, AGIUsageError, AGIInvalidCommandError,
)

from agi import (
 AGI,
 AGISIGHUPHangup,
)

from fastagi import (
 FastAGIServer, FastAGI,
)

import core

