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

from xml.dom.minidom import getDOMImplementation, parse
import os

from perroquetlib.config import config
from perroquetlib.repository.exercise_repository_group import ExerciseRepositoryGroup
from perroquetlib.repository.exercise_repository_exercise import ExerciseRepositoryExercise

class ExerciseRepository:

    def __init__(self):
        self.name =""
        self.description = ""
        self.version = ""
        self.url = ""
        self.exercisesGroupList = []
        self.config = config




    def setName(self, name):
        self.name = name

    def setDescription(self, description):
        self.description = description

    def setVersion(self, version):
        self.version = version

    def setName(self, name):
        self.name = name

    def getName(self):
        return self.name

    def setType(self, type):
        self.type = type

    def getType(self):
        return self.type

    def setId(self, id):
        self.id = id

    def getId(self):
        return self.id

    def setUrl(self, url):
        self.url = url

    def getUrl(self):
        return self.url

    def getDescription(self):
        return self.description

    def getVersion(self):
        return self.version

    def addGroup(self, group):
        self.exercisesGroupList.append(group)
        group.setParent(self)

    def getGroups(self):
        return self.exercisesGroupList

    def getOrphanGroups(self):
        groupPathList = os.listDir(self.getLocalPath())

        groupUsedPath = []
        orphanGroupList = []
        for group in self.getGroups():
            groupUsedPath.append(group.getLocalPath())

        for groupPath in groupPathList:
            if groupPath not in groupUsedPath:
                group = ExerciseRepositoryManager.createGroupFromPath(repoPath)
                orphanGroupList.append(group)

        return orphanGroupList

    def getLocalPath(self):
        return os.path.join(self.config.get("local_repo_root_dir"), self.id)

    def generateDescription(self):
        self._generateDescription()
        for group in self.getGroups():
            group.generateDescription()

    def _generateDescription(self):

        if not os.path.isdir(self.getLocalPath()):
            try:
                os.makedirs(self.getLocalPath())
            except OSError, (ErrorNumber, ErrorMessage): # Python <=2.5
                if ErrorNumber == errno.EEXIST:
                    pass
                else: raise

        impl = getDOMImplementation()

        newdoc = impl.createDocument(None, "perroquet_repository", None)
        root_element = newdoc.documentElement

        # Name
        xml_name = newdoc.createElement("name")
        xml_name.appendChild(newdoc.createTextNode(self.getName()))
        root_element.appendChild(xml_name)

        # Id
        xml_id = newdoc.createElement("id")
        xml_id.appendChild(newdoc.createTextNode(self.getId()))
        root_element.appendChild(xml_id)

        # Description
        xml_description = newdoc.createElement("description")
        xml_description.appendChild(newdoc.createTextNode(self.getDescription()))
        root_element.appendChild(xml_description)

        # Version
        xml_version = newdoc.createElement("version")
        xml_version.appendChild(newdoc.createTextNode(self.getVersion()))
        root_element.appendChild(xml_version)

        # Url
        xml_url = newdoc.createElement("url")
        xml_url.appendChild(newdoc.createTextNode(self.getUrl()))
        root_element.appendChild(xml_url)


        xml_string = newdoc.toprettyxml()
        xml_string = xml_string.encode('utf8')
        repoDescriptionPath = os.path.join(self.getLocalPath(),"repository.xml")
        f = open(repoDescriptionPath, 'w')
        f.write(xml_string)
        f.close()

    def initFromPath(self,path):

        repoDescriptionPath = os.path.join(path,"repository.xml")
        if os.path.isfile(repoDescriptionPath):
            f = open(repoDescriptionPath, 'r')
            dom = parse(f)
            self.parseDescription(dom)
        else:
            self.setId(os.path.basename(path))
            self.setName(os.path.basename(path))

        groupPathList = os.listdir(self.getLocalPath())

        for groupPath in groupPathList:
            path = os.path.join(self.getLocalPath(), groupPath)
            if os.path.isdir(path):
                group = ExerciseRepositoryGroup()
                group.initFromPath(path)
                self.addGroup(group)

    def parseDescription(self,dom):
        self.setName(self._getText(dom.getElementsByTagName("name")[0].childNodes))
        self.setDescription(self._getText(dom.getElementsByTagName("description")[0].childNodes))
        self.setId(self._getText(dom.getElementsByTagName("id")[0].childNodes))
        self.setVersion(self._getText(dom.getElementsByTagName("version")[0].childNodes))
        if len(dom.getElementsByTagName("url")) > 0:
            self.setUrl(self._getText(dom.getElementsByTagName("url")[0].childNodes))

    def parseDistantRepositoryFile(self, handle):
        dom = parse(handle)

        self.parseDescription(dom)
        self.setType("distant")

        xml_groups = dom.getElementsByTagName("exercises_groups")[0]

        for xml_group in xml_groups.getElementsByTagName("exercises_group"):
            group = ExerciseRepositoryGroup()
            group.parseDescription(xml_group)
            self.addGroup(group)

            xml_exercises = xml_group.getElementsByTagName("exercises")[0]
            for xml_exercise in xml_exercises.getElementsByTagName("exercise"):
                exercise = ExerciseRepositoryExercise()
                exercise.parseDescription(xml_exercise)
                group.addExercise(exercise)


    def _getText(self, nodelist):
        rc = ""
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
        rc = rc.strip()
        return rc
