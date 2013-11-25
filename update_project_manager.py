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

try:
    import cmdln
except:
    print 'Error spec2yocto require "python-cmdln" please install it.'
    sys.exit( 1 )
    
TERMINAL_COLORS = {"black": "\033[30;1m",
                   "red": "\033[31;1m",
                   "green": "\033[32;1m",
                   "yellow": "\033[33;1m",
                   "blue": "\033[34;1m",
                   "magenta": "\033[35;1m",
                   "cyan": "\033[36;1m",
                   "white": "\033[37;1m",
                   "default": "\033[0m"}



    
def colorize( text, color = "green" ):
    """
    Return a colorized copy of `text`.
    See Utils.TERMINAL_COLORS.keys() for available colors.
    """
    return TERMINAL_COLORS.get( color, "" ) + text + TERMINAL_COLORS["default"]
  

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
            
      

def clean_path( raw_name ):
    return os.path.basename(raw_name)
  
def parse_manifest_xml( src, remote_dico={}, packages_dico={}, alias_dico={} ):
    primaryFile = open( src, "r" )
    primaryXML = primaryFile.read()
    primaryFile.close()
    
    aElement = ElementTree.fromstring( primaryXML )
    default_remote=None
    for value in aElement:
        for project in value.getiterator():
            if project.tag == "project":
                git_name = project.attrib['name']
                if 'path' in project.attrib:
                    git_path =  project.attrib['path']
                else:
                    git_path =  git_name
                    
                revision = clean_revision( project.attrib['revision'] )
                
                if 'remote' in  project.attrib:
                    remote=project.attrib['remote']
                else:
                    remote = default_remote
                    
                    
                packages_dico[clean_path( git_path)] = [git_name, git_path, revision, remote]
                
            elif project.tag == "default":
                  default_remote = project.attrib['remote']
            elif project.tag == "remote":
                fetch = project.attrib['fetch']
                name = project.attrib['name']
                remote_dico[name]=fetch
            elif project.tag == "{http://tizen.org}alias":
                scr = project.attrib['scr']
                name = project.attrib['name']
                if scr not in alias_dico.keys():
                    alias_dico[scr]=[]
                if name not in alias_dico[scr]:
                    alias_dico[scr].append(name)
            else:
                print "ERROR",project.tag
         
    if default_remote is not None:
         for pkg in packages_dico.keys():
             [git_name, git_path, revision, remote] = packages_dico[pkg]
             if remote is None:
                 packages_dico[pkg]=[git_name, git_path, revision, default_remote]
         
    return  remote_dico,  packages_dico, alias_dico

def get_package_manifest_xml( src ):
    remote_dico,  packages_dico, alias_dico = parse_manifest_xml( src )
    
    packages_list=packages_dico.keys()
    for package_name in packages_list: 
        if package_name in alias_dico.keys(): 
            for p_alias in alias_dico[package_name]: 
                packages_list.append(p_alias)
    
    packages_list.sort()
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

def print_list_package( src):
    packages_list = get_package_manifest_xml( src )
    print "\n".join( packages_list )


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
 
def clean_revision( raw_name ):
    if "-" in raw_name:
        return raw_name.split( "-" )[0]
    else:
        return raw_name
 
start_manifext_xml='''<?xml version="1.0" encoding="UTF-8"?>
<manifest  xmlns:tz="http://tizen.org">\n'''


  
end_manifext_xml='''</manifest>'''
 
def generate_manifest(remote_dico, packages_dico, alias_dico, blacklist_list):
    
    file_res = start_manifext_xml
    
    default_remote="tizen-gerrit"
    for remote in remote_dico.keys():
      fetch=remote_dico[remote]
      file_res+="    <remote fetch=\"%s\" name=\"%s\" />\n" % (fetch,remote)
    
    if default_remote not in remote_dico.keys():
      default_remote=None
    else:
      file_res+="    <default remote=\"%s\"/>\n" % default_remote
    
    list_package_tmp = packages_dico.keys()
    list_package_tmp.sort()
    list_package=[]
    
    for package_name in list_package_tmp: 
        if package_name not in blacklist_list:
            list_package.append(package_name)
            if package_name in alias_dico.keys():
                for p_alias in alias_dico[package_name]:
                    file_res+="    <tz:alias scr=\"%s\" name=\"%s\"/>\n" % (package_name,p_alias)
            
    list_package.sort()
    for package_name in list_package:
          [git_name, git_path, gitTag, remote]=packages_dico[package_name]
          if default_remote == remote:
              file_res+= "    <project name=\"%s\" path=\"%s\" revision=\"%s\" />\n" % (git_name, clean_path( git_path ), gitTag)
          else:
              file_res+= "    <project name=\"%s\" path=\"%s\" revision=\"%s\" remote=\"%s\" />\n" % (git_name, clean_path( git_path ), gitTag, remote)
         
    file_res+=end_manifext_xml
    return file_res

def merge_manifest(blacklist_file,alias_file,manifest_xml_srcs,manifest_xml_dst):
  
    if alias_file is not None or alias_file == "":
        alias_dico= parse_alias_file( alias_file )
    else:
        alias_dico={}
        
    if blacklist_file is not None or blacklist_file == "":
        blacklist_list=parse_blacklist_file(blacklist_file)
    else:
        blacklist_list=[]
    
    packages_dico={}
    remote_dico={}
    for manifest_xml_src in manifest_xml_srcs:
        remote_dico, packages_dico, alias_dico = parse_manifest_xml(manifest_xml_src, remote_dico, packages_dico, alias_dico )
    
    res=generate_manifest(remote_dico, packages_dico, alias_dico, blacklist_list)
    file_res= open(manifest_xml_dst,"w")
    file_res.write(res)
    file_res.close()
    
    return 0

def create_package_from_manifest(project_dir, manifest_xml_src):
  
    project_dir = os.path.abspath( project_dir )
    manifest_xml_src = os.path.abspath( manifest_xml_src )
    
    
    if not os.path.isdir( project_dir ):
        error_message = "%s is not a directory."
        print  error_message % ( project_dir )
        sys.exit( 1 )

    if not os.path.isdir( os.path.join( project_dir, ".osc" ) ):
        error_message = "%s is not a osc directory."
        print  error_message % ( project_dir )
        sys.exit( 1 )
    
    
    remote_dico, packages_dico, alias_dico = parse_manifest_xml( manifest_xml_src )
    
    
    for package_name in packages_dico.keys():

        [git_name, git_path, gitTag, remote] = packages_dico[package_name]

        fetch=remote_dico[remote]
        if "//" in fetch:
            fetch=fetch.split("//")[1]
        
        write_package_service( fetch,
                               project_dir,
                               package_name,
                               git_name,
                               gitTag )


_service = """<services>
  <service name="gbp_git">
  <param name="url">%s:%s</param>
   <param name="revision">%s</param>
   <param name="package_name">%s</param>
   </service>
</services>"""

def create_service( fetch, git_name, revision, package_name ):
    return _service % ( fetch, git_name, revision, package_name )
  
def write_package_service( fetch, project_dir, package_name , git_name, package_revision ):
    service = create_service( fetch, git_name, package_revision, package_name )
    pkgPath = project_dir + "/" + package_name
    pkgPathSrv = pkgPath + "/_service"

    if not os.path.isdir( pkgPath ):
        os.mkdir( pkgPath )

    g = open( pkgPathSrv, 'w' )
    g.write( service )
    g.close()


class update_project_manager_commandline( cmdln.Cmdln ):
    name = "update_project_manager"
    version = "0.1"
    
    UPM_CONFIG = update_project_manager_config()
    
    def do_list_project( self, subcmd, opts):
        """${cmd_name}: return the project list.

        ${cmd_usage}--
        ${cmd_option_list}
        """
        self.UPM_CONFIG.print_list_project()


    def do_get_manifest_list( self, subcmd, opts, project   ):
        """${cmd_name}: return the proto directory.

        ${cmd_usage}--
        ${cmd_option_list} 
        """
        res = self.UPM_CONFIG.get_manifest_list( project )
        print " ".join( res )
        
    def do_get_arch( self, subcmd, opts, project ):
        """${cmd_name}: return the proto directory.

        ${cmd_usage}--
        ${cmd_option_list}
        """
        self.UPM_CONFIG.print_arch( project )

    def do_list_package( self, subcmd, opts, manifest_path ):
        """${cmd_name}: return the proto directory.

        ${cmd_usage}--
        ${cmd_option_list}
        """
        print_list_package( manifest_path )

    def do_project_is_disable( self, subcmd, opts,meta_project_file ):
        """${cmd_name}: return the proto directory.

        ${cmd_usage}--
        ${cmd_option_list}
        """
        project_is_disable( meta_project_file )

    def do_get_manifest_file( self, subcmd, opts, project,manifest ):
        """${cmd_name}: return the proto directory.

        ${cmd_usage}--
        ${cmd_option_list}
        """
        self.UPM_CONFIG.print_manifest_file( project, manifest )

    def do_get_alias_file( self, subcmd, opts, project ):
        """${cmd_name}: return the proto directory.
        
        ${cmd_usage}--
        ${cmd_option_list}
        """
        self.UPM_CONFIG.print_alias_file( project )
        
    def do_get_blacklist_file( self, subcmd, opts, project ):
        """${cmd_name}: return the proto directory.

        ${cmd_usage}--
        ${cmd_option_list}
        """
        self.UPM_CONFIG.print_blacklist_file( project )
        
    @cmdln.option( "--blacklist",
                  action = "store",
                  default = None,
                  help = "blacklist file." )
    @cmdln.option( "--alias",
                  action = "store",
                  default = None,
                  help = "alias file." )
    @cmdln.option( "--manifest_dst",
                  action = "store",
                  default = None,
                  help = "manifest xml file dst." )
    def do_merge_project_manifest( self, subcmd, opts, *manifest ):
        """${cmd_name}: return the proto directory.

        ${cmd_usage}--
        ${cmd_option_list}
        """
        res=merge_manifest(opts.blacklist, opts.alias, list(manifest), opts.manifest_dst)
        return res

    @cmdln.option( "--project_dir",
                  action = "store",
                  default = os.curdir,
                  help = "manifest xml file dst." )
    def do_create_package_from_manifest( self, subcmd, opts, manifest ):
        """${cmd_name}: return the proto directory.

        ${cmd_usage}--
        ${cmd_option_list}
        """
        res=create_package_from_manifest(opts.project_dir, manifest)
        return res


def main():
    commandline = update_project_manager_commandline()
    
    try:
        res = commandline.main()
    except ValueError as ve:
        print
        print >> sys.stderr, colorize( str( ve ), "red" )
        res = 1
    except EnvironmentError as ioe:
        print
        print >> sys.stderr, colorize( str( ioe ), "red" )
        res = 1

    sys.exit( res )


if __name__ == '__main__':
    main()
