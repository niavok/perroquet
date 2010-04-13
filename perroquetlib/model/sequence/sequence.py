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

from word import Word

class Sequence(object):
    def __init__(self, language):

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

        self.language = language
        allChar = self.language.availableChars
        self.validChar = "["+allChar+"]"
        self.notValidChar = "[^"+allChar+"]"
        self.repeat_count = 0
        
        self.beginTime = 0
        self.endTime = 0

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
                self._wordList.append(Word(word, self.language))
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
                    self._wordList.append(Word(textToParse, self.language))
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
                raise NotImplementedError

    def previous_word(self, loop=False):
        "go to the previous word"
        if self.get_active_word_index() > 0:
            self._activeWordIndex -= 1
            self.get_active_word().set_pos(self.get_active_word().get_last_pos())
        else:
            if not loop:
                pass
            else:
                raise NotImplementedError

    def select_sequence_word(self, wordIndex,wordIndexPos):
        """Go to the first editable position after the position of wordIndex
        word and wordIndexPos character"""
        raise NotImplementedError

    def write_char(self, char):
        if not self.get_active_word().is_valid():
            self.get_active_word().write_char(char)
        else:
            self._next_false_word()
            self.write_char(char)
        self.update_after_write()

    def _write_sentence(self, sentence):
        """write many chars. a ' ' mean next word.
        Only for tests"""
        raise NotImplementedError

    def delete_next_char(self):
        """delete the next deletable character"""
        raise NotImplementedError

    def delete_previous_char(self):
        """delete the previous deletable character"""
        raise NotImplementedError

    def first_word(self):
        """goto first editable character"""
        raise NotImplementedError

    def last_word(self):
        """goto last editable character"""
        raise NotImplementedError

    def next_char(self):
        """goto next editable character"""
        raise NotImplementedError

    def previous_char(self):
        """goto to previous editable character"""
        raise NotImplementedError

    def is_valid(self):
        """Return True if the entire sequence is valid, else return False"""
        raise NotImplementedError

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
        raise NotImplementedError
        
    def get_time_begin(self):
        return self.beginTime

    def get_time_end(self):
        return self.endTime

    def set_time_begin(self, time):
        self.beginTime = time

    def set_time_end(self, time):
        self.endTime = time

    def show_hint(self):
        if not self.get_active_word().is_valid():
            self.get_active_word().show_hint()
        else:
            if self.get_active_word_index()==self.get_word_count()-1:
                return
            else:
                self.next_word()
                self.show_hint()

    def set_repeat_count(self, repeat_count):
        self.repeat_count = repeat_count

    def get_repeat_count(self):
        return self.repeat_count

    def __print__(self):
        return "-".join(w.get_text() for w in self.get_words())+" VS "+"-".join(w.get_valid() for w in self.get_words())

    def __repr__(self):
        return self.__print__()

