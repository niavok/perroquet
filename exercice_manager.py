# -*- coding: utf-8 -*-
from xml.dom.minidom import getDOMImplementation


class ExerciceLoader(object):
    def Load(self, path):
        print TODO
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


        if self.correctionPath != "":
            xml_correction_paths = newdoc.createElement("correction")
            xml_correction_paths.appendChild(newdoc.createTextNode(self.correctionPath))
            xml_paths.appendChild(xml_correction_paths)

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
        
    def SetCorrectionPath(self, path):
        self.correctionPath = path
        
    def SetCurrentSequence(self, id):
        self.sequenceId = id

    def SetSequenceList(self, sequenceList):
        self.sequenceList = sequenceList
