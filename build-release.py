#!/usr/bin/env python
"""
Release-building script for pystrix.
"""
import tarfile
import fileinput

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

def doc_filter(tarinfo):
    return _filter(tarinfo, ('.py','.rst','Makefile'))
    
if __name__ == '__main__':
    base_name = "pystrix-" + VERSION
    archive_name = base_name + ".tar.bz2"
    print("Assembling " + archive_name)
    f = tarfile.open(name=archive_name, mode="w:bz2")
    for line in fileinput.input("pystrix.spec", inplace=True, backup=False):
        if line.startswith('%define initversion'):
            line = "%%define initversion %s" % VERSION 
        print("%s" % (line.rstrip()))
    f.add('pystrix.spec', arcname="%s/pystrix.spec" % base_name)
    f.add('COPYING', arcname="%s/COPYING" % base_name)
    f.add('COPYING.LESSER', arcname="%s/COPYING.LESSER" % base_name)
    print("\tAdded license files")
    f.add('doc',arcname="%s/doc" % base_name, filter=doc_filter)
    f.add('build-release.py', arcname="%s/build-release.py" % base_name, filter=python_filter)
    f.add('setup.py', arcname="%s/setup.py" % base_name, filter=python_filter)
    f.add('pystrix', arcname="%s/pystrix" % base_name, filter=python_filter)
    f.close()
    
