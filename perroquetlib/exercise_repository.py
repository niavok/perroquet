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

class ExerciseRepository(object):

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

    class ExercisesGroup(object):
        def __init__(self):
            self.name =""
            self.description = ""

        def setName(self, name):
            self.name = name

        def setDescription(self, description):
            self.description = description

    class Exercise(object):
        def __init__(self):
            self.name =""
            self.description = ""

        def setName(self, name):
            self.name = name

        def setDescription(self, description):
            self.description = description
