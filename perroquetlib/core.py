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


import thread, time, re, gtk, os
from video_player import VideoPlayer
from subtitles_loader import SubtitlesLoader
from exercice_manager import ExerciceSaver
from exercice_manager import ExerciceLoader
from sequence import Sequence

class Core(object):
    WAIT_BEGIN = 0
    WAIT_END = 1

    def __init__(self):
        self.subtitles = SubtitlesLoader()
        self.outputSavePath = ""
        self.player = None
        self.last_save = False

    def SetGui(self, gui):
        self.gui = gui

    def SetPaths(self, videoPath, exercicePath, translationPath, load = True):
        self.outputSavePath = ""
        self.videoPath = videoPath
        self.exercicePath = exercicePath
        self.translationPath = translationPath
        self.repeatCount = 0
        self.subList = self.subtitles.GetSubtitleList(exercicePath)

        self.subList = self.subtitles.CompactSubtitlesList(self.subList)

        self.translationList = None
        if translationPath != "":
            self.translationList = self.subtitles.GetSubtitleList(translationPath)

        if self.player != None:
            self.player.Close()

        self.player = VideoPlayer()
        self.player.SetWindowId(self.gui.GetVideoWindowId())
        self.player.Open(videoPath)
        self.InitExercice()
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


    def InitExercice(self):
        self.player.SetCallback(self.TimeCallback)
        self.sequenceList = []
        self.paused = False
        for sub in self.subList:
            self.sequence = Sequence()
            self.sequence.Load(sub.GetText())
            self.sequenceList.append(self.sequence)

        self.currentSubId = 0
        self.gui.Activate("loaded")
        self.ActivateSequence()
        self.ExtractWordList()
        self.timeUpdateThreadId = thread.start_new_thread(self.timeUpdateThread, ())


    def TimeCallback(self):
        if self.state == Core.WAIT_BEGIN:
            self.player.SetNextCallbackTime(self.subList[self.currentSubId].GetTimeEnd() + 500)
            self.state = Core.WAIT_END
        elif self.state == Core.WAIT_END:
            self.state = Core.WAIT_BEGIN
            #self.currentSubId += 1
            #self.player.SetNextCallbackTime(self.subList[self.currentSubId].GetTimeBegin())
            if self.validSequence:
                gtk.gdk.threads_enter()
                self.NextSequence(False)
                gtk.gdk.threads_leave()
            else:
                self.Pause()



    def RepeatSequence(self):
        self.GotoSequenceBegin()
        self.Play()

    def SelectSequence(self, num, load = True):
        if self.currentSubId == num:
            return
        self.currentSubId = num
        self.ActivateSequence()
        if load:
            self.RepeatSequence()
        self.SetCanSave(True)

    def NextSequence(self, load = True):
        if self.currentSubId < len(self.sequenceList)-1:
            self.currentSubId += 1
        self.ActivateSequence()
        if load:
            self.RepeatSequence()
        self.SetCanSave(True)

    def PreviousSequence(self):
        if self.currentSubId > 0:
            self.currentSubId -= 1
        self.ActivateSequence()
        self.RepeatSequence()
        self.SetCanSave(True)

    def ActivateSequence(self):
        self.state = Core.WAIT_BEGIN
        self.player.SetNextCallbackTime(self.subList[ self.currentSubId].GetTimeBegin())
        self.sequence = self.sequenceList[self.currentSubId]

        self.validSequence = self.sequence.IsValid()

        self.gui.SetSequenceNumber(self.currentSubId, len(self.subList))
        self.gui.SetSequence(self.sequence)
        self.ActivateTranslation()
        self.UpdateStats()




    def ActivateTranslation(self):
        if not self.translationList:
            self.gui.SetTranslation("")
        else:
            translation = ""
            currentBegin = self.subList[ self.currentSubId].GetTimeBegin()
            currentEnd = self.subList[ self.currentSubId].GetTimeEnd()
            for sub in self.translationList:
                begin = sub.GetTimeBegin()
                end = sub.GetTimeEnd()
                if (begin >= currentBegin and begin <= currentEnd) or (end >= currentBegin and end <= currentEnd) or (begin <= currentBegin and end >= currentEnd):
                    translation +=  sub.GetText() + " "

            self.gui.SetTranslation(translation)

    def UpdateStats(self):
        sequenceCount = len(self.sequenceList)
        sequenceFound = 0
        wordCount = 0
        wordFound = 0
        for sequence in self.sequenceList:
            wordCount = wordCount + sequence.GetWordCount()
            if sequence.IsValid():
                sequenceFound += 1
                wordFound += sequence.GetWordCount()
            else :
                wordFound += sequence.GetWordFound()
        if wordFound == 0:
            repeatRate = float(0)
        else:
            repeatRate = float(self.repeatCount) / float(wordFound)
        self.gui.SetStats(sequenceCount,sequenceFound, wordCount, wordFound, repeatRate)



    def ValidateSequence(self):
        if self.sequence.IsValid():
            self.validSequence = True
            self.RepeatSequence()

    def GotoSequenceBegin(self, asSoonAsReady = False):
        self.state = Core.WAIT_END
        begin_time = self.subList[self.currentSubId].GetTimeBegin() - 1000
        if begin_time < 0:
            begin_time = 0
        if asSoonAsReady:
            self.player.SeekAsSoonAsReady(begin_time)
        else:
            self.player.Seek(begin_time)
        self.player.SetNextCallbackTime(self.subList[self.currentSubId].GetTimeEnd())
        self.SetCanSave(True)


    def WriteCharacter(self, character):

        if re.match('^[0-9\'a-zA-Z]$',character):
            self.sequence.WriteCharacter(character)
            self.gui.SetSequence(self.sequence)
            self.ValidateSequence()
            self.SetCanSave(True)
        else:
            self.gui.SetSequence(self.sequence)


    def NextWord(self):
        self.sequence.NextWord(False)
        self.gui.SetSequence(self.sequence)
        self.SetCanSave(True)

    def PreviousWord(self):
        self.sequence.PreviousWord(False)
        self.gui.SetSequence(self.sequence)
        self.SetCanSave(True)

    def SelectSequenceWord(self, wordIndex,wordIndexPos):
        self.sequence.SelectSequenceWord(wordIndex,wordIndexPos)
        self.gui.SetSequence(self.sequence)
        self.SetCanSave(True)

    def FirstWord(self):
        self.sequence.FirstWord()

        self.gui.SetSequence(self.sequence)
        self.SetCanSave(True)

    def LastWord(self):
        self.sequence.LastWord()
        self.gui.SetSequence(self.sequence)
        self.SetCanSave(True)

    def DeletePreviousChar(self):
        self.sequence.DeletePreviousCharacter()
        self.gui.SetSequence(self.sequence)
        self.ValidateSequence()
        self.SetCanSave(True)

    def DeleteNextChar(self):
        self.sequence.DeleteNextCharacter()
        self.gui.SetSequence(self.sequence)
        self.ValidateSequence()
        self.SetCanSave(True)

    def PreviousChar(self):
        self.sequence.PreviousCharacter()
        self.gui.SetSequence(self.sequence)
        self.SetCanSave(True)

    def NextChar(self):
        self.sequence.NextCharacter()
        self.gui.SetSequence(self.sequence)
        self.SetCanSave(True)

    def CompleteWord(self):
        self.sequence.CompleteWord()
        self.gui.SetSequence(self.sequence)
        self.ValidateSequence()
        self.SetCanSave(True)

    def TooglePause(self):
        if self.player.IsPaused() and self.paused:
            self.Play()
        elif not self.player.IsPaused() and not self.paused:
            self.Pause()

    def SeekSequence(self, time):
        begin_time = self.subList[self.currentSubId].GetTimeBegin() - 1000
        if begin_time < 0:
            begin_time = 0

        pos = begin_time + time
        self.player.Seek(pos)
        self.player.SetNextCallbackTime(self.subList[self.currentSubId].GetTimeEnd() + 500)
        self.state = Core.WAIT_END
        self.Play()


    def timeUpdateThread(self):
        timeUpdateThreadId = self.timeUpdateThreadId
        while timeUpdateThreadId == self.timeUpdateThreadId:
            time.sleep(0.5)
            pos_int = self.player.GetCurrentTime()
            if pos_int != None:
                end_time = self.subList[self.currentSubId].GetTimeEnd()
                begin_time = self.subList[self.currentSubId].GetTimeBegin() - 1000
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
        saver = ExerciceSaver()
        saver.SetPath(self.outputSavePath)
        saver.SetVideoPath(self.videoPath)
        saver.SetExercicePath(self.exercicePath)
        saver.SetTranslationPath(self.translationPath)
        saver.SetCurrentSequence(self.currentSubId)
        saver.SetRepeatCount(self.repeatCount)
        saver.SetSequenceList(self.sequenceList)
        saver.Save()
        
        self.gui.config.Set("lastopenfile", self.outputSavePath)

        self.SetCanSave(False)

    def LoadExercice(self, path):
        self.gui.Activate("closed")
        loader = ExerciceLoader()
        if not loader.Load(path):
            return

        if not self.VerifyPath(loader.GetVideoPath(), loader.GetExercicePath(), loader.GetTranslationPath()):
            self.outputSavePath = path
            self.gui.SetTitle(self.outputSavePath, False)
            self.videoPath = loader.GetVideoPath()
            self.exercicePath = loader.GetExercicePath()
            self.translationPath = loader.GetTranslationPath()
            self.gui.Activate("load_failed")
            self.gui.AskProperties()
            return

        self.SetPaths( loader.GetVideoPath(), loader.GetExercicePath(), loader.GetTranslationPath(), False)
        self.outputSavePath = path
        self.gui.SetTitle(self.outputSavePath, False)
        loader.UpdateSequenceList(self.sequenceList)
        self.currentSubId = loader.GetCurrentSequence()
        self.repeatCount = loader.GetRepeatCount()
        self.sequenceList[self.currentSubId].SetActiveWordIndex(loader.GetCurrentWord())
        self.ActivateSequence()
        self.GotoSequenceBegin(True)
        self.Play()

    def VerifyPath(self, videoPath, exercicePath, translationPath):
        error = False
        if not os.path.exists(videoPath):
            error = True;
            self.gui.SignalExerciceBadPath(videoPath)

        if not os.path.exists(exercicePath):
            error = True;
            self.gui.SignalExerciceBadPath(exercicePath)

        if translationPath != "" and not os.path.exists(translationPath):
            error = True;
            self.gui.SignalExerciceBadPath(translationPath)

        return not error

    def UpdatePaths(self, videoPath, exercicePath, translationPath):

        if not self.VerifyPath(videoPath, exercicePath, translationPath):
            self.gui.Activate("load_failed")
            self.gui.SetTitle(self.outputSavePath, False)
            self.videoPath = videoPath
            self.exercicePath = exercicePath
            self.translationPath = translationPath
            return

        loader = ExerciceLoader()
        if not loader.Load(self.outputSavePath):
            return

        path = self.outputSavePath
        self.SetPaths( videoPath, exercicePath, translationPath, False)
        self.outputSavePath = path
        self.gui.SetTitle(self.outputSavePath, True)
        self.SetCanSave(True)
        loader.UpdateSequenceList(self.sequenceList)
        self.currentSubId = loader.GetCurrentSequence()
        self.repeatCount = loader.GetRepeatCount()
        self.sequenceList[self.currentSubId].SetActiveWordIndex(loader.GetCurrentWord())
        self.ActivateSequence()

    def GetPaths(self):
        return (self.videoPath, self.exercicePath, self.translationPath)

    def ExtractWordList(self):
        wordList = []

        for sequence in self.sequenceList:
            sequenceWordList = sequence.GetWordList()
            for word in sequenceWordList:
                wordList.append(word.lower())

        wordList = list(set(wordList))
        wordList.sort()
        self.gui.SetWordList(wordList)

    def UserRepeat(self):
        self.repeatCount +=1


    def SetCanSave(self, save):

        self.gui.SetCanSave(save)
        if self.last_save != save:
            self.last_save = save
            self.gui.SetTitle(self.outputSavePath, save)

    def IsAllowQuit(self):
        return not self.last_save
