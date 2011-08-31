"""
pystrix

Purpose
=======
 pystrix is a collection of classes that provide a simple interface for
 interacting with an Asterisk server with Python.
 
 It differs from its contemporaries by being provided as a toolkit, rather than
 a framework, allowing it to be used as part of larger projects that may be
 incompatible, by design or evolution, with the Twisted framework.
 
Usage
=====
 Asterisk's type-namespace is pretty easy to keep separate from most program
 logic, so importing this package is recommended over importing its modules.
 
 For more complete information, please see the examples directory distributed
 with the source code.
 
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
"""
from agi_core import (
 CHANNEL_DOWN_AVAILABLE, CHANNEL_DOWN_RESERVED, CHANNEL_OFFHOOK, CHANNEL_DIALED, CHANNEL_ALERTING,
 CHANNEL_REMOTE_ALERTING, CHANNEL_UP, CHANNEL_BUSY,
 FORMAT_SLN, FORMAT_G723, FORMAT_G729, FORMAT_GSM, FORMAT_ALAW, FORMAT_ULAW, FORMAT_VOX, FORMAT_WAV,
 LOG_DEBUG, LOG_INFO, LOG_WARN, LOG_ERROR, LOG_CRITICAL,
 TDD_ON, TDD_OFF, TDD_MATE,
 AGIException, AGIError, AGIUnknownError, AGIAppError, AGIHangup, AGISIGPIPEHangup, AGIResultHangup,
 AGIDBError, AGIDeadChannelError, AGIUsageError, AGIInvalidCommandError,
)

from agi import (
 AGI,
 AGISIGHUPHangup,
)

from fagi import (
 FastAGIServer, FastAGI,
)

from manager import (
 ManagerMsg, Event, Manager,
 ManagerException, ManagerSocketException, ManagerAuthException,
)

