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
import ConfigParser.ConfigParser

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
    defaultConf = {
        "lastOpenFile" = None
        }

    def init(self):
        self.properties = {}
        self.properties["version"] = APP_VERSION
        self.properties["app_name"] = APP_NAME
        self.properties["gettext_package"] = "perroquet"
        self.properties["executable"] = os.path.dirname(sys.executable)
        self.properties["script"] = sys.path[0]
        self.properties["config_dir"] = os.path.join(
            os.path.expanduser("~"), 
            "perroquet_config")
        
        if os.path.isfile(os.path.join(self.properties["script"], 'data/perroquet.ui')):
            self.properties["ui_path"] = os.path.join(self.properties["script"], 'data/perroquet.ui')
        elif  os.path.isfile(os.path.join(self.properties["script"], '../share/perroquet/perroquet.ui')):
            self.properties["ui_path"] = os.path.join(self.properties["script"], '../share/perroquet/perroquet.ui')
        else:
            print "Error : gui file 'perroquet.ui' not found"
            sys.exit(1)

        # locale
        if os.path.exists(os.path.join(self.properties["script"], 'build/mo')):
            self.properties["localedir"] =  os.path.join(self.properties["script"], 'build/mo')
        else:
            self.properties["localedir"] =  os.path.join(self.properties["script"], '../share/locale')

        if os.path.isfile(os.path.join(self.properties["script"], 'data/perroquet.png')):
            self.properties["logo_path"] = os.path.join(self.properties["script"], 'data/perroquet.png')
        else:
            self.properties["logo_path"] = os.path.join(self.properties["script"], '../share/perroquet/perroquet.png')



        gettext.install (self.Get("gettext_package"),self.Get("localedir"))

    def _load_Files(self):
        href = os.path.join( self.Get("config_dir", "config")
        
        self.configParser = ConfigParser.ConfigParser()
        if len( self.configParser.read(href)) == 0:
            print "No conf file find"
        for (key, values) in defaultConf.items("):
            if not key in self.configParser.options():
                self.configParser.set("default", key, value)

    def Get(self, key):

        return self.properties[key]
