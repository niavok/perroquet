#! /usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2009-2010 Frédéric Bertolus.
# Copyright (C) 2009-2010 Matthieu Bizien.
#
# This file is part of Perroquet.
#
# Perroquet is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Perroquet is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Perroquet.  If not, see <http://www.gnu.org/licenses/>.
from perroquetlib.config import Config
from perroquetlib.exercise_repository import ExerciseRepository
from xml.dom.minidom import getDOMImplementation, parse
import urllib2

class ExerciseRepositoryManager(object):

    def __init__(self):
        self.config = Config()

    def getExerciseRepositoryList(self):
        repositoryPathList = self.config.Get("repository_path_list")
        repositoryList = []

        for path in repositoryPathList:
            f = open(path, 'r')
            for line in f:
                line = line.rstrip()
                if line[0] == "#":
                    #Comment line
                    continue

                req = urllib2.Request(line)
                try:
                    handle = urllib2.urlopen(req)
                except IOError:
                    print "Fail to connection to repository '"+line+"'"
                else:
                    repositoryList.append(self.parseRepositoryFile(handle))

        return repositoryList


    def parseRepositoryFile(self, handle):
        dom = parse(handle)
        repository = ExerciseRepository()
        repository.setName(self.getText(dom.getElementsByTagName("name")[0].childNodes))
        repository.setDescription(self.getText(dom.getElementsByTagName("description")[0].childNodes))
        repository.setVersion(self.getText(dom.getElementsByTagName("version")[0].childNodes))

        return repository

    def getText(self, nodelist):
        rc = ""
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
        rc = rc.strip()
        return rc

