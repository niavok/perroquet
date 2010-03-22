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

from xml.dom.minidom import getDOMImplementation, parse
import os

from exercise import Exercise
from sub_exercise import SubExercise
from perroquetlib.config import config
from languages_manager import LanguagesManager

from exercise_parser import save, load

class ExerciseSaver(object):
    def save(self, exercise, path): 
        save(exercise, path)

class ExerciseLoader(object):

    def load(self, path):
        return load(path)
    
    def _load_v1_0_0(self,dom, path):

        #Name
        self.exercise.set_name(None)

        #Language
        languageManager = LanguagesManager()
        (langId, langName, langChars) = languageManager.get_default_language()
        self.exercise.set_language_id(langId)

        #Template
        self.exercise.set_template(False)

        #Random order
        self.exercise.set_random_order(False)

        xml_progress = dom.getElementsByTagName("progress")[0]
        currentSequence = int(self.get_text(xml_progress.getElementsByTagName("current_sequence")[0].childNodes))
        currentWord = int(self.get_text(xml_progress.getElementsByTagName("current_word")[0].childNodes))

        xml_sequences = xml_progress.getElementsByTagName("sequences")[0]

        self.progress = []

        for xml_sequence in xml_sequences.getElementsByTagName("sequence"):
            id = int(self.get_text(xml_sequence.getElementsByTagName("id")[0].childNodes))
            state = self.get_text(xml_sequence.getElementsByTagName("state")[0].childNodes)
            words = []

            if state == "in_progress":
                xml_words = xml_sequence.getElementsByTagName("words")[0]
                for xml_world in xml_words.getElementsByTagName("word"):
                    words.append(self.get_text(xml_world.childNodes))

            self.progress.append((id, state, words))


        # Stats
        xml_stats = dom.getElementsByTagName("stats")[0]
        self.exercise.set_repeat_count(int(self.get_text(xml_stats.getElementsByTagName("repeat_count")[0].childNodes)))

        #Subexercises
        self.subExo = []

        subExercise = SubExercise(self.exercise)

        #Sequences
        self.progress = []

        xml_progress = dom.getElementsByTagName("progress")[0]
        xml_sequences = xml_progress.getElementsByTagName("sequences")[0]
        for xml_sequence in xml_sequences.getElementsByTagName("sequence"):
            id = int(self.get_text(xml_sequence.getElementsByTagName("id")[0].childNodes))
            state = self.get_text(xml_sequence.getElementsByTagName("state")[0].childNodes)
            words = []

            if state == "in_progress":
                xml_words = xml_sequence.getElementsByTagName("words")[0]
                for xml_world in xml_words.getElementsByTagName("word"):
                    words.append(self.get_text(xml_world.childNodes))

            self.progress.append((id, state, words))

        #Paths
        xml_paths = dom.getElementsByTagName("paths")[0]
        subExercise.set_video_path(self.get_text(xml_paths.getElementsByTagName("video")[0].childNodes))
        subExercise.set_exercise_path(self.get_text(xml_paths.getElementsByTagName("exercice")[0].childNodes))
        subExercise.set_translation_path(self.get_text(xml_paths.getElementsByTagName("translation")[0].childNodes))

        self.exercise.subExercisesList.append(subExercise)

        self.subExo.append(self.progress)

        #Convert relative path
        for subExo in self.exercise.subExercisesList:
            if not os.path.isfile(subExo.get_exercise_path()):
                absPath = os.path.join(os.path.dirname(path), subExo.get_exercise_path())
                if not os.path.isfile(absPath):
                    subExo.set_exercise_path("")
                else:
                    subExo.set_exercise_path(absPath)

            if not os.path.isfile(subExo.get_video_path()):
                absPath = os.path.join(os.path.dirname(path), subExo.get_video_path())
                if not os.path.isfile(absPath):
                    subExo.set_video_path("")
                else:
                    subExo.set_video_path(absPath)

            if not os.path.isfile(subExo.get_translation_path()):
                absPath = os.path.join(os.path.dirname(path), subExo.get_translation_path())
                if not os.path.isfile(absPath):
                    subExo.set_translation_path("")
                else:
                    subExo.set_translation_path(absPath)


        self.exercise.initialize()

        self.update_sequence_list()

        self.exercise.goto_sequence(currentSequence)

        self.exercise.get_current_sequence().set_active_word_index(currentWord)

        if not self.exercise.is_template():
            self.exercise.set_output_save_path(path)

        return self.exercise



