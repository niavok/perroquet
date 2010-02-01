#!/usr/bin/env python
# -*- coding: utf-8 -*-

from perroquetlib.word import *
import unittest

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
    def testUsualsFunc(self):
        w=Word("batman")
        self.assert_(w.isEmpty())
        self.assertFalse(w.isValid())
        self.assertEqual(w.getValid(), "batman")
        
        w.setText("bat")
        self.assertEqual(w.getText(), "bat")
        self.assertFalse(w.isEmpty())
        self.assertFalse(w.isValid())
        
        w.setText("batman")
        self.assertFalse(w.isEmpty())
        self.assert_(w.isValid())
        
        w.setText("tt")
        self.assertFalse(w.isValid())
        
        w.complete()
        self.assertFalse(w.isEmpty())
        self.assert_(w.isValid())
    
    def testShowHint(self):
        w=Word("joker")
        w.setText ( "jo" )
        for i in range(4):
            self.assertFalse(w.isValid())
            w.showHint()
        self.assert_(w.isValid())
        self.failUnlessRaises(ValidWordError, w.showHint)
    
    def test_writeChar(self):
        w=Word("robin")
        for i, char in enumerate(w.getValid()):
            w.writeChar(char)
            self.assertEqual(w.getText(), w.getValid()[:i+1])
        
        w=Word("spiderman")
        for i in "spi":
            w.writeChar(i)
        w.setText("spi"+w._helpChar*6)
        w.writeChar("d")
        self.assertEqual(w.getText(), "spid"+w._helpChar*5)
        
        w.setPos(9)
        w.writeChar("m")
        self.assertEqual(w.getText(), "spidm")
        
    
    def test_setPos(self):
        w=Word("superman")
        w.setText("suprman")
        w.setPos(3)
        self.assertEqual(w.getPos(), 3)
        w.writeChar("e")
        self.assert_(w.isValid())
        
        w.setPos(-1)
        self.assertEqual(w.getPos(), 8)
        
        self.failUnlessRaises(NoCharPossible, lambda :w.setPos(len(w.getValid())+1))
        self.failUnlessRaises(NoCharPossible, lambda :w.setPos(-2))
        w.setPos(len(w.getValid()))
    
    def test_Delete(self):
        w=Word("angel")
        
        w.setText("XYangel")
        w.setPos(1)
        w.deleteNextChar()      #Y
        w.deletePreviousChar()  #X
        self.assertEqual(w.getText(), w.getValid())
        
        w.setText("WangelW")
        w.setPos(0)
        self.failUnlessRaises(NoCharPossible, w.deletePreviousChar)
        w.setPos(len(w.getText()))
        self.failUnlessRaises(NoCharPossible, w.deleteNextChar)
        
        w.setPos(1)
        w.deletePreviousChar()
        w.setPos(5)
        w.deleteNextChar()
        self.assertEqual(w.getText(), w.getValid())
        
if __name__=="__main__":
    unittest.main()
