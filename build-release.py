#!/usr/bin/env python
"""
Release-building script for pystrix.
"""
import tarfile

from pystrix import VERSION

def _filter(tarinfo, acceptable_extensions):
    if tarinfo.name.startswith('.'): #Ignore hidden files
        return None
        
    if tarinfo.isdir(): #Directories are good
        return tarinfo
        
    if tarinfo.name.endswith(acceptable_extensions): #It's a file we want
        print("\tAdded " + tarinfo.name)
        return tarinfo
        
    return None #DO NOT WANT
    
def python_filter(tarinfo):
    return _filter(tarinfo, ('.py',))
    
if __name__ == '__main__':
    archive_name = "pystrix-" + VERSION + ".tar.bz2"
    print("Assembling " + archive_name)
    f = tarfile.open(name=archive_name, mode="w:bz2")
    f.add('COPYING')
    f.add('COPYING.LESSER')
    print("\tAdded license files")
    f.add('setup.py', filter=python_filter)
    f.add('pystrix', filter=python_filter)
    f.close()
    
