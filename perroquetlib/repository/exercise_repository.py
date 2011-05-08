#! /usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2009-2011 Frédéric Bertolus.
# Copyright (C) 2009-2011 Matthieu Bizien.
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

import errno
import os
from xml.dom.minidom import getDOMImplementation, parse

from perroquetlib.config import config
from perroquetlib.repository.exercise_repository_exercise import ExerciseRepositoryExercise
from perroquetlib.repository.exercise_repository_group import ExerciseRepositoryGroup

#FIXME import needed but bug
#from perroquetlib.repository.exercise_repository_manager import ExerciseRepositoryManager

class ExerciseRepository:

    def __init__(self):
        self.name = ""
        self.description = ""
        self.version = ""
        self.url = ""
        self.exercisesGroupList = []
        self.config = config
        self.system = False



    def set_system(self, system):
        """Define if the repo is a system repository or only a local one

        A system repository store common data in a system directory and only the
        progress in the local directory
        """
        self.system = system;

    def set_name(self, name):
        self.name = name

    def set_description(self, description):
        self.description = description

    def set_version(self, version):
        self.version = version

    def get_name(self):
        return self.name

    def set_type(self, type):
        self.type = type

    def get_type(self):
        return self.type

    def set_id(self, id):
        self.id = id

    def get_id(self):
        return self.id

    def set_url(self, url):
        self.url = url

    def get_url(self):
        return self.url

    def get_description(self):
        return self.description

    def get_version(self):
        return self.version

    def add_group(self, group):
        self.exercisesGroupList.append(group)
        group.set_parent(self)

    def get_groups(self):
        return self.exercisesGroupList

    def get_orphan_groups(self):
        #FIXME ugly
        from perroquetlib.repository.exercise_repository_manager import ExerciseRepositoryManager
        groupPathList = os.listDir(self.get_local_path())

        groupUsedPath = []
        orphanGroupList = []
        for group in self.get_groups():
            groupUsedPath.append(group.get_local_path())

        for groupPath in groupPathList:
            if groupPath not in groupUsedPath: #FIXME used or not ???
                group = ExerciseRepositoryManager.createGroupFromPath(repoPath)
                    #FIXME repoPath unknow var
                orphanGroupList.append(group)

        return orphanGroupList

    def get_local_path(self):
        if self.system:
            return os.path.join(self.config.get("system_repo_root_dir"), self.id)
        else:
            return os.path.join(self.config.get("local_repo_root_dir"), self.id)

    def get_personal_local_path(self):
        return os.path.join(self.config.get("local_repo_root_dir"), self.id)


    def generate_description(self):
        self._generate_description()
        for group in self.get_groups():
            group.generate_description()

    def _generate_description(self):

        if not os.path.isdir(self.get_local_path()):
            try:
                os.makedirs(self.get_local_path())
            except OSError, (ErrorNumber, ErrorMessage): # Python <=2.5
                if ErrorNumber == errno.EEXIST:
                    pass
                else: raise

        impl = getDOMImplementation()

        newdoc = impl.createDocument(None, "perroquet_repository", None)
        root_element = newdoc.documentElement

        # Name
        xml_name = newdoc.createElement("name")
        xml_name.appendChild(newdoc.createTextNode(self.get_name()))
        root_element.appendChild(xml_name)

        # Id
        xml_id = newdoc.createElement("id")
        xml_id.appendChild(newdoc.createTextNode(self.get_id()))
        root_element.appendChild(xml_id)

        # Description
        xml_description = newdoc.createElement("description")
        xml_description.appendChild(newdoc.createTextNode(self.get_description()))
        root_element.appendChild(xml_description)

        # Version
        xml_version = newdoc.createElement("version")
        xml_version.appendChild(newdoc.createTextNode(self.get_version()))
        root_element.appendChild(xml_version)

        # Url
        xml_url = newdoc.createElement("url")
        xml_url.appendChild(newdoc.createTextNode(self.get_url()))
        root_element.appendChild(xml_url)


        xml_string = newdoc.toprettyxml()
        xml_string = xml_string.encode('utf8')
        repoDescriptionPath = os.path.join(self.get_local_path(), "repository.xml")
        f = open(repoDescriptionPath, 'w')
        f.write(xml_string)
        f.close()

    def init_from_path(self, path):

        # Read repositories from xml description file
        repoDescriptionPath = os.path.join(path, "repository.xml")
        if os.path.isfile(repoDescriptionPath):
            f = open(repoDescriptionPath, 'r')
            dom = parse(f)
            self.parse_description(dom)
        else:
            self.set_id(os.path.basename(path))
            self.set_name(os.path.basename(path))

        groupPathList = os.listdir(self.get_local_path())

        for groupPath in groupPathList:
            path = os.path.join(self.get_local_path(), groupPath)
            if os.path.isdir(path):
                group = ExerciseRepositoryGroup()
                group.init_from_path(path)
                group.set_system(self.system)
                self.add_group(group)

    def parse_description(self, dom):
        self.set_name(self._get_text(dom.getElementsByTagName("name")[0].childNodes))
        self.set_description(self._get_text(dom.getElementsByTagName("description")[0].childNodes))
        self.set_id(self._get_text(dom.getElementsByTagName("id")[0].childNodes))
        self.set_version(self._get_text(dom.getElementsByTagName("version")[0].childNodes))
        if len(dom.getElementsByTagName("url")) > 0:
            self.set_url(self._get_text(dom.getElementsByTagName("url")[0].childNodes))

    def parse_distant_repository_file(self, handle):
        dom = parse(handle)

        self.parse_description(dom)
        self.set_type("distant")

        xml_groups = dom.getElementsByTagName("exercises_groups")[0]

        for xml_group in xml_groups.getElementsByTagName("exercises_group"):
            group = ExerciseRepositoryGroup()
            group.parse_description(xml_group)
            self.add_group(group)

            xml_exercises = xml_group.getElementsByTagName("exercises")[0]
            for xml_exercise in xml_exercises.getElementsByTagName("exercise"):
                exercise = ExerciseRepositoryExercise()
                exercise.parse_description(xml_exercise)
                group.add_exercise(exercise)


    def _get_text(self, nodelist):
        rc = ""
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
        rc = rc.strip()
        return rc
