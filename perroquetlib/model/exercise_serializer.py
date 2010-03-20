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

class ExerciseSaver(object):


    def save(self,exercise, outputPath):
        self.outputPath = outputPath
        self.config = config

        impl = getDOMImplementation()

        newdoc = impl.createDocument(None, "perroquet", None)
        root_element = newdoc.documentElement

        # Version
        xml_version = newdoc.createElement("version")
        xml_version.appendChild(newdoc.createTextNode(self.config.get("version")))
        root_element.appendChild(xml_version)

        #Name
        if exercise.getName() != None:
            xml_node = newdoc.createElement("name")
            xml_node.appendChild(newdoc.createTextNode(exercise.getName()))
            root_element.appendChild(xml_node)

        #Language
        if exercise.getLanguageId() != None:
            xml_node = newdoc.createElement("language")
            xml_node.appendChild(newdoc.createTextNode(exercise.getLanguageId()))
            root_element.appendChild(xml_node)

        #Template
        xml_node = newdoc.createElement("template")
        xml_node.appendChild(newdoc.createTextNode(str(exercise.isTemplate())))
        root_element.appendChild(xml_node)

        #RandomOrder
        xml_node = newdoc.createElement("random_order")
        xml_node.appendChild(newdoc.createTextNode(str(exercise.isRandomOrder())))
        root_element.appendChild(xml_node)

        #Exercise
        xml_exercise = newdoc.createElement("exercise")

        xml_current_sequence = newdoc.createElement("current_sequence")
        xml_current_sequence.appendChild(newdoc.createTextNode(str(exercise.getCurrentSequenceId())))
        xml_exercise.appendChild(xml_current_sequence)

        xml_current_word = newdoc.createElement("current_word")
        xml_current_word.appendChild(newdoc.createTextNode(str(exercise.getCurrentSequence().getActiveWordIndex())))
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
            xml_video_paths.appendChild(newdoc.createTextNode(subExo.getVideoExportPath()))
            xml_paths.appendChild(xml_video_paths)

            xml_exercice_paths = newdoc.createElement("exercise")
            xml_exercice_paths.appendChild(newdoc.createTextNode(subExo.getExerciseExportPath()))
            xml_paths.appendChild(xml_exercice_paths)

            xml_translation_paths = newdoc.createElement("translation")
            xml_translation_paths.appendChild(newdoc.createTextNode(subExo.getTranslationExportPath()))
            xml_paths.appendChild(xml_translation_paths)

            xml_sequences = newdoc.createElement("sequences")
            xml_subExo.appendChild(xml_sequences)
            for id, sequence in enumerate(subExo.getSequenceList()):
                if sequence.isValid():
                    xml_sequence = newdoc.createElement("sequence")
                    xml_sequence_id = newdoc.createElement("id")
                    xml_sequence_id.appendChild(newdoc.createTextNode(str(id)))
                    xml_sequence.appendChild(xml_sequence_id)
                    xml_sequence_state = newdoc.createElement("state")
                    xml_sequence_state.appendChild(newdoc.createTextNode("done"))
                    xml_sequence.appendChild(xml_sequence_state)

                    xml_sequences.appendChild(xml_sequence)
                elif not sequence.isEmpty():
                    xml_sequence = newdoc.createElement("sequence")
                    xml_sequence_id = newdoc.createElement("id")
                    xml_sequence_id.appendChild(newdoc.createTextNode(str(id)))
                    xml_sequence.appendChild(xml_sequence_id)
                    xml_sequence_state = newdoc.createElement("state")
                    xml_sequence_state.appendChild(newdoc.createTextNode("in_progress"))
                    xml_sequence.appendChild(xml_sequence_state)

                    xml_sequence_words = newdoc.createElement("words")

                    for word in (w.getText() for w in sequence.getWords()):
                        xml_sequence_word = newdoc.createElement("word")
                        xml_sequence_word.appendChild(newdoc.createTextNode(word))
                        xml_sequence_words.appendChild(xml_sequence_word)

                    xml_sequence.appendChild(xml_sequence_words)

                    xml_sequences.appendChild(xml_sequence)


        #Stats
        xml_stats = newdoc.createElement("stats")

        xml_repeatCount = newdoc.createElement("repeat_count")
        xml_repeatCount.appendChild(newdoc.createTextNode(str(exercise.getRepeatCount())))
        xml_stats.appendChild(xml_repeatCount)

        root_element.appendChild(xml_stats)

        #Properties
        xml_properties = newdoc.createElement("properties")

        xml_repeatAfterComplete = newdoc.createElement("repeat_after_complete")
        xml_repeatAfterComplete.appendChild(newdoc.createTextNode(str(exercise.getRepeatAfterCompleted())))
        xml_properties.appendChild(xml_repeatAfterComplete)

        xml_maxSequenceLength = newdoc.createElement("max_sequence_length")
        xml_maxSequenceLength.appendChild(newdoc.createTextNode(str(exercise.getMaxSequenceLength())))
        xml_properties.appendChild(xml_maxSequenceLength)

        xml_timeBetweenSequences = newdoc.createElement("time_between_sequence")
        xml_timeBetweenSequences.appendChild(newdoc.createTextNode(str(exercise.getTimeBetweenSequence())))
        xml_properties.appendChild(xml_timeBetweenSequences)

        xml_playMarginBefore = newdoc.createElement("play_margin_before")
        xml_playMarginBefore.appendChild(newdoc.createTextNode(str(exercise.getPlayMarginBefore())))
        xml_properties.appendChild(xml_playMarginBefore)

        xml_playMarginAfter = newdoc.createElement("play_margin_after")
        xml_playMarginAfter.appendChild(newdoc.createTextNode(str(exercise.getPlayMarginAfter())))
        xml_properties.appendChild(xml_playMarginAfter)


        root_element.appendChild(xml_properties)

        xml_string = newdoc.toprettyxml()
        xml_string = xml_string.encode('utf8')

        f = open(self.outputPath, 'w')
        f.write(xml_string)
        f.close()










class ExerciseLoader(object):

    def Load(self, path):
        self.exercise = Exercise()

        dom = parse(path)
        if len(dom.getElementsByTagName("version")) > 0:
            version = self.getText(dom.getElementsByTagName("version")[0].childNodes)

            if version >= "1.1.0":
                self._load_v1_1_0(dom, path)
            elif version >= "1.0.0":
                self._load_v1_0_0(dom, path)
            else:
                print "Unknown file version: "+version
                self.exercise = None
        else:
            print "Invalid perroquet file"
            self.exercise = None

        dom.unlink()

        return self.exercise

    def getText(self, nodelist):
        rc = ""
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
        rc = rc.strip()
        return rc


    def UpdateSequenceList(self ):
        for subExo,self.progress in zip(self.exercise.subExercisesList,self.subExo):
            sequenceList = subExo.getSequenceList()

            for (id, state, words) in self.progress:
                if id >= len(sequenceList):
                    break
                sequence = sequenceList[id]
                if state == "done":
                    sequence.completeAll()
                elif state == "in_progress":
                    i = 0
                    for word in words:
                        if id >= sequence.getWordCount():
                            break
                        sequence.getWords()[i].setText(word)
                        i = i+1

    def _load_v1_1_0(self,dom, path):
        #Name
        if len(dom.getElementsByTagName("name")) > 0:
            self.exercise.setName(self.getText(dom.getElementsByTagName("name")[0].childNodes))

        #Language
        if len(dom.getElementsByTagName("language")) > 0:
            self.exercise.setLanguageId(self.getText(dom.getElementsByTagName("language")[0].childNodes))
        else:
            languageManager = LanguagesManager()
            (langId, langName, langChars) = languageManager.getDefaultLanguage()
            self.exercise.setLanguageId(langId)

        #Template
        if len(dom.getElementsByTagName("template")) > 0:
            self.exercise.setTemplate(self.getText(dom.getElementsByTagName("template")[0].childNodes) == "True")

        #Random order
        if len(dom.getElementsByTagName("random_order")) > 0:
            self.exercise.setRandomOrder(self.getText(dom.getElementsByTagName("random_order")[0].childNodes) == "True")


        #Exercise
        xml_exercise = dom.getElementsByTagName("exercise")[0]

        #Exercise - CurrentWord
        currentWord = int(self.getText(xml_exercise.getElementsByTagName("current_word")[0].childNodes))
        #Exercise - CurrentSequence
        currentSequence = int(self.getText(xml_exercise.getElementsByTagName("current_sequence")[0].childNodes))

        # Stats
        xml_stats = dom.getElementsByTagName("stats")[0]
        self.exercise.setRepeatCount(int(self.getText(xml_stats.getElementsByTagName("repeat_count")[0].childNodes)))

        # Properties
        if len(dom.getElementsByTagName("properties")) > 0:
            xml_properties = dom.getElementsByTagName("properties")[0]
            if len(xml_properties.getElementsByTagName("repeat_after_complete")) > 0:
                self.exercise.setRepeatAfterCompleted(self.getText(xml_properties.getElementsByTagName("repeat_after_complete")[0].childNodes) == "True")
            if len(xml_properties.getElementsByTagName("time_between_sequence")) > 0:
                self.exercise.setTimeBetweenSequence(float(self.getText(xml_properties.getElementsByTagName("time_between_sequence")[0].childNodes)))
            if len(xml_properties.getElementsByTagName("max_sequence_length")) > 0:
                self.exercise.setMaxSequenceLength(float(self.getText(xml_properties.getElementsByTagName("max_sequence_length")[0].childNodes)))
            if len(xml_properties.getElementsByTagName("play_margin_before")) > 0:
                self.exercise.setPlayMarginBefore(int(self.getText(xml_properties.getElementsByTagName("play_margin_before")[0].childNodes)))
            if len(xml_properties.getElementsByTagName("play_margin_after")) > 0:
                self.exercise.setPlayMarginAfter(int(self.getText(xml_properties.getElementsByTagName("play_margin_after")[0].childNodes)))


        #Subexercises
        self.subExo = []
        for xml_subExercise in xml_exercise.getElementsByTagName("sub_exercise"):
            subExercise = SubExercise(self.exercise)

            #Sequences
            xml_sequences = xml_subExercise.getElementsByTagName("sequences")[0]

            self.progress = []

            for xml_sequence in xml_sequences.getElementsByTagName("sequence"):
                id = int(self.getText(xml_sequence.getElementsByTagName("id")[0].childNodes))
                state = self.getText(xml_sequence.getElementsByTagName("state")[0].childNodes)
                words = []

                if state == "in_progress":
                    xml_words = xml_sequence.getElementsByTagName("words")[0]
                    for xml_world in xml_words.getElementsByTagName("word"):
                        words.append(self.getText(xml_world.childNodes))

                self.progress.append((id, state, words))

            #Paths
            xml_paths = xml_subExercise.getElementsByTagName("paths")[0]
            subExercise.setVideoPath(self.getText(xml_paths.getElementsByTagName("video")[0].childNodes))
            subExercise.setExercisePath(self.getText(xml_paths.getElementsByTagName("exercise")[0].childNodes))
            subExercise.setTranslationPath(self.getText(xml_paths.getElementsByTagName("translation")[0].childNodes))

            self.exercise.subExercisesList.append(subExercise)

            self.subExo.append(self.progress)



        #Convert relative path
        for subExo in self.exercise.subExercisesList:
            if not os.path.isfile(subExo.getExercisePath()):
                absPath = os.path.join(os.path.dirname(path), subExo.getExercisePath())
                if not os.path.isfile(absPath):
                    subExo.setExercisePath("")
                else:
                    subExo.setExercisePath(absPath)

            if not os.path.isfile(subExo.getVideoPath()):
                absPath = os.path.join(os.path.dirname(path), subExo.getVideoPath())
                if not os.path.isfile(absPath):
                    subExo.setVideoPath("")
                else:
                    subExo.setVideoPath(absPath)

            if not os.path.isfile(subExo.getTranslationPath()):
                absPath = os.path.join(os.path.dirname(path), subExo.getTranslationPath())
                if not os.path.isfile(absPath):
                    subExo.setTranslationPath("")
                else:
                    subExo.setTranslationPath(absPath)


        self.exercise.Initialize()

        self.UpdateSequenceList()

        self.exercise.GotoSequence(currentSequence)

        self.exercise.getCurrentSequence().setActiveWordIndex(currentWord)

        if not self.exercise.isTemplate():
            self.exercise.setOutputSavePath(path)

        return self.exercise

    def _load_v1_0_0(self,dom, path):

        #Name
        self.exercise.setName(None)

        #Language
        languageManager = LanguagesManager()
        (langId, langName, langChars) = languageManager.getDefaultLanguage()
        self.exercise.setLanguageId(langId)

        #Template
        self.exercise.setTemplate(False)

        #Random order
        self.exercise.setRandomOrder(False)

        xml_progress = dom.getElementsByTagName("progress")[0]
        currentSequence = int(self.getText(xml_progress.getElementsByTagName("current_sequence")[0].childNodes))
        currentWord = int(self.getText(xml_progress.getElementsByTagName("current_word")[0].childNodes))

        xml_sequences = xml_progress.getElementsByTagName("sequences")[0]

        self.progress = []

        for xml_sequence in xml_sequences.getElementsByTagName("sequence"):
            id = int(self.getText(xml_sequence.getElementsByTagName("id")[0].childNodes))
            state = self.getText(xml_sequence.getElementsByTagName("state")[0].childNodes)
            words = []

            if state == "in_progress":
                xml_words = xml_sequence.getElementsByTagName("words")[0]
                for xml_world in xml_words.getElementsByTagName("word"):
                    words.append(self.getText(xml_world.childNodes))

            self.progress.append((id, state, words))


        # Stats
        xml_stats = dom.getElementsByTagName("stats")[0]
        self.exercise.setRepeatCount(int(self.getText(xml_stats.getElementsByTagName("repeat_count")[0].childNodes)))

        #Subexercises
        self.subExo = []

        subExercise = SubExercise(self.exercise)

        #Sequences
        self.progress = []

        xml_progress = dom.getElementsByTagName("progress")[0]
        xml_sequences = xml_progress.getElementsByTagName("sequences")[0]
        for xml_sequence in xml_sequences.getElementsByTagName("sequence"):
            id = int(self.getText(xml_sequence.getElementsByTagName("id")[0].childNodes))
            state = self.getText(xml_sequence.getElementsByTagName("state")[0].childNodes)
            words = []

            if state == "in_progress":
                xml_words = xml_sequence.getElementsByTagName("words")[0]
                for xml_world in xml_words.getElementsByTagName("word"):
                    words.append(self.getText(xml_world.childNodes))

            self.progress.append((id, state, words))

        #Paths
        xml_paths = dom.getElementsByTagName("paths")[0]
        subExercise.setVideoPath(self.getText(xml_paths.getElementsByTagName("video")[0].childNodes))
        subExercise.setExercisePath(self.getText(xml_paths.getElementsByTagName("exercice")[0].childNodes))
        subExercise.setTranslationPath(self.getText(xml_paths.getElementsByTagName("translation")[0].childNodes))

        self.exercise.subExercisesList.append(subExercise)

        self.subExo.append(self.progress)

        #Convert relative path
        for subExo in self.exercise.subExercisesList:
            if not os.path.isfile(subExo.getExercisePath()):
                absPath = os.path.join(os.path.dirname(path), subExo.getExercisePath())
                if not os.path.isfile(absPath):
                    subExo.setExercisePath("")
                else:
                    subExo.setExercisePath(absPath)

            if not os.path.isfile(subExo.getVideoPath()):
                absPath = os.path.join(os.path.dirname(path), subExo.getVideoPath())
                if not os.path.isfile(absPath):
                    subExo.setVideoPath("")
                else:
                    subExo.setVideoPath(absPath)

            if not os.path.isfile(subExo.getTranslationPath()):
                absPath = os.path.join(os.path.dirname(path), subExo.getTranslationPath())
                if not os.path.isfile(absPath):
                    subExo.setTranslationPath("")
                else:
                    subExo.setTranslationPath(absPath)


        self.exercise.Initialize()

        self.UpdateSequenceList()

        self.exercise.GotoSequence(currentSequence)

        self.exercise.getCurrentSequence().setActiveWordIndex(currentWord)

        if not self.exercise.isTemplate():
            self.exercise.setOutputSavePath(path)

        return self.exercise



