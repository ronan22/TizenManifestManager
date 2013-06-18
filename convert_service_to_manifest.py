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
from xml.etree import ElementTree

for tmp_res in os.listdir( "." ):
    if tmp_res != ".osc":
        with open( tmp_res + "/_service" ) as file_service:
            _service = file_service.read()

        aElement = ElementTree.fromstring( _service )
        for project in aElement.getiterator():
            if project.tag == "param":
                if project.attrib["name"] == 'url':
                    url = project.text
                elif project.attrib["name"] == 'filename':
                    filename = project.text
                elif project.attrib["name"] == 'revision':
                    revision = project.text
        print "  <project name=\"" + filename + "\" path=\"" + url + "\" revision=\"" + revision + "\"/>"
