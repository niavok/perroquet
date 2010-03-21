import re
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Perroquet. If not, see <http://www.gnu.org/licenses/>.

from perroquetlib.config.perroquet_config import config
from perroquetlib.gui.gui import Gui

class GuiController:

    def __init__(self):
        """GuiControlle constructor"""
        self.core = None
        self.word_list = None

        # Mode can be closed, loaded or load_failed
        self.mode = "closed"
        self.gui = Gui()
  
    def set_core(self, core):
        """Define perroquet core to use"""
        self.core = core



    def activate(self, mode):
        self.mode = mode
        self.refresh()


    def refresh(self):
        "Enable or disable ihm component"
        if self.mode == "loaded":
            self.gui.set_enable_sequence_index_selection(True)
            self.gui.set_enable_sequence_time_selection(True)
            self.gui.set_enable_hint(True)
            self.gui.set_enable_replay_sequence(True)
            self.gui.set_enable_properties(True)
            self.gui.set_enable_advanced_properties(True)
            self.gui.set_enable_translation(True)
            self.gui.set_enable_save_as(True)
            self.gui.set_enable_save(True)
            self.gui.set_enable_export_as_template(True)
            self.gui.set_enable_export_as_package(True)

            


            #Disable speed change slider if the media player not support it
            if self.core.getPlayer().isSpeedChangeable():
                self.gui.set_enable_speed_selection(True)     
            else:
                self.gui.set_enable_speed_selection(False)

        if self.mode == "load_failed":
            self.gui.set_enable_sequence_index_selection(False)
            self.gui.set_enable_sequence_time_selection(False)
            self.gui.set_enable_hint(False)
            self.gui.set_enable_replay_sequence(False)
            self.gui.set_enable_properties(True)
            self.gui.set_enable_advanced_properties(True)
            self.gui.set_enable_translation(False)
            self.gui.set_enable_save_as(False)
            self.gui.set_enable_save(False)
            self.gui.set_enable_export_as_template(False)
            self.gui.set_enable_export_as_package(False)
            self.gui.set_enable_speed_selection(False)
            
        if self.mode == "closed":
            self.gui.set_enable_sequence_index_selection(False)
            self.gui.set_enable_sequence_time_selection(False)
            self.gui.set_enable_hint(False)
            self.gui.set_enable_replay_sequence(False)
            self.gui.set_enable_properties(False)
            self.gui.set_enable_advanced_properties(False)
            self.gui.set_enable_translation(False)
            self.gui.set_enable_save_as(False)
            self.gui.set_enable_save(False)
            self.gui.set_enable_export_as_template(False)
            self.gui.set_enable_export_as_package(False)
            self.gui.set_enable_speed_selection(False)
            
        if config.get("interface_show_play_pause_buttons") == 1:
            self.gui.set_visible_play(True)
            self.gui.set_visible_pause(True)
        else:
            self.gui.set_visible_play(False)
            self.gui.set_visible_pause(False)

    def get_video_window_id(self):
        return self.gui.get_video_window_id()

    def activate_video_area(self,state):
        self.gui.activate_video_area(state)


    def set_word_list(self, word_list):
        self.word_list = word_list
        self.update_word_list()

    def update_word_list(self):
        """Apply filter and send the new list to the gui"""

        filtered_word_list = []

        filter_regexp = self.gui.get_words_filter()

        try:
            re.search(filter_regexp,"")
        except re.error:
            filter_regexp = ""
            pass

        for word in self.word_list:
            if re.search(filter_regexp,word):
                filtered_word_list.append(word)

        self.gui.set_word_list(filtered_word_list)

    def set_playing(self, state):
        self.gui.set_enable_play(not state)
        self.gui.set_enable_pause(state)

    def set_can_save(self, state):
        self.gui.set_enable_save(state)

    def set_title(self, title, save):

        newTitle = _("Perroquet")

        if save:
            newTitle += " *"

        if title != "":
            newTitle += " - " + title

        self.gui.set_title(newTitle)