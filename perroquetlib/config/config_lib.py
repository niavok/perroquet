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

"""Library used to create easily configuration"""

import os, sys
import gettext
import ConfigParser

APP_NAME = 'perroquet'
APP_VERSION = '1.1.0 dev'

class Config:
    """Usage: config = Config()
    Warning: all keys must be lowercase"""
    functionsOfSection = {
        "int": int,
        "string": lambda x: x  ,}
    
    def __init__(self):
        self._properties = {}
        self._writableParsers = [] #[(localParser, writableOptions, writablePath),...]
        
    
    def loadWritableConfigFile(self, writablePath, referencePath):
        """Load an ini config file that can be modified. Don't deal with file management"""
        #localParser exists because we din't want to fill the wirtablePath
        #in case the config change
        parser      = ConfigParser.ConfigParser()
        localParser = ConfigParser.ConfigParser()
        
        if not os.path.isfile(referencePath):
            raise IOError, referencePath
        
        #Load
        localParser.read(writablePath)
        
        parser.read(referencePath)
        writableOptions = dict([(option, section)
                for section in parser.sections()
                for option in parser.options(section) ])
        parser.read(writablePath)
        
        #Write
        for section in parser.sections():
            for (key, value) in parser.items(section):
                self.Set(key, self.functionsOfSection[section](value))
        self._writableParsers.append((localParser, writableOptions, writablePath))

    def Get(self, key):
        """Get a propertie"""
        if not key.islower():
            raise KeyError, key+" is not lowercase"
        return self._properties[key]

    def Set(self, key, value):
        """Set a propertie"""
        if not key.islower():
            raise KeyError, key+" is not lowercase"

        self._properties[key] = value
        
        for (parser, writableOptions, _) in self._writableParsers:
            if key in writableOptions.keys():
                section = writableOptions[key]
                if not parser.has_section(section):
                    localParser.add_section(section)
                parser.set(section, key, value)
            
    def Save(self):
        """Save the properties that have changed"""
        #FIXME: need to create all the recursive dirs, not only the final path
        for (parser, _, path) in self._writableParsers:
            parser.write(open(path, "w"))
    
    def __str__(self):
        return str(self._properties)
    
    def __repr__(self):
        return "<Config "+str(self)[:50]+">"
