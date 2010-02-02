#!/usr/bin/env python
# -*- coding: utf-8 -*-

from perroquetlib.sequence import *
import unittest

def Seq(text):
    s=Sequence()
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
