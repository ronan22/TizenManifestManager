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

from xml.etree import ElementTree

start_manifext_xml='''<?xml version="1.0" encoding="UTF-8"?>
<manifest>
  <remote fetch="ssh://review.tizen.org" name="tizen-gerrit" review="https://review.tizen.org/gerrit"/>
  <default remote="tizen-gerrit"/>\n'''
  
end_manifext_xml='''</manifest>'''


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

def tagIsNewer(tag1,tag2):
  if tag1 == tag2:
    return False
  
  listTag=[tag1,tag2]
  listTag.sort()
  
  return tag2 == listTag[1]
  

def checkRemote(remote,packages_dico):
    subProcessor=SubprocessCrt()
    
    file_res=start_manifext_xml
  
    list_package=packages_dico.keys()
    list_package.sort()
    i=1
    
    for package_name in list_package:
      print "package %s    %s/%s" % ( package_name, i, len(list_package) )
      gitPath=packages_dico[package_name][0]
      gitTag=packages_dico[package_name][1]

      cmd="git ls-remote --tags %s:%s" % (remote, gitPath)
      try:
        tag_list=subProcessor.exec_subprocess(cmd)
        dicoresult=getLastTag(tag_list)
        resTag=dicoresult.keys()
        resTag.sort()
        lastSha,lastTag = dicoresult[ resTag[-1]]
        
        currentSha=None
        for sTag in resTag:
	  sha,tag= dicoresult[sTag]
	  if tag == gitTag:
	    currentSha=sha
	    
        
        if "submit" in gitTag: 
          if tagIsNewer(gitTag,lastTag) and currentSha!=lastSha:
	      print "Tag ",lastTag," is newer then ",gitTag
              file_res+= "  <project name=\"%s\" path=\"%s\" revision=\"%s\"/>\n" % (gitPath,gitPath,lastTag)
              
      except:
          print cmd," failed"
      i=i+1
      
    file_res+=end_manifext_xml
    return file_res


def cleanTag_line(tag_line):
  if "\t" in tag_line:
    return tag_line.split("\t")[0] , tag_line.split("\t")[1].replace("refs/tags/","")
  else:
    return None,tag_line

def getTagDate(clean_tag):
  return clean_tag.split("/")[-1]
  
def getLastTag(tag_list):
    dicoresult={}
    for tag_line in tag_list.split("\n"):
      if "submit" in tag_line:
	sha, clean_tag= cleanTag_line(tag_line)
	date_tag=getTagDate(clean_tag)
	if date_tag.endswith("^{}"):
	  dicoresult[ date_tag[:-3] ]=[ sha, clean_tag[:-3] ]
      
    return dicoresult

      

def main():
    manifest_xml_src = sys.argv[1]
    manifest_xml_dst = sys.argv[2]
    
    remote,packages_dico = parse_manifest_xml( manifest_xml_src )
    
    res=checkRemote(remote,packages_dico)
    file_res= open(manifest_xml_dst,"w")
    file_res.write(res)
    file_res.close()


if __name__ == '__main__':
    main()













