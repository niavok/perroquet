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


class Language:
    def __init__(self, id, name, availableChars, helpChar="~"):
        self.id = id
        self.name = name
        self.availableChars = availableChars
        self.helpChar = helpChar
        self._aliases = []

    def add_alias(self, alias, meaning):
        self._aliases.append((alias,meaning))

    def add_synonyms(self, l):
        for alias in l:
            for meaning in (e for e in l if e!=alias):
                self.add_alias(alias, meaning)

    def is_alias(self, alias, meaning):
        return (alias, meaning) in self._aliases



class LanguagesManager:

    LOOK_FOR_ID = 0
    LOOK_FOR_NAME = 1
    LOOK_FOR_CHARLIST = 2

    def __init__(self):
        self.config = config
        self.languageList = []
        self._load()

    def get_languages_list(self):
        return self.languageList

    def get_language_by_id(self,idToFind):
        for language in self.languageList:
            if language.id == idToFind:
                return language
        return None

    def get_default_language(self):
        return self.languageList[0]

    def _load(self):
        path = self.config.get("languages_list_path");
        self._parse_language_file(path)

    def _parse_language_file(self,path):
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
                current_availableChars = line
                state = LanguagesManager.LOOK_FOR_ID

                language = Language(current_id,current_name,current_availableChars)
                self.languageList.append(language)

