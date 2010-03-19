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

from perroquetlib.config import config

class LanguagesManager:

    LOOK_FOR_ID = 0
    LOOK_FOR_NAME = 1
    LOOK_FOR_CHARLIST = 2

    def __init__(self):
        self.config = config
        self.languageList = []
        self._load()

    def getLanguagesList(self):
        return self.languageList

    def getLanguageById(self,idToFind):
        for language in self.languageList:
            (id,name,charList) = language
            if id == idToFind:
                return language
        return None

    def getDefaultLanguage(self):
        return self.languageList[0]

    def _load(self):
        path = self.config.get("languages_list_path");
        self._parseLanguageFile(path)

    def _parseLanguageFile(self,path):
        self.languageList = []
        f = open(path, 'r')
        state = LanguagesManager.LOOK_FOR_ID
        for line in f:
            line = line.rstrip()
            line = line.decode("utf8")

            if state == LanguagesManager.LOOK_FOR_ID:
                if len(line) > 0:
                    current_id = line
                    state = LanguagesManager.LOOK_FOR_NAME
            elif state == LanguagesManager.LOOK_FOR_NAME:
                 if len(line) > 0:
                    current_name = line
                    state = LanguagesManager.LOOK_FOR_CHARLIST
            elif state == LanguagesManager.LOOK_FOR_CHARLIST:
                current_charList = line
                state = LanguagesManager.LOOK_FOR_ID
                self.languageList.append((current_id,current_name,current_charList))
