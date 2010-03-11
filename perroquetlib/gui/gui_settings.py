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

class GuiSettings:
    def __init__(self, parent):

        self.config = config
        self.parent = parent

        self.builder = gtk.Builder()
        self.builder.set_translation_domain("perroquet")
        self.builder.add_from_file(self.config.Get("ui_settings_path"))
        self.builder.connect_signals(self)
        self.dialog = self.builder.get_object("dialogSettings")
        self.dialog.set_modal(True)
        self.dialog.set_transient_for(self.parent)

        self.iterPath = None


    def Run(self):
        self.Load()
        self.dialog.run()
        self.dialog.destroy()

    def Load(self):

        adjustmentTimeBetweenSequence = self.builder.get_object("adjustmentTimeBetweenSequence")
        adjustmentTimeBetweenSequence.set_value(float(config.Get("default_exercise_time_between_sequences"))/1000)

        adjustmentMaximumSequenceTime = self.builder.get_object("adjustmentMaximumSequenceTime")
        adjustmentMaximumSequenceTime.set_value(float(config.Get("default_exercise_max_sequence_length"))/1000)

        adjustmentTimeBeforeSequence = self.builder.get_object("adjustmentTimeBeforeSequence")
        adjustmentTimeBeforeSequence.set_value(float(config.Get("default_exercise_play_margin_after")))

        adjustmentTimeAfterSequence = self.builder.get_object("adjustmentTimeAfterSequence")
        adjustmentTimeAfterSequence.set_value(float(config.Get("default_exercise_play_margin_before")))

        checkbuttonRepeatAfterComplete = self.builder.get_object("checkbuttonRepeatAfterComplete")
        checkbuttonRepeatAfterComplete.set_active(config.Get("default_exercise_repeat_after_competed") == 1)

        checkbuttonRandomOrder = self.builder.get_object("checkbuttonRandomOrder")
        checkbuttonRandomOrder.set_active(config.Get("default_exercise_random_order") == 1)

        #Interface
        checkbuttonShowPlayPauseButtons = self.builder.get_object("checkbuttonShowPlayPauseButtons")
        checkbuttonShowPlayPauseButtons.set_active(config.Get("interface_show_play_pause_buttons") == 1)

        # Language
        self.liststoreLanguage = gtk.ListStore(str,str)

        languageManager = LanguagesManager()
        languagesList =languageManager.getLanguagesList()

        currentLangId = config.Get("default_exercise_language")

        for language in languagesList:
            (langId,langName,chars) = language
            iter = self.liststoreLanguage.append([langName,langId])
            if langId == currentLangId:
                currentIter = iter


        comboboxLanguage = self.builder.get_object("comboboxLanguage")

        cell = gtk.CellRendererText()
        comboboxLanguage.set_model(self.liststoreLanguage)
        comboboxLanguage.pack_start(cell, True)
        comboboxLanguage.add_attribute(cell, 'text', 0)

        comboboxLanguage.set_active_iter(currentIter)

    def on_buttonExercisePropOk_clicked(self,widget,data=None):

        adjustmentTimeBetweenSequence = self.builder.get_object("adjustmentTimeBetweenSequence")
        config.Set("default_exercise_time_between_sequences",int(1000*adjustmentTimeBetweenSequence.get_value()))

        adjustmentMaximumSequenceTime = self.builder.get_object("adjustmentMaximumSequenceTime")
        config.Set("default_exercise_max_sequence_length",int(1000*adjustmentMaximumSequenceTime.get_value()))

        adjustmentTimeBeforeSequence = self.builder.get_object("adjustmentTimeBeforeSequence")
        config.Set("default_exercise_play_margin_before",int(adjustmentTimeBeforeSequence.get_value()))

        adjustmentTimeAfterSequence = self.builder.get_object("adjustmentTimeAfterSequence")
        config.Set("default_exercise_play_margin_after",int(adjustmentTimeAfterSequence.get_value()))

        checkbuttonRepeatAfterComplete = self.builder.get_object("checkbuttonRepeatAfterComplete")
        if checkbuttonRepeatAfterComplete.get_active():
            config.Set("default_exercise_repeat_after_competed",1)
        else:
            config.Set("default_exercise_repeat_after_competed",0)

        checkbuttonRandomOrder = self.builder.get_object("checkbuttonRandomOrder")
        if checkbuttonRandomOrder.get_active():
            config.Set("default_exercise_random_order",1)
        else:
            config.Set("default_exercise_random_order",0)

        #Interface
        checkbuttonShowPlayPauseButtons = self.builder.get_object("checkbuttonShowPlayPauseButtons")
        if checkbuttonShowPlayPauseButtons.get_active():
            config.Set("interface_show_play_pause_buttons",1)
        else:
            config.Set("interface_show_play_pause_buttons",0)



        #Language
        comboboxLanguage = self.builder.get_object("comboboxLanguage")
        self.liststoreLanguage.get_iter_first()
        iter = comboboxLanguage.get_active_iter()
        langId = self.liststoreLanguage.get_value(iter,1)

        config.Set("default_exercise_language",langId)

        self.dialog.response(gtk.RESPONSE_OK)

    def on_buttonExercisePropCancel_clicked(self,widget,data=None):
        self.dialog.response(gtk.RESPONSE_CANCEL)

    def on_buttonDefautTimeBetweenSequences_clicked(self,widget,data=None):
        """adjustmentTimeBetweenSequence = self.builder.get_object("adjustmentTimeBetweenSequence")
        exercice = Exercise()
        adjustmentTimeBetweenSequence.set_value(exercice.GetTimeBetweenSequence())"""
        print "TODO"

    def on_buttonDefautMaximumSequenceTime_clicked(self,widget,data=None):
        """adjustmentMaximumSequenceTime = self.builder.get_object("adjustmentMaximumSequenceTime")
        exercice = Exercise()
        adjustmentMaximumSequenceTime.set_value(exercice.GetMaxSequenceLength())"""
        print "TODO"

    def on_buttonDefautTimeBeforeSequence_clicked(self,widget,data=None):
        """adjustmentTimeBeforeSequence = self.builder.get_object("adjustmentTimeBeforeSequence")
        exercice = Exercise()
        adjustmentTimeBeforeSequence.set_value(exercice.getPlayMarginBefore())"""
        print "TODO"

    def on_buttonDefautTimeAfterSequence_clicked(self,widget,data=None):
        """adjustmentTimeAfterSequence = self.builder.get_object("adjustmentTimeAfterSequence")
        exercice = Exercise()
        adjustmentTimeAfterSequence.set_value(exercice.getPlayMarginAfter())"""
        print "TODO"





