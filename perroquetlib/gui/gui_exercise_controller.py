# -*- coding: utf-8 -*-

# Copyright (C) 2009-2010 Frédéric Bertolus.
# Copyright (C) 2009-2010 Matthieu Bizien.
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

class GuiExerciseController:
    
    def __init__(self, core, gui):
        self.gui = gui
        self.core = core
        
        self.current_index = 0
        self.current_word_index = -1
        self.current_pos_index = 0
        self.word_index_map = []
        self.word_pos_map = []
        self.cursor_position = 0
        self.formatted_text = []

        self.style_tag_list = []
        self._genererate_style_tag_list()

    def set_sequence(self, sequence):
        self._generate_formatted_exercise_text(sequence)

        self.gui.set_typing_area_text(self.formatted_text)
        self.gui.set_typing_area_cursor_position(self.cursor_position)
        self.gui.set_focus_typing_area()
      

    def _generate_formatted_exercise_text(self, sequence):

        self._clear()
        
        pos = 0

        for i, symbol in enumerate(sequence.getSymbols()):
            pos += len(symbol)
            self._add_symbol(symbol)
            if i < len(sequence.getWords()):
                if sequence.getActiveWordIndex() == i:
                    self.cursor_position = pos
                if sequence.getWords()[i].isEmpty():
                    self._add_word(" ", 0, isEmpty=True)
                    pos += 1
                elif sequence.getWords()[i].isValid():
                    self._add_word(sequence.getWords()[i].getValid(lower=False), 0, isFound=True)
                    pos += len(sequence.getWords()[i].getText())
                else:
                    self._add_word(sequence.getWords()[i].getText(), sequence.getWords()[i].getScore())
                    pos += len(sequence.getWords()[i].getText())


        self.word_index_map.append(self.current_word_index)
        self.word_pos_map.append(self.current_pos_index)

        self.cursor_position = self.cursor_position + sequence.getActiveWord().getPos()
        

    def _add_word(self, word, score, isFound=False, isEmpty=False):

        score250 = int(score*250) #score between -250 and 250
        if isEmpty:
            tagName = "word_empty"
        elif isFound:
            tagName = "word_found"
        elif score > 0 :
            tagName = "word_near"+str(score250)
        else:
            tagName = "word_to_found"+str(score250)

        self.formatted_text.append((word, tagName))

        self.current_word_index += 1
        self.current_pos_index = 0

        for _ in range(self.current_index, self.current_index + len(word)):
            self.word_index_map.append(self.current_word_index)
            self.word_pos_map.append(self.current_pos_index)
            self.current_pos_index += 1

        self.current_index += len(word)
        
    def _add_symbol(self, symbol):
        if len(symbol) == 0:
            return
        self.formatted_text.append((symbol,"symbol"))
        
        for _ in range(self.current_index, self.current_index + len(symbol)):
            self.word_index_map.append(self.current_word_index)
            self.word_pos_map.append(self.current_pos_index)

        self.current_index += len(symbol)

    def _clear(self):
        self.current_index = 0
        self.current_word_index = -1
        self.current_pos_index = 0
        self.word_index_map = []
        self.word_pos_map = []
        self.cursor_position = 0
        self.formatted_text = []

    def _genererate_style_tag_list(self):

        color_not_found = (0,0,80)
        color_found = (10,150,10)

        def get_bcolor_not_found(score250):
            return _compute_color_between(
                (150, 210, 250),
                (255, 100, 100),
                float(score250) /250.0)

        def get_bcolor_near(score250):
            return _compute_color_between(
                (150, 210, 250),
                (150, 255, 100),
                float(score250) /250.0)

        def _compute_color_between(colorFrom, colorTo, coeff):
            (redFrom, greenFrom, blueFrom)  =  colorFrom
            (redTo, greenTo, blueTo)  =  colorTo
            red = int((1-coeff)*redFrom + coeff*redTo)
            green = int((1-coeff)*greenFrom + coeff*greenTo)
            blue = int((1-coeff)*blueFrom + coeff*blueTo)
            return (red, green, blue)

        self.style_tag_list.append(("symbol",18.0,None, None))
        self.style_tag_list.append(("word_empty",18.0,color_not_found, get_bcolor_not_found(0)))
        self.style_tag_list.append(("word_found",18.0,color_found, None))
        
        for score250 in xrange(251):
            self.style_tag_list.append(("word_to_found"+str(-score250),
            18.0,
            color_not_found,
            get_bcolor_not_found(score250)))

            self.style_tag_list.append(("word_near"+str(score250),
            18.0,
            color_not_found,
            get_bcolor_near(score250)))

        self.gui.set_typing_area_style_list(self.style_tag_list)

    def notify_move_cursor(self,movement):
        """Documentation"""
        if movement =="previous_char" :
            self.core.PreviousChar()
        elif movement =="next_char" :
            self.core.NextChar()
        elif movement =="first_word" :
            self.core.FirstWord()
        elif movement =="last_word" :
            self.core.LastWord()
        elif movement =="previous_word" :
            self.core.PreviousWord()()
        elif movement =="next_word" :
            self.core.NextWord()
        else:
            word_index = self.word_index_map[movement]
            word_index_position = self.word_pos_map[movement]
            if word_index == -1:
                wordIndex = 0
            self.core.SelectSequenceWord(word_index,word_index_position)
