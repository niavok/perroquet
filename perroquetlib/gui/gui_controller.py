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


import gettext
import re
from perroquetlib.config.perroquet_config import config
from perroquetlib.gui.gui import Gui
from perroquetlib.gui.gui_exercise_controller import GuiExerciseController
_ = gettext.gettext

class GuiController:

    def __init__(self):
        """GuiController constructor"""
        self.core = None
        self.word_list = None

        # Mode can be closed, loaded or load_failed
        self.mode = "closed"
        
        self.gui = Gui(self)
        self.gui_exercise_controller = None
        self.translation_visible = False
        self.current_speed = 1.0

        if not config.get("showlateralpanel"):
            self.gui.set_visible_lateral_panel(False)
        else:
            self.gui.set_checked_lateral_panel(True)
            self.gui.set_visible_lateral_panel(True)
            config.set("showlateralpanel", 1)
  
    def set_core(self, core):
        """Define perroquet core to use"""
        self.core = core
        self.gui_exercise_controller = GuiExerciseController(self.core, self.gui)



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

    def set_speed(self, speed):
        self.current_speed = speed
        self.gui.set_speed(speed)

    def set_sequence_number(self, sequenceNumber, sequenceCount):
        sequenceNumber = sequenceNumber + 1
        self.gui.set_sequence_index_selection(sequenceNumber,sequenceCount)

        self.gui.set_enable_next_sequence(sequenceNumber != sequenceCount)
        self.gui.set_enable_previous_sequence(sequenceNumber != 1)
 
    def set_sequence_time(self, sequence_position, sequence_time):
        if sequence_position > sequence_time:
            sequence_position = sequence_time
        if sequence_position < 0:
            sequence_position = 0
        self.gui.set_sequence_time_selection(sequence_position, sequence_time)

    def set_sequence(self, sequence):
       self.gui_exercise_controller.set_sequence(sequence)

    def set_translation(self, translation):
        self.gui.set_translation(translation)

    def set_statitics(self, sequenceCount,sequenceFound, wordCount, wordFound, repeatRate):
        text = ""
        text = text + _("- Sequences: %(found)s/%(count)s (%(percent)s %%)\n") % {'found' : str(sequenceFound), 'count' : str(sequenceCount), 'percent' : str(round(100*sequenceFound/sequenceCount,1)) }
        text = text + _("- Words: %(found)s/%(count)s (%(percent)s %%)\n") % {'found' : str(wordFound), 'count' : str(wordCount), 'percent' : str(round(100*wordFound/wordCount,1))}
        text = text + _("- Repeat ratio: %s per words") % str(round(repeatRate,1))
        self.gui.set_statitics(text)

    def run(self):
        self.gui.run()

    def toggle_lateral_panel(self):
        if config.get("showlateralpanel"):
            self.gui.set_visible_lateral_panel(False)
            config.set("showlateralpanel", 0)
        else:
            self.gui.set_visible_lateral_panel(True)
            config.set("showlateralpanel", 1)

    def toggle_translation(self):
        if not self.translation_visible:
            self.gui.set_visible_translation_panel(True)
            self.gui.set_enable_translation(True)
            self.translation_visible = True
        else:
            self.gui.set_visible_translation_panel(False)
            self.gui.set_enable_translation(False)
            self.translation_visible = False

    def notify_typing(self, new_text):

        for char in new_text:
            if char == " ":
                self.core.NextWord()
            else:
                self.core.WriteChar(char)

    def notify_move_cursor(self,movement):
        self.gui_exercise_controller.notify_move_cursor(movement)
        

    def notify_key_press(self,keyname):
        if keyname == "Return" or keyname == "KP_Enter":
            self.core.UserRepeat()
            self.core.repeat_sequence()
        elif keyname == "BackSpace":
            self.core.DeletePreviousChar()
        elif keyname == "Delete":
            self.core.DeleteNextChar()
        elif keyname == "Page_Down":
            self.core.PreviousSequence()
        elif keyname == "Page_Up":
            self.core.next_sequence()
        elif keyname == "Down":
           self.core.PreviousSequence()
        elif keyname == "Up":
           self.core.next_sequence()
        elif keyname == "Tab":
            self.core.NextWord()
        elif keyname == "ISO_Left_Tab":
            self.core.PreviousWord()
        elif keyname == "F1":
            self.core.CompleteWord()
        elif keyname == "F2":
            self.toggle_translation()
        elif keyname == "F9":
            self.toggle_lateral_panel()
        elif keyname == "Pause":
            self.core.togglePause()
        elif keyname == "KP_Add":
            if self.current_speed > 0.9:
                self.core.set_speed(1.0)
            else:
                self.core.set_speed(self.current_speed+0.1)
        elif keyname == "KP_Subtract":
            if self.current_speed < 0.85:
                self.core.set_speed(0.75)
            else:
                self.core.set_speed(self.current_speed-0.1)
        else:
            return False

        return True;


    def notify_quit(self):
        if not config.get("autosave"):
            if not self.core.getCanSave():
                self.gui.quit()
                return False #True for quit
            if self.gui.ask_confirm_quit_without_save():
                config.save()
                self.gui.quit()
                return False #True for quit
            else:
                return True #True for not quit
        else:
            self.core.save()
            config.save()
            self.gui.quit()
            return True #True for quit
