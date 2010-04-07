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

import gtk
import gettext
from perroquetlib.config import config
_ = gettext.gettext

class GuiPasswordDialog:
    def __init__(self, parent, type):

        self.config = config
        self.parent = parent

        self.builder = gtk.Builder()
        self.builder.set_translation_domain("perroquet")
        self.builder.add_from_file(self.config.get("ui_password_path"))
        self.builder.connect_signals(self)
        self.dialog = self.builder.get_object("dialog_password")

        self.pagePaths = self.builder.get_object("pagePaths")
        self.pageSequences = self.builder.get_object("pageSequences")

        self.dialog.set_modal(True)
        self.dialog.set_transient_for(self.parent)
        self.result = False

        if type == "correction":
            self.builder.get_object("labelLabel").set_text(_("Correction password :"))
            self.dialog.set_title("Password for unlock correction")
        elif type == "properties":
            self.builder.get_object("labelLabel").set_text(_("Properties password :"))
            self.dialog.set_title("Password for unlock properties")
    

    def run(self):
        self.dialog.run()
        self.dialog.destroy()
        return self.result

    def on_button_reset_ok_clicked(self, widget, data=None):
        self.result = self.builder.get_object("entry_password").get_text()
        self.dialog.response(gtk.RESPONSE_OK)

    def on_button_reset_cancel_clicked(self, widget, data=None):
        self.result = None
        self.dialog.response(gtk.RESPONSE_CANCEL)

    def on_entry_password_activate(self, widget, data=None):
        self.result = self.builder.get_object("entry_password").get_text()
        self.dialog.response(gtk.RESPONSE_OK)

    def on_dialog_password_delete_event(self, widget, data=None):
        self.result = None
        self.dialog.response(gtk.RESPONSE_CANCEL)
        return True

