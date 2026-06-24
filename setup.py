#!/usr/bin/env python
"""
Deployment script for pystrix.
"""

from pystrix import VERSION

from setuptools import setup
import os


CLASSIFIERS = [
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
    'Programming Language :: Python :: 3.12',
    'Topic :: Communications :: Telephony'
]

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    author='Marta Solano',
    author_email='marta.solano@ivrtechnology.com',
    name='pystrix',
    version=VERSION,
    description='Python bindings for Asterisk Manager Interface and Asterisk Gateway Interface',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/IVRTech/pystrix',
    license='GNU Lesser General Public License v3 or later',
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    python_requires='>=3.9',
    packages=[
     'pystrix',
     'pystrix.agi',
     'pystrix.ami',
    ]
)
