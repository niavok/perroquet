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

class Parser(ConfigParser.ConfigParser):
    """A general class to make parsers"""
    def __init__(self):
        ConfigParser.ConfigParser.__init__(self)
        
    def getOptions(self):
        "return {option1: section1, ...}"
        return dict([(option, section)
                for section in self.sections()
                for option in self.options(section) ])


class WritableParser(Parser):
    """A class that deal with writable parsers"""
    def __init__(self, path):
        Parser.__init__(self)
        self.path = path
        self.read(self.path)
        self._options = Parser.getOptions(self)
        
    def save(self):
        #TODO create the dir .config/perroquet if not existant
        self.write(open(self.path, "w"))
        
    def set_if_existant_key(self, key, value):
        if key in self._options.keys():
            section = self._options[key]
            if not self.has_section(section):
                self.add_section(section)
            self.set(section, key, value)
    
    def setOptions(self, dictionnary):
        self._options = dictionnary
    
    def getOptions(self):
        return self._options
    
    
class Config:
    """Usage: config = Config()
    Warning: all keys must be lowercase"""
    functionsOfSection = {
        "int": int,
        "string": lambda x: x  ,}
    
    def __init__(self):
        self._properties = {}
        self._writableParsers = []
        
    def loadWritableConfigFile(self, writablePath, referencePath):
        """Load an ini config file that can be modified."""
        #localParser exists because we din't want to copy referencePath to
        # the wirtablePath in case the config change
     
        #Load
        parser = Parser()
        if not os.path.isfile(referencePath):
            raise IOError, referencePath
        parser.read(referencePath)
        writableOptions = parser.getOptions()
        parser.read(writablePath)
        
        #Write
        for (option, section) in writableOptions.items():
            self.Set(option, self.functionsOfSection[section](parser.get(section, option)))
        
        #Remember
        localParser = WritableParser( writablePath)
        localParser.setOptions( writableOptions )
        self._writableParsers.append(localParser)

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
        for writableParser in self._writableParsers:
            writableParser.set_if_existant_key(key, value)
            
    def Save(self):
        """Save the properties that have changed"""
        #FIXME: need to create all the recursive dirs, not only the final path
        for writableParser in self._writableParsers:
            writableParser.save()
    
    def __str__(self):
        return str(self._properties).replace(", ", "\n")
    
    def __repr__(self):
        return "<Config "+str(self)[:50]+">"
