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

from config_lib import Config

APP_NAME = 'perroquet'
APP_VERSION = '1.1.0 dev'

config = Config()

#General
config.Set("version", APP_VERSION)
config.Set("app_name", APP_NAME)


#Paths
config.Set("executable", os.path.dirname(sys.executable))
config.Set("script", sys.path[0])
config.Set("localconfigdir", os.path.join(os.path.expanduser("~"),
    ".config/perroquet"))
config.Set("localdatadir", os.path.join(os.path.expanduser("~"),
    ".local/share/perroquet"))
config.Set("local_repo_root_dir",
    os.path.join(config.Get("localdatadir"), "repo_root"))
config.Set("globalconfigdir", "/etc/perroquet") #FIXME ugly

#Path sources.conf
localSourceFile = os.path.join( config.Get("localconfigdir"), "sources.conf")
globalSourceFile = os.path.join( config.Get("globalconfigdir"), "sources.conf")
scriptSourceFile = os.path.join( config.Get("script"), "data/sources.conf")
sourcePathList = []
if os.path.isfile(scriptSourceFile):
    sourcePathList.append(scriptSourceFile)
if os.path.isfile(globalSourceFile):
    sourcePathList.append(globalSourceFile)
if os.path.isfile(localSourceFile):
    sourcePathList.append(localSourceFile)
config.Set("repository_source_list", os.path.join(sourcePathList))
config.Set("personal_repository_source_path", localSourceFile)

#path locale
if os.path.exists(os.path.join(config.Get("script"), 'build/mo')):
    config.Set("localedir",  os.path.join(config.Get("script"), 'build/mo'))
else:
    config.Set("localedir",  os.path.join(config.Get("script"), '../share/locale'))

if os.path.isfile(os.path.join(config.Get("script"), 'data/perroquet.png')):
    config.Set("logo_path", os.path.join(config.Get("script"), 'data/perroquet.png'))
else:
    config.Set("logo_path", os.path.join(config.Get("script"), '../share/perroquet/perroquet.png'))

if os.path.isfile(os.path.join(config.Get("script"), 'data/audio_icon.png')):
    config.Set("audio_icon", os.path.join(config.Get("script"), 'data/audio_icon.png'))
else:
    config.Set("audio_icon", os.path.join(config.Get("script"), '../share/perroquet/audio_icon.png'))



#gettext
config.Set("gettext_package", "perroquet")
gettext.install (config.Get("gettext_package"),config.Get("localedir"))


#Loading files
#perroquet.ui
if os.path.isfile(os.path.join(config.Get("script"), 'data/perroquet.ui')):
    config.Set("ui_path", os.path.join(config.Get("script"), 'data/perroquet.ui'))
elif  os.path.isfile(os.path.join(config.Get("script"), '../share/perroquet/perroquet.ui')):
    config.Set("ui_path", os.path.join(config.Get("script"), '../share/perroquet/perroquet.ui'))
else:
    raise IOError, "Error : gui file 'perroquet.ui' not found"

#settings.ui
if os.path.isfile(os.path.join(config.Get("script"), 'data/settings.ui')):
    config.Set("ui_settings_path", os.path.join(config.Get("script"), 'data/settings.ui'))
elif  os.path.isfile(os.path.join(config.Get("script"), '../share/perroquet/settings.ui')):
    config.Set("ui_settings_path", os.path.join(config.Get("script"), '../share/perroquet/settings.ui'))
else:
    raise IOError,  "Error : gui file 'settings.ui' not found"


#properties.ui
if os.path.isfile(os.path.join(config.Get("script"), 'data/properties.ui')):
    config.Set("ui_sequence_properties_path", os.path.join(config.Get("script"), 'data/properties.ui'))
elif  os.path.isfile(os.path.join(config.Get("script"), '../share/perroquet/properties.ui')):
    config.Set("ui_sequence_properties_path", os.path.join(config.Get("script"), '../share/perroquet/properties.ui'))
else:
    raise IOError,  "Error : gui file 'properties.ui' not found"

#reset.ui
if os.path.isfile(os.path.join(config.Get("script"), 'data/reset.ui')):
    config.Set("ui_reset_path", os.path.join(config.Get("script"), 'data/reset.ui'))
elif  os.path.isfile(os.path.join(config.Get("script"), '../share/perroquet/reset.ui')):
    config.Set("ui_reset_path", os.path.join(config.Get("script"), '../share/perroquet/reset.ui'))
else:
    raise IOError,  "Error : gui file 'reset.ui' not found"

#properties_advanced.ui
if os.path.isfile(os.path.join(config.Get("script"), 'data/properties_advanced.ui')):
    config.Set("ui_sequence_properties_advanced_path", os.path.join(config.Get("script"), 'data/properties_advanced.ui'))
elif  os.path.isfile(os.path.join(config.Get("script"), '../share/perroquet/properties.ui')):
    config.Set("ui_sequence_properties_advanced_path", os.path.join(config.Get("script"), '../share/perroquet/properties_advanced.ui'))
else:
    raise IOError,  "Error : gui file 'properties_advanced.ui' not found"

#exercise_manager.ui
if os.path.isfile(os.path.join(config.Get("script"), 'data/exercise_manager.ui')):
    config.Set("ui_exercise_manager_path", os.path.join(config.Get("script"), 'data/exercise_manager.ui'))
elif  os.path.isfile(os.path.join(config.Get("script"), '../share/perroquet/exercise_manager.ui')):
    config.Set("ui_exercise_manager_path", os.path.join(config.Get("script"), '../share/perroquet/exercise_manager.ui'))
else:
    raise IOError,  "Error : gui file 'exercise_manager.ui' not found"

#languages.list
if os.path.isfile(os.path.join(config.Get("script"), 'data/languages.list')):
    config.Set("languages_list_path", os.path.join(config.Get("script"), 'data/languages.list'))
elif  os.path.isfile(os.path.join(config.Get("script"), '../share/perroquet/languages.list')):
    config.Set("languages_list_path", os.path.join(config.Get("script"), '../share/perroquet/languages.list'))
else:
    raise IOError,  "Error : data file 'languages.list' not found"

#config.ini
globalPaths = (
    os.path.join( config.Get("globalconfigdir"), "config.ini"),
    os.path.join(config.Get("script"), 'data/config.ini') ,)
existantGlobalPaths = [path for path in globalPaths if os.path.isfile(path)]
if existantGlobalPaths == []:
    raise IOError,  "Error : global conf file 'config.ini' not found"
else:
    globalPath = existantGlobalPaths[0]
localPath = os.path.join( config.Get("localconfigdir"), "config.ini")
if not os.path.isfile(localPath):
    print "No local conf file found"
config.loadWritableConfigFile(localPath, globalPath)

