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

class ExerciseRepository:

    def __init__(self):
        self.name =""
        self.description = ""
        self.version = ""
        self.exercisesGroupList = []


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

    def getDescription(self):
        return self.description

    def getVersion(self):
        return self.version

    def addGroup(self, group):
        self.exercisesGroupList.append(group)

    def getGroups(self):
        return self.exercisesGroupList

    class ExercisesGroup:
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

        def addExercise(self, exercise):
            self.exercisesList.append(exercise)
            print exercise.getName()
            print exercise.getDescription()

        def getExercises(self):
            return self.exercisesList

    class Exercise:
        def __init__(self):
            self.name =""
            self.description = ""

        def setName(self, name):
            self.name = name

        def getName(self):
            return self.name

        def setDescription(self, description):
            self.description = description

        def getDescription(self):
            return self.description

        def setLicence(self, licence):
            self.licence = licence

        def getLicence(self):
            return self.licence

        def setLanguage(self, language):
            self.language = language

        def getLanguage(self):
            return self.language

        def setMediaType(self, mediaType):
            self.mediaType = mediaType

        def getMediaType(self):
            return self.mediaType

        def setVersion(self, version):
            self.version = version

        def getVersion(self):
            return self.version

        def setAuthor(self, author):
            self.author = author

        def getAuthor(self):
            return self.author

        def setAuthorWebsite(self, authorWebsite):
            self.authorWebsite = authorWebsite

        def getAuthorWebsite(self):
            return self.authorWebsite

        def setAuthorContact(self, authorContact):
            self.authorContact = authorContact

        def getAuthorContact(self):
            return self.authorContact

        def setPackager(self, packager):
            self.packager = packager

        def getPackager(self):
            return self.packager

        def setPackagerWebsite(self, packagerWebsite):
            self.packagerWebsite = packagerWebsite

        def getPackagerWebsite(self):
            return self.packagerWebsite

        def setPackagerContact(self, packagerContact):
            self.packagerContact = packagerContact

        def getPackagerContact(self):
            return self.packagerContact

        def setFilePath(self, filePath):
            self.filePath = filePath

        def getFilePath(self):
            return self.filePath

        def setTranslationsList(self, translationList):
            self.translationList = translationList

        def getTranslationsList(self):
            return self.translationList

