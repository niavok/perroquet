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

import re

from word import Word, ValidWordError, NoCharPossible

class Sequence(object):
    def __init__(self, charToFind):

        # self._symbolList = what is between words (or "")
        # self._wordList = a list of Words items that we want to find
        # self._workValidityList = 1 if the word if good, 0 if it is empty
        #        -levenshtein between it and the normal word otherwise
        #
        # self._activeWordIndex = the word that is currently being edited
        # self.get_active_word().get_pos() = the position in that word
        #
        # self._helpChar = the char printed when you want a hint
        #
        # Note: self._symbolList, self._wordList
        #  have always the same length

        self._symbolList = []
        self._wordList = []

        self._activeWordIndex = 0

        self._helpChar = '~'

        allChar = charToFind
        self.validChar = "["+allChar+"]"
        self.notValidChar = "[^"+allChar+"]"

    def load(self, text):
        #TODO FIXME
        textToParse = text
        #We want swswsw... (s=symbol, w=word)
        #So if the 1st char isn't a symbole, we want an empty symbole
        if re.match(self.validChar, textToParse[0]):
            self._symbolList.append('')
        while len(textToParse) > 0:
            # if the text begin with a word followed by a not word char
            if re.match('^('+self.validChar+'+)'+self.notValidChar, textToParse):
                m = re.search('^('+self.validChar+'+)'+self.notValidChar, textToParse)
                word = m.group(1)
                sizeToCut =  len(word)
                textToParse = textToParse[sizeToCut:]
                self._wordList.append(Word(word))
            # if the text begin with no word char but followed by a word
            elif re.match('^('+self.notValidChar+'+)'+self.validChar, textToParse):
                m = re.search('^('+self.notValidChar+'+)'+self.validChar, textToParse)
                symbol = m.group(1)
                sizeToCut = len(symbol)
                textToParse = textToParse[sizeToCut:]
                self._symbolList.append(symbol)
            # if there is only one word or one separator
            else:
                # if there is only one word
                if re.match('^('+self.validChar+'+)', textToParse):
                    self._wordList.append(Word(textToParse))
                # if there is only one separator
                else:
                    self._symbolList.append(textToParse)
                break

    def get_symbols(self):
        return self._symbolList

    def get_words(self):
        return self._wordList

    def get_word_count(self):
        return len(self._wordList)

    def get_active_word_index(self):
        return self._activeWordIndex

    def set_active_word_index(self, index):
        if index==-1:
            index=self.get_word_count()

        if index<0 or index>self.get_word_count():
            raise AttributeError, str(index)

        self._activeWordIndex = index

    def get_last_index(self):
        return len(self._wordList) - 1

    def get_active_word(self):
        return self.get_words()[self.get_active_word_index()]

    def get_word_found(self):
        return len([w for w in self.get_words() if w.is_valid()])

    def next_word(self, loop=False):
        "go to the next word"
        if self.get_active_word_index() < self.get_last_index():
            self._activeWordIndex +=1
            self.get_active_word().set_pos(0)
        else:
            if not loop:
                pass
            else:
                raise NotImplemented

    def next_false_word(self, loop=False):
        "go to the next non valid word"
        if loop:
            raise NotImplemented
        if self.get_active_word().is_valid():
            if self.is_valid() or self.get_active_word_index() == self.get_last_index():
                return
            self.next_word()
            self.next_false_word()

    def previous_word(self, loop=False):
        "go to the previous word"
        if self.get_active_word_index() > 0:
            self._activeWordIndex -= 1
            self.get_active_word().set_pos(self.get_active_word().get_last_pos())
        else:
            if not loop:
                pass
            else:
                raise NotImplemented

    def previous_false_word(self, loop=False):
        "go to the previous non valid word"
        if loop:
            raise NotImplemented
        if self.get_active_word().is_valid():
            if self.is_valid() or self.get_active_word_index() == 0:
                return
            self.previous_word()
            self.previous_false_word()

    def select_sequence_word(self, wordIndex,wordIndexPos):
        self.get_active_word().set_pos(wordIndexPos)
        self.set_active_word_index(wordIndex)

        self.next_false_word()

    def write_char(self, char):
        try:
            self.get_active_word().write_char(char)
            if self.get_active_word().is_valid():
                self.next_char()
        except ValidWordError:
            self.next_word()
            self.next_false_word()
            self.write_char(char)
        self.update_after_write()

    def _write_sentence(self, sentence):
        """write many chars. a ' ' mean next word.
        Only for tests"""
        for char in sentence:
            if char==" ":
                pass
            elif char=="+":
                self.next_word()
                self.next_false_word()
            else:
                self.write_char(char)

    def delete_next_char(self):
        self.previous_false_word()
        try:
            self.get_active_word().delete_next_char()
        except NoCharPossible:
            if self.get_active_word_index() < self.get_word_count():
                self.previous_word()
                self.delete_next_char()
        self.update_after_write()

    def delete_previous_char(self):
        self.previous_false_word()
        try:
            self.get_active_word().delete_previous_char()
        except NoCharPossible:
            if self.get_active_word_index() > 0:
                self.previous_word()
                self.delete_previous_char()
        except ValidWordError:
            if self.get_active_word_index() > 0:
                self.previous_word()
                self.delete_previous_char()

        self.update_after_write()

    def first_false_word(self):
        self._activeWordIndex = 0
        self.get_active_word().set_pos(0)
        self.next_false_word()

    def last_false_word(self):
        self._activeWordIndex = self.get_last_index()
        self.get_active_word().set_pos(self.get_active_word().get_last_pos())
        self.previous_false_word()

    def next_char(self):
        try:
            self.get_active_word().next_char()
        except NoCharPossible:
            self.next_word()
            self.next_false_word()
            self.get_active_word().set_pos(0)

    def previous_char(self):
        try:
            self.get_active_word().previous_char()
        except NoCharPossible:
            self.previous_word()
            self.previous_false_word()
            self.get_active_word().set_pos(-1)

    def is_valid(self):
        return all(w.is_valid() for w in self.get_words())

    def is_empty(self):
        return all(w.is_empty() for w in self.get_words())

    def complete_all(self):
        """Reveal all words"""
        for w in self.get_words():
            w.complete()
            
    def reset(self):
        "RAZ the current seq"
        for w in self.get_words():
            w.reset()

    def update_after_write(self):
        "update after a modification of the text"
        self._check_location()

    def _check_location(self):
        """Check if a word is correct but at a wrong place."""
        for w1 in self.get_words():
            for j, w2 in enumerate(self.get_words()):
                if w1.get_score()<=0 and w1.get_text()==w2.get_valid() and not w2.is_valid():
                    w2.set_text(w1.get_text())
                    w1.set_text("")
                    self.set_active_word_index(j)
                    self.next_false_word()

    def get_time_begin(self):
        return self.beginTime

    def get_time_end(self):
        return self.endTime

    def set_time_begin(self, time):
        self.beginTime = time

    def set_time_end(self, time):
        self.endTime = time

    def show_hint(self):
        try:
            self.get_active_word().show_hint()
        except ValidWordError:
            if self.get_active_word_index()==self.get_word_count()-1:
                return
            else:
                self.next_word()
                self.show_hint()

    def __print__(self):
        return "-".join(w.get_text() for w in self.get_words())+" VS "+"-".join(w.get_valid() for w in self.get_words())

    def __repr__(self):
        return self.__print__()
