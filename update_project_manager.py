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

# author: Ronan Le Martret ronan@fridu.net

import sys
import os

import ConfigParser
from xml.etree import ElementTree


class update_project_manager_config( object ):
    '''
    Parse the file "spec2yocto_configure",
    '''
    def __init__( self ):
        self.__config_parser = ConfigParser.ConfigParser()
        self.__config_parser.optionxform = str
        file_conf = "/etc/TizenManifestManager/update_project.conf"

        if os.path.isfile( file_conf ):
            self.__config_file = open( file_conf , 'rw' )
            self.__config_parser.readfp( self.__config_file )
        else:
            self.__config_file = None

    def __get_list( self, section, option, default_value ):
        '''
        generic function to get list value.
        '''
        if ( section in self.__config_parser.sections() ) and \
           ( option in self.__config_parser.options( section ) ):
            tmp_res = str( self.__config_parser.get( section, option ) )
            return tmp_res.split( "," )
        else:
            return default_value

    def print_list_project( self ):
        '''
        function to print list of project.
        '''
        if self.__config_file is not None:
            print " ".join( self.__config_parser.sections() )
        return 0


    def print_arch( self, project ):
        '''
        function to print arch of project.
        '''
        val = self.__get_list( project, "arch", [""] )
        print val[0]

    def get_manifest_list( self, project ):
        '''
        function to print arch of project.
        '''
        val = self.__get_list( project, "manifest", [] )
        return val


    def print_manifest_file( self, project, manifest ):
        '''
        function to print arch of project.
        '''
        val = self.__get_list( project, manifest, [""] )
        print val[0]

    def print_default_git_src( self, project ):
        '''
        function to print arch of project.
        '''
        val = self.__get_list( project, "default_git_src", None )
        if val is not None:
            print val[0]

    def print_alias_file( self, project ):
        '''
        function to print arch of project.
        '''
        val = self.__get_list( project, "alias", None )
        if val is not None:
            print val[0]  
            
    def print_blacklist_file( self, project ):
        '''
        function to print arch of project.
        '''
        val = self.__get_list( project, "blacklist", None )
        if val is not None:
            print val[0]    
            
      

def clean_name( raw_name ):
    if "/" in raw_name:
        return raw_name.split( "/" )[-1]
    else:
        return raw_name

def parse_manifest_xml( src ):
    primaryFile = open( src, "r" )
    primaryXML = primaryFile.read()
    primaryFile.close()
    aElement = ElementTree.fromstring( primaryXML )
    packages_list = []

    for value in aElement:
        for project in value.getiterator():
            if project.tag == "project":
                name = clean_name( project.attrib['name'] )
                packages_list.append( name )

    return  packages_list

def project_is_disable( meta_project_file ):
    primaryFile = open( meta_project_file, "r" )
    primaryXML = primaryFile.read()
    primaryFile.close()

    aElement = ElementTree.fromstring( primaryXML )
    packages_list = []

    for value in aElement:
        for project in value.getiterator():
            if project.tag == "build":
                for build in value.getiterator():
                    if build.tag == "disable":
                        print "yes"
                        return 0

def print_list_package( src, alias, blacklist):
  
    alias_dico=parse_alias_file(alias)
    blacklist_list=parse_blacklist_file(blacklist)
    
    packages_list = parse_manifest_xml( src )
    
    for package in packages_list:
      if package in blacklist_list:
           packages_list.remove(package)
      else:
        if package in alias_dico.keys():
          packages_list.extend(alias_dico[package]) 
    
    print " ".join( packages_list )



def parse_alias_file( src ):
    aliasFile = open( src, "r" )
    aliastxt=aliasFile.read()
    aliasFile.close()
    res={}
    
    for line in aliastxt.split("\n"):
      tmp_res= line.split(" ")
      if len(tmp_res)>=2:
          res[ tmp_res[0] ] = tmp_res[1:]
    
    return res
  
def parse_blacklist_file( src ):
    aliasFile = open( src, "r" )
    aliastxt=aliasFile.read()
    aliasFile.close()
    res=[]
    
    for line in aliastxt.split("\n"):
      res.append(line)
    
    return res
    
  

def main():
    '''
    main fonction of update_project_manager
    '''
    command_list = ["list_project",
                    "get_manifest_list {project}",
                    "get_arch {project}",
                    "get_default_git_src {project}",
                    "list_package {manifest_file}",
                    "project_is_disable {meta_project_file}",
                    "get_manifest_file {project} {manifest}",
                    "get_alias_file {project}",
                    "get_blacklist_file {project}"]
    
    if len( sys.argv ) < 2 :
        print "%s take on parameter \"%s\"." % ( sys.argv[0], ", ".join( command_list ) )
        sys.exit( 1 )

    command = sys.argv[1]
    if len( sys.argv ) >= 3 :
        parameter_1 = sys.argv[2]
    else:
        parameter_1 = None

    if len( sys.argv ) >= 4 :
        parameter_2 = sys.argv[3]
    else:
        parameter_2 = None

    if len( sys.argv ) >= 5 :
        parameter_3 = sys.argv[4]
    else:
        parameter_3 = None

    UPM_CONFIG = update_project_manager_config()
    if command == "list_project":
        UPM_CONFIG.print_list_project()

    if command == "get_manifest_list" :
        if parameter_1 is None:
            print "%s %s take a {project} as parameter." % ( sys.argv[0], "get_manifest_list" )
            sys.exit( 1 )
        res = UPM_CONFIG.get_manifest_list( parameter_1 )

        print " ".join( res )


    elif command == "get_arch":
        if parameter_1 is None:
            print "%s %s take a {project} as parameter." % ( sys.argv[0], "get_arch" )
            sys.exit( 1 )
        UPM_CONFIG.print_arch( parameter_1 )

    elif command == "get_default_git_src":
        if parameter_1 is None:
            print "%s %s take a {project} as parameter." % ( sys.argv[0], "get_default_git_src" )
            sys.exit( 1 )
        UPM_CONFIG.print_default_git_src( parameter_1 )

    elif command == "list_package":
        if parameter_1 is None:
            print "%s %s take a {project} as parameter." % ( sys.argv[0], "get_default_git_src" )
            sys.exit( 1 )
        print_list_package( parameter_1,parameter_2,parameter_3 )

    elif command == "project_is_disable":
        if parameter_1 is None:
            print "%s %s take a {meta_project_file} as parameter." % ( sys.argv[0], "project_is_disable" )
            sys.exit( 1 )
        project_is_disable( parameter_1 )


    elif command == "get_manifest_file":
        if parameter_1 is None or parameter_2 is None:
            print "%s %s take {project} and {manifest} as parameter." % ( sys.argv[0], "get_manifest_file" )
            sys.exit( 1 )
        UPM_CONFIG.print_manifest_file( parameter_1, parameter_2 )

    elif command == "get_alias_file":
        if parameter_1 is None :
            print "%s %s take {project} as parameter." % ( sys.argv[0], "get_alias_file" )
            sys.exit( 1 )
        UPM_CONFIG.print_alias_file( parameter_1 )
        
    elif command == "get_blacklist_file":
        if parameter_1 is None :
            print "%s %s take {project} as parameter." % ( sys.argv[0], "get_blacklist_file" )
            sys.exit( 1 )
        UPM_CONFIG.print_blacklist_file( parameter_1 )
        
    sys.exit( 0 )

if __name__ == '__main__':
    main()
