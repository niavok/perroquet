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


import thread, time, gtk, os
from video_player import VideoPlayer
from exercise_serializer import ExerciseSaver
from exercise_serializer import ExerciseLoader
from exercise import Exercise
from word import NoCharPossible, ValidWordError

# The Core make the link between the GUI, the vidéo player, the current
# open exercise and all others part of the application
class Core(object):
    WAIT_BEGIN = 0
    WAIT_END = 1

    def __init__(self):
        self.player = None
        self.last_save = False
        self.exercise = None



    #Call by the main, give an handler to the main gui
    def SetGui(self, gui):
        self.gui = gui

    #Create a new exercice based on paths. Load the new exercise and
    #begin to play
    def NewExercise(self, videoPath, exercisePath, translationPath, langId):
        self.exercise = Exercise()
        self.exercise.setMediaChangeCallback(self.mediaChangeCallBack)
        self.exercise.new()
        self.SetPaths(videoPath, exercisePath, translationPath)
        self.exercise.setLanguageId(langId)
        self.exercise.Initialize()
        self.Reload(True);
        self.ActivateSequence()
        self.gui.SetTitle("", True)

    #Configure the paths for the current exercice. Reload subtitles list.
    def SetPaths(self, videoPath, exercisePath, translationPath):
        self.exercise.SetVideoPath(videoPath)
        self.exercise.SetExercisePath(exercisePath)
        self.exercise.SetTranslationPath(translationPath)
        self.exercise.Initialize()

    #Reload media player and begin to play (if the params is True)
    def Reload(self, load):
        if self.player != None:
            self.player.Close()

        self.player = VideoPlayer()
        self.player.SetWindowId(self.gui.GetVideoWindowId())
        self.player.Open(self.exercise.GetVideoPath())
        self.player.SetCallback(self.TimeCallback)
        self.paused = False
        self.gui.Activate("loaded")
        self.UpdateWordList()
        self.timeUpdateThreadId = thread.start_new_thread(self.timeUpdateThread, ())

        if load:
            self.Play()
        else:
            self.Pause()

    #Play the media
    def Play(self):
        self.gui.SetPlaying(True)
        self.player.Play()
        self.paused = False

    #Pause the media
    def Pause(self):
        self.gui.SetPlaying(False)
        self.player.Pause()
        self.paused = True

    #Modify media speed
    def SetSpeed(self, speed):
        self.gui.SetSpeed(speed)
        self.player.SetSpeed(speed)

    #Callback call by video player to notify change of media position.
    #Stop the media at the end of uncompleted sequences
    def TimeCallback(self):
        if self.state == Core.WAIT_BEGIN:
            self.player.SetNextCallbackTime(self.exercise.getCurrentSequence().getTimeEnd() + 500)
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
        self.ActivateSequence()
        if load:
            self.RepeatSequence()
        self.SetCanSave(True)

    #Goto next sequence
    def NextSequence(self, load = True):
        if self.exercise.GotoNextSequence():
            self.SetCanSave(True)
        self.ActivateSequence()
        if load:
            self.RepeatSequence()

    #Goto previous sequence
    def PreviousSequence(self, load = True):
        if self.exercise.GotoPreviousSequence():
            self.SetCanSave(True)
        self.ActivateSequence()
        if load:
            self.RepeatSequence()

    #Update interface with new sequence. Configure stop media callback
    def ActivateSequence(self):
        self.state = Core.WAIT_BEGIN
        self.SetSpeed(1)
        self.player.SetNextCallbackTime(self.exercise.getCurrentSequence().getTimeBegin())

        self.gui.SetSequenceNumber(self.exercise.getCurrentSequenceId(), self.exercise.GetSequenceCount())
        self.gui.SetSequence(self.exercise.getCurrentSequence())
        self.ActivateTranslation()
        self.UpdateStats()

    #Update displayed translation on new active sequence
    def ActivateTranslation(self):
        if not self.exercise.GetTranslationList():
            self.gui.SetTranslation("")
        else:
            translation = ""
            currentBegin = self.exercise.getCurrentSequence().getTimeBegin()
            currentEnd = self.exercise.getCurrentSequence().getTimeEnd()
            for sub in self.exercise.GetTranslationList():
                begin = sub.GetTimeBegin()
                end = sub.GetTimeEnd()
                if (begin >= currentBegin and begin <= currentEnd) or (end >= currentBegin and end <= currentEnd) or (begin <= currentBegin and end >= currentEnd):
                    translation += sub.GetText() + " "

            self.gui.SetTranslation(translation)

    #Update displayed stats on new active sequence
    def UpdateStats(self):
        sequenceCount = self.exercise.GetSequenceCount()
        sequenceFound = 0
        wordCount = 0
        wordFound = 0
        for sequence in self.exercise.GetSequenceList():
            wordCount = wordCount + sequence.getWordCount()
            if sequence.isValid():
                sequenceFound += 1
                wordFound += sequence.getWordCount()
            else :
                wordFound += sequence.GetWordFound()
        if wordFound == 0:
            repeatRate = float(0)
        else:
            repeatRate = float(self.exercise.GetRepeatCount()) / float(wordFound)
        self.gui.SetStats(sequenceCount,sequenceFound, wordCount, wordFound, repeatRate)

    #Verify if the sequence is complete
    def ValidateSequence(self):
        if self.exercise.getCurrentSequence().isValid():
            if self.exercise.GetRepeatAfterCompleted():
                self.RepeatSequence()
            else:
                self.NextSequence(False)
                self.Play()

    #Goto beginning of the current sequence. Can start to play as soon
    #as the media player is ready
    def GotoSequenceBegin(self, asSoonAsReady = False):
        self.state = Core.WAIT_END
        begin_time = self.exercise.getCurrentSequence().getTimeBegin() - 1000
        if begin_time < 0:
            begin_time = 0
        if asSoonAsReady:
            self.player.SeekAsSoonAsReady(begin_time)
        else:
            self.player.Seek(begin_time)
        self.player.SetNextCallbackTime(self.exercise.getCurrentSequence().getTimeEnd())


    #Write a char in current sequence at cursor position
    def WriteChar(self, char):

        if self.exercise.isCharacterMatch(char):
            self.exercise.getCurrentSequence().writeChar(char)
            self.gui.SetSequence(self.exercise.getCurrentSequence())
            self.ValidateSequence()
            self.SetCanSave(True)
        else:
            self.gui.SetSequence(self.exercise.getCurrentSequence())

    #Goto next word in current sequence
    def NextWord(self):
        self.exercise.getCurrentSequence().nextWord()
        self.gui.SetSequence(self.exercise.getCurrentSequence())

    #Goto previous word in current sequence
    def PreviousWord(self):
        self.exercise.getCurrentSequence().previousWord()
        self.gui.SetSequence(self.exercise.getCurrentSequence())

    #Choose current word in current sequence
    def SelectSequenceWord(self, wordIndex,wordIndexPos):
        try:
            self.exercise.getCurrentSequence().selectSequenceWord(wordIndex,wordIndexPos)
        except NoCharPossible:
            self.exercise.getCurrentSequence().selectSequenceWord(wordIndex,-1)
        self.gui.SetSequence(self.exercise.getCurrentSequence())

    #Goto first word in current sequence
    def FirstWord(self):
        self.exercise.getCurrentSequence().firstFalseWord()
        self.gui.SetSequence(self.exercise.getCurrentSequence())

    #Goto last word in current sequence
    def LastWord(self):
        self.exercise.getCurrentSequence().lastFalseWord()
        self.gui.SetSequence(self.exercise.getCurrentSequence())

    #Delete a char before the cursor in current sequence
    def DeletePreviousChar(self):
        self.exercise.getCurrentSequence().deletePreviousChar()
        self.gui.SetSequence(self.exercise.getCurrentSequence())
        self.ValidateSequence()
        self.SetCanSave(True)

    #Delete a char after the cursor in current sequence
    def DeleteNextChar(self):
        self.exercise.getCurrentSequence().deleteNextChar()
        self.gui.SetSequence(self.exercise.getCurrentSequence())
        self.ValidateSequence()
        self.SetCanSave(True)

    #Goto previous char in current sequence
    def PreviousChar(self):
        self.exercise.getCurrentSequence().previousChar()
        #The sequence don't change but the cursor position is no more up to date
        self.gui.SetSequence(self.exercise.getCurrentSequence())

    #Goto next char in current sequence
    def NextChar(self):
        self.exercise.getCurrentSequence().nextChar()
        #The sequence don't change but the cursor position is no more up to date
        self.gui.SetSequence(self.exercise.getCurrentSequence())

    #Reveal correction for word at cursor in current sequence
    def CompleteWord(self):
        self.exercise.getCurrentSequence().showHint()
        self.gui.SetSequence(self.exercise.getCurrentSequence())
        self.exercise.getCurrentSequence().nextChar()
        self.ValidateSequence()
        self.SetCanSave(True)

    #Pause or play media
    def togglePause(self):
        if self.player.IsPaused() and self.paused:
            self.Play()
        elif not self.player.IsPaused() and not self.paused:
            self.Pause()

    #Change position in media and play it
    def SeekSequence(self, time):
        begin_time = self.exercise.getCurrentSequence().getTimeBegin() - 1000
        if begin_time < 0:
            begin_time = 0

        pos = begin_time + time
        self.player.Seek(pos)
        self.player.SetNextCallbackTime(self.exercise.getCurrentSequence().getTimeEnd() + 500)
        self.state = Core.WAIT_END
        self.Play()

    #Thread to update slider position in gui
    def timeUpdateThread(self):
        timeUpdateThreadId = self.timeUpdateThreadId
        while timeUpdateThreadId == self.timeUpdateThreadId:
            time.sleep(0.5)
            pos_int = self.player.GetCurrentTime()
            if pos_int != None:
                end_time = self.exercise.getCurrentSequence().getTimeEnd()
                begin_time = self.exercise.getCurrentSequence().getTimeBegin() - 1000
                if begin_time < 0:
                    begin_time = 0
                duration = end_time - begin_time
                pos = pos_int -begin_time
                self.gui.SetSequenceTime(pos, duration)

    #Save current exercice
    def Save(self, saveAs = False):

        if saveAs or self.exercise.getOutputSavePath() == None:
            outputSavePath = self.gui.AskSavePath()
            if outputSavePath == None:
                return
            self.exercise.setOutputSavePath(outputSavePath)

        saver = ExerciseSaver()
        saver.Save(self.exercise, self.exercise.getOutputSavePath())

        self.gui.config.Set("lastopenfile", self.exercise.getOutputSavePath())

        self.SetCanSave(False)

    #Load the exercice at path
    def LoadExercise(self, path):
        self.gui.Activate("closed")
        loader = ExerciseLoader()
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
                self.gui.SignalExerciseBadPath(error)

            self.SetCanSave(False)
            self.gui.Activate("load_failed")
            self.gui.AskProperties()
            return

        self.Reload(False)
        if self.exercise.getOutputSavePath() == None:
            self.SetCanSave(True)
        else:
            self.SetCanSave(False)
        self.ActivateSequence()
        self.GotoSequenceBegin(True)
        self.Play()

    #Change paths of current exercice and reload subtitles and video
    def UpdatePaths(self, videoPath, exercisePath, translationPath):
        self.exercise.SetVideoPath(videoPath)
        self.exercise.SetExercisePath(exercisePath)
        self.exercise.SetTranslationPath(translationPath)

        validPaths, errorList = self.exercise.IsPathsValid()
        if not validPaths:
            for error in errorList:
                self.gui.SignalExerciseBadPath(error)
            self.gui.Activate("load_failed")
            self.SetCanSave(False)
            return

        self.SetPaths( videoPath, exercisePath, translationPath)
        self.Reload(True)
        self.SetCanSave(True)
        self.ActivateSequence()
        self.GotoSequenceBegin(True)
        self.Play()

    def UpdateProperties(self):

        self.exercise.Initialize()
        self.Reload(True)
        self.SetCanSave(True)
        self.ActivateSequence()
        self.GotoSequenceBegin(True)
        self.Play()

    #Get paths of current exercise
    def GetPaths(self):
        return (self.exercise.GetVideoPath(), self.exercise.GetExercisePath(), self.exercise.GetTranslationPath())

    #Udpates vocabulary list in interface
    def UpdateWordList(self):
        self.gui.SetWordList(self.exercise.ExtractWordList())

    #Notify the user use the repeat command (for stats)
    def UserRepeat(self):
        self.exercise.IncrementRepeatCount()
        self.SetCanSave(True)

    #Signal to the gui that the exercise has unsaved changes
    def SetCanSave(self, save):

        self.gui.SetCanSave(save)

        if self.exercise == None:
            title = ""
        elif self.exercise.getName() != None:
            title = self.exercise.getName()
        elif self.exercise.getOutputSavePath() != None:
            title = self.exercise.getOutputSavePath()
        else:
            title = _("Untitled exercise")

        self.last_save = save
        self.gui.SetTitle(title, save)

    def GetCanSave(self):
        return self.last_save

    def GetExercise(self):
        return self.exercise


    def mediaChangeCallBack(self):
        print "new media : "+self.exercise.GetVideoPath()
        """self.Pause()
        self.player.Open(self.exercise.GetVideoPath())
        """
        self.Reload(True)
        self.ActivateSequence()
        self.GotoSequenceBegin(True)
        self.Play()
