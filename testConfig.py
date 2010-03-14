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

import os, shutil

import unittest
from perroquetlib.config import Config

pathRef = "./testConfigReference.ini"
pathWritable = "./testConfigWritable.ini"
pathTemp = "./testConfigTemp.ini"
pathTemp2 = "./a/b/c/testConfigTemp.ini"

class testConfig(unittest.TestCase):
    def testLoad(self):
        c=Config()
        c.loadWritableConfigFile(pathWritable, pathRef)
        
        self.assertEqual(c.Get("firstint"), 5)
        self.assertEqual(c.Get("sndint"), 8)
        
        self.assertEqual(c.Get("christmas"), "merry Christmas\nand happy new year")
        self.assertEqual(c.Get("newyear"), "champagne")
        
    def testSave(self):
        shutil.copy(pathWritable, pathTemp)
        c=Config()
        c.loadWritableConfigFile(pathTemp, pathRef)
        c.Set("firstint", 666)
        c.Save()
        c=Config()
        c.loadWritableConfigFile(pathTemp, pathRef)
        self.assertEqual(c.Get("firstint"), 666)
        os.remove(pathTemp)
        
        c=Config()
        c.loadWritableConfigFile(pathTemp2, pathRef)
        c.Set("firstint", 666)
        c.Save()
        c.loadWritableConfigFile(pathTemp2, pathRef)
        self.assertEqual(c.Get("firstint"), 666)
        shutil.rmtree("./a")
        
    
    def testError(self):
        c=Config()
        self.failUnlessRaises(KeyError, lambda :c.Set("MAJ", 3))
        self.failUnlessRaises(KeyError, lambda :c.Get("MAJ"))

        c.loadWritableConfigFile(pathWritable, pathRef)
        self.failUnlessRaises(KeyError, lambda :c.Get("easter"))


if __name__=="__main__":
    unittest.main()
        

