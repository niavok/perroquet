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

import os

from perroquetlib.model.sub_exercise import SubExercise
from perroquetlib.model.languages_manager import LanguagesManager

from lib import get_text

VERSION = "1.0.0"

def save(path):
    raise NotImplementedError

def load(self, exercise, dom, path):
    #Name
    exercise.set_name(None)

    #Language
    languageManager = LanguagesManager()
    exercise.set_language_id(languageManager.get_default_language().id)

    #Template
    exercise.set_template(False)

    #Random order
    exercise.set_random_order(False)

    xml_progress = dom.getElementsByTagName("progress")[0]
    currentSequence = int(get_text(xml_progress.getElementsByTagName("current_sequence")[0].childNodes))
    currentWord = int(get_text(xml_progress.getElementsByTagName("current_word")[0].childNodes))

    xml_sequences = xml_progress.getElementsByTagName("sequences")[0]

    progress = []

    for xml_sequence in xml_sequences.getElementsByTagName("sequence"):
        id = int(get_text(xml_sequence.getElementsByTagName("id")[0].childNodes))
        state = get_text(xml_sequence.getElementsByTagName("state")[0].childNodes)
        words = []
        repeat_count = 0

        if state == "in_progress":
            xml_words = xml_sequence.getElementsByTagName("words")[0]
            for xml_world in xml_words.getElementsByTagName("word"):
                words.append(get_text(xml_world.childNodes))

        progress.append((id, state, words, repeat_count))


    # Stats
    xml_stats = dom.getElementsByTagName("stats")[0]
    exercise.set_repeat_count(int(get_text(xml_stats.getElementsByTagName("repeat_count")[0].childNodes)))

    #Subexercises
    subExos = []

    subExercise = SubExercise(exercise)

    #Sequences
    progress = []

    xml_progress = dom.getElementsByTagName("progress")[0]
    xml_sequences = xml_progress.getElementsByTagName("sequences")[0]
    for xml_sequence in xml_sequences.getElementsByTagName("sequence"):
        id = int(get_text(xml_sequence.getElementsByTagName("id")[0].childNodes))
        state = get_text(xml_sequence.getElementsByTagName("state")[0].childNodes)
        words = []

        if state == "in_progress":
            xml_words = xml_sequence.getElementsByTagName("words")[0]
            for xml_world in xml_words.getElementsByTagName("word"):
                words.append(get_text(xml_world.childNodes))

        progress.append((id, state, words))

    #Paths
    xml_paths = dom.getElementsByTagName("paths")[0]
    subExercise.set_video_path(get_text(xml_paths.getElementsByTagName("video")[0].childNodes))
    subExercise.set_exercise_path(get_text(xml_paths.getElementsByTagName("exercice")[0].childNodes))
    subExercise.set_translation_path(get_text(xml_paths.getElementsByTagName("translation")[0].childNodes))

    exercise.subExercisesList.append(subExercise)

    subExos.append(progress)

    #Convert relative path
    for subExo in exercise.subExercisesList:
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

    exercise.initialize()

    self.update_sequence_list()
    exercise.goto_sequence(currentSequence)
    exercise.get_current_sequence().set_active_word_index(currentWord)

    if not exercise.is_template():
        exercise.set_output_save_path(path)

    return exercise

