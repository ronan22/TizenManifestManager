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

from urllib import urlopen
import sys
import os
from xml.etree import ElementTree

class HTTPAccessFailure( Exception ):
    '''Indicate the http access failed'''

def download_url( url ):
    print "Opening url %s " % url
    r = urlopen( url )
    if r.code != 200:
        raise HTTPAccessFailure()
    page = r.read()

    return page

def get_project_id( xml ):
    aElement = ElementTree.fromstring( xml )

    for value in aElement:
        for project in value.getiterator():
            if project.tag == "id":
                return project.text

def main():
    if len( sys.argv ) < 2 :
        error_message = "%s take 2 parameters: file_dst, manifest_url"
        print  error_message % ( sys.argv[0] )
        sys.exit( 1 )

    file_dst = sys.argv[1]
    manifest_url = sys.argv[2]

    if manifest_url.index("@SNAPSHOT_ID@"):
        # extract project base url based on builddata subdir
        print "Resolving @SNAPSHOT_ID@..."
        idx = manifest_url.index("/builddata/");
        if ( idx <= 0 ):
            print "Unable to find builddata dir in manifest URL"
            sys.exit(1)
        project_base_url = manifest_url[:idx]
        xml_str = download_url( project_base_url + "/build.xml")
        project_id = get_project_id( xml_str )
        print "Found snapshot %s" % project_id
        manifest_url = manifest_url.replace("@SNAPSHOT_ID@",project_id)
        print "Resolved URL: %s" % manifest_url
        
    manifest_xml = download_url( manifest_url )

    with open( file_dst, 'w' ) as a_file:
        a_file.write( manifest_xml )

    print "Done."


if __name__ == '__main__':
    main()
