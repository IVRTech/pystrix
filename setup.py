#!/usr/bin/env python
"""
Deployment script for pystrix.
"""
__author__ = 'Neil Tallim'

from distutils.core import setup

from pystrix import VERSION

setup(
 name = 'pystrix',
 version = VERSION,
 description = 'Python bindings for Asterisk Manager Interface and Asterisk Gateway Interface',
 author = 'Neil Tallim',
 author_email = 'neil.tallim@linux.com',
 license = 'LGPLv3',
 url = 'http://code.google.com/p/media-storage/',
 packages = [
  'pystrix',
  'pystrix.agi',
  'pystrix.ami',
  ],
)

