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
from perroquetlib.exercise_repository import *
from xml.dom.minidom import getDOMImplementation, parse
import urllib2

class ExerciseRepositoryManager:

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
                    repositoryList.append(self._parseRepositoryFile(handle))

        return repositoryList


    def _parseRepositoryFile(self, handle):
        dom = parse(handle)
        repository = ExerciseRepository()
        repository.setName(self._getText(dom.getElementsByTagName("name")[0].childNodes))
        repository.setDescription(self._getText(dom.getElementsByTagName("description")[0].childNodes))
        repository.setId(self._getText(dom.getElementsByTagName("id")[0].childNodes))
        repository.setVersion(self._getText(dom.getElementsByTagName("version")[0].childNodes))

        xml_groups = dom.getElementsByTagName("exercises_groups")[0]

        for xml_group in xml_groups.getElementsByTagName("exercises_group"):
            group = ExerciseRepository.ExercisesGroup()
            group.setName(self._getText(xml_group.getElementsByTagName("name")[0].childNodes))
            group.setId(self._getText(xml_group.getElementsByTagName("id")[0].childNodes))
            group.setDescription(self._getText(xml_group.getElementsByTagName("description")[0].childNodes))
            repository.addGroup(group)

            xml_exercises = xml_group.getElementsByTagName("exercises")[0]
            for xml_exercise in xml_exercises.getElementsByTagName("exercise"):
                exercise = ExerciseRepository.Exercise()
                group.addExercise(exercise)
                exercise.setName(self._getText(xml_exercise.getElementsByTagName("name")[0].childNodes))
                exercise.setId(self._getText(xml_exercise.getElementsByTagName("id")[0].childNodes))
                exercise.setDescription(self._getText(xml_exercise.getElementsByTagName("description")[0].childNodes))
                exercise.setLicence(self._getText(xml_exercise.getElementsByTagName("licence")[0].childNodes))
                exercise.setLanguage(self._getText(xml_exercise.getElementsByTagName("language")[0].childNodes))
                exercise.setMediaType(self._getText(xml_exercise.getElementsByTagName("media_type")[0].childNodes))
                exercise.setVersion(self._getText(xml_exercise.getElementsByTagName("exercise_version")[0].childNodes))
                exercise.setAuthor(self._getText(xml_exercise.getElementsByTagName("author")[0].childNodes))
                exercise.setAuthorWebsite(self._getText(xml_exercise.getElementsByTagName("author_website")[0].childNodes))
                exercise.setAuthorContact(self._getText(xml_exercise.getElementsByTagName("author_contact")[0].childNodes))
                exercise.setPackager(self._getText(xml_exercise.getElementsByTagName("packager")[0].childNodes))
                exercise.setPackagerWebsite(self._getText(xml_exercise.getElementsByTagName("packager_website")[0].childNodes))
                exercise.setPackagerContact(self._getText(xml_exercise.getElementsByTagName("packager_contact")[0].childNodes))
                exercise.setFilePath(self._getText(xml_exercise.getElementsByTagName("file")[0].childNodes))

                xml_translations = xml_exercise.getElementsByTagName("translations")[0]
                translationList = []
                for xml_translation in xml_translations.getElementsByTagName("translation"):
                    translationList.append(self._getText(xml_translation.childNodes))

                exercise.setTranslationsList(translationList)


        return repository

    def _getText(self, nodelist):
        rc = ""
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
        rc = rc.strip()
        return rc

