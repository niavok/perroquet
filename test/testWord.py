#!/usr/bin/env python
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Perroquet.  If not, see <http://www.gnu.org/licenses/>.

import unittest

from perroquetlib.model.sequence import *
from perroquetlib.model.languages_manager import LanguagesManager

language = LanguagesManager().get_default_language()
def word(text):
    w = Word(text, language)
    return w

class TestLevenshtein(unittest.TestCase):
    knowValues=( (("", ""), 0),
                 (("", "cheval"), 6),
                 (("ch", "cheval"), 4),
                 (("aa", "brebis"), 6),
                 (("e", "brebis"), 5),
                 )
                 
    def test(self):
        for (w1, w2),numeral in self.knowValues:              
            result = levenshtein(w1, w2)           
            self.assertEqual(numeral, result)       

class TestWord(unittest.TestCase):
    def test_usuals_func(self):
        w=word("batman")
        self.assert_(w.is_empty())
        self.assertFalse(w.is_valid())
        self.assertEqual(w.get_valid(), "batman")
        
        w.set_text("bat")
        self.assertEqual(w.get_text(), "bat")
        self.assertFalse(w.is_empty())
        self.assertFalse(w.is_valid())
        
        w.set_text("batman")
        self.assertFalse(w.is_empty())
        self.assert_(w.is_valid())
        
        w.set_text("tt")
        self.assertFalse(w.is_valid())
        
        w.complete()
        self.assertFalse(w.is_empty())
        self.assert_(w.is_valid())
    
    def test_show_hint(self):
        w=word("joker")
        w.set_text ( "jo" )
        for i in range(4):
            self.assertFalse(w.is_valid())
            w.show_hint()
        self.assert_(w.is_valid())
        #self.failUnlessRaises(ValidWordError, w.show_hint)
    
    def test_write_char(self):
        w=word("robin")
        for i, char in enumerate(w.get_valid()):
            w.write_char(char)
            self.assertEqual(w.get_text(), w.get_valid()[:i+1])
        
        w=word("spiderman")
        for i in "spi":
            w.write_char(i)
        w.set_text("spi"+w._helpChar*6)
        w.write_char("d")
        self.assertEqual(w.get_text(), "spid"+w._helpChar*5) 
        
        w.set_pos(9)
        w.write_char("m")
        self.assertEqual(w.get_text(), "spidm")
        
        w.set_text(w.get_valid())
        #self.failUnlessRaises(ValidWordError, lambda: w.write_char("r"))
    
    def test_set_pos(self):
        w=word("superman")
        w.set_text("suprman")
        w.set_pos(3)
        self.assertEqual(w.get_pos(), 3)
        w.write_char("e")
        self.assert_(w.is_valid())
        
        w.set_pos(-1)
        self.assertEqual(w.get_pos(), 8)
        
        self.failUnlessRaises(NoCharPossible, lambda :w.set_pos(len(w.get_valid())+1))
        self.failUnlessRaises(NoCharPossible, lambda :w.set_pos(-2))
        w.set_pos(len(w.get_valid()))
    
    def test_delete(self):
        w=word("angel")
        
        w.set_text("XYangel")
        w.set_pos(1)
        w.delete_next_char()      #Y
        w.delete_previous_char()  #X
        self.assertEqual(w.get_text(), w.get_valid())
        
        w.set_text("WangelW")
        w.set_pos(0)
        self.failUnlessRaises(NoCharPossible, w.delete_previous_char)
        w.set_pos(len(w.get_text()))
        self.failUnlessRaises(NoCharPossible, w.delete_next_char)
        
        w.set_pos(1)
        w.delete_previous_char()
        w.set_pos(5)
        w.delete_next_char()
        self.assertEqual(w.get_text(), w.get_valid())
        
if __name__=="__main__":
    unittest.main()
