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

from perroquetlib.sequence import *
import unittest

def Seq(text):
    s=Sequence("0-9\'a-zA-Z")
    s.load(text)
    return s

class TestSequence(unittest.TestCase):
    def testSimple(self):     
        s=Seq("the little cat")
        self.assertEqual( len(s.getWords()), 3)
        for w, w2 in zip(s.getWords(), ("the little cat").split(" ")):
            self.assertEqual(w.getText(), "")
            self.assertEqual(w.getValid(), w2)
            
    def testsimpleWrite(self):
        s=Seq("a")
        s.writeChar("a")
        self.assert_(s.isValid())
        
        s=Seq("the")
        s._writeSentence("the")
        self.assert_(s.isValid())
        
        s=Seq("the cat")
        s._writeSentence("thecat")
        for w, w2 in zip(s.getWords(), ("the cat").split()):
            self.assertEqual(w.getText(), w2)
        self.assert_(s.isValid())
        
        s=Seq("small birth")
        s._writeSentence("smallbirth")
        for w, w2 in zip(s.getWords(), ("small birth").split()):
            self.assertEqual(w.getText(), w2)
        self.assert_(s.isValid())
        
        s=Seq("a small birth")
        s._writeSentence("a small birth")
        for w, w2 in zip(s.getWords(), ("a small birth").split()):
            self.assertEqual(w.getText(), w2)
        self.assert_(s.isValid())
        
    def test_next_prev_write(self):
        s=Seq("a smart bird")
        s._writeSentence("a small+birth")
        for i in range(5):
            s.previousChar()
        s.deletePreviousChar()
        s.deletePreviousChar()
        for w, w2 in zip(s.getWords(), ("a sma birth").split()):
            self.assertEqual(w.getText(), w2)
        
        s._writeSentence("rt")
        for w, w2 in zip(s.getWords(), ("a smart birth").split()):
            self.assertEqual(w.getText(), w2)
        
        for i in range(3):
            s.nextChar()
            self.assertEqual(s.getActiveWordIndex(), 2)
        
        s.deleteNextChar()
        s.deleteNextChar()
        for w, w2 in zip(s.getWords(), ("a smart bir").split()):
            self.assertEqual(w.getText(), w2)
        
        s._writeSentence("d")
        for w, w2 in zip(s.getWords(), ("a smart bird").split()):
            self.assertEqual(w.getText(), w2)
        self.assert_(s.isValid())
        
        #TODO another test with valid words... if I want ;)
        
if __name__=="__main__":
    unittest.main()
