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
from languages_manager import LanguagesManager
from exercise import Exercise
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
        print "TODO"
        """checkbuttonRepeatAfterComplete = self.builder.get_object("checkbuttonRepeatAfterComplete")
        checkbuttonRepeatAfterComplete.set_active(self.core.GetExercise().GetRepeatAfterCompleted())

        checkbuttonRandomOrder = self.builder.get_object("checkbuttonRandomOrder")
        checkbuttonRandomOrder.set_active(self.core.GetExercise().isRandomOrder())

        self.liststoreLanguage = gtk.ListStore(str,str)

        languageManager = LanguagesManager()
        languagesList =languageManager.getLanguagesList()

        currentLangId = self.core.GetExercise().getLanguageId()

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

        adjustmentTimeBetweenSequence = self.builder.get_object("adjustmentTimeBetweenSequence")
        adjustmentTimeBetweenSequence.set_value(self.core.GetExercise().GetTimeBetweenSequence())

        adjustmentMaximumSequenceTime = self.builder.get_object("adjustmentMaximumSequenceTime")
        adjustmentMaximumSequenceTime.set_value(self.core.GetExercise().GetMaxSequenceLength())

        adjustmentTimeBeforeSequence = self.builder.get_object("adjustmentTimeBeforeSequence")
        adjustmentTimeBeforeSequence.set_value(self.core.GetExercise().getPlayMarginBefore())

        adjustmentTimeAfterSequence = self.builder.get_object("adjustmentTimeAfterSequence")
        adjustmentTimeAfterSequence.set_value(self.core.GetExercise().getPlayMarginAfter())



        """


    def on_buttonExercisePropOk_clicked(self,widget,data=None):


        """checkbuttonRepeatAfterComplete = self.builder.get_object("checkbuttonRepeatAfterComplete")
        self.core.GetExercise().SetRepeatAfterCompleted(checkbuttonRepeatAfterComplete.get_active())

        checkbuttonRandomOrder = self.builder.get_object("checkbuttonRandomOrder")
        self.core.GetExercise().setRandomOrder(checkbuttonRandomOrder.get_active())

        comboboxLanguage = self.builder.get_object("comboboxLanguage")
        self.liststoreLanguage.get_iter_first()
        iter = comboboxLanguage.get_active_iter()
        langId = self.liststoreLanguage.get_value(iter,1)

        self.core.GetExercise().setLanguageId(langId)

        adjustmentTimeBetweenSequence = self.builder.get_object("adjustmentTimeBetweenSequence")
        self.core.GetExercise().SetTimeBetweenSequence(adjustmentTimeBetweenSequence.get_value())

        adjustmentMaximumSequenceTime = self.builder.get_object("adjustmentMaximumSequenceTime")
        self.core.GetExercise().SetMaxSequenceLength(adjustmentMaximumSequenceTime.get_value())

        adjustmentTimeBeforeSequence = self.builder.get_object("adjustmentTimeBeforeSequence")
        self.core.GetExercise().setPlayMarginBefore(int(adjustmentTimeBeforeSequence.get_value()))

        adjustmentTimeAfterSequence = self.builder.get_object("adjustmentTimeAfterSequence")
        self.core.GetExercise().setPlayMarginAfter(int(adjustmentTimeAfterSequence.get_value()))
        """
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





