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

class SequenceDynamicCorrection(Sequence):
    """Sequence which lock valids words"""
    def is_valid(self):
        """Return True if the entire sequence is valid, else return False"""
        return all(w.is_valid() for w in self.get_words())

    def select_sequence_word(self, wordIndex, wordIndexPos):
        self.set_active_word_index(wordIndex)
        self.get_active_word().set_pos(wordIndexPos)
        if self.get_active_word().is_valid():
            self.next_word()

    def delete_next_char(self):
        try:
            self.get_active_word().delete_next_char()
        except NoCharPossible:
                current_word_index = self.get_active_word_index()
                self.next_word()
                if current_word_index != self.get_active_word_index():
                    self.delete_next_char()
        self.update_after_write()

    def delete_previous_char(self):
        if not self.get_active_word().is_valid():
            try:
                self.get_active_word().delete_previous_char()
            except NoCharPossible:
                current_word_index = self.get_active_word_index()
                self.previous_word()
                if current_word_index != self.get_active_word_index():
                    self.delete_previous_char()
        else:
            self._previous_word()
            if self.get_active_word_index() > 0:
                self.delete_previous_char()
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
        if self.get_active_word().is_valid():
            current_word = self.get_active_word_index()
            self.previous_word()
            if current_word != self.get_active_word_index():
                self.get_active_word().end()
        else:
            try:
                self.get_active_word().previous_char()
            except NoCharPossible:
                current_word = self.get_active_word_index()
                self.previous_word()
                if current_word != self.get_active_word_index():
                    self.get_active_word().end()

    def first_word(self):
        self._activeWordIndex = 0
        self.get_active_word().set_pos(0)
        if self.get_active_word().is_valid() and not self.is_valid():
            self.next_word()
        self.get_active_word().set_pos(0)

    def last_word(self):
        self._activeWordIndex = self.get_last_index()
        self.get_active_word().set_pos(self.get_active_word().get_last_pos())
        if self.get_active_word().is_valid() and not self.is_valid():
            self.previous_word()
        self.get_active_word().set_pos(-1)

    def update_after_write(self):
        "update after a modification of the text"
        self._check_location()

    def write_char(self, char):
        if not self.get_active_word().is_valid():
            self.get_active_word().write_char(char)
        else:
            self.next_word()
            if not self.get_active_word().is_valid():
                self.write_char(char)
            else:
                #Nothing to write
                return
        self.update_after_write()

    def _check_location(self):
        """Check if a word is correct but at a wrong place."""
        for w1 in self.get_words():
            for j, w2 in enumerate(self.get_words()):
                if w1.get_score() <= 0 and w1.is_equal(w2.get_valid()) and not w2.is_valid():
                    w2.set_text(w1.get_text())
                    w1.set_text("")
                    self.set_active_word_index(j)
                    self.get_active_word().end()

    def _next_word(self, loop=False):
        "go to the next word"
        if self.get_active_word_index() < self.get_last_index():
            self._activeWordIndex += 1
            self.get_active_word().set_pos(0)
        else:
            if not loop:
                pass
            else:
                raise NotImplementedError

    def _previous_word(self, loop=False):
        "go to the previous word"
        if self.get_active_word_index() > 0:
            self._activeWordIndex -= 1
            self.get_active_word().set_pos(
                    self.get_active_word().get_last_pos())
        else:
            if not loop:
                pass
            else:
                raise NotImplementedError

    def next_word(self, loop=False):
        "go to the next non valid word"
        current_word = self.get_active_word_index()
        self._next_word()

        if current_word == self.get_active_word_index():
            self.get_active_word().set_pos(-1)

        if loop:
            raise NotImplementedError
        if self.get_active_word().is_valid():
            if self.is_valid() or self.get_active_word_index() == self.get_last_index():
                self.last_word();
                return False
            return self.next_word()
        else:
            return True

    def previous_word(self, loop=False):
        "go to the previous non valid word"
        current_word = self.get_active_word_index()
        self._previous_word()

        if current_word == self.get_active_word_index():
            self.get_active_word().set_pos(0)

        if loop:
            raise NotImplementedError
        if self.get_active_word().is_valid():
            if self.is_valid() or self.get_active_word_index() == 0:
                self.first_word();
                return False
            return self.previous_word()
        else:
            return True

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
