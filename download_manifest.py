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
from xml.etree import ElementTree

class HTTPAccessFailure( Exception ):
    '''Indicate the http access failed'''

def download_url( url ):
    r = urlopen( url )
    if r.code != 200:
        raise HTTPAccessFailure()
    page = r.read()

    return page

def download_manifest_url( url ):
    r = urlopen( url )
    if r.code != 200:
        raise HTTPAccessFailure()
    page = r.read()

    return page

def download_build_xml( url ):
    return download_url( url + "/builddata/build.xml" )


def get_project_id( xml ):
    aElement = ElementTree.fromstring( xml )

    for value in aElement:
        for project in value.getiterator():
            if project.tag == "id":
                return project.text

def get_project_arch( xml ):
    aElement = ElementTree.fromstring( xml )
    arch_list = []
    for value in aElement:
        for project in value.getiterator():
            if project.tag == "archs":
                for arch in project.getiterator():
                    if arch.tag == "arch":
                        arch_list.append( arch.text )

    return arch_list



def main():
    if len( sys.argv ) < 2 :
        error_message = "%s take 2 parameters at least one parameter, project_base_url and arch."
        print  error_message % ( sys.argv[0] )
        sys.exit( 1 )

    project_base_url = sys.argv[1]

    if len( sys.argv ) >= 3:
        arch = sys.argv[2]
    else:
        arch = None

    xml_str = download_build_xml( project_base_url )
    project_id = get_project_id( xml_str )

    list_arch = get_project_arch( xml_str )

    if ( arch is None ) and ( len( list_arch ) > 0 ):
        arch = list_arch[0]

    if arch is None:
        print "no arch define."
        sys.exit( 1 )

    manifest_name = "%s_%s.xml" % ( project_id, arch )
    manifest_url = project_base_url + "/builddata/manifest/" + manifest_name
    manifest_xml = download_manifest_url( manifest_url )

    with open( manifest_name, 'w' ) as a_file:
        a_file.write( manifest_xml )

    print manifest_name



if __name__ == '__main__':
    main()
