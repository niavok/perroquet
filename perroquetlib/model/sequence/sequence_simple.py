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

from perroquetlib.model.sequence.sequence import Sequence
from perroquetlib.model.sequence.word import NoCharPossible

class SequenceSimple(Sequence):
    """Sequence which dont't lock valids words"""


    def select_sequence_word(self, wordIndex, wordIndexPos):
        self.get_active_word().set_pos(wordIndexPos)
        self.set_active_word_index(wordIndex)

    def is_valid(self):
        """An uncorrected sequence is never valid"""
        return False

    def delete_next_char(self):
        try:
            self.get_active_word().delete_next_char()
        except NoCharPossible:
            if self.get_active_word_index() < self.get_word_count():
                self.next_word()
                self.delete_next_char()
        self.update_after_write()

    def next_char(self):
        try:
            self.get_active_word().next_char()
        except NoCharPossible:
            current_word = self.get_active_word_index()
            self.next_word()
            if current_word != self.get_active_word_index():
                self.get_active_word().set_pos(0);

    def previous_char(self):
        try:
            self.get_active_word().previous_char()
        except NoCharPossible:
            current_word = self.get_active_word_index()
            self.previous_word()
            if current_word != self.get_active_word_index():
                self.get_active_word().set_pos(-1);

    def delete_previous_char(self):
        try:
            self.get_active_word().delete_previous_char()
        except NoCharPossible:
            if self.get_active_word_index() > 0:
                self.previous_word()
                self.delete_previous_char()
        self.update_after_write()

    def first_word(self):
        self._activeWordIndex = 0
        self.get_active_word().set_pos(0)

    def last_word(self):
        self._activeWordIndex = self.get_last_index()
        self.get_active_word().set_pos(self.get_active_word().get_last_pos())

    def next_word(self, loop=False):
        "go to the next word"
        if self.get_active_word_index() < self.get_last_index():
            self._activeWordIndex += 1
            self.get_active_word().set_pos(0)
        else:
            self.get_active_word().set_pos(-1)
            if not loop:
                pass
            else:
                raise NotImplementedError

    def previous_word(self, loop=False):
        "go to the previous word"
        if self.get_active_word_index() > 0:
            self._activeWordIndex -= 1
            self.get_active_word().set_pos(
                    self.get_active_word().get_last_pos())
        else:
            self.get_active_word().set_pos(0)
            if not loop:
                pass
            else:
                raise NotImplementedError


    def write_char(self, char):
        self.get_active_word().write_char(char)
        self.update_after_write()

    def _write_sentence(self, sentence):
        """write many chars. a ' ' mean next word.
        Only for tests"""
        for char in sentence:
            if char == " ":
                pass
            elif char == "+":
                self.next_word()
            else:
                self.write_char(char)
