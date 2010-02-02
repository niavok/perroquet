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
from exercise import Exercise
from perroquetlib.config import Config

class ExerciseLoader(object):

    def getText(self, nodelist):
        rc = ""
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
        rc = rc.strip()
        return rc


    def Load(self, path):

        self.exercise = Exercise()

        dom = parse(path)
        xml_paths = dom.getElementsByTagName("paths")[0]
        self.exercise.SetVideoPath(self.getText(xml_paths.getElementsByTagName("video")[0].childNodes))
        self.exercise.SetExercisePath(self.getText(xml_paths.getElementsByTagName("exercise")[0].childNodes))

        self.exercise.SetTranslationPath(self.getText(xml_paths.getElementsByTagName("translation")[0].childNodes))

        xml_progress = dom.getElementsByTagName("progress")[0]
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
        self.exercise.SetRepeatCount(int(self.getText(xml_stats.getElementsByTagName("repeat_count")[0].childNodes)))

        # Properties
        if len(dom.getElementsByTagName("properties")) > 0:
            xml_properties = dom.getElementsByTagName("properties")[0]
            if len(xml_properties.getElementsByTagName("repeat_after_complete")) > 0:
                self.exercise.SetRepeatAfterCompleted(self.getText(xml_properties.getElementsByTagName("repeat_after_complete")[0].childNodes) == "True")
            if len(xml_properties.getElementsByTagName("time_between_sequence")) > 0:
                self.exercise.SetTimeBetweenSequence(float(self.getText(xml_properties.getElementsByTagName("time_between_sequence")[0].childNodes)))
            if len(xml_properties.getElementsByTagName("max_sequence_length")) > 0:
                self.exercise.SetMaxSequenceLength(float(self.getText(xml_properties.getElementsByTagName("max_sequence_length")[0].childNodes)))

        self.exercise.LoadSubtitles()
        self.UpdateSequenceList()

        self.exercise.SetCurrentSequence(int(self.getText(xml_progress.getElementsByTagName("current_sequence")[0].childNodes)))

        self.exercise.GetCurrentSequence().setActiveWordIndex(currentWord)


        dom.unlink()

        return self.exercise


    def UpdateSequenceList(self ):

        sequenceList = self.exercise.GetSequenceList()

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
                    sequence.GetWords()[i].setText(word)
                    i = i+1

class ExerciseSaver(object):

    def Save(self,exercise, outputPath):
        self.outputPath = outputPath
        self.config = Config()

        impl = getDOMImplementation()

        newdoc = impl.createDocument(None, "perroquet", None)
        root_element = newdoc.documentElement

        # Version
        xml_version = newdoc.createElement("version")
        xml_version.appendChild(newdoc.createTextNode(self.config.Get("version")))
        root_element.appendChild(xml_version)

        # Paths
        xml_paths = newdoc.createElement("paths")

        xml_video_paths = newdoc.createElement("video")
        xml_video_paths.appendChild(newdoc.createTextNode(exercise.GetVideoPath()))
        xml_paths.appendChild(xml_video_paths)

        xml_exercice_paths = newdoc.createElement("exercise")
        xml_exercice_paths.appendChild(newdoc.createTextNode(exercise.GetExercisePath()))
        xml_paths.appendChild(xml_exercice_paths)

        xml_translation_paths = newdoc.createElement("translation")
        xml_translation_paths.appendChild(newdoc.createTextNode(exercise.GetTranslationPath()))
        xml_paths.appendChild(xml_translation_paths)

        root_element.appendChild(xml_paths)

        # Progress
        xml_progress = newdoc.createElement("progress")

        xml_current_sequence = newdoc.createElement("current_sequence")
        xml_current_sequence.appendChild(newdoc.createTextNode(str(exercise.GetCurrentSequenceId())))
        xml_progress.appendChild(xml_current_sequence)

        xml_current_word = newdoc.createElement("current_word")
        xml_current_word.appendChild(newdoc.createTextNode(str(exercise.GetCurrentSequence().getActiveWordIndex())))
        xml_progress.appendChild(xml_current_word)

        xml_sequences = newdoc.createElement("sequences")
        id = 0
        for sequence in exercise.GetSequenceList():
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

            id = id +1
        xml_progress.appendChild(xml_sequences)

        root_element.appendChild(xml_progress)

        #Stats
        xml_stats = newdoc.createElement("stats")

        xml_repeatCount = newdoc.createElement("repeat_count")
        xml_repeatCount.appendChild(newdoc.createTextNode(str(exercise.GetRepeatCount())))
        xml_stats.appendChild(xml_repeatCount)

        root_element.appendChild(xml_stats)

        #Properties
        xml_properties = newdoc.createElement("properties")

        xml_repeatAfterComplete = newdoc.createElement("repeat_after_complete")
        xml_repeatAfterComplete.appendChild(newdoc.createTextNode(str(exercise.GetRepeatAfterCompleted())))
        xml_properties.appendChild(xml_repeatAfterComplete)

        xml_maxSequenceLength = newdoc.createElement("max_sequence_length")
        xml_maxSequenceLength.appendChild(newdoc.createTextNode(str(exercise.GetMaxSequenceLength())))
        xml_properties.appendChild(xml_maxSequenceLength)

        xml_timeBetweenSequences = newdoc.createElement("time_between_sequence")
        xml_timeBetweenSequences.appendChild(newdoc.createTextNode(str(exercise.GetTimeBetweenSequence())))
        xml_properties.appendChild(xml_timeBetweenSequences)

        root_element.appendChild(xml_properties)

        xml_string = newdoc.toprettyxml()

        f = open(self.outputPath, 'w')
        f.write(xml_string)
        f.close()
