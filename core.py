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

        #for sub in self.subList:
        #    print str(sub.GetId()) + " " + sub.GetText()
        if self.player != None:
            self.player.Close()

        self.player = VideoPlayer()
        self.player.SetWindowId(self.gui.GetVideoWindowId())
        self.player.Open(videoPath)
        self.InitExercice()
        if load:
            self.SetCanSave(True)
            self.player.Play()
            self.paused = False
        else:
            self.SetCanSave(False)
            self.player.Pause()
            self.paused = True



    def InitExercice(self):
        print "InitExercice"
        self.player.SetCallback(self.TimeCallback)
        self.sequenceList = []
        self.paused = False
        for sub in self.subList:
            self.sequence = Sequence()
            self.sequence.Load(sub.GetText())
            self.sequenceList.append(self.sequence)

        self.currentSubId = 0
        self.gui.Activate()
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
                self.player.Pause()



    def RepeatSequence(self):
        print "RepeatSequence"
        self.GotoSequenceBegin()
        self.player.Play()
        self.paused = False

    def SelectSequence(self, num, load = True):
        print "SelectSequence " + str(num) + " " + str(self.currentSubId)
        if self.currentSubId == num:
            return
        self.currentSubId = num
        self.ActivateSequence()
        if load:
            self.RepeatSequence()
        self.SetCanSave(True)

    def NextSequence(self, load = True):
        print "NextSequence"
        if self.currentSubId < len(self.sequenceList)-1:
            self.currentSubId += 1
        self.ActivateSequence()
        if load:
            self.RepeatSequence()
        self.SetCanSave(True)

    def PreviousSequence(self):
        print "PreviousSequence"
        if self.currentSubId > 0:
            self.currentSubId -= 1
        self.ActivateSequence()
        self.RepeatSequence()
        self.SetCanSave(True)

    def ActivateSequence(self):
        print "ActivateSequence"
        self.state = Core.WAIT_BEGIN
        self.player.SetNextCallbackTime(self.subList[ self.currentSubId].GetTimeBegin())
        self.sequence = self.sequenceList[self.currentSubId]

        self.validSequence = self.sequence.IsValid()

        print "ActivateSequence: loaded"
        self.gui.SetSequenceNumber(self.currentSubId, len(self.subList))
        self.gui.SetSequence(self.sequence)
        self.ActivateTranslation()
        self.UpdateStats()
        print "ActivateSequence: end"




    def ActivateTranslation(self):
        print "ActivateTranslation"
        if not self.translationList:
            print "absent"
            self.gui.SetTranslation("")
        else:
            print "present"
            translation = ""
            currentBegin = self.subList[ self.currentSubId].GetTimeBegin()
            currentEnd = self.subList[ self.currentSubId].GetTimeEnd()
            for sub in self.translationList:
                begin = sub.GetTimeBegin()
                end = sub.GetTimeEnd()
                if (begin >= currentBegin and begin <= currentEnd) or (end >= currentBegin and end <= currentEnd) or (begin <= currentBegin and end >= currentEnd):
                    print "concat"
                    translation +=  sub.GetText() + " "

            self.gui.SetTranslation(translation)

    def UpdateStats(self):
        print "UpdateStats"
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

    def GotoSequenceBegin(self):
        print "GotoSequenceBegin"
        self.state = Core.WAIT_END
        begin_time = self.subList[self.currentSubId].GetTimeBegin() - 1000
        if begin_time < 0:
            begin_time = 0
        self.player.Seek(begin_time)
        self.player.SetNextCallbackTime(self.subList[self.currentSubId].GetTimeEnd())
        self.SetCanSave(True)

    def WriteCharacter(self, character):
        if character == "apostrophe":
            character = "'"
        if re.match('^[0-9\'a-zA-Z]$',character):
            self.sequence.WriteCharacter(character)
            self.gui.SetSequence(self.sequence)
            self.ValidateSequence()
        self.SetCanSave(True)


    def NextWord(self):
        self.sequence.NextWord(False)
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
        print "TooglePause " + str(self.player.IsPaused()) + " " + str(self.paused)
        if self.player.IsPaused() and self.paused:
            self.player.Play()
            self.paused = False
        elif not self.player.IsPaused() and not self.paused:
            self.player.Pause()
            self.paused = True

    def SeekSequence(self, time):
        begin_time = self.subList[self.currentSubId].GetTimeBegin() - 1000
        if begin_time < 0:
            begin_time = 0

        pos = begin_time + time
        self.player.Seek(pos)
        self.player.SetNextCallbackTime(self.subList[self.currentSubId].GetTimeEnd() + 500)
        self.state = Core.WAIT_END
        self.player.Play()
        self.paused = False


    def timeUpdateThread(self):
        timeUpdateThreadId = self.timeUpdateThreadId
        #gtk.gdk.threads_enter()
        #self.time_label.set_text("00:00 / 00:00")
        #gtk.gdk.threads_leave()
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

    def Save(self):

        if self.outputSavePath == "":
            self.outputSavePath = self.gui.AskSavePath()

        if self.outputSavePath == "":
            return

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

        self.SetCanSave(False)

    def LoadExercice(self, path):
        loader = ExerciceLoader()
        if not loader.Load(path):
            return

        if not self.VerifyPath(loader.GetVideoPath(), loader.GetExercicePath(), loader.GetTranslationPath()):
            self.outputSavePath = path
            self.gui.SetTitle(self.outputSavePath, False)
            self.videoPath = loader.GetVideoPath()
            self.exercicePath = loader.GetExercicePath()
            self.translationPath = loader.GetTranslationPath()
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
