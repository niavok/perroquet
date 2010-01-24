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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Perroquet.  If not, see <http://www.gnu.org/licenses/>.


import thread, time, re, gtk, os
from video_player import VideoPlayer
from exercise_manager import ExerciseSaver
from exercise_manager import ExerciseLoader
from exercise import Exercise

class Core(object):
    WAIT_BEGIN = 0
    WAIT_END = 1

    def __init__(self):
        self.outputSavePath = ""
        self.player = None
        self.last_save = False
        self.exercise = None


    def SetGui(self, gui):
        self.gui = gui

    def NewExercise(self, videoPath, exercisePath, translationPath, load = True):
        self.exercise = Exercise()
        self.outputSavePath = ""
        self.SetPaths(videoPath, exercisePath, translationPath)
        self.InitExercise()
        self.Reload(load);
        self.ActivateSequence()
        self.gui.SetTitle("", True)

    def SetPaths(self, videoPath, exercisePath, translationPath):
        self.exercise.SetVideoPath(videoPath)
        self.exercise.SetExercisePath(exercisePath)
        self.exercise.SetTranslationPath(translationPath)
        self.exercise.LoadSubtitles()

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
            self.SetCanSave(True)
            self.Play()
        else:
            self.SetCanSave(False)
            self.Pause()

    def Play(self):
        self.gui.SetPlaying(True)
        self.player.Play()
        self.paused = False

    def Pause(self):
        self.gui.SetPlaying(False)
        self.player.Pause()
        self.paused = True

    def SetSpeed(self, speed):
        self.gui.SetSpeed(speed)
        self.player.SetSpeed(speed)

    def InitExercise(self):
        self.exercise.Initialize()


    def TimeCallback(self):
        if self.state == Core.WAIT_BEGIN:
            self.player.SetNextCallbackTime(self.exercise.GetCurrentSequence().GetTimeEnd() + 500)
            self.state = Core.WAIT_END
        elif self.state == Core.WAIT_END:
            self.state = Core.WAIT_BEGIN
            if self.exercise.GetCurrentSequence().IsValid():
                gtk.gdk.threads_enter()
                self.NextSequence(False)
                gtk.gdk.threads_leave()
            else:
                self.Pause()

    def RepeatSequence(self):
        self.GotoSequenceBegin()
        self.Play()

    def SelectSequence(self, num, load = True):
        if self.exercise.GetCurrentSequenceId() == num:
            return
        self.exercise.GotoSequence(num)
        self.ActivateSequence()
        if load:
            self.RepeatSequence()
        self.SetCanSave(True)

    def NextSequence(self, load = True):
        if self.exercise.GotoNextSequence():
            self.SetCanSave(True)
        self.ActivateSequence()
        if load:
            self.RepeatSequence()

    def PreviousSequence(self, load = True):
        if self.exercise.GotoPreviousSequence():
            self.SetCanSave(True)
        self.ActivateSequence()
        if load:
            self.RepeatSequence()

    def ActivateSequence(self):
        self.state = Core.WAIT_BEGIN
        self.SetSpeed(1)
        self.player.SetNextCallbackTime(self.exercise.GetCurrentSequence().GetTimeBegin())

        self.gui.SetSequenceNumber(self.exercise.GetCurrentSequenceId(), self.exercise.GetSequenceCount())
        self.gui.SetSequence(self.exercise.GetCurrentSequence())
        self.ActivateTranslation()
        self.UpdateStats()

    def ActivateTranslation(self):
        if not self.exercise.GetTranslationList():
            self.gui.SetTranslation("")
        else:
            translation = ""
            currentBegin = self.exercise.GetCurrentSequence().GetTimeBegin()
            currentEnd = self.exercise.GetCurrentSequence().GetTimeEnd()
            for sub in self.exercise.GetTranslationList():
                begin = sub.GetTimeBegin()
                end = sub.GetTimeEnd()
                if (begin >= currentBegin and begin <= currentEnd) or (end >= currentBegin and end <= currentEnd) or (begin <= currentBegin and end >= currentEnd):
                    translation +=  sub.GetText() + " "

            self.gui.SetTranslation(translation)

    def UpdateStats(self):
        sequenceCount = self.exercise.GetSequenceCount()
        sequenceFound = 0
        wordCount = 0
        wordFound = 0
        for sequence in  self.exercise.GetSequenceList():
            wordCount = wordCount + sequence.GetWordCount()
            if sequence.IsValid():
                sequenceFound += 1
                wordFound += sequence.GetWordCount()
            else :
                wordFound += sequence.GetWordFound()
        if wordFound == 0:
            repeatRate = float(0)
        else:
            repeatRate = float(self.exercise.GetRepeatCount()) / float(wordFound)
        self.gui.SetStats(sequenceCount,sequenceFound, wordCount, wordFound, repeatRate)

    def ValidateSequence(self):
        if self.exercise.GetCurrentSequence().IsValid():
            self.RepeatSequence()

    def GotoSequenceBegin(self, asSoonAsReady = False):
        self.state = Core.WAIT_END
        begin_time = self.exercise.GetCurrentSequence().GetTimeBegin() - 1000
        if begin_time < 0:
            begin_time = 0
        if asSoonAsReady:
            self.player.SeekAsSoonAsReady(begin_time)
        else:
            self.player.Seek(begin_time)
        self.player.SetNextCallbackTime(self.exercise.GetCurrentSequence().GetTimeEnd())
        self.SetCanSave(True)


    def WriteCharacter(self, character):

        if re.match('^[0-9\'a-zA-Z]$',character):
            self.exercise.GetCurrentSequence().WriteCharacter(character)
            self.gui.SetSequence(self.exercise.GetCurrentSequence())
            self.ValidateSequence()
            self.SetCanSave(True)
        else:
            self.gui.SetSequence(self.exercise.GetCurrentSequence())


    def NextWord(self):
        self.exercise.GetCurrentSequence().NextWord(False)
        self.gui.SetSequence(self.exercise.GetCurrentSequence())
        self.SetCanSave(True)

    def PreviousWord(self):
        self.exercise.GetCurrentSequence().PreviousWord(False)
        self.gui.SetSequence(self.exercise.GetCurrentSequence())
        self.SetCanSave(True)

    def SelectSequenceWord(self, wordIndex,wordIndexPos):
        self.exercise.GetCurrentSequence().SelectSequenceWord(wordIndex,wordIndexPos)
        self.gui.SetSequence(self.exercise.GetCurrentSequence())
        self.SetCanSave(True)

    def FirstWord(self):
        self.exercise.GetCurrentSequence().FirstWord()

        self.gui.SetSequence(self.exercise.GetCurrentSequence())
        self.SetCanSave(True)

    def LastWord(self):
        self.exercise.GetCurrentSequence().LastWord()
        self.gui.SetSequence(self.exercise.GetCurrentSequence())
        self.SetCanSave(True)

    def DeletePreviousChar(self):
        self.exercise.GetCurrentSequence().DeletePreviousCharacter()
        self.gui.SetSequence(self.exercise.GetCurrentSequence())
        self.ValidateSequence()
        self.SetCanSave(True)

    def DeleteNextChar(self):
        self.exercise.GetCurrentSequence().DeleteNextCharacter()
        self.gui.SetSequence(self.exercise.GetCurrentSequence())
        self.ValidateSequence()
        self.SetCanSave(True)

    def PreviousChar(self):
        self.exercise.GetCurrentSequence().PreviousCharacter()
        self.gui.SetSequence(self.exercise.GetCurrentSequence())
        self.SetCanSave(True)

    def NextChar(self):
        self.exercise.GetCurrentSequence().NextCharacter()
        self.gui.SetSequence(self.exercise.GetCurrentSequence())
        self.SetCanSave(True)

    def CompleteWord(self):
        self.exercise.GetCurrentSequence().CompleteWord()
        self.gui.SetSequence(self.exercise.GetCurrentSequence())
        self.ValidateSequence()
        self.SetCanSave(True)

    def TooglePause(self):
        if self.player.IsPaused() and self.paused:
            self.Play()
        elif not self.player.IsPaused() and not self.paused:
            self.Pause()

    def SeekSequence(self, time):
        begin_time = self.exercise.GetCurrentSequence().GetTimeBegin() - 1000
        if begin_time < 0:
            begin_time = 0

        pos = begin_time + time
        self.player.Seek(pos)
        self.player.SetNextCallbackTime(self.exercise.GetCurrentSequence().GetTimeEnd() + 500)
        self.state = Core.WAIT_END
        self.Play()


    def timeUpdateThread(self):
        timeUpdateThreadId = self.timeUpdateThreadId
        while timeUpdateThreadId == self.timeUpdateThreadId:
            time.sleep(0.5)
            pos_int = self.player.GetCurrentTime()
            if pos_int != None:
                end_time = self.exercise.GetCurrentSequence().GetTimeEnd()
                begin_time = self.exercise.GetCurrentSequence().GetTimeBegin() - 1000
                if begin_time < 0:
                    begin_time = 0
                duration =  end_time - begin_time
                pos = pos_int -begin_time
                self.gui.SetSequenceTime(pos, duration)

    def Save(self, saveAs = False):

        if saveAs or self.outputSavePath == "":
            outputSavePath = self.gui.AskSavePath()
            if outputSavePath == None:
                return
            self.outputSavePath = outputSavePath

        self.gui.SetTitle(self.outputSavePath, False)
        saver = ExerciseSaver()
        saver.Save(self.exercise, self.outputSavePath)

        self.gui.config.Set("lastopenfile", self.outputSavePath)

        self.SetCanSave(False)

    def LoadExercise(self, path):
        self.gui.Activate("closed")
        loader = ExerciseLoader()
        try:
            self.exercise = loader.Load(path)
        except:
            print "Error: invalid file"
            return
        if not self.exercise:
            return

        validPaths, errorList = self.exercise.IsPathsValid()
        if not validPaths:
            for error in errorList:
                self.gui.SignalExerciseBadPath(error)

            self.outputSavePath = path
            self.gui.SetTitle(self.outputSavePath, False)
            self.gui.Activate("load_failed")
            self.gui.AskProperties()
            return

        self.Reload(False)
        self.outputSavePath = path
        self.gui.SetTitle(self.outputSavePath, False)
        self.ActivateSequence()
        self.GotoSequenceBegin(True)
        self.Play()

    def UpdatePaths(self, videoPath, exercisePath, translationPath):
        self.exercise.SetVideoPath(videoPath)
        self.exercise.SetExercisePath(exercisePath)
        self.exercise.SetTranslationPath(translationPath)

        validPaths, errorList = self.exercise.IsPathsValid()
        if not validPaths:
            for error in errorList:
                self.gui.SignalExerciseBadPath(error)
            self.gui.Activate("load_failed")
            self.gui.SetTitle(self.outputSavePath, False)
            return

        self.SetPaths( videoPath, exercisePath, translationPath)
        self.Reload(True)
        self.gui.SetTitle(self.outputSavePath, True)
        self.SetCanSave(True)
        self.ActivateSequence()
        self.GotoSequenceBegin(True)
        self.Play()

    def GetPaths(self):
        return (self.exercise.GetVideoPath(), self.exercise.GetExercisePath(), self.exercise.GetTranslationPath())

    def UpdateWordList(self):
        self.gui.SetWordList(self.exercise.ExtractWordList())

    def UserRepeat(self):
        self.exercise.IncrementRepeatCount()


    def SetCanSave(self, save):

        self.gui.SetCanSave(save)
        if self.last_save != save:
            self.last_save = save
            self.gui.SetTitle(self.outputSavePath, save)

    def GetCanSave(self):
        return self.last_save
