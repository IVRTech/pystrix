#!/usr/bin/env python
"""
Deployment script for pystrix.
"""
__author__ = 'Neil Tallim'

from distutils.core import setup

setup(
 name = 'pystrix',
 version = '0.9.1',
 description = 'Python bindings for Asterisk Manager Interface and Asterist Gateway Interface',
 author = 'Neil Tallim',
 author_email = 'neil.tallim@linux.com',
 license = 'LGPLv3',
 url = 'http://code.google.com/p/pystrix/',
 packages = [
  'pystrix',
  'pystrix.agi',
  'pystrix.ami',
 ],
)
