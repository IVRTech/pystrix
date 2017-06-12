#!/usr/bin/env python
"""
Deployment script for pystrix.
"""

from pystrix import VERSION

from setuptools import setup
import os


CLASSIFIERS = [
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Topic :: Communications :: Telephony'
]

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    author='Marta Solano',
    author_email='marta.solano@ivrtechnology.com',
    name='pystrix',
    version=VERSION,
    description='Python bindings for Asterisk Manager Interface and Asterisk Gateway Interface',
    long_description=README,
    url='https://github.com/IVRTech/pystrix',
    license='GNU General Public License',
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    packages=[
     'pystrix',
     'pystrix.agi',
     'pystrix.ami',
    ]
)
