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
from sequence import Sequence   #Can be removed ?
from sub_exercise import SubExercise
from languages_manager import LanguagesManager
from perroquetlib.config import config
import os, re, random, copy

class Exercise(object):

    def __init__(self):
        self.subtitles = SubtitlesLoader()
        self.repeatCount = 0
        self.currentSubExerciseId = 0
        self.subExercisesList = []
        self.currentSubExercise = None
        self.repeatAfterCompeted = True
        self.maxSequenceLength = 60.0
        self.timeBetweenSequence = 0.0
        self.outputSavePath = None
        self.template = False
        self.name = None
        self.mediaChangeCallback = None
        self.language = None
        self.randomOrder = False
        self.playMarginAfter = 500
        self.playMarginBefore = 1000

    def Initialize(self):
        self._LoadSubtitles()
        if self.randomOrder:
            self.order = [x for x in range(self.GetSequenceCount())]
            random.shuffle(self.order)
            self.reverseOrder = copy.copy(self.order)
            for i,j in enumerate(self.order):
                self.reverseOrder[j] = i

    def new(self):
        if len(self.subExercisesList) == 0:
            self.currentSubExercise = SubExercise(self)
            self.subExercisesList.append(self.currentSubExercise)
            self.currentSubExerciseId = 0
            self.currentSequenceId = 0
            languageManager = LanguagesManager()
            self.language = languageManager.getDefaultLanguage()

            self.maxSequenceLength = float(config.Get("default_exercise_max_sequence_length"))/1000
            self.timeBetweenSequence = float(config.Get("default_exercise_time_between_sequences"))/1000
            self.playMarginAfter = config.Get("default_exercise_play_margin_before")
            self.playMarginBefore = config.Get("default_exercise_play_margin_after")

    def _LoadSubtitles(self):

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
                if self.currentSubExercise != subExo:
                    self.currentSubExercise = subExo
                    self.notifyMediaChange()
                return True
            else:
                localId -= len(subExo.GetSequenceList())


        self.GotoSequence(self.GetSequenceCount()-1)
        return False


    def GotoNextSequence(self):

        if self.randomOrder:
            randomId = self.reverseOrder[self.currentSequenceId]
            randomId += 1
            if randomId >= len(self.order):
                randomId = 0
            return self.GotoSequence(self.order[randomId])
        else:
            return self.GotoSequence(self.currentSequenceId+1)

    def GotoPreviousSequence(self):


        if self.randomOrder:
            randomId = self.reverseOrder[self.currentSequenceId]
            randomId -= 1
            if randomId < 0:
                randomId = len(self.order)-1
            return self.GotoSequence(self.order[randomId])
        else:
            if self.currentSequenceId > 0:
                return self.GotoSequence(self.currentSequenceId-1)
            else:
                return False



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
        self.currentSubExercise.SetVideoPath(videoPath)

    def SetExercisePath(self, exercisePath):
        self.currentSubExercise.SetExercisePath(exercisePath)

    def SetTranslationPath(self, translationPath):
        self.currentSubExercise.SetTranslationPath(translationPath)

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
        return self.currentSubExercise.GetVideoPath()

    def GetExercisePath(self):
        return self.currentSubExercise.GetExercisePath()

    def GetTranslationPath(self):
        return self.currentSubExercise.GetTranslationPath()

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

    def isRandomOrder(self):
        return self.randomOrder

    def setRandomOrder(self, isRandomOrder):
        self.randomOrder = isRandomOrder

    def setMediaChangeCallback(self, mediaChangeCallback):
        self.mediaChangeCallback = mediaChangeCallback

    def notifyMediaChange(self):
        if self.mediaChangeCallback != None:
            self.mediaChangeCallback()


    def setLanguageId(self, langId):
        languageManager = LanguagesManager()
        self.language =languageManager.getLanguageById(langId)

    def getLanguageId(self):
        (langId, langName, langCharList) = self.language
        return langId

    def isCharacterMatch(self,char):
        (langId, langName, langCharList) = self.language
        return re.match('^['+langCharList+']$',char)

    def getPlayMarginBefore(self):
        return self.playMarginBefore

    def setPlayMarginBefore(self, margin):
        self.playMarginBefore = margin

    def getPlayMarginAfter(self):
        return self.playMarginAfter

    def setPlayMarginAfter(self, margin):
        self.playMarginAfter = margin
