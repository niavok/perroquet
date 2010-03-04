#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import unittest
from perroquetlib.config2 import Config

pathRef = "./testConfigReference.ini"
pathWritable = "./testConfigWritable.ini"
pathTemp = "./testConfigTemp.ini"

class testConfig(unittest.TestCase):
    def testLoad(self):
        c=Config()
        c.loadWritableConfigFile(pathWritable, pathRef)
        
        self.assertEqual(c.Get("firstint"), 5)
        self.assertEqual(c.Get("sndint"), 8)
        
        self.assertEqual(c.Get("christmas"), "merry Christmas\nand happy new year")
        self.assertEqual(c.Get("newyear"), "champagne")
        
    def testSave(self):
        fW = open(pathWritable, "r")
        fT = open(pathTemp, "w")
        fT.write(fW.read())
        fT.close()
        fW.close()
        
        c=Config()
        c.loadWritableConfigFile(pathTemp, pathRef)
        c.Set("firstint", 666)
        c.Save()
        
        c=Config()
        c.loadWritableConfigFile(pathTemp, pathRef)
        self.assertEqual(c.Get("firstint"), 666)
       
        os.remove(pathTemp)
    
    def testError(self):
        c=Config()
        self.failUnlessRaises(KeyError, lambda :c.Set("MAJ", 3))
        self.failUnlessRaises(KeyError, lambda :c.Get("MAJ"))

if __name__=="__main__":
    unittest.main()
        

