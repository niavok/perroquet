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

import os, sys
import gettext
import ConfigParser

APP_NAME = 'perroquet'
APP_VERSION = '1.1.0 dev'

def first(self, testFunction, items, finalItem=None): #FIXME many paths
    """Return the name with the first item that match the test function. If 
    impossible, match with finalItem
    test: item -> bool      (for ex os.path.exists, os.path.isfile...)
    """
    l=(i for i, item in enumerate(items) if testFunction(item))
    try:
        firstItemIndex=l.next()
    except StopIteration:
        if finalItem:
            return finalItem
        else:
            raise IOError, "Error : "+name+" not found"
    else:
        return items[firstItemIndex]

class ConfigSingleton(object):
    """useful for gettexe"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
            cls._instance.init()
        return cls._instance

class configFile:
    def __init__(self, writablePath, referencePath):
        self.writablePath = writablePath
        self.referencePath = referencePath
        
    def getKeys(self):
        pass
    
    def save(self):
        pass

class emptyConfig(ConfigSingleton):
    """usage: config = Config()
    Warning: all keys must be lowercase"""
    def init(self):
        self._properties = {}
        self._writableOptions = {}

        self._setLocalPaths();

        configParser = self._loadConfigFiles()
        self._properties.update( dict(configParser.items("string")) )
        self._properties.update( dict(
            ((s, int(i)) for (s,i) in configParser.items("int")) ))

    
    def loadConfigFile(self, writablePath=None, referencePath):
        """Load an ini config file"""
        configParser = ConfigParser.ConfigParser()
        
        if os.path.isfile(self._globalConfFilHref):
            configParser.read(self._globalConfFilHref)
        elif  os.path.isfile(os.path.join(self.Get("script"), 'data/config')):
            configParser.read(os.path.join(self.Get("script"), 'data/config'))
        else:
            raise IOError,  "Error : global conf file 'config' not found at "+ os.path.join(self.Get("script"), 'data/config')

        self._localConfigParser = ConfigParser.ConfigParser()
        if len( self._localConfigParser.read(self._localConfFilHref)) == 0:
            print "No local conf file find"

        self._writableOptions = dict([(option, section)
                for section in configParser.sections()
                for option in configParser.options(section) ])

        for section in self._localConfigParser.sections():
            for (key, value) in self._localConfigParser.items(section):
                configParser.set(section, key, value)

        return configParser

    def Get(self, key):
        """get a propertie"""
        if not key.islower():
            raise KeyError, key+" is not lowercase"
        return self._properties[key]

    def Set(self, key, value):
        """Set a propertie"""
        if not key.islower():
            raise KeyError, key+" is not lowercase"

        self._properties[key] = value

        if key in self._writableOptions.keys():
            section = self._writableOptions[key]
            if not self._localConfigParser.has_section(section):
                self._localConfigParser.add_section(section)
            self._localConfigParser.set(section, key, value)

    def Save(self):
        """Save the properties that have changed"""
        #FIXME: need to create the whole path, not only the final dir
        if not os.path.exists(self.Get("localconfigdir")):
           os.mkdir( self.Get("localconfigdir") )
        self._localConfigParser.write( open(self._localConfFilHref, "w"))

    def loadRepositorySources(self):
        localSourceFile = os.path.join( self.Get("localconfigdir"), "sources.conf")
        globalSourceFile = os.path.join( self.Get("globalconfigdir"), "sources.conf")
        scriptSourceFile = os.path.join( self.Get("script"), "data/sources.conf")

        sourcePathList = []
    
        if os.path.isfile(scriptSourceFile):
            sourcePathList.append(scriptSourceFile)
        if os.path.isfile(globalSourceFile):
            sourcePathList.append(globalSourceFile)
        if os.path.isfile(localSourceFile):
            sourcePathList.append(localSourceFile)

        self.Set("repository_source_list", os.path.join(sourcePathList))
        self.Set("personal_repository_source_path", localSourceFile)


