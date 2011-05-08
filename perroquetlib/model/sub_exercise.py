# -*- coding: utf-8 -*-

# Copyright (C) 2009-2011 Frédéric Bertolus.
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



import os

from perroquetlib.model.sequence import SequenceDynamicCorrection
from perroquetlib.model.sequence import SequenceSimple
from subtitles_loader import SubtitlesLoader


class SubExercise(object):

    def __init__(self, parent):
        self.subtitles = SubtitlesLoader()
        self.currentSequenceId = 0
        self.sequenceList = []
        self.parent = parent
        self.videoExportPath = None
        self.exerciseExportPath = None
        self.translationExportPath = None

    def load_subtitles(self):

        self.subList = self.subtitles.get_subtitle_list(self.exercisePath)
        self.subList = self.subtitles.compact_subtitles_list(self.subList, self.parent.timeBetweenSequence, self.parent.maxSequenceLength)

        self.translationList = None
        if self.translationPath != "":
            self.translationList = self.subtitles.get_subtitle_list(self.translationPath)

        oldSequenceList = self.sequenceList

        self.sequenceList = []

        for sub in self.subList:
            if self.parent.is_use_dynamic_correction():
                sequence = SequenceDynamicCorrection(self.parent.language)
            else:
                sequence = SequenceSimple(self.parent.language)
            sequence.load(sub.get_text())
            sequence.set_time_begin(sub.get_time_begin())
            sequence.set_time_end(sub.get_time_end())
            self.sequenceList.append(sequence)

        #Restore found words
        if len(oldSequenceList) > 0:
            oldSequenceIndex = 0
            newSequenceIndex = 0

            oldWordIndex = 0
            newWordIndex = 0

            while oldSequenceIndex < len(oldSequenceList) and newSequenceIndex < len(self.sequenceList):

                if oldWordIndex >= oldSequenceList[oldSequenceIndex].get_word_count():
                    oldSequenceIndex += 1
                    oldWordIndex = 0

                    if oldSequenceIndex >= len(oldSequenceList):
                        break

                if newWordIndex >= len(self.sequenceList[newSequenceIndex].get_words()):
                    newSequenceIndex += 1
                    newWordIndex = 0

                    if newSequenceIndex >= len(self.sequenceList):
                        break

                self.sequenceList[newSequenceIndex].get_words()[newWordIndex].set_text(oldSequenceList[oldSequenceIndex].get_words()[oldWordIndex].get_text())
                oldWordIndex += 1
                newWordIndex += 1



    def extract_word_list(self):
        wordList = []

        for sequence in self.sequenceList:
            for word in sequence.get_words():
                wordList.append(word.get_valid())

        return wordList

    def goto_sequence(self, id):
        self.currentSequenceId = id
        self.update_current_infos()

    def goto_next_sequence(self):
        if self.currentSequenceId < len(self.sequenceList)-1:
            self.currentSequenceId += 1
            self.update_current_infos()
            return True
        else:
            return False

    def goto_previous_sequence(self):
        if self.currentSequenceId > 0:
            self.currentSequenceId -= 1
            self.update_current_infos()
            return True
        else:
            return False

    def update_current_infos(self):
        self.currentSequence = self.sequenceList[self.currentSequenceId]
        self.currentSequenceValid = self.currentSequence.is_valid()

    def is_paths_valid(self):
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

    def increment_repeat_count(self):
        self.repeatCount += 1

    def set_video_path(self, videoPath):
        self.videoPath = videoPath

    def set_exercise_path(self, exercisePath):
        self.exercisePath = exercisePath

    def set_translation_path(self, translationPath):
        self.translationPath = translationPath

    #Define path to use when the parent file is exported
    def set_video_export_path(self, videoPath):
        self.videoExportPath = videoPath

    #Define path to use when the parent file is exported
    def set_exercise_export_path(self, exercisePath):
        self.exerciseExportPath = exercisePath

    #Define path to use when the parent file is exported
    def set_translation_export_path(self, translationPath):
        self.translationExportPath = translationPath

    def set_current_sequence(self, id):
        if id >= len(self.sequenceList):
            self.currentSequenceId = len(self.sequenceList)-1
        else:
            self.currentSequenceId = id

    def get_sequence_list(self):
        return self.sequenceList

    def get_current_sequence(self):
        return self.sequenceList[self.currentSequenceId]

    def get_current_sequence_id(self):
        return self.currentSequenceId

    def get_sequence_count(self):
        return len(self.sequenceList)

    def get_video_path(self):
        return self.videoPath

    def get_exercise_path(self):
        return self.exercisePath

    def get_translation_path(self):
        return self.translationPath

    #get path to use when the parent file is exported. If no specila
    #path is set, the absolute path is used
    def get_video_export_path(self):
        if self.videoExportPath:
            return self.videoExportPath
        else:
            return self.videoPath

    #get path to use when the parent file is exported. If no specila
    #path is set, the absolute path is used
    def get_exercise_export_path(self):
        if self.exerciseExportPath:
            return self.exerciseExportPath
        else:
            return self.exercisePath

    #get path to use when the parent file is exported. If no specila
    #path is set, the absolute path is used
    def get_translation_export_path(self):
        if self.translationExportPath:
            return self.translationExportPath
        else:
            return self.translationPath

    def get_translation_list(self):
        return self.translationList
