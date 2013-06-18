#!/usr/bin/env python

#
# Copyright 2013, Intel Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#

'''
Created on 14 nov. 2013

@author: Ronan Le Martret

'''

import os
import sys


# Implementation taken from http://hetland.org
def levenshtein( a, b ):
    """Calculates the Levenshtein distance between a and b."""
    n, m = len( a ), len( b )
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a, b = b, a
        n, m = m, n

    current = range( n + 1 )
    for i in range( 1, m + 1 ):
        previous, current = current, [i] + [0] * n
        for j in range( 1, n + 1 ):
            add, delete = previous[j] + 1, current[j - 1] + 1
            change = previous[j - 1]
            if a[j - 1] != b[i - 1]:
                change = change + 1
            current[j] = min( add, delete, change )

    return current[n]


def get_packaging_files(package_path):
    res=[]
    for tmp_res in os.listdir( package_path ):
        if tmp_res.endswith( ".spec" ) and os.path.isfile( package_path + "/" + tmp_res ):
            res.append(tmp_res)
    return res
        
def findBestSpecFile( package_path, package_name ):
    """Find the name of the spec file which matches best with `package_name`"""
    specFileList = get_packaging_files( package_path )

    specFile = None
    if len( specFileList ) < 1:
        # No spec file in list
        specFile = None
    elif len( specFileList ) == 1:
        # Only one spec file
        specFile = specFileList[0]
    else:
        sameStart = []
        for spec in specFileList:
            if str( spec[:-5] ) == str( package_name ):
                # This spec file has the same name as the package
                specFile = spec
                break
            elif spec.startswith( package_name ):
                # This spec file has a name which looks like the package
                sameStart.append( spec )

        if specFile is None:
            if len( sameStart ) > 0:
                # Sort the list of 'same start' by the Levenshtein distance
                sameStart.sort( key = lambda x: levenshtein( x, package_name ) )
                specFile = sameStart[0]
            else:
                # No spec file starts with the name of the package,
                # sort the whole spec file list by the Levenshtein distance
                specFileList.sort( key = lambda x: levenshtein( x, package_name ) )
                specFile = specFileList[0]

    if specFile is None:
        msg = "Found no spec file matching package name '%s'" % package_name
        print msg
        return -1

    print "packaging/" + specFile
    return 0

def main():
    if len( sys.argv ) < 3 :
        error_message = "%s take on parameter at least 2 parameters, package_path and package_name."
        print  error_message % ( sys.argv[0] )
        sys.exit( 1 )

    package_path = os.path.abspath( sys.argv[1] ) + "/packaging"
    if not os.path.isdir( package_path ):
        error_message = "%s is not a directory."
        print  error_message % ( package_path )
        sys.exit( 1 )

    package_name = sys.argv[2]

    return findBestSpecFile( package_path, package_name )




if __name__ == '__main__':
    main()
