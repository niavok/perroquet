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
from perroquetlib.model.languages_manager import LanguagesManager
_ = gettext.gettext

class GuiSequenceProperties:
    def __init__(self, core, parent):

        self.core = core
        self.config = config
        self.parent = parent

        self.builder = gtk.Builder()
        self.builder.set_translation_domain("perroquet")
        self.builder.add_from_file(self.config.get("ui_sequence_properties_path"))
        self.builder.connect_signals(self)
        self.dialog = self.builder.get_object("dialogExerciseProperties")

        self.pagePaths = self.builder.get_object("pagePaths")
        self.pageSequences = self.builder.get_object("pageSequences")

        self.dialog.set_modal(True)
        self.dialog.set_transient_for(self.parent)



    def run(self):
        self.load()
        self.dialog.run()
        self.dialog.destroy()

    def load(self):
        (videoPath,exercisePath,translationPath)  = self.core.get_paths()

        if videoPath == "":
            videoPath = "None"

        if exercisePath == "":
            exercisePath = "None"

        if translationPath == "":
            translationPath = "None"



        videoChooser = self.builder.get_object("filechooserbuttonVideoProp")
        exerciseChooser = self.builder.get_object("filechooserbuttonExerciseProp")
        translationChooser = self.builder.get_object("filechooserbuttonTranslationProp")
        videoChooser.set_filename(videoPath)
        exerciseChooser.set_filename(exercisePath)
        translationChooser.set_filename(translationPath)

        checkbuttonRepeatAfterComplete = self.builder.get_object("checkbuttonRepeatAfterComplete")
        checkbuttonRepeatAfterComplete.set_active(self.core.get_exercise().get_repeat_after_completed())

        self.liststoreLanguage = gtk.ListStore(str,str)

        languageManager = LanguagesManager()
        languagesList =languageManager.get_languages_list()

        currentLangId = self.core.get_exercise().get_language_id()

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



    def on_button_exercise_prop_ok_clicked(self,widget,data=None):
        dialogExerciseProperties = self.builder.get_object("dialogExerciseProperties")

        videoChooser = self.builder.get_object("filechooserbuttonVideoProp")
        videoPath = videoChooser.get_filename()
        exerciseChooser = self.builder.get_object("filechooserbuttonExerciseProp")
        exercisePath = exerciseChooser.get_filename()
        translationChooser = self.builder.get_object("filechooserbuttonTranslationProp")
        translationPath = translationChooser.get_filename()
        if videoPath == "None" or videoPath == None:
            videoPath = ""
        if exercisePath == "None" or exercisePath == None:
            exercisePath = ""
        if translationPath == "None" or translationPath == None:
            translationPath = ""


        checkbuttonRepeatAfterComplete = self.builder.get_object("checkbuttonRepeatAfterComplete")
        self.core.get_exercise().set_repeat_after_completed(checkbuttonRepeatAfterComplete.get_active())

        comboboxLanguage = self.builder.get_object("comboboxLanguage")
        self.liststoreLanguage.get_iter_first()
        iter = comboboxLanguage.get_active_iter()
        langId = self.liststoreLanguage.get_value(iter,1)

        self.core.get_exercise().set_language_id(langId)


        self.core.UpdatePaths(videoPath,exercisePath, translationPath)

        self.core.set_can_save(True)

        self.dialog.response(gtk.RESPONSE_OK)

    def on_button_exercise_prop_cancel_clicked(self,widget,data=None):
        self.dialog.response(gtk.RESPONSE_CANCEL)

