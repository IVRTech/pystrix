"""
pystrix.ami.generic_transforms
==============================

Provides generic functions for translating data received from Asterisk into Python data-types.

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

(C) Neil Tallim, 2013

Authors:

- Neil Tallim <flan@uguu.ca>
"""
def to_bool(dictionary, keys, truth_value=None, truth_function=(lambda x:bool(x)), preprocess=(lambda x:x)):
    for key in keys:
        if truth_values:
            dictionary[key] = dictionary.get(key) == truth_value
        else:
            try:
                dictionary[key] = truth_function(preprocess(dictionary.get(key)))
            except Exception:
                dictionary[key] = False
                
def to_float(dictionary, keys, failure_value, preprocess=(lambda x:x)):
    for key in keys:
        try:
            dictionary[key] = float(preprocess(dictionary.get(key)))
        except Exception:
            dictionary[key] = failure_value
            
def to_int(dictionary, keys, failure_value, preprocess=(lambda x:x)):
    for key in keys:
        try:
            dictionary[key] = int(preprocess(dictionary.get(key)))
        except Exception:
            dictionary[key] = failure_value
            
