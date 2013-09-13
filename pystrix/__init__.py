"""
pystrix
=======

pystrix is a collection of classes that provide a simple interface for
interacting with an Asterisk server with Python.

It differs from its contemporaries by being provided as a toolkit, rather than
a framework, allowing it to be used as part of larger projects that may be
incompatible, by design or evolution, with the Twisted framework.

Usage
-----

Importing this package, or the 'agi' or 'ami' sub-packages is recommended over
importing individual modules.
 
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
import agi
import ami

VERSION = '0.9.7'
COPYRIGHT = '2013, Neil Tallim <flan@uguu.ca>'
