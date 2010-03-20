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

import thread
import time
import gtk

from video_player import VideoPlayer
from model.exercise_serializer import ExerciseLoader, ExerciseSaver
from model.exercise import Exercise
from model.sequence import NoCharPossible
from config import config
from perroquetlib.repository.exercise_repository_manager import ExerciseRepositoryManager

# The Core make the link between the GUI, the vidéo player, the current
# open exercise and all others part of the application
class Core(object):
    WAIT_BEGIN = 0
    WAIT_END = 1

    def __init__(self):
        self.player = None
        self.last_save = False
        self.exercise = None
        self.config = config

    #Call by the main, give an handler to the main gui
    def setGui(self, gui):
        self.gui = gui

    #Create a new exercice based on paths. Load the new exercise and
    #begin to play
    def NewExercise(self, videoPath, exercisePath, translationPath, langId):
        self.exercise = Exercise()
        self.exercise.setMediaChangeCallback(self.mediaChangeCallBack)
        self.exercise.new()
        self.exercise.setLanguageId(langId)
        self._setPaths(videoPath, exercisePath, translationPath)
        self.exercise.Initialize()
        self._Reload(True);
        self._ActivateSequence()
        self.gui.setTitle("", True)

    #Configure the paths for the current exercice. Reload subtitles list.
    def _setPaths(self, videoPath, exercisePath, translationPath):
        self.exercise.setVideoPath(videoPath)
        self.exercise.setExercisePath(exercisePath)
        self.exercise.setTranslationPath(translationPath)
        self.exercise.Initialize()

    #Reload media player and begin to play (if the params is True)
    def _Reload(self, load):
        if self.player != None:
            self.player.Close()

        self.player = VideoPlayer()
        self.player.setWindowId(self.gui.getVideoWindowId())
        self.player.ActivateVideoCallback(self.gui.activateVideo)
        self.player.Open(self.exercise.getVideoPath())
        self.player.setCallback(self._TimeCallback)
        self.paused = False
        self.gui.activateVideo(False)
        self.gui.activate("loaded")
        self._updateWordList()
        self.timeUpdateThreadId = thread.start_new_thread(self.timeUpdateThread, ())

        if load:
            self.Play()
        else:
            self.Pause()

    #Play the media
    def Play(self):
        self.gui.setPlaying(True)
        self.player.Play()
        self.paused = False

    #Pause the media
    def Pause(self):
        self.gui.setPlaying(False)
        self.player.Pause()
        self.paused = True

    #Modify media speed
    def setSpeed(self, speed):
        self.gui.setSpeed(speed)
        self.player.setSpeed(speed)

    #Callback call by video player to notify change of media position.
    #Stop the media at the end of uncompleted sequences
    def _TimeCallback(self):
        if self.state == Core.WAIT_BEGIN:
            self.player.setNextCallbackTime(self.exercise.getCurrentSequence().getTimeEnd() + self.exercise.getPlayMarginAfter())
            self.state = Core.WAIT_END
        elif self.state == Core.WAIT_END:
            self.state = Core.WAIT_BEGIN
            if self.exercise.getCurrentSequence().isValid():
                gtk.gdk.threads_enter()
                self.NextSequence(False)
                gtk.gdk.threads_leave()
            else:
                self.Pause()

    #Repeat the currence sequence
    def RepeatSequence(self):
        self.GotoSequenceBegin()
        self.Play()

    #Change the active sequence
    def SelectSequence(self, num, load = True):
        if self.exercise.getCurrentSequenceId() == num:
            return
        self.exercise.GotoSequence(num)
        self._ActivateSequence()
        if load:
            self.RepeatSequence()
        self.setCanSave(True)

    #Goto next sequence
    def NextSequence(self, load = True):
        if self.exercise.GotoNextSequence():
            self.setCanSave(True)
        self._ActivateSequence()
        if load:
            self.RepeatSequence()

    #Goto previous sequence
    def PreviousSequence(self, load = True):
        if self.exercise.GotoPreviousSequence():
            self.setCanSave(True)
        self._ActivateSequence()
        if load:
            self.RepeatSequence()

    #Update interface with new sequence. Configure stop media callback
    def _ActivateSequence(self):
        self.state = Core.WAIT_BEGIN
        self.setSpeed(1)
        self.player.setNextCallbackTime(self.exercise.getCurrentSequence().getTimeBegin())

        self.gui.setSequenceNumber(self.exercise.getCurrentSequenceId(), self.exercise.getSequenceCount())
        self.gui.setSequence(self.exercise.getCurrentSequence())
        self._ActivateTranslation()
        self._updateStats()

    #_update displayed translation on new active sequence
    def _ActivateTranslation(self):
        if not self.exercise.getTranslationList():
            self.gui.setTranslation("")
        else:
            translation = ""
            currentBegin = self.exercise.getCurrentSequence().getTimeBegin()
            currentEnd = self.exercise.getCurrentSequence().getTimeEnd()
            for sub in self.exercise.getTranslationList():
                begin = sub.getTimeBegin()
                end = sub.getTimeEnd()
                if (begin >= currentBegin and begin <= currentEnd) or (end >= currentBegin and end <= currentEnd) or (begin <= currentBegin and end >= currentEnd):
                    translation += sub.getText() + " "

            self.gui.setTranslation(translation)

    #Update displayed stats on new active sequence
    def _updateStats(self):
        sequenceCount = self.exercise.getSequenceCount()
        sequenceFound = 0
        wordCount = 0
        wordFound = 0
        for sequence in self.exercise.getSequenceList():
            wordCount = wordCount + sequence.getWordCount()
            if sequence.isValid():
                sequenceFound += 1
                wordFound += sequence.getWordCount()
            else :
                wordFound += sequence.getWordFound()
        if wordFound == 0:
            repeatRate = float(0)
        else:
            repeatRate = float(self.exercise.getRepeatCount()) / float(wordFound)
        self.gui.setStats(sequenceCount,sequenceFound, wordCount, wordFound, repeatRate)

    def _update(self):
        self.gui.setSequence(self.exercise.getCurrentSequence())
        self._ValidateSequence()

    #Verify if the sequence is complete
    def _ValidateSequence(self):
        if self.exercise.getCurrentSequence().isValid():
            if self.exercise.getRepeatAfterCompleted():
                self.RepeatSequence()
            else:
                self.NextSequence(False)
                self.Play()

    #Goto beginning of the current sequence. Can start to play as soon
    #as the media player is ready
    def GotoSequenceBegin(self, asSoonAsReady = False):
        self.state = Core.WAIT_END
        begin_time = self.exercise.getCurrentSequence().getTimeBegin() - self.exercise.getPlayMarginBefore()
        if begin_time < 0:
            begin_time = 0
        if asSoonAsReady:
            self.player.SeekAsSoonAsReady(begin_time)
        else:
            self.player.Seek(begin_time)
        self.player.setNextCallbackTime(self.exercise.getCurrentSequence().getTimeEnd())


    #Write a char in current sequence at cursor position
    def WriteChar(self, char):
        if self.exercise.isCharacterMatch(char):
            self.exercise.getCurrentSequence().writeChar(char)
            self._update()
            self.setCanSave(True)
        else:
            pass

    #Goto next word in current sequence
    def NextWord(self):
        self.exercise.getCurrentSequence().nextWord()
        self._update()

    #Goto previous word in current sequence
    def PreviousWord(self):
        self.exercise.getCurrentSequence().previousWord()
        self._update()

    #Choose current word in current sequence
    def SelectSequenceWord(self, wordIndex, wordIndexPos):
        try:
            self.exercise.getCurrentSequence().selectSequenceWord(wordIndex,wordIndexPos)
        except NoCharPossible:
            self.exercise.getCurrentSequence().selectSequenceWord(wordIndex,-1)
        self._update()

    #Goto first word in current sequence
    def FirstWord(self):
        self.exercise.getCurrentSequence().firstFalseWord()
        self._update()

    #Goto last word in current sequence
    def LastWord(self):
        self.exercise.getCurrentSequence().lastFalseWord()
        self._update()

    #Delete a char before the cursor in current sequence
    def DeletePreviousChar(self):
        self.exercise.getCurrentSequence().deletePreviousChar()
        self._update()
        self.setCanSave(True)

    #Delete a char after the cursor in current sequence
    def DeleteNextChar(self):
        self.exercise.getCurrentSequence().deleteNextChar()
        self._update()
        self.setCanSave(True)

    #Goto previous char in current sequence
    def PreviousChar(self):
        self.exercise.getCurrentSequence().previousChar()
        #The sequence don't change but the cursor position is no more up to date
        self._update()

    #Goto next char in current sequence
    def NextChar(self):
        self.exercise.getCurrentSequence().nextChar()
        #The sequence don't change but the cursor position is no more up to date
        self._update()

    #Reveal correction for word at cursor in current sequence
    def CompleteWord(self):
        self.exercise.getCurrentSequence().showHint()
        self.exercise.getCurrentSequence().nextChar()
        self._update()
        self.setCanSave(True)

    #reset whole exercise
    def resetExerciseContent(self):
        self.exercise.reset()
        self.exercise.GotoSequence(0) #FIXME
        self._update()
        self.setCanSave(True)
        print "need to stop the current sequence" #FIXME

    #Pause or play media
    def togglePause(self):
        if self.player.IsPaused() and self.paused:
            self.Play()
        elif not self.player.IsPaused() and not self.paused:
            self.Pause()

    #Change position in media and play it
    def SeekSequence(self, time):
        begin_time = self.exercise.getCurrentSequence().getTimeBegin() - self.exercise.getPlayMarginBefore()
        if begin_time < 0:
            begin_time = 0

        pos = begin_time + time
        self.player.Seek(pos)
        self.player.setNextCallbackTime(self.exercise.getCurrentSequence().getTimeEnd() + self.exercise.getPlayMarginAfter())
        self.state = Core.WAIT_END
        self.Play()

    #Thread to update slider position in gui
    def timeUpdateThread(self):
        timeUpdateThreadId = self.timeUpdateThreadId
        while timeUpdateThreadId == self.timeUpdateThreadId:
            time.sleep(0.5)
            pos_int = self.player.getCurrentTime()
            if pos_int != None:
                end_time = self.exercise.getCurrentSequence().getTimeEnd()
                begin_time = self.exercise.getCurrentSequence().getTimeBegin() - self.exercise.getPlayMarginBefore()
                if begin_time < 0:
                    begin_time = 0
                duration = end_time - begin_time
                pos = pos_int -begin_time
                self.gui.setSequenceTime(pos, duration)

    #Save current exercice
    def save(self, saveAs = False):
        if not self.exercise:
            print "Error core.save called but no exercise load"
            return

        if saveAs or self.exercise.getOutputSavePath() == None:
            outputSavePath = self.gui.ask_save_path()
            if outputSavePath == None:
                return
            self.exercise.setOutputSavePath(outputSavePath)

        saver = ExerciseSaver()
        saver.save(self.exercise, self.exercise.getOutputSavePath())

        self.config.set("lastopenfile", self.exercise.getOutputSavePath())

        #lastopenfileS
        l=self.config.get("lastopenfiles")
        path = self.exercise.getOutputSavePath()
        self.config.set("lastopenfiles", [path]+[p for p in l if p!=path])

        self.setCanSave(False)

    #Load the exercice at path
    def LoadExercise(self, path):
        self.gui.activate("closed")
        loader = ExerciseLoader()
        if self.exercise:
            self.save()
        try:
            self.exercise = loader.Load(path)
            self.exercise.setMediaChangeCallback(self.mediaChangeCallBack)
        except IOError:
            print "No file at "+path
            return
        if not self.exercise:
            return


        validPaths, errorList = self.exercise.IsPathsValid()
        if not validPaths:
            for error in errorList:
                self.gui.signal_exercise_bad_path(error)

            self.setCanSave(False)
            self.gui.activate("load_failed")
            self.gui.ask_properties()
            return

        self._Reload(False)
        if self.exercise.getOutputSavePath() == None:
            self.setCanSave(True)
        else:
            self.setCanSave(False)
        self._ActivateSequence()
        self.GotoSequenceBegin(True)
        self.Play()

    #Change paths of current exercice and reload subtitles and video
    def _updatePaths(self, videoPath, exercisePath, translationPath):
        self.exercise.setVideoPath(videoPath)
        self.exercise.setExercisePath(exercisePath)
        self.exercise.setTranslationPath(translationPath)

        validPaths, errorList = self.exercise.IsPathsValid()
        if not validPaths:
            for error in errorList:
                self.gui.signal_exercise_bad_path(error)
            self.gui.activate("load_failed")
            self.setCanSave(False)
            return

        self._setPaths( videoPath, exercisePath, translationPath)
        self._Reload(True)
        self.setCanSave(True)
        self._ActivateSequence()
        self.GotoSequenceBegin(True)
        self.Play()

    def UpdateProperties(self):
        self.exercise.Initialize()
        self._Reload(True)
        self.setCanSave(True)
        self._ActivateSequence()
        self.GotoSequenceBegin(True)
        self.Play()

    #get paths of current exercise
    def getPaths(self):
        return (self.exercise.getVideoPath(), self.exercise.getExercisePath(), self.exercise.getTranslationPath())

    #Udpates vocabulary list in interface
    def _updateWordList(self):
        self.gui.setWordList(self.exercise.ExtractWordList())

    #Notify the user use the repeat command (for stats)
    def UserRepeat(self):
        self.exercise.IncrementRepeatCount()
        self.setCanSave(True)

    #Signal to the gui that the exercise has unsaved changes
    def setCanSave(self, save):
        self.gui.setCanSave(save)

        if self.exercise == None:
            title = ""
        elif self.exercise.getName() != None:
            title = self.exercise.getName()
        elif self.exercise.getOutputSavePath() != None:
            title = self.exercise.getOutputSavePath()
        else:
            title = _("Untitled exercise")

        self.last_save = save
        self.gui.setTitle(title, save)

    def getCanSave(self):
        return self.last_save

    def getExercise(self):
        return self.exercise

    def getPlayer(self):
        return self.player

    def mediaChangeCallBack(self):
        print "new media : "+self.exercise.getVideoPath()
        """self.Pause()
        self.player.Open(self.exercise.getVideoPath())
        """
        self._Reload(True)
        self._ActivateSequence()
        self.GotoSequenceBegin(True)
        self.Play()

    def exportAsTemplate(self):
        self.gui.ask_properties_advanced()
        path = self.gui.AskExportAsTemplatePath()
        if path:
            saver = ExerciseSaver()
            self.exercise.setTemplate(True)
            saver.save(self.exercise, path)
            self.exercise.setTemplate(False)

    def exportAsPackage(self):
        self.gui.ask_properties_advanced()
        path = self.gui.AskExportAsPackagePath()
        if path:
            repoManager = ExerciseRepositoryManager()
            repoManager.exportAsPackage(self.exercise,path)
        print "Export done"

    def import_package(self):
        import_path = self.gui.ask_import_package()

        if import_path is not None:
            repo_manager = ExerciseRepositoryManager()
            error = repo_manager.import_package(import_path)
            if error is None:
                self.gui.display_message(_("Import finish succesfully. Use the exercises manager to use the newly installed exercise."))
            else:
                self.gui.display_message(_("Import failed."+ " " + error ))
