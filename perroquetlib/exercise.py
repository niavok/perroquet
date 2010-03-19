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

import os, re, random, copy

from subtitles_loader import SubtitlesLoader
from sub_exercise import SubExercise
from languages_manager import LanguagesManager
from perroquetlib.config import config

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
            self.order = [x for x in range(self.getSequenceCount())]
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

            self.maxSequenceLength = float(config.get("default_exercise_max_sequence_length"))/1000
            self.timeBetweenSequence = float(config.get("default_exercise_time_between_sequences"))/1000
            self.playMarginAfter = config.get("default_exercise_play_margin_before")
            self.playMarginBefore = config.get("default_exercise_play_margin_after")

            self.repeatAfterCompeted = (config.get("default_exercise_repeat_after_competed") == 1)
            self.randomOrder = (config.get("default_exercise_random_order") == 1)

            self.setLanguageId(config.get("default_exercise_language"))

    def _LoadSubtitles(self):

        for subExo in self.subExercisesList:
            subExo.LoadSubtitles()

    # Reset the work done in the exercise
    def reset(self):
        for sequence in self.getSequenceList():
            sequence.reset()

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
            if localId < len(subExo.getSequenceList()):
                subExo.setCurrentSequence(localId)
                if self.currentSubExercise != subExo:
                    self.currentSubExercise = subExo
                    self.notifyMediaChange()
                return True
            else:
                localId -= len(subExo.getSequenceList())


        self.GotoSequence(self.getSequenceCount()-1)
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

    def setVideoPath(self, videoPath):
        self.currentSubExercise.setVideoPath(videoPath)

    def setExercisePath(self, exercisePath):
        self.currentSubExercise.setExercisePath(exercisePath)

    def setTranslationPath(self, translationPath):
        self.currentSubExercise.setTranslationPath(translationPath)

    def getCurrentSequence(self):
        return self.currentSubExercise.getCurrentSequence()

    def getCurrentSequenceId(self):
        return self.currentSequenceId

    def getSequenceList(self):
        list = []
        for subExo in self.subExercisesList:
            list += subExo.getSequenceList()
        return list

    def getSequenceCount(self):
        count = 0
        for subExo in self.subExercisesList:
            count += subExo.getSequenceCount()
        return count

    def setRepeatCount(self, count):
        self.repeatCount = count

    def getRepeatCount(self):
        return self.repeatCount

    def getVideoPath(self):
        return self.currentSubExercise.getVideoPath()

    def getExercisePath(self):
        return self.currentSubExercise.getExercisePath()

    def getTranslationPath(self):
        return self.currentSubExercise.getTranslationPath()

    def getTranslationList(self):
        return self.currentSubExercise.getTranslationList()

    def setRepeatAfterCompleted(self, state):
        self.repeatAfterCompeted = state

    def getRepeatAfterCompleted(self):
        return self.repeatAfterCompeted

    def setTimeBetweenSequence(self, time):
        self.timeBetweenSequence = time

    def getTimeBetweenSequence(self):
        return self.timeBetweenSequence

    def setMaxSequenceLength(self, time):
        self.maxSequenceLength = time

    def getMaxSequenceLength(self):
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

