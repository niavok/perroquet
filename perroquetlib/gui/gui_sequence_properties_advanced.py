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
from perroquetlib.exercise import Exercise
_ = gettext.gettext

class GuiSequencePropertiesAdvanced:
    def __init__(self, core, parent):

        self.core = core
        self.config = config
        self.parent = parent

        self.builder = gtk.Builder()
        self.builder.set_translation_domain("perroquet")
        self.builder.add_from_file(self.config.Get("ui_sequence_properties_advanced_path"))
        self.builder.connect_signals(self)
        self.dialog = self.builder.get_object("dialogExercisePropertiesAdvanced")
        self.treeviewPathsList = self.builder.get_object("treeviewPathsList")
        self.dialog.set_modal(True)
        self.dialog.set_transient_for(self.parent)

        self.iterPath = None


    def Run(self):
        self.Load()
        self.dialog.run()
        self.dialog.destroy()

    def Load(self):


        exercise = self.core.GetExercise()

        if len(exercise.subExercisesList) > 0:
            self._LoadPath(exercise.subExercisesList[0].GetVideoPath(), exercise.subExercisesList[0].GetExercisePath(), exercise.subExercisesList[0].GetTranslationPath())
        else:
            self._Load("","","")

        self.pathListStore = gtk.ListStore(str,str,str,str)

        for subExercise in exercise.subExercisesList:
            name = os.path.basename(subExercise.GetVideoPath())
            self.pathListStore.append([name, subExercise.GetVideoPath(), subExercise.GetExercisePath(), subExercise.GetTranslationPath()])

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

        entryExerciseName = self.builder.get_object("entryExerciseName")
        if self.core.GetExercise().getName():
            entryExerciseName.set_text(self.core.GetExercise().getName())
        else:
            entryExerciseName.set_text("")


        self._updatePathButtons()

    def _LoadPath(self, videoPath, exercisePath, translationPath):

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


    def on_treeviewPathsList_cursor_changed(self,widget,data=None):
        (modele, iter) =  self.treeviewSelectionPathsList.get_selected()

        self._StorePathChanges()

        self.iterPath = iter
        self._updatePathButtons()
        if iter == None:
            return

        videoPath, exercisePath, translationPath = modele.get(iter, 1, 2, 3)

        self._LoadPath(videoPath,exercisePath,translationPath)

    def _updatePathButtons(self):
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


    def on_buttonExercisePropOk_clicked(self,widget,data=None):
        dialogExerciseProperties = self.builder.get_object("dialogExercisePropertiesAdvanced")

        self._StorePathChanges()

        checkbuttonRepeatAfterComplete = self.builder.get_object("checkbuttonRepeatAfterComplete")
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

        entryExerciseName = self.builder.get_object("entryExerciseName")
        self.core.GetExercise().setName(entryExerciseName.get_text())



        # Update paths
        if len(self.pathListStore) != len(self.core.GetExercise().subExercisesList):
            self.core.GetExercise().subExercisesList = []
            for subPath in self.pathListStore:
                self.core.GetExercise().subExercisesList.append(SubExercise(self.exercise))

        for i,subPath in enumerate(self.pathListStore):
            self.core.GetExercise().subExercisesList[i].SetVideoPath(subPath[1])
            self.core.GetExercise().subExercisesList[i].SetExercisePath(subPath[2])
            self.core.GetExercise().subExercisesList[i].SetTranslationPath(subPath[3])

        self.core.UpdateProperties()
        self.core.SetCanSave(True)

        self.dialog.response(gtk.RESPONSE_OK)

    def on_buttonExercisePropCancel_clicked(self,widget,data=None):
        self.dialog.response(gtk.RESPONSE_CANCEL)

    def _StorePathChanges(self):

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

    def on_filechooserbuttonVideoProp_file_set(self,widget,data=None):
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

    def on_buttonDownPath_clicked(self,widget,data=None):
        self.pathListStore.move_after(self.iterPath, self.pathListStore.iter_next(self.iterPath))
        self._updatePathButtons()


    def on_buttonUpPath_clicked(self,widget,data=None):
        self.pathListStore.move_before(self.iterPath, self.previous_iter(self.pathListStore, self.iterPath))
        self._updatePathButtons()

    def on_buttonAddPath_clicked(self,widget,data=None):
        self._StorePathChanges()
        iter = self.pathListStore.insert_after(self.iterPath, [self.pathListStore.get_value(self.iterPath,0), self.pathListStore.get_value(self.iterPath,1), self.pathListStore.get_value(self.iterPath,2), self.pathListStore.get_value(self.iterPath,3) ])
        self.iterPath = None
        self.treeviewSelectionPathsList.select_iter(iter)

    def on_buttonRemovePath_clicked(self,widget,data=None):
        self.pathListStore.remove(self.iterPath)
        self.iterPath = None
        self._updatePathButtons()


    def on_buttonDefautTimeBetweenSequences_clicked(self,widget,data=None):
        adjustmentTimeBetweenSequence = self.builder.get_object("adjustmentTimeBetweenSequence")
        exercice = Exercise()
        adjustmentTimeBetweenSequence.set_value(exercice.GetTimeBetweenSequence())

    def on_buttonDefautMaximumSequenceTime_clicked(self,widget,data=None):
        adjustmentMaximumSequenceTime = self.builder.get_object("adjustmentMaximumSequenceTime")
        exercice = Exercise()
        adjustmentMaximumSequenceTime.set_value(exercice.GetMaxSequenceLength())

    def on_buttonDefautTimeBeforeSequence_clicked(self,widget,data=None):
        adjustmentTimeBeforeSequence = self.builder.get_object("adjustmentTimeBeforeSequence")
        exercice = Exercise()
        adjustmentTimeBeforeSequence.set_value(exercice.getPlayMarginBefore())

    def on_buttonDefautTimeAfterSequence_clicked(self,widget,data=None):
        adjustmentTimeAfterSequence = self.builder.get_object("adjustmentTimeAfterSequence")
        exercice = Exercise()
        adjustmentTimeAfterSequence.set_value(exercice.getPlayMarginAfter())





