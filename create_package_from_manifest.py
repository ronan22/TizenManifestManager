#!/usr/bin/env python

import os
import sys
from xml.etree import ElementTree

_service = """<services>
  <service name=\"tar_scm\">
  <param name=\"url\">%s:%s</param>
   <param name=\"revision\">%s</param>
   <param name=\"scm\">git</param>
    <param name=\"usegbp\">yes</param>
  </service>
</services>"""

def clean_name( raw_name ):
    if "/" in raw_name:
        return raw_name.split( "/" )[-1]
    else:
        return raw_name

def clean_revision( raw_name ):
    if "-" in raw_name:
        return raw_name.split( "-" )[0]
    else:
        return raw_name


def parse_manifest_xml( src ):
    primaryFile = open( src, "r" )
    primaryXML = primaryFile.read()
    primaryFile.close()

    aElement = ElementTree.fromstring( primaryXML )
    remote = ""
    packages_dico = {}
    for value in aElement:
        for project in value.getiterator():
            if project.tag == "project":
                path = project.attrib['path']
                name = clean_name( project.attrib['name'] )
                revision = clean_revision( project.attrib['revision'] )
                packages_dico[name] = [path, revision]
            elif project.tag == "default":
                  remote = project.attrib['remote']
            elif project.tag == "remote":
                fetch = project.attrib['fetch']
                name = project.attrib['name']
                review = project.attrib['review']
            else:
                print "ERROR"

    return remote, packages_dico

def create_service( remote, path, revision ):
    return _service % ( remote, path, revision )

def write_package_service( remote, project_dir, package_name , package_path, package_revision ):
    service = create_service( remote, package_path, package_revision )
    pkgPath = project_dir + "/" + package_name
    pkgPathSrv = pkgPath + "/_service"

    if not os.path.isdir( pkgPath ):
        os.mkdir( pkgPath )

    g = open( pkgPathSrv, 'w' )
    g.write( service )
    g.close()



def main():
    if len( sys.argv ) < 2 :
        error_message = "%s take on parameter at least one parameter, the manifest.xml path."
        print  error_message % ( sys.argv[0] )
        sys.exit( 1 )

    manifest_xml_src = sys.argv[1]

    if len( sys.argv ) >= 3 :
        remote_default = sys.argv[2]
    else:
        remote_default = None

    if len( sys.argv ) >= 4 :
        project_dir = os.path.abspath( sys.argv[3] )
    else:
        project_dir = os.path.abspath( os.curdir )

    if not os.path.isdir( project_dir ):
        error_message = "%s is not a directory."
        print  error_message % ( project_dir )
        sys.exit( 1 )

    if not os.path.isdir( os.path.join( project_dir, ".osc" ) ):
        error_message = "%s is not a osc directory."
        print  error_message % ( project_dir )
        sys.exit( 1 )



    remote, packages_dico = parse_manifest_xml( manifest_xml_src )

    if remote_default is not None:
        remote = remote_default

    for package_name in packages_dico.keys():
        write_package_service( remote,
                              project_dir,
                              package_name,
                              packages_dico[package_name][0],
                              packages_dico[package_name][1] )


if __name__ == '__main__':
    main()
