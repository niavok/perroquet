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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Perroquet.  If not, see <http://www.gnu.org/licenses/>.





from xml.dom.minidom import getDOMImplementation, parse


class ExerciceLoader(object):

    def getText(self, nodelist):
        rc = ""
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
        rc = rc.strip()
        return rc


    def Load(self, path):
        dom = parse(path)
        xml_paths = dom.getElementsByTagName("paths")[0]
        self.videoPath = self.getText(xml_paths.getElementsByTagName("video")[0].childNodes)
        self.exercicePath = self.getText(xml_paths.getElementsByTagName("exercice")[0].childNodes)

        self.translationPath = self.getText(xml_paths.getElementsByTagName("translation")[0].childNodes)

        print  self.videoPath
        print  self.exercicePath

        xml_progress = dom.getElementsByTagName("progress")[0]
        self.currentSequence = int(self.getText(xml_progress.getElementsByTagName("current_sequence")[0].childNodes))
        self.currentWord = int(self.getText(xml_progress.getElementsByTagName("current_word")[0].childNodes))

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
        self.repeatCount = int(self.getText(xml_stats.getElementsByTagName("repeat_count")[0].childNodes))

        dom.unlink()

        return True


    def UpdateSequenceList(self, sequenceList):

        for (id, state, words) in self.progress:
            sequence = sequenceList[id]
            if state == "done":
                sequence.CompleteAll()
            elif state == "in_progress":
                i = 0
                for word in words:
                    sequence.GetWorkList()[i] = word
                    i = i+1

    def GetCurrentSequence(self):
        return self.currentSequence

    def GetCurrentWord(self):
        return self.currentWord

    def GetVideoPath(self):
        return self.videoPath

    def GetExercicePath(self):
        return self.exercicePath

    def GetTranslationPath(self):
        return self.translationPath

    def GetRepeatCount(self):
        return self.repeatCount

class ExerciceSaver(object):

    def Save(self):
        impl = getDOMImplementation()

        newdoc = impl.createDocument(None, "perroquet", None)
        root_element = newdoc.documentElement

        # Version
        xml_version = newdoc.createElement("version")
        xml_version.appendChild(newdoc.createTextNode("1.0.0"))
        root_element.appendChild(xml_version)

        # Paths
        xml_paths = newdoc.createElement("paths")

        xml_video_paths = newdoc.createElement("video")
        xml_video_paths.appendChild(newdoc.createTextNode(self.videoPath))
        xml_paths.appendChild(xml_video_paths)

        xml_exercice_paths = newdoc.createElement("exercice")
        xml_exercice_paths.appendChild(newdoc.createTextNode(self.exercicePath))
        xml_paths.appendChild(xml_exercice_paths)

        xml_translation_paths = newdoc.createElement("translation")
        xml_translation_paths.appendChild(newdoc.createTextNode(self.translationPath))
        xml_paths.appendChild(xml_translation_paths)

        root_element.appendChild(xml_paths)

        # Progress
        xml_progress = newdoc.createElement("progress")

        xml_current_sequence = newdoc.createElement("current_sequence")
        xml_current_sequence.appendChild(newdoc.createTextNode(str(self.sequenceId)))
        xml_progress.appendChild(xml_current_sequence)

        xml_current_word = newdoc.createElement("current_word")
        xml_current_word.appendChild(newdoc.createTextNode(str(self.sequenceList[self.sequenceId].GetActiveWordIndex())))
        xml_progress.appendChild(xml_current_word)

        xml_sequences = newdoc.createElement("sequences")
        id = 0
        for sequence in self.sequenceList:
            if sequence.IsValid():
                xml_sequence = newdoc.createElement("sequence")
                xml_sequence_id = newdoc.createElement("id")
                xml_sequence_id.appendChild(newdoc.createTextNode(str(id)))
                xml_sequence.appendChild(xml_sequence_id)
                xml_sequence_state = newdoc.createElement("state")
                xml_sequence_state.appendChild(newdoc.createTextNode("done"))
                xml_sequence.appendChild(xml_sequence_state)

                xml_sequences.appendChild(xml_sequence)
            elif not sequence.IsEmpty():
                xml_sequence = newdoc.createElement("sequence")
                xml_sequence_id = newdoc.createElement("id")
                xml_sequence_id.appendChild(newdoc.createTextNode(str(id)))
                xml_sequence.appendChild(xml_sequence_id)
                xml_sequence_state = newdoc.createElement("state")
                xml_sequence_state.appendChild(newdoc.createTextNode("in_progress"))
                xml_sequence.appendChild(xml_sequence_state)

                xml_sequence_words = newdoc.createElement("words")

                for word in sequence.GetWorkList():
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
        xml_repeatCount.appendChild(newdoc.createTextNode(str(self.repeatCount)))
        xml_stats.appendChild(xml_repeatCount)

        root_element.appendChild(xml_stats)


        xml_string = newdoc.toprettyxml()

        f = open(self.outputPath, 'w')
        f.write(xml_string)
        f.close()

    def SetPath(self, path):
        self.outputPath = path

    def SetVideoPath(self, path):
        self.videoPath = path

    def SetExercicePath(self, path):
        self.exercicePath = path

    def SetTranslationPath(self, path):
        self.translationPath = path

    def SetCurrentSequence(self, id):
        self.sequenceId = id

    def SetSequenceList(self, sequenceList):
        self.sequenceList = sequenceList

    def SetRepeatCount(self, repeatCount):
        self.repeatCount = repeatCount
