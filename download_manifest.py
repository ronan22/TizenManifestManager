#!/usr/bin/env python


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
