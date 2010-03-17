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


import gtk, time, urllib, re, os, gettext
import locale

from perroquetlib.config import config
from perroquetlib.languages_manager import LanguagesManager
from perroquetlib.structure import Word

from gui_sequence_properties import GuiSequenceProperties
from gui_sequence_properties_advanced import GuiSequencePropertiesAdvanced
from gui_reset_exercise import GuiResetExercise
from gui_settings import GuiSettings
from gui_exercise_manager import GuiExerciseManager

_ = gettext.gettext

class Gui:
    def __init__(self):
        self.config = config

        locale.bindtextdomain(self.config.Get("gettext_package"),self.config.Get("localedir"))


        self.builder = gtk.Builder()
        self.builder.set_translation_domain("perroquet")
        self.builder.add_from_file(self.config.Get("ui_path"))
        self.builder.connect_signals(self)
        self.window = self.builder.get_object("MainWindow")
        self.window.set_icon_from_file(self.config.Get("logo_path"))

        self.aboutDialog = self.builder.get_object("aboutdialog")
        icon = gtk.gdk.pixbuf_new_from_file(self.config.Get("logo_path"))
        self.aboutDialog.set_logo(icon)
        self.aboutDialog.set_version(self.config.Get("version"))

        # Sound icon
        print config.Get("audio_icon")
        self.builder.get_object("imageAudio").set_from_file(config.Get("audio_icon"))

        self.typeLabel = self.builder.get_object("typeView")

        self.initTypeLabel()

        self.translationVisible = False
        self.disableChangedTextEvent = False
        self.mode = "closed"

        self.activateVideo(False)

        if not self.config.Get("showlateralpanel"):
            self.builder.get_object("vbox2").hide()
        else:
            #ugly but needed (?)
            self.builder.get_object("checkmenuitemLateralPanel").set_active(True)
            self.builder.get_object("vbox2").show()
            self.config.Set("showlateralpanel", 1)

        self._updateLastOpenFilesTab()

    def SignalExerciseBadPath(self, path):
        dialog = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL,
                                   gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                   _("The file '%s' doesn't exist. Please modify exercise paths") % path)
        dialog.set_title(_("Load error"))

        response = dialog.run()
        dialog.destroy()

    def SetCore(self, core):
        self.core = core

    def GetVideoWindowId(self):
        return self.builder.get_object("videoArea").window.xid

    def activateVideo(self,state):
        if state:
            self.builder.get_object("videoArea").show()
            self.builder.get_object("imageAudio").hide()
        else:
            self.builder.get_object("videoArea").hide()
            self.builder.get_object("imageAudio").show()


    def SetSpeed(self, speed):
        self.settedSpeed = int(speed*100)
        ajustement = self.builder.get_object("adjustmentSpeed")
        ajustement.configure (self.settedSpeed, 75, 100, 1, 10, 0)

    def SetSequenceNumber(self, sequenceNumber, sequenceCount):
        ajustement = self.builder.get_object("adjustmentSequenceNum")
        sequenceNumber = sequenceNumber + 1
        self.settedSeq = sequenceNumber
        ajustement.configure (sequenceNumber, 1, sequenceCount, 1, 10, 0)
        self.builder.get_object("labelSequenceNumber").set_text(str(sequenceNumber) + "/" + str(sequenceCount))

        toolbuttonNextSequence = self.builder.get_object("toolbuttonNextSequence")
        toolbuttonPreviousSequence = self.builder.get_object("toolbuttonPreviousSequence")
        if sequenceNumber == 1:
            toolbuttonPreviousSequence.set_sensitive(False)
        else:
            toolbuttonPreviousSequence.set_sensitive(True)

        if sequenceNumber == sequenceCount :
            toolbuttonNextSequence.set_sensitive(False)
        else:
            toolbuttonNextSequence.set_sensitive(True)

    def SetSequenceTime(self, sequencePos, sequenceTime):
        if sequencePos > sequenceTime:
            sequencePos = sequenceTime
        if sequencePos < 0:
            sequencePos = 0
        self.settedPos = sequencePos /100
        ajustement = self.builder.get_object("adjustmentSequenceTime")
        ajustement.configure (self.settedPos, 0, sequenceTime/100, 1, 10, 0)
        textTime = round(float(sequencePos)/1000,1)
        textDuration = round(float(sequenceTime)/1000,1)
        self.builder.get_object("labelSequenceTime").set_text(str(textTime) + "/" + str(textDuration) + " s")

    def SetPlaying(self, state):
        self.builder.get_object("toolbuttonPlay").set_sensitive(not state)
        self.builder.get_object("toolbuttonPause").set_sensitive(state)

    def SetCanSave(self, state):
        self.builder.get_object("saveButton").set_sensitive(state)
        self.builder.get_object("imagemenuitemSave").set_sensitive(state)

    def SetWordList(self, wordList):
        self.wordList = wordList
        self.UpdateWordList()

    def UpdateWordList(self):
        buffer = self.builder.get_object("textviewWordList").get_buffer()
        entry = self.builder.get_object("entryFilter")

        iter1 = buffer.get_start_iter()
        iter2 = buffer.get_end_iter()
        buffer.delete(iter1, iter2)


        formattedWordList = ""

        regexp = entry.get_text()

        try:
            re.search(regexp,"")
        except re.error:
            regexp = ""
            pass

        for word in self.wordList:
            if re.search(regexp,word):
                formattedWordList = formattedWordList + word + "\n"

        iter = buffer.get_end_iter()
        buffer.insert(iter,formattedWordList)

    def SetTranslation(self, translation):
        textviewTranslation = self.builder.get_object("textviewTranslation").get_buffer()
        textviewTranslation.set_text(translation)

    def SetStats(self, sequenceCount,sequenceFound, wordCount, wordFound, repeatRate):
        labelProgress = self.builder.get_object("labelProgress")
        text = ""
        text = text + _("- Sequences: %(found)s/%(count)s (%(percent)s %%)\n") % {'found' : str(sequenceFound), 'count' : str(sequenceCount), 'percent' : str(round(100*sequenceFound/sequenceCount,1)) }
        text = text + _("- Words: %(found)s/%(count)s (%(percent)s %%)\n") % {'found' : str(wordFound), 'count' : str(wordCount), 'percent' : str(round(100*wordFound/wordCount,1))}
        text = text + _("- Repeat ratio: %s per words") % str(round(repeatRate,1))
        labelProgress.set_label(text)

    def SetTitle(self, title, save):

        newTitle = _("Perroquet")

        if save:
            newTitle += " *"

        if title != "":
            newTitle += " - " + title

        self.window.set_title(newTitle)

    def SetSequence(self, sequence):
        self.disableChangedTextEvent = True
        self.ClearBuffer()
        pos = 1
        cursor_pos = 0

        text = ""
        buffer = self.typeLabel.get_buffer()
        self.AddSymbol(" ")


        for i, symbol in enumerate(sequence.getSymbols()):
            pos += len(symbol)
            self.AddSymbol(symbol)
            if i < len(sequence.getWords()):
                if sequence.getActiveWordIndex() == i:
                    cursor_pos = pos
                if sequence.getWords()[i].isEmpty():
                    self.UpdateWord(" ", 0, isEmpty=True)
                    pos += 1
                elif sequence.getWords()[i].isValid():
                    self.UpdateWord(sequence.getWords()[i].getValid(lower=False), 0, isFound=True)
                    pos += len(sequence.getWords()[i].getText())
                else:
                    self.UpdateWord(sequence.getWords()[i].getText(), sequence.getWords()[i].getScore())
                    pos += len(sequence.getWords()[i].getText())

        self.wordIndexMap.append(self.currentWordIndex)
        self.wordPosMap.append(self.currentPosIndex)

        self.window.set_focus(self.typeLabel)
        newCurPos = cursor_pos + sequence.getActiveWord().getPos()
        iter = buffer.get_iter_at_offset(newCurPos)
        buffer.place_cursor(iter)
        self.disableChangedTextEvent = False
        self.sequenceText = buffer.get_text(buffer.get_start_iter(),buffer.get_end_iter())

    def ClearBuffer(self):
        buffer = self.typeLabel.get_buffer()
        iter1 = buffer.get_start_iter()
        iter2 = buffer.get_end_iter()
        buffer.delete(iter1, iter2)

        self.currentIndex = 0
        self.currentWordIndex = -1
        self.currentPosIndex = 0
        self.wordIndexMap = []
        self.wordPosMap = []

    def AddSymbol(self, symbol):
        if len(symbol) == 0:
            return
        buffer = self.typeLabel.get_buffer()
        size = buffer.get_char_count()
        iter1 = buffer.get_end_iter()
        buffer.insert(iter1,symbol)
        iter1 = buffer.get_iter_at_offset(size)
        iter2 = buffer.get_end_iter()
        buffer.apply_tag_by_name("symbol", iter1, iter2)

        for i in range(self.currentIndex, self.currentIndex + len(symbol)):
            self.wordIndexMap.append(self.currentWordIndex)
            self.wordPosMap.append(self.currentPosIndex)
        self.currentIndex += len(symbol)

    def UpdateWord(self, word, score, isFound=False, isEmpty=False):
        buffer = self.typeLabel.get_buffer()
        iter1 = buffer.get_end_iter()
        size = buffer.get_char_count()
        buffer.insert(iter1,word)
        iter1 = buffer.get_iter_at_offset(size)
        iter2 = buffer.get_end_iter()

        score250 = int(score*250) #score between -250 and 250
        if isEmpty:
            tagName = "word_empty"
        elif isFound:
            tagName = "word_found"
        elif score > 0 :
            tagName = "word_near"+str(score250)
        else:
            tagName = "word_to_found"+str(score250)

        buffer.apply_tag_by_name(tagName, iter1, iter2)
        self.currentWordIndex += 1
        self.currentPosIndex = 0

        for i in range(self.currentIndex, self.currentIndex + len(word)):
            self.wordIndexMap.append(self.currentWordIndex)
            self.wordPosMap.append(self.currentPosIndex)
            self.currentPosIndex += 1
        self.currentIndex += len(word)

    def initTypeLabel(self):
        """creates the labels used for the coloration of the text"""
        buffer = self.typeLabel.get_buffer()

        color_not_found = self.window.get_colormap().alloc_color(
            0*256,
            0*256,
            80*256)
        bcolor_not_found_bad = self.window.get_colormap().alloc_color(
            250*256,
            218*256,
            200*256)
        color_found = self.window.get_colormap().alloc_color(
            10*256,
            150*256,
            10*256)
        def get_bcolor_not_found(score250):
            return self.window.get_colormap().alloc_color(
                (150+score250*100/250)*256,
                (210-score250*210/250/2)*256,
                (250-score250/2)*256)
            (red, green, blue) = computeColorBetween(
                (150, 210, 250),
                (255, 100, 100),
                float(score250) /250.0)
            return self.window.get_colormap().alloc_color(red*256,green*256,blue*256)

        def get_bcolor_near(score250):
            (red, green, blue) = computeColorBetween(
                (150, 210, 250),
                (150, 255, 100),
                float(score250) /250.0)
            return self.window.get_colormap().alloc_color(red*256,green*256,blue*256)

        def computeColorBetween(colorFrom, colorTo, coeff):
            (redFrom, greenFrom, blueFrom)  =  colorFrom
            (redTo, greenTo, blueTo)  =  colorTo
            red = int((1-coeff)*redFrom + coeff*redTo)
            green = int((1-coeff)*greenFrom + coeff*greenTo)
            blue = int((1-coeff)*blueFrom + coeff*blueTo)
            return (red, green, blue)

        buffer.create_tag("symbol",
            size_points=18.0)
        buffer.create_tag("word_empty",
            background=get_bcolor_not_found(0),
            foreground=color_not_found,
            size_points=18.0)
        for score250 in xrange(251):
            buffer.create_tag("word_to_found"+str(-score250),
                background=get_bcolor_not_found(score250),
                foreground=color_not_found,
                size_points=18.0)
        buffer.create_tag("word_found",
            foreground=color_found,
            size_points=18.0)
        for score250 in xrange(251):
            buffer.create_tag("word_near"+str(score250),
                background=get_bcolor_near(score250),
                foreground=color_not_found,
                size_points=18.0)

    def AskSavePath(self):
        saver = SaveFileSelector(self.window)
        path =saver.run()
        if path == None:
            return

        if path == "None" or path == None :
            path = ""
        elif not path.endswith(".perroquet"):
            path = path +".perroquet"
        return path

    def AskExportAsTemplatePath(self):
        saver = ExportAsTemplateFileSelector(self.window)
        path =saver.run()
        if path == None:
            return

        if path == "None" or path == None :
            path = ""
        elif not path.endswith(".perroquet"):
            path = path +".perroquet"
        return path

    def AskExportAsPackagePath(self):
        saver = ExportAsPackageFileSelector(self.window)
        path =saver.run()
        if path == None:
            return

        if path == "None" or path == None :
            path = ""
        elif not path.endswith(".tar"):
            path = path +".tar"
        return path

    def AskProperties(self):
        dialogExerciseProperties = GuiSequenceProperties(self.core, self.window)
        dialogExerciseProperties.Run()

    def AskPropertiesAdvanced(self):
        dialogExerciseProperties = GuiSequencePropertiesAdvanced(self.core, self.window)
        dialogExerciseProperties.Run()

    def AskSettings(self):
        dialogSettings = GuiSettings(self.window)
        dialogSettings.Run()
        self.Refresh()

    def Activate(self, mode):
        self.mode = mode
        self.Refresh()

    def Refresh(self):

        if self.mode == "loaded":
            self.builder.get_object("hscaleSequenceNum").set_sensitive(True)
            self.builder.get_object("hscaleSequenceTime").set_sensitive(True)
            self.builder.get_object("toolbuttonHint").set_sensitive(True)
            self.builder.get_object("toolbuttonReplaySequence").set_sensitive(True)
            self.builder.get_object("toolbuttonProperties").set_sensitive(True)
            self.builder.get_object("toggletoolbuttonShowTranslation").set_sensitive(True)
            self.builder.get_object("imagemenuitemSaveAs").set_sensitive(True)
            self.builder.get_object("imagemenuitemSave").set_sensitive(True)
            self.builder.get_object("checkmenuitemTranslation").set_sensitive(True)
            self.builder.get_object("imagemenuitemHint").set_sensitive(True)
            #Disable speed change slider if the media player not support it
            if self.core.getPlayer().isSpeedChangeable():
                self.builder.get_object("hscaleSpeed").set_sensitive(True)
            else:
                self.builder.get_object("hscaleSpeed").set_sensitive(False)
            self.builder.get_object("imagemenuitemProperties").set_sensitive(True)
            self.builder.get_object("imagemenuitemAdvancedProperties").set_sensitive(True)
            self.builder.get_object("imagemenuitemExportAsTemplate").set_sensitive(True)


        if self.mode == "load_failed":
            self.builder.get_object("hscaleSequenceNum").set_sensitive(False)
            self.builder.get_object("hscaleSequenceTime").set_sensitive(False)
            self.builder.get_object("toolbuttonHint").set_sensitive(False)
            self.builder.get_object("toolbuttonReplaySequence").set_sensitive(False)
            self.builder.get_object("toolbuttonProperties").set_sensitive(True)
            self.builder.get_object("toggletoolbuttonShowTranslation").set_sensitive(False)
            self.builder.get_object("imagemenuitemSaveAs").set_sensitive(False)
            self.builder.get_object("imagemenuitemSave").set_sensitive(False)
            self.builder.get_object("checkmenuitemTranslation").set_sensitive(False)
            self.builder.get_object("imagemenuitemHint").set_sensitive(False)
            self.builder.get_object("hscaleSpeed").set_sensitive(False)
            self.builder.get_object("imagemenuitemProperties").set_sensitive(True)
            self.builder.get_object("imagemenuitemAdvancedProperties").set_sensitive(True)
            self.builder.get_object("imagemenuitemExportAsTemplate").set_sensitive(True)

        if self.mode == "closed":
            self.builder.get_object("hscaleSequenceNum").set_sensitive(False)
            self.builder.get_object("hscaleSequenceTime").set_sensitive(False)
            self.builder.get_object("toolbuttonHint").set_sensitive(False)
            self.builder.get_object("toolbuttonReplaySequence").set_sensitive(False)
            self.builder.get_object("toolbuttonProperties").set_sensitive(False)
            self.builder.get_object("toggletoolbuttonShowTranslation").set_sensitive(False)
            self.builder.get_object("imagemenuitemSaveAs").set_sensitive(False)
            self.builder.get_object("imagemenuitemSave").set_sensitive(False)
            self.builder.get_object("checkmenuitemTranslation").set_sensitive(False)
            self.builder.get_object("imagemenuitemHint").set_sensitive(False)
            self.builder.get_object("hscaleSpeed").set_sensitive(False)
            self.builder.get_object("imagemenuitemProperties").set_sensitive(False)
            self.builder.get_object("imagemenuitemAdvancedProperties").set_sensitive(False)
            self.builder.get_object("imagemenuitemExportAsTemplate").set_sensitive(False)

        if config.Get("interface_show_play_pause_buttons") == 1:
            self.builder.get_object("toolbuttonPlay").show()
            self.builder.get_object("toolbuttonPause").show()
        else:
            self.builder.get_object("toolbuttonPlay").hide()
            self.builder.get_object("toolbuttonPause").hide()

    def Run(self):
        gtk.gdk.threads_init()
        self.window.show()
        gtk.main()


    def _updateLastOpenFilesTab(self):
        print "updateLastOpenFilesTab"
        gtkTree = self.builder.get_object("lastopenfilesTreeView")

        if not gtkTree.get_columns() == []:
            raise Exception

        cell = gtk.CellRendererText()

        treeviewcolumnName = gtk.TreeViewColumn(_("Name"))

        treeViewColumn = gtk.TreeViewColumn(_("Path"))
        treeViewColumn.pack_start(cell, False)
        treeViewColumn.add_attribute(cell, 'markup', 0)
        treeViewColumn.set_expand(False)
        gtkTree.append_column(treeViewColumn)

        print gtkTree.get_columns()

        treeStore = gtk.TreeStore(str)
        for file in self.config.Get("lastopenfiles"):
            print file
            treeStore.append(None, [file])

        gtkTree.set_model(treeStore)

    #---------------------- Now the functions called directly by the gui--------

    def on_MainWindow_delete_event(self,widget,data=None):
        if not self.config.Get("autosave"):
            if not self.core.GetCanSave():
                gtk.main_quit()
                return False

            dialog = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL,
                                       gtk.MESSAGE_INFO, gtk.BUTTONS_YES_NO,
                                       _("Do you really quit without save ?"))
            dialog.set_title(_("Confirm quit"))

            response = dialog.run()
            dialog.destroy()
            if response == gtk.RESPONSE_YES:
                gtk.main_quit()
                self.config.Save()
                return False # returning False makes "destroy-event" be signalled
                             # for the window.
            else:
                return True # returning True avoids it to signal "destroy-event"
        else:
            self.core.Save()
            gtk.main_quit()
            self.config.Save()
            return True


    def on_newExerciseButton_clicked(self,widget,data=None):
        self.newExerciseDialog = self.builder.get_object("newExerciseDialog")

        videoChooser = self.builder.get_object("filechooserbuttonVideo")
        exerciseChooser = self.builder.get_object("filechooserbuttonExercise")
        translationChooser = self.builder.get_object("filechooserbuttonTranslation")
        videoChooser.set_filename("None")
        exerciseChooser.set_filename("None")
        translationChooser.set_filename("None")

        self.liststoreLanguage = gtk.ListStore(str,str)

        languageManager = LanguagesManager()
        languagesList =languageManager.getLanguagesList()

        for language in languagesList:
            (langId,langName,chars) = language
            iter = self.liststoreLanguage.append([langName,langId])
            if langId == config.Get("default_exercise_language"):
                currentIter = iter

        comboboxLanguage = self.builder.get_object("comboboxLanguage")

        #Clear old values
        comboboxLanguage.clear()

        """columns = comboboxLanguage.get_columns()
        for column in columns:
            comboboxLanguage.remove_column(column)"""

        cell = gtk.CellRendererText()
        comboboxLanguage.set_model(self.liststoreLanguage)
        comboboxLanguage.pack_start(cell, True)
        comboboxLanguage.add_attribute(cell, 'text', 0)

        comboboxLanguage.set_active_iter(currentIter)

        self.newExerciseDialog.show()



    def on_buttonNewExerciseOk_clicked(self,widget,data=None):
        videoChooser = self.builder.get_object("filechooserbuttonVideo")
        videoPath = videoChooser.get_filename()
        exerciseChooser = self.builder.get_object("filechooserbuttonExercise")
        exercisePath = exerciseChooser.get_filename()
        translationChooser = self.builder.get_object("filechooserbuttonTranslation")
        translationPath = translationChooser.get_filename()
        if videoPath == "None" or videoPath == None:
            videoPath = ""
        if exercisePath == "None" or exercisePath == None:
            exercisePath = ""
        if translationPath == "None" or translationPath == None:
            translationPath = ""

        comboboxLanguage = self.builder.get_object("comboboxLanguage")
        self.liststoreLanguage.get_iter_first()
        iter = comboboxLanguage.get_active_iter()
        langId = self.liststoreLanguage.get_value(iter,1)

        self.core.NewExercise(videoPath,exercisePath, translationPath, langId)
        self.newExerciseDialog.hide()

    def on_buttonNewExerciseCancel_clicked(self,widget,data=None):
        self.newExerciseDialog.hide()

    def on_imagemenuitemExportAsTemplate_activate(self,widget,data=None):
        self.core.exportAsTemplate()

    def on_imagemenuitemExportAsPackage_activate(self,widget,data=None):
        self.core.exportAsPackage()

    def on_textbufferView_changed(self,widget):
        if self.mode != "loaded":
            self.ClearBuffer();
            return False;

        if self.disableChangedTextEvent:
           return False;

        buffer = self.typeLabel.get_buffer()
        oldText = self.sequenceText
        newText = buffer.get_text(buffer.get_start_iter(),buffer.get_end_iter())
        index = self.typeLabel.get_buffer().props.cursor_position

        newText= newText.decode("utf-8")
        oldText= oldText.decode("utf-8")

        newLength = len(newText) - len(oldText)
        newString = newText[index-newLength:index]

        for char in newString:
            if char == " ":
                 self.core.NextWord()
            else:
                self.core.WriteChar(char)

        return True

    def on_typeView_key_press_event(self,widget, event):

        keyname = gtk.gdk.keyval_name(event.keyval)
        if keyname == "Return" or keyname == "KP_Enter":
            self.core.UserRepeat()
            self.core.RepeatSequence()
        elif keyname == "BackSpace":
            self.core.DeletePreviousChar()
        elif keyname == "Delete":
            self.core.DeleteNextChar()
        elif keyname == "Page_Down":
            self.core.PreviousSequence()
        elif keyname == "Page_Up":
            self.core.NextSequence()
        elif keyname == "Down":
           self.core.PreviousSequence()
        elif keyname == "Up":
           self.core.NextSequence()
        elif keyname == "Tab":
            self.core.NextWord()
        elif keyname == "ISO_Left_Tab":
            self.core.PreviousWord()
        elif keyname == "F1":
            self.core.CompleteWord()
        elif keyname == "F2":
            toggletoolbuttonShowTranslation = self.builder.get_object("toggletoolbuttonShowTranslation")
            toggletoolbuttonShowTranslation.set_active(not toggletoolbuttonShowTranslation.get_active())
        elif keyname == "F9":
            self.toggleLateralPanel()
        elif keyname == "Pause":
            self.core.togglePause()
        elif keyname == "KP_Add":
            if self.settedSpeed > 90:
                self.core.SetSpeed(1.0)
            else:
                self.core.SetSpeed(float(self.settedSpeed+10)/100)
        elif keyname == "KP_Subtract":
            if self.settedSpeed < 85:
                self.core.SetSpeed(0.75)
            else:
                self.core.SetSpeed(float(self.settedSpeed-10)/100)
        else:
            return False

        return True;

    def on_toolbuttonNextSequence_clicked(self,widget,data=None):
        self.core.NextSequence()

    def on_toolbuttonPreviousSequence_clicked(self,widget,data=None):
        self.core.PreviousSequence()

    def on_toolbuttonReplaySequence_clicked(self,widget,data=None):
        self.core.UserRepeat()
        self.core.RepeatSequence()

    def on_adjustmentSequenceNum_value_changed(self,widget,data=None):

        value = int(self.builder.get_object("adjustmentSequenceNum").get_value())

        if value != self.settedSeq:
            self.core.SelectSequence(value - 1)

    def on_adjustmentSequenceTime_value_changed(self,widget,data=None):
        value = int(self.builder.get_object("adjustmentSequenceTime").get_value())
        if value != self.settedPos:
            self.core.SeekSequence(value*100)

    def on_adjustmentSpeed_value_changed(self,widget,data=None):
        value = int(self.builder.get_object("adjustmentSpeed").get_value())
        if value != self.settedSpeed:
            self.core.SetSpeed(float(value)/100)

    def on_toolbuttonHint_clicked(self,widget,data=None):
        self.core.CompleteWord()

    def on_toolbuttonPlay_clicked(self,widget,data=None):
        self.core.Play()

    def on_toolbuttonPause_clicked(self,widget,data=None):
        self.core.Pause()

    def on_saveButton_clicked(self, widget, data=None):
        self.core.Save()

    def on_loadButton_clicked(self, widget, data=None):

        loader = OpenFileSelector(self.window)
        result =loader.run()
        if result == None:
            return

        self.core.LoadExercise(result)

    def on_buttonSaveExerciseOk_clicked(self, widget, data=None):
        saveChooser = self.builder.get_object("filechooserdialogSave")
        saveChooser.hide()

    def on_entryFilter_changed(self, widget, data=None):
        self.UpdateWordList()

    def on_toggletoolbuttonShowTranslation_toggled(self, widget, data=None):
        toggletoolbuttonShowTranslation = self.builder.get_object("toggletoolbuttonShowTranslation")
        if toggletoolbuttonShowTranslation.props.active != self.translationVisible:
            self.toggleTranslation()

    def on_typeView_move_cursor(self, textview, step_size, count, extend_selection):


        if step_size == gtk.MOVEMENT_VISUAL_POSITIONS:
            if count == -1:
                self.core.PreviousChar()
            elif count == 1:
                self.core.NextChar()
        elif step_size == gtk.MOVEMENT_DISPLAY_LINE_ENDS:
            if count == -1:
                self.core.FirstWord()
            elif count == 1:
                self.core.LastWord()
        elif step_size == gtk.MOVEMENT_WORDS:
            if count == -1:
                self.core.PreviousWord()
            elif count == 1:
                self.core.NextWord()

        return True

    def on_typeView_button_release_event(self, widget, data=None):

        if self.mode != "loaded":
            return True
        index = self.typeLabel.get_buffer().props.cursor_position


        wordIndex = self.wordIndexMap[index]
        wordIndexPos = self.wordPosMap[index]
        if wordIndex == -1:
            wordIndex = 0
        self.core.SelectSequenceWord(wordIndex,wordIndexPos)

    def on_toolbuttonProperties_clicked(self, widget, data=None):
        self.AskProperties()

    def on_imagemenuitemExerciceManager_activate(self, widget, data=None):
        self.DisplayExerciceManager()

    def DisplayExerciceManager(self):
        dialogExerciseManager = GuiExerciseManager(self.core, self.window)
        dialogExerciseManager.Run()

    def on_imagemenuitemAbout_activate(self,widget,data=None):
        self.builder.get_object("aboutdialog").show()

    def on_imagemenuitemHint_activate(self,widget,data=None):
        return self.on_toolbuttonHint_clicked(widget, data)

    def on_checkmenuitemLateralPanel_toggled(self,widget,data=None):
        self.toggleLateralPanel()

    def on_checkmenuitemTranslation_toggled(self,widget,data=None):
        checkmenuitemTranslation = self.builder.get_object("checkmenuitemTranslation")
        if checkmenuitemTranslation.props.active != self.translationVisible:
            self.toggleTranslation()

    def toggleLateralPanel(self):
        scrolledwindowTranslation = self.builder.get_object("vbox2")
        if self.config.Get("showlateralpanel"):
            scrolledwindowTranslation.hide()
            self.config.Set("showlateralpanel", 0)
        else:
            scrolledwindowTranslation.show()
            self.config.Set("showlateralpanel", 1)

    def toggleTranslation(self):
        scrolledwindowTranslation = self.builder.get_object("scrolledwindowTranslation")
        toggletoolbuttonShowTranslation = self.builder.get_object("toggletoolbuttonShowTranslation")
        checkmenuitemTranslation = self.builder.get_object("checkmenuitemTranslation")
        if not self.translationVisible:
            scrolledwindowTranslation.show()
            toggletoolbuttonShowTranslation.set_active(True)
            checkmenuitemTranslation.set_active(True)
            self.translationVisible = True
        else:
            scrolledwindowTranslation.hide()
            toggletoolbuttonShowTranslation.set_active(False)
            checkmenuitemTranslation.set_active(False)
            self.translationVisible = False

    def on_imagemenuitemProperties_activate(self,widget,data=None):
        return self.on_toolbuttonProperties_clicked(widget, data)

    def on_imagemenuitemAdvancedProperties_activate(self,widget,data=None):
        self.AskPropertiesAdvanced()

    def on_imagemenuitemSettings_activate(self,widget,data=None):
        self.AskSettings()


    def on_imagemenuitemQuit_activate(self,widget,data=None):
        return self.on_MainWindow_delete_event(widget, data)

    def on_imagemenuitemSaveAs_activate(self,widget,data=None):
        self.core.Save(True)

    def on_imagemenuitemSave_activate(self,widget,data=None):
        return self.on_saveButton_clicked(widget, data)

    def on_imagemenuitemOpen_activate(self,widget,data=None):
        return self.on_loadButton_clicked(widget, data)

    def on_imagemenuitemNew_activate(self,widget,data=None):
        return self.on_newExerciseButton_clicked(widget, data)

    def on_filechooserbuttonVideo_file_set(self,widget,data=None):

        videoChooser = self.builder.get_object("filechooserbuttonVideo")
        exerciseChooser = self.builder.get_object("filechooserbuttonExercise")
        translationChooser = self.builder.get_object("filechooserbuttonTranslation")

        fileName = videoChooser.get_filename()
        if fileName and os.path.isfile(fileName):
            filePath = os.path.dirname(fileName)
            if not exerciseChooser.get_filename() or not os.path.isfile(exerciseChooser.get_filename()):
                exerciseChooser.set_current_folder(filePath)
            if not translationChooser.get_filename() or not os.path.isfile(translationChooser.get_filename()):
                translationChooser.set_current_folder(filePath)

    def on_aboutdialog_delete_event(self,widget,data=None):
        self.builder.get_object("aboutdialog").hide()
        return True

    def on_aboutdialog_response(self,widget,data=None):
        self.builder.get_object("aboutdialog").hide()
        return True

    def on_menuitemResetProgress_activate(self, widget, data=None):
        self.resetExerciseContent()

    def on_ResetExerciseContent_clicked(self, widget, data=None):
        self.resetExerciseContent()

    def resetExerciseContent(self):
        dialogExerciseProperties = GuiResetExercise(self.core, self.window)
        dialogExerciseProperties.Run()
        return True


EVENT_FILTER = None


class FileSelector(gtk.FileChooserDialog):
        "A normal file selector"

        def __init__(self, parent, title = None, action = gtk.FILE_CHOOSER_ACTION_OPEN, stockbutton = None):

                if stockbutton is None:
                        if action == gtk.FILE_CHOOSER_ACTION_OPEN:
                                stockbutton = gtk.STOCK_OPEN

                        elif action == gtk.FILE_CHOOSER_ACTION_SAVE:
                                stockbutton = gtk.STOCK_SAVE

                gtk.FileChooserDialog.__init__(
                        self, title, parent, action,
                        ( gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, stockbutton, gtk.RESPONSE_OK )
                )

                self.set_local_only(False)
                self.set_default_response(gtk.RESPONSE_OK)

                self.inputsection = None


        def add_widget(self, title, widget):
                "Adds a widget to the file selection"

                if self.inputsection == None:
                        self.inputsection = ui.InputSection()
                        self.set_extra_widget(self.inputsection)

                self.inputsection.append_widget(title, widget)


        """def get_filename(self):
                "Returns the file URI"

                uri = self.get_filename()

                if uri == None:
                        return None

                else:
                        return urllib.unquote(uri)"""


        def run(self):
                "Displays and runs the file selector, returns the filename"

                self.show_all()

                if EVENT_FILTER != None:
                        self.window.add_filter(EVENT_FILTER)

                response = gtk.FileChooserDialog.run(self)
                filename = self.get_filename()
                self.destroy()

                if response == gtk.RESPONSE_OK:
                        return filename

                else:
                        return None




class OpenFileSelector(FileSelector):
        "A file selector for opening files"

        def __init__(self, parent):
                FileSelector.__init__(
                        self, parent, _('Select File to Open'),
                        gtk.FILE_CHOOSER_ACTION_OPEN, gtk.STOCK_OPEN
                )

                filter = gtk.FileFilter()
                filter.set_name(_('Perroquet files'))
                filter.add_pattern("*.perroquet")
                self.add_filter(filter)

                filter = gtk.FileFilter()
                filter.set_name(_('All files'))
                filter.add_pattern("*")
                self.add_filter(filter)

class SaveFileSelector(FileSelector):
        "A file selector for saving files"

        def __init__(self, parent):
                FileSelector.__init__(
                        self, parent, _('Select File to Save to'),
                        gtk.FILE_CHOOSER_ACTION_SAVE, gtk.STOCK_SAVE
                )

                filter = gtk.FileFilter()
                filter.set_name(_('Perroquet files'))
                filter.add_pattern("*.perroquet")
                self.add_filter(filter)

                filter = gtk.FileFilter()
                filter.set_name(_('All files'))
                filter.add_pattern("*")
                self.add_filter(filter)

                self.set_do_overwrite_confirmation(True)

class ExportAsTemplateFileSelector(FileSelector):
        "A file selector for saving files"

        def __init__(self, parent):
                FileSelector.__init__(
                        self, parent, _('Select File to Export to'),
                        gtk.FILE_CHOOSER_ACTION_SAVE, gtk.STOCK_SAVE
                )

                filter = gtk.FileFilter()
                filter.set_name(_('Perroquet template files'))
                filter.add_pattern("*.perroquet")
                self.add_filter(filter)

                filter = gtk.FileFilter()
                filter.set_name(_('All files'))
                filter.add_pattern("*")
                self.add_filter(filter)

                self.set_do_overwrite_confirmation(True)

class ExportAsPackageFileSelector(FileSelector):
        "A file selector for saving files"

        def __init__(self, parent):
                FileSelector.__init__(
                        self, parent, _('Select File to Export to'),
                        gtk.FILE_CHOOSER_ACTION_SAVE, gtk.STOCK_SAVE
                )

                filter = gtk.FileFilter()
                filter.set_name(_('Perroquet package files'))
                filter.add_pattern("*.tar")
                self.add_filter(filter)

                filter = gtk.FileFilter()
                filter.set_name(_('All files'))
                filter.add_pattern("*")
                self.add_filter(filter)

                self.set_do_overwrite_confirmation(True)


