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
from xml.dom.minidom import getDOMImplementation

from lib import get_text, update_sequence_list
from perroquetlib.model.languages_manager import LanguagesManager
from perroquetlib.model.sub_exercise import SubExercise

VERSION = "1.1.0"

def save(exercise, outputPath):

    impl = getDOMImplementation()

    newdoc = impl.createDocument(None, "perroquet", None)
    root_element = newdoc.documentElement

    # Version
    xml_version = newdoc.createElement("version")
    xml_version.appendChild(newdoc.createTextNode(VERSION))
    root_element.appendChild(xml_version)

    #Name
    if exercise.get_name() != None:
        xml_node = newdoc.createElement("name")
        xml_node.appendChild(newdoc.createTextNode(exercise.get_name()))
        root_element.appendChild(xml_node)

    #Language
    if exercise.get_language_id() != None:
        xml_node = newdoc.createElement("language")
        xml_node.appendChild(newdoc.createTextNode(exercise.get_language_id()))
        root_element.appendChild(xml_node)

    #Template
    xml_node = newdoc.createElement("template")
    xml_node.appendChild(newdoc.createTextNode(str(exercise.is_template())))
    root_element.appendChild(xml_node)

    #RandomOrder
    xml_node = newdoc.createElement("random_order")
    xml_node.appendChild(newdoc.createTextNode(str(exercise.is_random_order())))
    root_element.appendChild(xml_node)

    #Locks
    xml_locks = newdoc.createElement("locks")

    if exercise.is_lock_help():
        xml_lock = newdoc.createElement("help_lock")
        xml_locks.appendChild(xml_lock)

    if exercise.is_lock_properties():
        xml_lock = newdoc.createElement("properties_lock")
        if exercise.lock_properties_password is not None or exercise.lock_properties_salt is not None:
            xml_node = newdoc.createElement("hash")
            xml_node.appendChild(newdoc.createTextNode(str(exercise.lock_properties_password)))
            xml_lock.appendChild(xml_node)

            xml_node = newdoc.createElement("salt")
            xml_node.appendChild(newdoc.createTextNode(str(exercise.lock_properties_salt)))
            xml_lock.appendChild(xml_node)

        xml_locks.appendChild(xml_lock)

    if exercise.is_lock_correction():
        xml_lock = newdoc.createElement("correction_lock")
        if exercise.lock_correction_password is not None or exercise.lock_correction_salt is not None:
            xml_node = newdoc.createElement("hash")
            xml_node.appendChild(newdoc.createTextNode(str(exercise.lock_correction_password)))
            xml_lock.appendChild(xml_node)

            xml_node = newdoc.createElement("salt")
            xml_node.appendChild(newdoc.createTextNode(str(exercise.lock_correction_salt)))
            xml_lock.appendChild(xml_node)

        xml_locks.appendChild(xml_lock)

    root_element.appendChild(xml_locks)


    #Exercise
    xml_exercise = newdoc.createElement("exercise")

    xml_current_sequence = newdoc.createElement("current_sequence")
    xml_current_sequence.appendChild(newdoc.createTextNode(str(exercise.get_current_sequence_id())))
    xml_exercise.appendChild(xml_current_sequence)

    xml_current_word = newdoc.createElement("current_word")
    xml_current_word.appendChild(newdoc.createTextNode(str(exercise.get_current_sequence().get_active_word_index())))
    xml_exercise.appendChild(xml_current_word)

    root_element.appendChild(xml_exercise)

    #Exercise - SubExercises
    for subExo in exercise.subExercisesList:
        xml_subExo = newdoc.createElement("sub_exercise")
        xml_exercise.appendChild(xml_subExo)

        #Paths
        xml_paths = newdoc.createElement("paths")
        xml_subExo.appendChild(xml_paths)

        xml_video_paths = newdoc.createElement("video")
        xml_video_paths.appendChild(newdoc.createTextNode(subExo.get_video_export_path()))
        xml_paths.appendChild(xml_video_paths)

        xml_exercice_paths = newdoc.createElement("exercise")
        xml_exercice_paths.appendChild(newdoc.createTextNode(subExo.get_exercise_export_path()))
        xml_paths.appendChild(xml_exercice_paths)

        xml_translation_paths = newdoc.createElement("translation")
        xml_translation_paths.appendChild(newdoc.createTextNode(subExo.get_translation_export_path()))
        xml_paths.appendChild(xml_translation_paths)

        xml_sequences = newdoc.createElement("sequences")
        xml_subExo.appendChild(xml_sequences)
        for id, sequence in enumerate(subExo.get_sequence_list()):
            if sequence.is_valid():
                xml_sequence = newdoc.createElement("sequence")
                xml_sequence_id = newdoc.createElement("id")
                xml_sequence_id.appendChild(newdoc.createTextNode(str(id)))
                xml_sequence.appendChild(xml_sequence_id)
                xml_sequence_state = newdoc.createElement("state")
                xml_sequence_state.appendChild(newdoc.createTextNode("done"))
                xml_sequence.appendChild(xml_sequence_state)

                repeat_count = sequence.get_repeat_count()
                xml_sequence_repeat_count = newdoc.createElement("repeat_count")
                xml_sequence_repeat_count.appendChild(newdoc.createTextNode(str(repeat_count)))
                xml_sequence.appendChild(xml_sequence_repeat_count)

                xml_sequences.appendChild(xml_sequence)
            elif not sequence.is_empty():
                xml_sequence = newdoc.createElement("sequence")
                xml_sequence_id = newdoc.createElement("id")
                xml_sequence_id.appendChild(newdoc.createTextNode(str(id)))
                xml_sequence.appendChild(xml_sequence_id)
                xml_sequence_state = newdoc.createElement("state")
                xml_sequence_state.appendChild(newdoc.createTextNode("in_progress"))
                xml_sequence.appendChild(xml_sequence_state)

                repeat_count = sequence.get_repeat_count()
                xml_sequence_repeat_count = newdoc.createElement("repeat_count")
                xml_sequence_repeat_count.appendChild(newdoc.createTextNode(str(repeat_count)))
                xml_sequence.appendChild(xml_sequence_repeat_count)

                xml_sequence_words = newdoc.createElement("words")

                for word in (w.get_text() for w in sequence.get_words()):
                    xml_sequence_word = newdoc.createElement("word")
                    xml_sequence_word.appendChild(newdoc.createTextNode(word))
                    xml_sequence_words.appendChild(xml_sequence_word)

                xml_sequence.appendChild(xml_sequence_words)

                xml_sequences.appendChild(xml_sequence)

    #Stats
    xml_stats = newdoc.createElement("stats")

    xml_repeatCount = newdoc.createElement("repeat_count")
    xml_repeatCount.appendChild(newdoc.createTextNode(str(exercise.get_repeat_count())))
    xml_stats.appendChild(xml_repeatCount)

    root_element.appendChild(xml_stats)

    #Properties
    xml_properties = newdoc.createElement("properties")

    xml_repeatAfterComplete = newdoc.createElement("repeat_after_complete")
    xml_repeatAfterComplete.appendChild(newdoc.createTextNode(str(exercise.get_repeat_after_completed())))
    xml_properties.appendChild(xml_repeatAfterComplete)

    xml_use_dynamic_correction = newdoc.createElement("use_dynamic_correction")
    xml_use_dynamic_correction.appendChild(newdoc.createTextNode(str(exercise.is_use_dynamic_correction())))
    xml_properties.appendChild(xml_use_dynamic_correction)

    xml_maxSequenceLength = newdoc.createElement("max_sequence_length")
    xml_maxSequenceLength.appendChild(newdoc.createTextNode(str(exercise.get_max_sequence_length())))
    xml_properties.appendChild(xml_maxSequenceLength)

    xml_timeBetweenSequences = newdoc.createElement("time_between_sequence")
    xml_timeBetweenSequences.appendChild(newdoc.createTextNode(str(exercise.get_time_between_sequence())))
    xml_properties.appendChild(xml_timeBetweenSequences)

    xml_playMarginBefore = newdoc.createElement("play_margin_before")
    xml_playMarginBefore.appendChild(newdoc.createTextNode(str(exercise.get_play_margin_before())))
    xml_properties.appendChild(xml_playMarginBefore)

    xml_playMarginAfter = newdoc.createElement("play_margin_after")
    xml_playMarginAfter.appendChild(newdoc.createTextNode(str(exercise.get_play_margin_after())))
    xml_properties.appendChild(xml_playMarginAfter)

    xml_repeat_count_by_sequence_limit = newdoc.createElement("repeat_count_by_sequence_limit")
    xml_repeat_count_by_sequence_limit.appendChild(newdoc.createTextNode(str(exercise.get_repeat_count_limit_by_sequence())))
    xml_properties.appendChild(xml_repeat_count_by_sequence_limit)

    root_element.appendChild(xml_properties)

    xml_string = newdoc.toprettyxml()
    xml_string = xml_string.encode('utf8')

    f = open(outputPath, 'w')
    f.write(xml_string)
    f.close()






def load(exercise, dom, path):
    #Name
    if len(dom.getElementsByTagName("name")) > 0:
        exercise.set_name(get_text(dom.getElementsByTagName("name")[0].childNodes))

    #Language
    if len(dom.getElementsByTagName("language")) > 0:
        exercise.set_language_id(get_text(dom.getElementsByTagName("language")[0].childNodes))
    else:
        languageManager = LanguagesManager()
        exercise.set_language_id(languageManager.get_default_language().id)

    #Template
    if len(dom.getElementsByTagName("template")) > 0:
        exercise.set_template(get_text(dom.getElementsByTagName("template")[0].childNodes) == "True")

    #Random order
    if len(dom.getElementsByTagName("random_order")) > 0:
        exercise.set_random_order(get_text(dom.getElementsByTagName("random_order")[0].childNodes) == "True")

    #Locks
    if len(dom.getElementsByTagName("locks")) > 0:
        xml_locks = dom.getElementsByTagName("locks")[0]
        #Correction lock
        if len(xml_locks.getElementsByTagName("correction_lock")) > 0:
            exercise.lock_correction = True
            xml_lock = xml_locks.getElementsByTagName("correction_lock")[0]
            if len(xml_lock.getElementsByTagName("hash")) > 0:
                exercise.lock_correction_password = get_text(xml_lock.getElementsByTagName("hash")[0].childNodes)
            if len(xml_lock.getElementsByTagName("salt")) > 0:
                exercise.lock_correction_salt = get_text(xml_lock.getElementsByTagName("salt")[0].childNodes)

        #Properties lock
        if len(xml_locks.getElementsByTagName("properties_lock")) > 0:
            exercise.lock_properties = True
            xml_lock = xml_locks.getElementsByTagName("properties_lock")[0]
            if len(xml_lock.getElementsByTagName("hash")) > 0:
                exercise.lock_properties_password = get_text(xml_lock.getElementsByTagName("hash")[0].childNodes)
            if len(xml_lock.getElementsByTagName("salt")) > 0:
                exercise.lock_properties_salt = get_text(xml_lock.getElementsByTagName("salt")[0].childNodes)

        #Help lock
        if len(xml_locks.getElementsByTagName("help_lock")) > 0:
            exercise.lock_help = True


    #Exercise
    xml_exercise = dom.getElementsByTagName("exercise")[0]

    #Exercise - CurrentWord
    currentWord = int(get_text(xml_exercise.getElementsByTagName("current_word")[0].childNodes))
    #Exercise - CurrentSequence
    currentSequence = int(get_text(xml_exercise.getElementsByTagName("current_sequence")[0].childNodes))


    # Stats
    xml_stats = dom.getElementsByTagName("stats")[0]
    exercise.set_repeat_count(int(get_text(xml_stats.getElementsByTagName("repeat_count")[0].childNodes)))

    # Properties
    if len(dom.getElementsByTagName("properties")) > 0:
        xml_properties = dom.getElementsByTagName("properties")[0]
        if len(xml_properties.getElementsByTagName("repeat_after_complete")) > 0:
            exercise.set_repeat_after_completed(get_text(xml_properties.getElementsByTagName("repeat_after_complete")[0].childNodes) == "True")
        if len(xml_properties.getElementsByTagName("time_between_sequence")) > 0:
            exercise.set_time_between_sequence(float(get_text(xml_properties.getElementsByTagName("time_between_sequence")[0].childNodes)))
        if len(xml_properties.getElementsByTagName("max_sequence_length")) > 0:
            exercise.set_max_sequence_length(float(get_text(xml_properties.getElementsByTagName("max_sequence_length")[0].childNodes)))
        if len(xml_properties.getElementsByTagName("play_margin_before")) > 0:
            exercise.set_play_margin_before(int(get_text(xml_properties.getElementsByTagName("play_margin_before")[0].childNodes)))
        if len(xml_properties.getElementsByTagName("play_margin_after")) > 0:
            exercise.set_play_margin_after(int(get_text(xml_properties.getElementsByTagName("play_margin_after")[0].childNodes)))
        if len(xml_properties.getElementsByTagName("use_dynamic_correction")) > 0:
            exercise.set_use_dynamic_correction(get_text(xml_properties.getElementsByTagName("use_dynamic_correction")[0].childNodes) == "True")
        if len(xml_properties.getElementsByTagName("repeat_count_by_sequence_limit")) > 0:
            exercise.set_repeat_count_limit_by_sequence(int(get_text(xml_properties.getElementsByTagName("repeat_count_by_sequence_limit")[0].childNodes)))


    #Subexercises
    subExos = []
    for xml_subExercise in xml_exercise.getElementsByTagName("sub_exercise"):
        subExercise = SubExercise(exercise)

        #Sequences
        xml_sequences = xml_subExercise.getElementsByTagName("sequences")[0]

        progress = []

        for xml_sequence in xml_sequences.getElementsByTagName("sequence"):
            id = int(get_text(xml_sequence.getElementsByTagName("id")[0].childNodes))
            state = get_text(xml_sequence.getElementsByTagName("state")[0].childNodes)
            #Sequence repeat count
            if len(xml_sequence.getElementsByTagName("repeat_count")) > 0:
                repeat_count = int(get_text(xml_sequence.getElementsByTagName("repeat_count")[0].childNodes))
            else:
                repeat_count = 0
            words = []

            if state == "in_progress":
                xml_words = xml_sequence.getElementsByTagName("words")[0]
                for xml_world in xml_words.getElementsByTagName("word"):
                    words.append(get_text(xml_world.childNodes))

            progress.append((id, state, words, repeat_count))

        #Paths
        xml_paths = xml_subExercise.getElementsByTagName("paths")[0]
        subExercise.set_video_path(get_text(xml_paths.getElementsByTagName("video")[0].childNodes))
        subExercise.set_exercise_path(get_text(xml_paths.getElementsByTagName("exercise")[0].childNodes))
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

    update_sequence_list(exercise, subExos)

    exercise.goto_sequence(currentSequence)

    exercise.get_current_sequence().set_active_word_index(currentWord)

    if not exercise.is_template():
        exercise.set_output_save_path(path)

    return exercise
