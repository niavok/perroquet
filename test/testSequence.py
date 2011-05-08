#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2009-2011 Frédéric Bertolus.
# Copyright (C) 2009-2011 Matthieu Bizien.
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

import unittest

from perroquetlib.model.sequence import *
from perroquetlib.model.languages_manager import LanguagesManager

language = LanguagesManager().get_default_language()
def seq(text):
    s=SequenceDynamicCorrection(language)
    s.load(text)
    return s

class TestSequence(unittest.TestCase):
    def test_simple(self):     
        s=seq("the little cat")
        self.assertEqual( len(s.get_words()), 3)
        for w, w2 in zip(s.get_words(), ("the little cat").split(" ")):
            self.assertEqual(w.get_text(), "")
            self.assertEqual(w.get_valid(), w2)
            
    def testsimple_write(self):
        s=seq("a")
        s.write_char("a")
        self.assert_(s.is_valid())
        
        s=seq("the")
        s._write_sentence("the")
        self.assert_(s.is_valid())
        
        s=seq("the cat")
        s._write_sentence("thecat")
        for w, w2 in zip(s.get_words(), ("the cat").split()):
            self.assertEqual(w.get_text(), w2)
        self.assert_(s.is_valid())
        
        s=seq("small birth")
        s._write_sentence("smallbirth")
        for w, w2 in zip(s.get_words(), ("small birth").split()):
            self.assertEqual(w.get_text(), w2)
        self.assert_(s.is_valid())
        
        s=seq("a small birth")
        s._write_sentence("a small birth")
        for w, w2 in zip(s.get_words(), ("a small birth").split()):
            self.assertEqual(w.get_text(), w2)
        self.assert_(s.is_valid())
        
    def test_next_prev_write(self):
        s=seq("a smart bird")
        s._write_sentence("a small+birth")
        for i in range(5):
            s.previous_char()
        s.delete_previous_char()
        s.delete_previous_char()
        for w, w2 in zip(s.get_words(), ("a sma birth").split()):
            self.assertEqual(w.get_text(), w2)
        
        s._write_sentence("rt")
        for w, w2 in zip(s.get_words(), ("a smart birth").split()):
            self.assertEqual(w.get_text(), w2)
        
        for i in range(3):
            s.next_char()
            self.assertEqual(s.get_active_word_index(), 2)
        
        s.delete_next_char()
        s.delete_next_char()
        for w, w2 in zip(s.get_words(), ("a smart bir").split()):
            self.assertEqual(w.get_text(), w2)
            
        s._write_sentence("d")
        for w, w2 in zip(s.get_words(), ("a smart bird").split()):
            self.assertEqual(w.get_text(), w2)
        self.assert_(s.is_valid())
        
if __name__=="__main__":
    unittest.main()
