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
from sub_exercise import SubExercise
import os

class Exercise(object):

    def __init__(self):
        self.subtitles = SubtitlesLoader()
        self.repeatCount = 0
        self.currentSubExerciseId = 0
        self.subExercisesList = []
        self.repeatAfterCompeted = True
        self.maxSequenceLength = 60.0
        self.timeBetweenSequence = 0.0
        self.outputSavePath = None
        self.template = False
        self.name = None

    def Initialize(self):
        self.LoadSubtitles()

    def new(self):
        if len(self.subExercisesList) == 0:
            self.currentSubExercise = SubExercise(self)
            self.subExercisesList.append(self.currentSubExercise)
            self.currentSubExerciseId = 0
            self.currentSequenceId = 0

    def LoadSubtitles(self):

        for subExo in self.subExercisesList:
            subExo.LoadSubtitles()


    def ExtractWordList(self):
        wordList = []

        for subExo in self.subExercisesList:
            wordList = wordList + subExo.ExtractWordList()

        #Remove double words and sort
        wordList = list(set(wordList))
        wordList.sort()
        return wordList

    def GotoSequence(self, id):

        self.currentSequenceId = id
        localId = id


        for subExo in self.subExercisesList:
            if localId < len(subExo.GetSequenceList()):
                subExo.SetCurrentSequence(localId)
                self.currentSubExercise = subExo
                return True
            else:
                localId -= len(subExo.GetSequenceCount())


        self.currentSequenceId = self.GotoSequence(self.GetSequenceCount()-1)
        return False


    def GotoNextSequence(self):
        return self.GotoSequence(self.currentSequenceId+1)

    def GotoPreviousSequence(self):
        return self.GotoSequence(self.currentSequenceId-1)

    def IsPathsValid(self):
        error = False
        errorList = []

        for subExo in self.subExercisesList:
            (valid, subErrorList) = subExo.IsPathsValid()
            if not valid:
                error = True
            errorList = errorList + subErrorList

        return (not error), errorList

    def IncrementRepeatCount(self):
        self.repeatCount += 1

    def SetVideoPath(self, videoPath):
        self.subExercisesList[0].SetVideoPath(videoPath)

    def SetExercisePath(self, exercisePath):
        self.subExercisesList[0].SetExercisePath(exercisePath)

    def SetTranslationPath(self, translationPath):
         self.subExercisesList[0].SetTranslationPath(translationPath)

    def getCurrentSequence(self):
        return self.currentSubExercise.getCurrentSequence()

    def getCurrentSequenceId(self):
        return self.currentSequenceId

    def GetSequenceList(self):
        list = []
        for subExo in self.subExercisesList:
            list += subExo.GetSequenceList()
        return list

    def GetSequenceCount(self):
        count = 0
        for subExo in self.subExercisesList:
            count += subExo.GetSequenceCount()
        return count

    def SetRepeatCount(self, count):
        self.repeatCount = count

    def GetRepeatCount(self):
        return self.repeatCount

    def GetVideoPath(self):
        return self.subExercisesList[0].GetVideoPath()

    def GetExercisePath(self):
        return self.subExercisesList[0].GetExercisePath()

    def GetTranslationPath(self):
        return self.subExercisesList[0].GetTranslationPath()

    def GetTranslationList(self):
        return self.currentSubExercise.GetTranslationList()

    def SetRepeatAfterCompleted(self, state):
        self.repeatAfterCompeted = state

    def GetRepeatAfterCompleted(self):
        return self.repeatAfterCompeted

    def SetTimeBetweenSequence(self, time):
        self.timeBetweenSequence = time

    def GetTimeBetweenSequence(self):
        return self.timeBetweenSequence

    def SetMaxSequenceLength(self, time):
        self.maxSequenceLength = time

    def GetMaxSequenceLength(self):
        return self.maxSequenceLength

    def getOutputSavePath(self):
        return self.outputSavePath

    def setOutputSavePath(self, outputSavePath):
        self.outputSavePath = outputSavePath
        self.setTemplate(False)

    def getName(self):
        return self.name

    def setName(self, name):
        self.name = name

    def isTemplate(self):
        return self.template

    def setTemplate(self, isTemplate):
        self.template = isTemplate
