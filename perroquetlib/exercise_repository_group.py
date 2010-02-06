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

import os
from xml.dom.minidom import getDOMImplementation, parse

class ExerciseRepositoryGroup:
    def __init__(self):
        self.name =""
        self.description = ""
        self.exercisesList = []

    def setName(self, name):
        self.name = name

    def setDescription(self, description):
        self.description = description

    def getName(self):
        return self.name

    def getDescription(self):
        return self.description

    def setId(self, id):
        self.id = id

    def getId(self):
        return self.id

    def addExercise(self, exercise):
        self.exercisesList.append(exercise)
        exercise.setParent(self)

    def getExercises(self):
        return self.exercisesList

    def setParent(self,parent):
        self.parent = parent

    def getLocalPath(self):
        return os.path.join(self.parent.getLocalPath(), self.id)

    def parseDescription(self,xml_group):
        self.setName(self._getText(xml_group.getElementsByTagName("name")[0].childNodes))
        self.setId(self._getText(xml_group.getElementsByTagName("id")[0].childNodes))
        self.setDescription(self._getText(xml_group.getElementsByTagName("description")[0].childNodes))

    def generateDescription(self):
        self._generateDescription()
        for exo in self.getExercises():
            exo.generateDescription()

    def _generateDescription(self):

        if not os.path.isdir(self.getLocalPath()):
            try:
                os.makedirs(self.getLocalPath())
            except OSError as exc: # Python >2.5
                if exc.errno == errno.EEXIST:
                    pass
                else: raise

        impl = getDOMImplementation()

        newdoc = impl.createDocument(None, "perroquet_group", None)
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

        xml_string = newdoc.toprettyxml()
        xml_string = xml_string.encode('utf8')

        repoDescriptionPath = os.path.join(self.getLocalPath(),"group.xml")
        f = open(repoDescriptionPath, 'w')
        f.write(xml_string)
        f.close()

    def initFromPath(self, groupPath):
        groupDescriptionPath = os.path.join(groupPath,"group.xml")

        if os.path.isfile(groupDescriptionPath):
            f = open(groupDescriptionPath, 'r')
            dom = parse(f)
            self.parseDescription(dom)
        else:
            self.setId(os.path.basename(groupPath))
            self.setName(os.path.basename(groupPath))

        exercisePathList = os.listdir(groupPath)
        for exercisePath in exercisePathList:
            path = os.path.join(self.getLocalPath(), groupPath)
            if os.path.isdir(path):
                exo = ExerciseRepositoryExercise()
                exo.iniFromPath(path)
                group.addExercise(exo)


    def _getText(self, nodelist):
        rc = ""
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
        rc = rc.strip()
        return rc
