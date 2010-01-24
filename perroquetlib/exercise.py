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

from subtitles_loader import SubtitlesLoader
from sequence import Sequence
import os

class Exercise(object):

    def __init__(self):
        self.subtitles = SubtitlesLoader()
        self.repeatCount = 0
        self.currentSequenceId = 0
        self.sequenceList = []
        self.repeatAfterCompeted = True

    def Initialize(self):
        self.LoadSubtitles()



    def LoadSubtitles(self):

        self.subList = self.subtitles.GetSubtitleList(self.exercisePath)
        self.subList = self.subtitles.CompactSubtitlesList(self.subList)

        self.translationList = None
        if self.translationPath != "":
            self.translationList = self.subtitles.GetSubtitleList(self.translationPath)

        self.sequenceList = []
        for sub in self.subList:
            self.sequence = Sequence()
            self.sequence.Load(sub.GetText())
            self.sequence.SetTimeBegin(sub.GetTimeBegin())
            self.sequence.SetTimeEnd(sub.GetTimeEnd())
            self.sequenceList.append(self.sequence)


    def ExtractWordList(self):
        wordList = []

        for sequence in self.sequenceList:
            sequenceWordList = sequence.GetWordList()
            for word in sequenceWordList:
                wordList.append(word.lower())

        wordList = list(set(wordList))
        wordList.sort()
        return wordList

    def GotoSequence(self, id):
        self.currentSequenceId = id
        self.UpdateCurrentInfos()

    def GotoNextSequence(self):
        if self.currentSequenceId < len(self.sequenceList)-1:
            self.currentSequenceId += 1
            self.UpdateCurrentInfos()
            return True
        else:
            return False

    def GotoPreviousSequence(self):
        if self.currentSequenceId > 0:
            self.currentSequenceId -= 1
            self.UpdateCurrentInfos()
            return True
        else:
            return False


    def UpdateCurrentInfos(self):
        self.currentSequence = self.sequenceList[self.currentSequenceId]
        self.currentSequenceValid = self.currentSequence.IsValid()

    def IsPathsValid(self):
        error = False
        errorList = []
        if not os.path.exists(self.videoPath):
            error = True;
            errorList.append(self.videoPath)

        if not os.path.exists(self.exercisePath):
            error = True;
            errorList.append(self.exercisePath)

        if self.translationPath != "" and not os.path.exists(self.translationPath):
            error = True;
            errorList.append(self.translationPath)

        return (not error), errorList

    def IncrementRepeatCount(self):
        self.repeatCount += 1

    def SetVideoPath(self, videoPath):
        self.videoPath = videoPath

    def SetExercisePath(self, exercisePath):
        self.exercisePath = exercisePath

    def SetTranslationPath(self, translationPath):
        self.translationPath = translationPath

    def SetCurrentSequence(self, id):
        self.currentSequenceId = id

    def GetSequenceList(self):
        return self.sequenceList

    def GetCurrentSequence(self):
        return self.sequenceList[self.currentSequenceId]

    def GetCurrentSequenceId(self):
        return self.currentSequenceId

    def GetSequenceCount(self):
        return len(self.sequenceList)

    def SetRepeatCount(self, count):
        self.repeatCount = count

    def GetRepeatCount(self):
        return self.repeatCount

    def GetVideoPath(self):
        return self.videoPath

    def GetExercisePath(self):
        return self.exercisePath

    def GetTranslationPath(self):
        return self.translationPath

    def GetTranslationList(self):
        return self.translationList

    def SetRepeatAfterCompleted(self, state):
        self.repeatAfterCompeted = state

    def GetRepeatAfterCompleted(self):
        return self.repeatAfterCompeted
