#!/usr/bin/env python
"""
Deployment script for pystrix.
"""
__author__ = 'Neil Tallim'


from pystrix import VERSION

from setuptools import setup
import os

CLASSIFIERS = [
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.7',
    'Topic :: Communications :: Telephony'
]

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    author='Marta S.',
    author_email='marsoguti@gmail.com',
    name='pystrix',
    version=VERSION,
    description='Python bindings for Asterisk Manager Interface and Asterisk Gateway Interface',
    long_description=README,
    url='https://github.com/marsoguti/pystrix',
    license='GNU General Public License',
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    packages=[
     'pystrix',
     'pystrix.agi',
     'pystrix.ami',
    ]
)
