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
import os
import gettext

from perroquetlib.config import config
from perroquetlib.model.languages_manager import LanguagesManager
from perroquetlib.model.exercise import Exercise
from perroquetlib.model.sub_exercise import SubExercise

_ = gettext.gettext

class GuiSequencePropertiesAdvanced:
    def __init__(self, core, parent):

        self.core = core
        self.config = config
        self.parent = parent

        self.builder = gtk.Builder()
        self.builder.set_translation_domain("perroquet")
        self.builder.add_from_file(self.config.get("ui_sequence_properties_advanced_path"))
        self.builder.connect_signals(self)
        self.dialog = self.builder.get_object("dialogExercisePropertiesAdvanced")
        self.treeviewPathsList = self.builder.get_object("treeviewPathsList")
        self.dialog.set_modal(True)
        self.dialog.set_transient_for(self.parent)

        self.iterPath = None


    def run(self):
        self.load()
        self.dialog.run()
        self.dialog.destroy()

    def load(self):


        exercise = self.core.get_exercise()

        if len(exercise.subExercisesList) > 0:
            self.__load_path(exercise.subExercisesList[0].get_video_path(), exercise.subExercisesList[0].get_exercise_path(), exercise.subExercisesList[0].get_translation_path())
        else:
            self._Load("","","")

        self.pathListStore = gtk.ListStore(str,str,str,str)

        for subExercise in exercise.subExercisesList:
            name = os.path.basename(subExercise.get_video_path())
            self.pathListStore.append([name, subExercise.get_video_path(), subExercise.get_exercise_path(), subExercise.get_translation_path()])

        cell = gtk.CellRendererText()
        treeviewcolumnPath = gtk.TreeViewColumn(_("Path"))
        treeviewcolumnPath.pack_start(cell, True)
        treeviewcolumnPath.add_attribute(cell, 'markup', 0)
        treeviewcolumnPath.set_expand(True)

        columns = self.treeviewPathsList.get_columns()

        for column in columns:
            self.treeviewPathsList.remove_column(column)

        self.treeviewPathsList.append_column(treeviewcolumnPath)
        self.treeviewPathsList.set_model(self.pathListStore)
        self.treeviewSelectionPathsList = self.treeviewPathsList.get_selection()
        self.iterPath = self.pathListStore.get_iter_first()
        self.treeviewSelectionPathsList.select_iter(self.iterPath)

        checkbuttonRepeatAfterComplete = self.builder.get_object("checkbuttonRepeatAfterComplete")
        checkbuttonRepeatAfterComplete.set_active(self.core.get_exercise().get_repeat_after_completed())

        checkbuttonUseDynamicCorrection = self.builder.get_object("checkbuttonUseDynamicCorrection")
        checkbuttonUseDynamicCorrection.set_active(self.core.get_exercise().is_use_dynamic_correction())


        checkbuttonRandomOrder = self.builder.get_object("checkbuttonRandomOrder")
        checkbuttonRandomOrder.set_active(self.core.get_exercise().is_random_order())




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

        adjustmentTimeBetweenSequence = self.builder.get_object("adjustmentTimeBetweenSequence")
        adjustmentTimeBetweenSequence.set_value(self.core.get_exercise().get_time_between_sequence())

        adjustmentMaximumSequenceTime = self.builder.get_object("adjustmentMaximumSequenceTime")
        adjustmentMaximumSequenceTime.set_value(self.core.get_exercise().get_max_sequence_length())

        adjustmentTimeBeforeSequence = self.builder.get_object("adjustmentTimeBeforeSequence")
        adjustmentTimeBeforeSequence.set_value(self.core.get_exercise().get_play_margin_before())

        adjustmentTimeAfterSequence = self.builder.get_object("adjustmentTimeAfterSequence")
        adjustmentTimeAfterSequence.set_value(self.core.get_exercise().get_play_margin_after())

        entryExerciseName = self.builder.get_object("entryExerciseName")
        if self.core.get_exercise().get_name():
            entryExerciseName.set_text(self.core.get_exercise().get_name())
        else:
            entryExerciseName.set_text("")


        entryRepeatCountLimit = self.builder.get_object("entryRepeatCountLimit")
        entryRepeatCountLimit.set_text(str(self.core.get_exercise().get_repeat_count_limit_by_sequence()))

        #Locks
        checkbutton_lock_properties = self.builder.get_object("checkbutton_lock_properties")
        checkbutton_lock_properties.set_active(self.core.get_exercise().is_lock_properties())

        checkbutton_lock_correction = self.builder.get_object("checkbutton_lock_correction")
        checkbutton_lock_correction.set_active(self.core.get_exercise().is_lock_correction())
        self._update_path_buttons()

    def __load_path(self, videoPath, exercisePath, translationPath):

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

        if videoPath and os.path.isfile(videoPath):
            filePath = os.path.dirname(videoPath)
            if not exercisePath or not os.path.isfile(exercisePath):
                exerciseChooser.set_current_folder(filePath)
            if not translationPath or not os.path.isfile(translationPath):
                translationChooser.set_current_folder(filePath)


    def on_treeview_paths_list_cursor_changed(self,widget,data=None):
        (modele, iter) =  self.treeviewSelectionPathsList.get_selected()

        self.__store_path_changes()

        self.iterPath = iter
        self._update_path_buttons()
        if iter == None:
            return

        videoPath, exercisePath, translationPath = modele.get(iter, 1, 2, 3)

        self.__load_path(videoPath,exercisePath,translationPath)

    def _update_path_buttons(self):
        if self.iterPath == None:
            buttonRemovePath = self.builder.get_object("buttonRemovePath")
            buttonRemovePath.set_sensitive(False)
            buttonUpPath = self.builder.get_object("buttonUpPath")
            buttonUpPath.set_sensitive(False)
            buttonDownPath = self.builder.get_object("buttonDownPath")
            buttonDownPath.set_sensitive(False)
        else:
            buttonRemovePath = self.builder.get_object("buttonRemovePath")
            buttonRemovePath.set_sensitive(True)


            buttonUpPath = self.builder.get_object("buttonUpPath")
            if self.previous_iter(self.pathListStore,self.iterPath) == None:
                buttonUpPath.set_sensitive(False)
            else:
                buttonUpPath.set_sensitive(True)

            buttonDownPath = self.builder.get_object("buttonDownPath")
            if self.pathListStore.iter_next(self.iterPath) == None:
                buttonDownPath.set_sensitive(False)
            else:
                buttonDownPath.set_sensitive(True)


    def on_button_exercise_prop_ok_clicked(self,widget,data=None):
        self.__store_path_changes()

        checkbuttonRepeatAfterComplete = self.builder.get_object("checkbuttonRepeatAfterComplete")
        self.core.get_exercise().set_repeat_after_completed(checkbuttonRepeatAfterComplete.get_active())

        checkbuttonUseDynamicCorrection = self.builder.get_object("checkbuttonUseDynamicCorrection")
        self.core.get_exercise().set_use_dynamic_correction(checkbuttonUseDynamicCorrection.get_active())


        checkbuttonRandomOrder = self.builder.get_object("checkbuttonRandomOrder")
        self.core.get_exercise().set_random_order(checkbuttonRandomOrder.get_active())

        comboboxLanguage = self.builder.get_object("comboboxLanguage")
        self.liststoreLanguage.get_iter_first()
        iter = comboboxLanguage.get_active_iter()
        langId = self.liststoreLanguage.get_value(iter,1)

        self.core.get_exercise().set_language_id(langId)

        adjustmentTimeBetweenSequence = self.builder.get_object("adjustmentTimeBetweenSequence")
        self.core.get_exercise().set_time_between_sequence(adjustmentTimeBetweenSequence.get_value())

        adjustmentMaximumSequenceTime = self.builder.get_object("adjustmentMaximumSequenceTime")
        self.core.get_exercise().set_max_sequence_length(adjustmentMaximumSequenceTime.get_value())

        adjustmentTimeBeforeSequence = self.builder.get_object("adjustmentTimeBeforeSequence")
        self.core.get_exercise().set_play_margin_before(int(adjustmentTimeBeforeSequence.get_value()))

        adjustmentTimeAfterSequence = self.builder.get_object("adjustmentTimeAfterSequence")
        self.core.get_exercise().set_play_margin_after(int(adjustmentTimeAfterSequence.get_value()))

        entryExerciseName = self.builder.get_object("entryExerciseName")
        self.core.get_exercise().set_name(entryExerciseName.get_text())

        entryRepeatCountLimit = self.builder.get_object("entryRepeatCountLimit")
        self.core.get_exercise().set_repeat_count_limit_by_sequence(int(entryRepeatCountLimit.get_text()))
        entryRepeatCountLimit.set_text(str(self.core.get_exercise().get_repeat_count_limit_by_sequence()))

        if self.core.get_exercise().get_repeat_count_limit_by_sequence() == 0:
            self.core.get_exercise().clear_sequence_repeat_count()

        #Locks
        checkbutton_lock_properties = self.builder.get_object("checkbutton_lock_properties")
        lock_properties = checkbutton_lock_properties.get_active()
        entry_lock_properties = self.builder.get_object("entry_lock_properties")
        lock_properties_password =  entry_lock_properties.get_text()
        if len(lock_properties_password) == 0:
            lock_properties_password = None

        if lock_properties != self.core.get_exercise().is_lock_properties() or lock_properties_password is not None:
            self.core.get_exercise().set_lock_properties(lock_properties, lock_properties_password)


        checkbutton_lock_correction = self.builder.get_object("checkbutton_lock_correction")
        lock_correction = checkbutton_lock_correction.get_active()
        entry_lock_correction = self.builder.get_object("entry_lock_correction")
        lock_correction_password =  entry_lock_correction.get_text()
        if len(lock_correction_password) == 0:
            lock_correction_password = None

        if lock_correction != self.core.get_exercise().is_lock_correction() or lock_correction_password is not None:
            self.core.get_exercise().set_lock_correction(lock_correction, lock_correction_password)
      
        # Update paths
        if len(self.pathListStore) != len(self.core.get_exercise().subExercisesList):
            self.core.get_exercise().subExercisesList = []
            for subPath in self.pathListStore:
                self.core.get_exercise().subExercisesList.append(SubExercise(self.core.get_exercise()))

        for i,subPath in enumerate(self.pathListStore):
            self.core.get_exercise().subExercisesList[i].set_video_path(subPath[1])
            self.core.get_exercise().subExercisesList[i].set_exercise_path(subPath[2])
            self.core.get_exercise().subExercisesList[i].set_translation_path(subPath[3])

        self.core.update_properties()
        self.core.set_can_save(True)

        self.dialog.response(gtk.RESPONSE_OK)

    def on_button_exercise_prop_cancel_clicked(self,widget,data=None):
        self.dialog.response(gtk.RESPONSE_CANCEL)

    def __store_path_changes(self):

        if self.iterPath == None:
            return

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

        if self.iterPath == None:
            return

        self.iterPath

        self.pathListStore.set_value(self.iterPath,0, os.path.basename(videoPath))
        self.pathListStore.set_value(self.iterPath,1, videoPath)
        self.pathListStore.set_value(self.iterPath,2, exercisePath)
        self.pathListStore.set_value(self.iterPath,3, translationPath)

    def on_filechooserbutton_video_prop_file_set(self,widget,data=None):
        videoChooser = self.builder.get_object("filechooserbuttonVideoProp")
        exerciseChooser = self.builder.get_object("filechooserbuttonExerciseProp")
        translationChooser = self.builder.get_object("filechooserbuttonTranslationProp")

        fileName = videoChooser.get_filename()
        if fileName and os.path.isfile(fileName):
            filePath = os.path.dirname(fileName)
            if not exerciseChooser.get_filename() or not os.path.isfile(exerciseChooser.get_filename()):
                exerciseChooser.set_current_folder(filePath)
            if not translationChooser.get_filename() or not os.path.isfile(translationChooser.get_filename()):
                translationChooser.set_current_folder(filePath)

    def previous_iter(self, model, iter):
        if not iter:
            return None
        path = model.get_string_from_iter(iter)
        if not path:
            return None
        prow = int(path) - 1
        if prow == -1:
            return None
        prev = model.get_iter_from_string("%d" % prow)
        return prev

    def on_button_down_path_clicked(self,widget,data=None):
        self.pathListStore.move_after(self.iterPath, self.pathListStore.iter_next(self.iterPath))
        self._update_path_buttons()


    def on_button_up_path_clicked(self,widget,data=None):
        self.pathListStore.move_before(self.iterPath, self.previous_iter(self.pathListStore, self.iterPath))
        self._update_path_buttons()

    def on_button_add_path_clicked(self,widget,data=None):
        self.__store_path_changes()
        iter = self.pathListStore.insert_after(self.iterPath, [self.pathListStore.get_value(self.iterPath,0), self.pathListStore.get_value(self.iterPath,1), self.pathListStore.get_value(self.iterPath,2), self.pathListStore.get_value(self.iterPath,3) ])
        self.iterPath = None
        self.treeviewSelectionPathsList.select_iter(iter)

    def on_button_remove_path_clicked(self,widget,data=None):
        self.pathListStore.remove(self.iterPath)
        self.iterPath = None
        self._update_path_buttons()


    def on_button_defaut_time_between_sequences_clicked(self,widget,data=None):
        adjustmentTimeBetweenSequence = self.builder.get_object("adjustmentTimeBetweenSequence")
        exercice = Exercise()
        adjustmentTimeBetweenSequence.set_value(exercice.get_time_between_sequence())

    def on_button_defaut_maximum_sequence_time_clicked(self,widget,data=None):
        adjustmentMaximumSequenceTime = self.builder.get_object("adjustmentMaximumSequenceTime")
        exercice = Exercise()
        adjustmentMaximumSequenceTime.set_value(exercice.get_max_sequence_length())

    def on_button_defaut_time_before_sequence_clicked(self,widget,data=None):
        adjustmentTimeBeforeSequence = self.builder.get_object("adjustmentTimeBeforeSequence")
        exercice = Exercise()
        adjustmentTimeBeforeSequence.set_value(exercice.get_play_margin_before())

    def on_button_defaut_time_after_sequence_clicked(self,widget,data=None):
        adjustmentTimeAfterSequence = self.builder.get_object("adjustmentTimeAfterSequence")
        exercice = Exercise()
        adjustmentTimeAfterSequence.set_value(exercice.get_play_margin_after())





