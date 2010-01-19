# -*- coding: utf-8 -*-

# Copyright (C) 2009-2010 Frédéric Bertolus.
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
APP_VERSION = '1.0.1'

class ConfigSingleton(object):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
            cls._instance.init()
        return cls._instance

class Config(ConfigSingleton):
    #WARNING: no value must be None
    defaultConf = {
        "lastOpenFile" : ""
        }

    def init(self):
        self.properties = {}
        self.Set("version", APP_VERSION)
        self.Set("app_name", APP_NAME)
        self.Set("gettext_package", "perroquet")
        self.Set("executable", os.path.dirname(sys.executable))
        self.Set("script", sys.path[0])
        self.Set("config_dir", os.path.join(
            os.path.expanduser("~"), 
            "perroquet_config"))
        
        if os.path.isfile(os.path.join(self.Get("script"), 'data/perroquet.ui')):
            self.Set("ui_path", os.path.join(self.Get("script"), 'data/perroquet.ui'))
        elif  os.path.isfile(os.path.join(self.Get("script"), '../share/perroquet/perroquet.ui')):
            self.Set("ui_path", os.path.join(self.Get("script"), '../share/perroquet/perroquet.ui'))
        else:
            print "Error : gui file 'perroquet.ui' not found"
            sys.exit(1)

        # locale
        if os.path.exists(os.path.join(self.Get("script"), 'build/mo')):
            self.Set("localedir",  os.path.join(self.Get("script"), 'build/mo'))
        else:
            self.Set("localedir",  os.path.join(self.Get("script"), '../share/locale'))

        if os.path.isfile(os.path.join(self.Get("script"), 'data/perroquet.png')):
            self.Set("logo_path", os.path.join(self.Get("script"), 'data/perroquet.png'))
        else:
            self.Set("logo_path", os.path.join(self.Get("script"), '../share/perroquet/perroquet.png'))

        gettext.install (self.Get("gettext_package"),self.Get("localedir"))
        
        self.configParser = self._load_Files("config")
        self.properties.update( dict(self.configParser.items("config")) )

    def _load_Files(self, section):
        "Load the config file and add it to configParser"
        self._href = os.path.join( self.Get("config_dir"), "config")
        
        configParser = ConfigParser.ConfigParser()
        if len( configParser.read(self._href)) == 0:
            print "No conf file find"
        if not configParser.has_section(section):
            configParser.add_section(section)
        for (key, value) in self.__class__.defaultConf.items():
            if not key in configParser.options(section):
                configParser.set(section, key, value)
        return configParser

    def Get(self, key):
        return self.properties[key]
    
    def Set(self, key, value):
        self.properties[key] = value
        if key in self.__class__.defaultConf.keys():
            self.configParser.set("config", key, value)
    
    def Save(self):
        #FIXME: need to create the whole path, not only the final dir
        if not os.path.exists(self.Get("config_dir")):
           os.mkdir( self.Get("config_dir") )
        self.configParser.write( open(self._href, "w"))
