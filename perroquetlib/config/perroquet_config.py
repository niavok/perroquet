# -*- coding: utf-8 -*-

# Copyright (C) 2009-2011 Frédéric Bertolus.
# Copyright (C) 2009-2011 Matthieu Bizien.
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

import gettext
import os
import sys

from config_lib import Config

APP_NAME = 'perroquet'
APP_VERSION = '1.1.1'

config = Config()

#General
config.set("version", APP_VERSION)
config.set("app_name", APP_NAME)


#Paths
config.set("executable", os.path.dirname(sys.executable))
config.set("script", sys.path[0])
config.set("localconfigdir", os.path.join(os.path.expanduser("~"),
           ".config/perroquet"))
config.set("system_repo_root_dir",
           os.path.join("/usr/share/perroquet/repo_root"))

config.set("localdatadir", os.path.join(os.path.expanduser("~"),
           ".local/share/perroquet"))
config.set("local_repo_root_dir",
           os.path.join(config.get("localdatadir"), "repo_root"))
if os.path.exists("/etc/perroquet"):
    config.set("globalconfigdir", "/etc/perroquet") #FIXME ugly
else:
    config.set("globalconfigdir", "/usr/local/etc/perroquet") #FIXME ugly

#Path sources.conf
localSourceFile = os.path.join(config.get("localconfigdir"), "sources.conf")
globalSourceFile = os.path.join(config.get("globalconfigdir"), "sources.conf")
scriptSourceFile = os.path.join(config.get("script"), "data/sources.conf")
sourcePathList = []
if os.path.isfile(scriptSourceFile):
    sourcePathList.append(scriptSourceFile)
if os.path.isfile(globalSourceFile):
    sourcePathList.append(globalSourceFile)
if os.path.isfile(localSourceFile):
    sourcePathList.append(localSourceFile)
config.set("repository_source_list", os.path.join(sourcePathList))
config.set("personal_repository_source_path", localSourceFile)

#path locale
if os.path.exists(os.path.join(config.get("script"), 'build/mo')):
    config.set("localedir", os.path.join(config.get("script"), 'build/mo'))
else:
    config.set("localedir", os.path.join(config.get("script"), '../share/locale'))

if os.path.isfile(os.path.join(config.get("script"), 'data/perroquet.png')):
    config.set("logo_path", os.path.join(config.get("script"), 'data/perroquet.png'))
else:
    config.set("logo_path", os.path.join(config.get("script"), '../share/perroquet/perroquet.png'))

if os.path.isfile(os.path.join(config.get("script"), 'data/audio_icon.png')):
    config.set("audio_icon", os.path.join(config.get("script"), 'data/audio_icon.png'))
else:
    config.set("audio_icon", os.path.join(config.get("script"), '../share/perroquet/audio_icon.png'))



#gettext
config.set("gettext_package", "perroquet")
gettext.install (config.get("gettext_package"), config.get("localedir"))


#Loading files
#perroquet.ui
if os.path.isfile(os.path.join(config.get("script"), 'data/perroquet.ui')):
    config.set("ui_path", os.path.join(config.get("script"), 'data/perroquet.ui'))
elif  os.path.isfile(os.path.join(config.get("script"), '../share/perroquet/perroquet.ui')):
    config.set("ui_path", os.path.join(config.get("script"), '../share/perroquet/perroquet.ui'))
else:
    raise IOError, "Error : gui file 'perroquet.ui' not found"

#settings.ui
if os.path.isfile(os.path.join(config.get("script"), 'data/settings.ui')):
    config.set("ui_settings_path", os.path.join(config.get("script"), 'data/settings.ui'))
elif  os.path.isfile(os.path.join(config.get("script"), '../share/perroquet/settings.ui')):
    config.set("ui_settings_path", os.path.join(config.get("script"), '../share/perroquet/settings.ui'))
else:
    raise IOError, "Error : gui file 'settings.ui' not found"


#properties.ui
if os.path.isfile(os.path.join(config.get("script"), 'data/properties.ui')):
    config.set("ui_sequence_properties_path", os.path.join(config.get("script"), 'data/properties.ui'))
elif  os.path.isfile(os.path.join(config.get("script"), '../share/perroquet/properties.ui')):
    config.set("ui_sequence_properties_path", os.path.join(config.get("script"), '../share/perroquet/properties.ui'))
else:
    raise IOError, "Error : gui file 'properties.ui' not found"

#reset.ui
if os.path.isfile(os.path.join(config.get("script"), 'data/reset.ui')):
    config.set("ui_reset_path", os.path.join(config.get("script"), 'data/reset.ui'))
elif  os.path.isfile(os.path.join(config.get("script"), '../share/perroquet/reset.ui')):
    config.set("ui_reset_path", os.path.join(config.get("script"), '../share/perroquet/reset.ui'))
else:
    raise IOError, "Error : gui file 'reset.ui' not found"

#properties_advanced.ui
if os.path.isfile(os.path.join(config.get("script"), 'data/properties_advanced.ui')):
    config.set("ui_sequence_properties_advanced_path", os.path.join(config.get("script"), 'data/properties_advanced.ui'))
elif  os.path.isfile(os.path.join(config.get("script"), '../share/perroquet/properties.ui')):
    config.set("ui_sequence_properties_advanced_path", os.path.join(config.get("script"), '../share/perroquet/properties_advanced.ui'))
else:
    raise IOError, "Error : gui file 'properties_advanced.ui' not found"

#exercise_manager.ui
if os.path.isfile(os.path.join(config.get("script"), 'data/exercise_manager.ui')):
    config.set("ui_exercise_manager_path", os.path.join(config.get("script"), 'data/exercise_manager.ui'))
elif  os.path.isfile(os.path.join(config.get("script"), '../share/perroquet/exercise_manager.ui')):
    config.set("ui_exercise_manager_path", os.path.join(config.get("script"), '../share/perroquet/exercise_manager.ui'))
else:
    raise IOError, "Error : gui file 'exercise_manager.ui' not found"

#gui_password_dialog.ui
if os.path.isfile(os.path.join(config.get("script"), 'data/gui_password_dialog.ui')):
    config.set("ui_password_path", os.path.join(config.get("script"), 'data/gui_password_dialog.ui'))
elif  os.path.isfile(os.path.join(config.get("script"), '../share/perroquet/gui_password_dialog.ui')):
    config.set("ui_password_path", os.path.join(config.get("script"), '../share/perroquet/gui_password_dialog.ui'))
else:
    raise IOError, "Error : gui file 'gui_password_dialog.ui' not found"

#gui_message_dialog.ui
if os.path.isfile(os.path.join(config.get("script"), 'data/gui_message_dialog.ui')):
    config.set("ui_message_path", os.path.join(config.get("script"), 'data/gui_message_dialog.ui'))
elif  os.path.isfile(os.path.join(config.get("script"), '../share/perroquet/gui_message_dialog.ui')):
    config.set("ui_message_path", os.path.join(config.get("script"), '../share/perroquet/gui_message_dialog.ui'))
else:
    raise IOError, "Error : gui file 'gui_message_dialog.ui' not found"


#languages.list
if os.path.isfile(os.path.join(config.get("script"), 'data/languages.list')):
    config.set("languages_list_path", os.path.join(config.get("script"), 'data/languages.list'))
elif  os.path.isfile(os.path.join(config.get("script"), '../share/perroquet/languages.list')):
    config.set("languages_list_path", os.path.join(config.get("script"), '../share/perroquet/languages.list'))
else:
    raise IOError, "Error : data file 'languages.list' not found"

#config.ini
globalPaths = (
               os.path.join(config.get("globalconfigdir"), "config.ini"),
               os.path.join(config.get("script"), 'data/config.ini'), )
existantGlobalPaths = [path for path in globalPaths if os.path.isfile(path)]
if existantGlobalPaths == []:
    raise IOError, "Error : global conf file 'config.ini' not found"
else:
    globalPath = existantGlobalPaths[0]
localPath = os.path.join(config.get("localconfigdir"), "config.ini")
if not os.path.isfile(localPath):
    config.logger.warn("No local conf file found")
config.load_writable_config_file(localPath, globalPath)

#languages_aliases.ini
paths = (
         os.path.join(config.get("globalconfigdir"), "languages_aliases.ini"),
         os.path.join(config.get("script"), 'data/languages_aliases.ini'), )
existantPaths = [path for path in paths if os.path.isfile(path)]
if existantPaths == []:
    raise IOError, "Error : global conf file 'languages_aliases.ini' not found"
else:
    path = existantPaths[0]
config.load_config_file(path)
