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

import subprocess
import shlex
import fcntl
import os
import time

import select
import errno

import ConfigParser
from xml.etree import ElementTree

import signal

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

TO_EXIT=False
def signal_handler(signal, frame):
    global TO_EXIT
    TO_EXIT=True
    print 'You pressed Ctrl+C!'
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


def colorize( text, color = "green" ):
    """
    Return a colorized copy of `text`.
    See Utils.TERMINAL_COLORS.keys() for available colors.
    """
    return TERMINAL_COLORS.get( color, "" ) + text + TERMINAL_COLORS["default"]


class SubprocessCrt( object ):
    '''
    usefull class to control subprocess
    '''
    def __init__( self ):
        '''
        Initialize subprocess.
        '''
        self.output_res = ""
        self.__idle_time = 0

    def get_last_res( self ):
        '''
        return the last subprocess output.
        '''
        return self.output_res

    def __read_subprocess_output( self, outputs, f_stdout, f_stderr ):
        '''
        read the stdout, stderr of the subprocess
        '''
        timed_out = True
        select_timeout = 60
        for file_d in select.select( [f_stdout, f_stderr], [], [], select_timeout )[0]:
            timed_out = False
            output = file_d.read()
            if f_stdout == file_d:
                self.output_res += output
            else:
                if ( len( output ) > 0 ):
                    print "ERROR ****", output, len( output )

            for line in output.split( "\n" ):
                if not line == b"" or not output.endswith( "\n" ):
                    outputs[file_d]["EOF"] = False

                if line == b"" and not output.endswith( "\n" ):
                    outputs[file_d]["EOF"] = True
                elif line != "" :
                    res_clean = line.decode( "utf8", "replace" ).rstrip()

        if timed_out:
            self.__idle_time += select_timeout
        else:
            self.__idle_time = 0



    def exec_subprocess( self, command ):
        '''
        Execute the "command" in a sub process,
        the "command" must be a valid bash command.
        _args and _kwargs are for compatibility.
        '''

        self.output_res = ""

        # need Python 2.7.3 to do shlex.split(command)
        splitted_command = shlex.split( str( command ) )
        a_process = subprocess.Popen( splitted_command,
                             stdout = subprocess.PIPE,
                             stderr = subprocess.PIPE )
        f_stdout = a_process.stdout
        f_stderr = a_process.stderr

        flags = fcntl.fcntl( f_stdout, fcntl.F_GETFL )
        if not f_stdout.closed:
            fcntl.fcntl( f_stdout, fcntl.F_SETFL, flags | os.O_NONBLOCK )

        flags = fcntl.fcntl( f_stderr, fcntl.F_GETFL )
        if not f_stderr.closed:
            fcntl.fcntl( f_stderr, fcntl.F_SETFL, flags | os.O_NONBLOCK )

        outputs = {f_stdout: {"EOF": False},
                   f_stderr: {"EOF": False}}


        while ( ( not outputs[f_stdout]["EOF"] and
               not outputs[f_stderr]["EOF"] ) or
               ( a_process.poll() == None ) ):
            try:
                self.__read_subprocess_output( outputs, f_stdout, f_stderr )
            except select.error as error:
                # see http://bugs.python.org/issue9867
                if error.args[0] == errno.EINTR:
                    print "Got select.error: %s" % unicode( error )
                    continue
                else:
                    raise Exception()

        # maybe a_process.wait() is better ?
        poll_res = a_process.poll()
        if poll_res != 0:
            return poll_res
        return self.output_res




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

                packages_dico[clean_path( git_path)] = Git_Package(git_name, git_path, revision, remote)

                if '{http://tizen.org}origin_name' in project.attrib and \
                   '{http://tizen.org}origin_revision' in project.attrib and \
                   '{http://tizen.org}origin_remote' in project.attrib:
                  tzname = project.attrib['{http://tizen.org}origin_name']
                  tzrevision = project.attrib['{http://tizen.org}origin_revision']
                  tzremote = project.attrib['{http://tizen.org}origin_remote']
                  packages_dico[clean_path( git_path)].set_origin(tzname,tzrevision,tzremote)

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
         for attr in packages_dico.keys():
             if packages_dico[attr].remote is None:
                 packages_dico[attr].remote=default_remote

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

def generate_manifest(remote_dico, packages_dico, alias_dico={}, blacklist_list=[]):

    file_res = start_manifext_xml

    list_package_tmp = packages_dico.keys()
    list_package_tmp.sort()
    default_remote="tizen-gerrit"
    for remote in remote_dico.keys():
      fetch=remote_dico[remote]
      have_remote=False
      for package_name in list_package_tmp:
          if packages_dico[package_name].remote == remote:
              have_remote=True
              break
      if have_remote:
          file_res+="    <remote fetch=\"%s\" name=\"%s\" />\n" % (fetch,remote)

    if default_remote not in remote_dico.keys():
      default_remote=None
    else:
      file_res+="    <default remote=\"%s\"/>\n" % default_remote


    list_package=[]

    for package_name in list_package_tmp:
        if package_name not in blacklist_list:
            list_package.append(package_name)
            if package_name in alias_dico.keys():
                for p_alias in alias_dico[package_name]:
                    file_res+="    <tz:alias scr=\"%s\" name=\"%s\"/>\n" % (package_name,p_alias)

    list_package.sort()
    for package_name in list_package:
          file_res+=packages_dico[package_name].get_xml_line(default_remote)

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


    remote_dico, packages_dico, alias_dico = parse_manifest_xml( manifest_xml_src )


    for package_name in packages_dico.keys():
        git_package= packages_dico[package_name]

        fetch=remote_dico[git_package.remote]
        if "//" in fetch:
            fetch=fetch.split("//")[1]

        write_package_service( fetch,
                               project_dir,
                               package_name,
                               git_package.name,
                               git_package.revision )
        if package_name in alias_dico.keys():
            for package_alias in alias_dico[package_name]:
                print "package_alias",package_alias
                write_package_service( fetch,
                                       project_dir,
                                       package_alias,
                                       git_package.name,
                                       git_package.revision )


_service_template_1 = """<services>
  <service name="gbs">
  <param name="url">%s:%s</param>
   <param name="revision">%s</param>
   <param name="spec">%s</param>
   </service>
</services>"""

_service_template_2 = """<services>
  <service name="gbs">
  <param name="url">%s:%s</param>
   <param name="revision">%s</param>
   </service>
</services>"""

_service_template_tizen = """<services>
    <service name='gbs'>
        <param name='revision'>%s</param>
        <param name='url'>ssh://%s/%s</param>
    </service>
</services>"""


def create_service( fetch, git_name, revision, package_name ):
    return _service_template_tizen% ( revision, fetch, git_name  )

    #if package_name is None:
    #  return _service_template_2 % ( fetch, git_name, revision )
    #else:
    #  return _service_template_1 % ( fetch, git_name, revision, package_name )



def write_package_service( fetch, project_dir, package_name , git_name, package_revision ):
    service = create_service( fetch, git_name, package_revision, package_name )
    pkgPath = project_dir + "/" + package_name
    pkgPathSrv = pkgPath + "/_service"

    if not os.path.isdir( pkgPath ):
        os.mkdir( pkgPath )

    g = open( pkgPathSrv, 'w' )
    g.write( service )
    g.close()

def cleanTag_line(tag_line):
  if "\t" in tag_line:
    return tag_line.split("\t")[0] , tag_line.split("\t")[1].replace("refs/tags/","")
  else:
    return None,tag_line

def getLastTag(tag_list):
    dicoresult={}
    for tag_line in tag_list.split("\n"):
      if "accepted/" in tag_line or "submit/" in tag_line:
        sha, clean_tag= cleanTag_line(tag_line)
        date_tag=getTagDate(clean_tag)
        if date_tag is not None and date_tag.endswith("^{}"):
            dicoresult[ date_tag[:-3] ]=[ sha, clean_tag[:-3] ]
    return dicoresult

class Git_Package:
  def __init__(self,git_name, git_path, revision, remote):
    self.path=git_path
    self.name=git_name
    self.revision=revision
    self.remote=remote

    self.tz_origin_name=None
    self.tz_origin_revision=None
    self.tz_origin_remote=None

  def set_origin(self,name,revision,remote):
    self.tz_origin_name=name
    self.tz_origin_revision=revision
    self.tz_origin_remote=remote

  def __have_origin(self):
    return self.tz_origin_name is not None and \
           self.tz_origin_revision is not None and \
           self.tz_origin_remote is not None

  def get_update_package(self):
    if self.__have_origin():
       return Git_Package(self.tz_origin_name, self.path, self.tz_origin_revision, self.tz_origin_remote)
    else:
       return self

  def get_xml_line(self,default_remote=None):
     if default_remote is None or default_remote != self.remote:
       remote_tag = "remote=\"%s\"" % self.remote
     else:
       remote_tag = ""

     if self.__have_origin():
       remote_origin = "tz:origin_name=\"%s\"  tz:origin_revision=\"%s\" tz:origin_remote=\"%s\"" %(self.tz_origin_name, self.tz_origin_revision, self.tz_origin_remote)
     else:
       remote_origin = ""

     xml_line = "    <project name=\"%s\" path=\"%s\" revision=\"%s\" %s %s />\n" % (self.name, clean_path( self.path ), self.revision, remote_tag, remote_origin)

     return xml_line

class CommitRemote:
  def __init__(self):
    self.tag=None
    self.alias_tag=None
    self.commit=None
    self.alias_commit=None
    self.date_tag=None

    self.alias_sha=None
    self.sha=None

  def setCommitValue(self,date_tag,sha) :
    if date_tag.endswith("^{}"):
      self.alias_tag=date_tag
      self.tag=self.alias_tag[:-3]
      self.alias_sha=sha
    else:
      self.tag=date_tag
      self.sha=sha
    self.date_tag=getTagDate(self.tag)

  def getSha(self):
    if self.alias_sha is not None:
      return self.alias_sha
    else:
      return self.sha




class CommitCollection:
  def __init__(self,  gitTag):
    self.commit_dico = {}
    self.__origin_tag = gitTag
    self.__origin_date_tag = getTagDate(gitTag)
    self.__origin_sha = None

  def __have_a_valid_date(self,test_date=None):
    #What is a valid date?
    #TODO ???
    if test_date is None:
      test_date=self.__origin_date_tag
    if test_date is None:
      return False
    if len("20121215.161330") == len(test_date) and \
       test_date.count(".") == 1:
         return True

    return False

  def initFromString(self, tag_list):
    for tag_line in tag_list.split("\n"):
        sha, clean_tag= cleanTag_line(tag_line)

        commit_key=clean_tag
        if commit_key.endswith("^{}"):
            commit_key=commit_key[:-3]

        if commit_key not in self.commit_dico.keys():
            self.commit_dico[commit_key]=CommitRemote()

        self.commit_dico[commit_key].setCommitValue(clean_tag,sha)

  def __check_origin_sha(self):
    for commit_key in self.commit_dico.keys():
      if commit_key == self.__origin_tag:
          self.__origin_sha = self.commit_dico[commit_key].getSha()
          return True
      elif self.commit_dico[commit_key].getSha() == self.__origin_tag:
          return True

    return False

  def get_candidates(self):
    res=[]
    for commit_key in self.commit_dico.keys():
         if commit_key.startswith("accepted/")  and "/tizen/" in commit_key:
             if self.commit_dico[commit_key].getSha() != self.__origin_sha:
                  res.append(commit_key)
    return res

  def have_newer_tag(self):
    if self.__origin_date_tag is not None and not self.__have_a_valid_date():
      return False

    if not self.__check_origin_sha():
      print "No sha for commit origine"
      return False

    candidates_list=self.get_candidates()

    self.newer_commit=None
    self.newer_commit_date=None
    for candidate in candidates_list:
      if self.__have_a_valid_date(self.commit_dico[candidate].date_tag) and \
         self.is_newer(candidate):
           self.newer_commit = candidate
           self.newer_commit_date=self.commit_dico[candidate].date_tag

    return self.newer_commit is not None

  def getLastTag(self):
    return self.commit_dico[self.newer_commit].tag

  def is_newer(self, candidate):
    candidate_date=self.commit_dico[candidate].date_tag
    if candidate_date is None:
      return False
    elif self.__origin_date_tag is None and self.newer_commit is None:
      return True
    elif self.newer_commit is None:
        return candidate_date > self.__origin_date_tag
    else:
        return (candidate_date > self.__origin_date_tag ) and ( candidate_date > self.newer_commit_date)


def getTagDate(clean_tag):
  if not "/tizen/" in clean_tag:
    return None
  else:
    return clean_tag.split("/")[-1]



def checkRemote(remote_dico,packages_dico):
    global TO_EXIT
    subProcessor=SubprocessCrt()

    list_package=packages_dico.keys()
    list_package.sort()
    i=1

    for package_name in list_package:
      if TO_EXIT:
        break
      print "package %s    %s/%s" % ( package_name, i, len(list_package) )

      git_package = packages_dico[package_name].get_update_package()
      packages_dico[package_name]=git_package

      remote=remote_dico[git_package.remote]
      if "//" in remote:
            remote=remote.split("//")[1]

      cmd="git ls-remote --tags %s:%s" % (remote, git_package.name)
      try:
        tag_list=subProcessor.exec_subprocess(cmd)
        res=0
      except:
          print cmd," failed"
      if type(tag_list) == type(-1):
          i=i+1
          continue

      commitCol=CommitCollection( packages_dico[package_name].revision)
      commitCol.initFromString(tag_list)

      if commitCol.have_newer_tag():
          lastTag=commitCol.getLastTag()
          print "Tag ",lastTag," is newer then ",packages_dico[package_name].revision
          packages_dico[package_name].revision = lastTag
      i=i+1

    return packages_dico

def update_manifest(manifest_src, manifest_dst ):
    remote_dico, packages_dico, alias_dico = parse_manifest_xml( manifest_src )
    packages_dico=checkRemote(remote_dico,packages_dico)

    res=generate_manifest(remote_dico, packages_dico, alias_dico)
    file_res= open(manifest_dst,"w")
    file_res.write(res)
    file_res.close()

    return 0

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

    def do_update_manifest( self, subcmd, opts, manifest_src, manifest_dst ):
        """${cmd_name}: return the proto directory.

        ${cmd_usage}--
        ${cmd_option_list}
        """
        return update_manifest(manifest_src, manifest_dst )

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
