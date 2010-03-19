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

import gtk, time, urllib, re, os, gettext
import locale
from perroquetlib.config import config
from perroquetlib.languages_manager import LanguagesManager
_ = gettext.gettext

class GuiResetExercise:
    def __init__(self, core, parent):

        self.core = core
        self.config = config
        self.parent = parent

        self.builder = gtk.Builder()
        self.builder.set_translation_domain("perroquet")
        self.builder.add_from_file(self.config.get("ui_reset_path"))
        self.builder.connect_signals(self)
        self.dialog = self.builder.get_object("dialogReset")

        self.pagePaths = self.builder.get_object("pagePaths")
        self.pageSequences = self.builder.get_object("pageSequences")

        self.dialog.set_modal(True)
        self.dialog.set_transient_for(self.parent)

    def Run(self):
        self.dialog.run()
        self.dialog.destroy()

    def on_buttonResetOk_clicked(self, widget, data=None):
        self.core.resetExerciseContent()
        self.dialog.response(gtk.RESPONSE_OK)

    def on_buttonResetCancel_clicked(self, widget, data=None):
        self.dialog.response(gtk.RESPONSE_CANCEL)
