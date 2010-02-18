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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Perroquet. If not, see <http://www.gnu.org/licenses/>.

from subtitles_loader import SubtitlesLoader
from sequence import Sequence
import os

class SubExercise(object):

    def __init__(self, parent):
        self.subtitles = SubtitlesLoader()
        self.currentSequenceId = 0
        self.sequenceList = []
        self.parent = parent

    def Initialize(self):
        self.LoadSubtitles()

    def LoadSubtitles(self):

        self.subList = self.subtitles.GetSubtitleList(self.exercisePath)
        self.subList = self.subtitles.CompactSubtitlesList(self.subList, self.parent.timeBetweenSequence, self.parent.maxSequenceLength)

        self.translationList = None
        if self.translationPath != "":
            self.translationList = self.subtitles.GetSubtitleList(self.translationPath)

        oldSequenceList = self.sequenceList

        self.sequenceList = []

        for sub in self.subList:
            self.sequence = Sequence()
            self.sequence.load(sub.GetText())
            self.sequence.setTimeBegin(sub.GetTimeBegin())
            self.sequence.setTimeEnd(sub.GetTimeEnd())
            self.sequenceList.append(self.sequence)

        #Restore found words
        if len(oldSequenceList) > 0:
            oldSequenceIndex = 0
            newSequenceIndex = 0

            oldWordIndex = 0
            newWordIndex = 0

            while oldSequenceIndex < len( oldSequenceList) and newSequenceIndex < len(self.sequenceList):

                if oldWordIndex >= oldSequenceList[oldSequenceIndex].getWordCount():
                    oldSequenceIndex += 1
                    oldWordIndex = 0

                    if oldSequenceIndex >= len(oldSequenceList):
                        break

                if newWordIndex >= len(self.sequenceList[newSequenceIndex].getWords()):
                    newSequenceIndex += 1
                    newWordIndex = 0

                    if newSequenceIndex >= len(self.sequenceList):
                        break

                self.sequenceList[newSequenceIndex].getWords()[newWordIndex].setText(oldSequenceList[oldSequenceIndex].getWords()[oldWordIndex].getText())
                oldWordIndex += 1
                newWordIndex += 1



    def ExtractWordList(self):
        wordList = []

        for sequence in self.sequenceList:
            for word in sequence.getWords():
                wordList.append(word.getValid())

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
        self.currentSequenceValid = self.currentSequence.isValid()

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
        if id >= len(self.sequenceList):
            self.currentSequenceId = len(self.sequenceList)-1
        else:
            self.currentSequenceId = id

    def GetSequenceList(self):
        return self.sequenceList

    def getCurrentSequence(self):
        return self.sequenceList[self.currentSequenceId]

    def getCurrentSequenceId(self):
        return self.currentSequenceId

    def GetSequenceCount(self):
        return len(self.sequenceList)

    def GetVideoPath(self):
        return self.videoPath

    def GetExercisePath(self):
        return self.exercisePath

    def GetTranslationPath(self):
        return self.translationPath

    def GetTranslationList(self):
        return self.translationList
