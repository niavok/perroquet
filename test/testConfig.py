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

pathRef = "./test/testConfigReference.ini"
pathWritable = "./test/testConfigWritable.ini"
pathTemp = "./test/testConfigTemp.ini"
pathTemp2 = "./a/b/c/testConfigTemp.ini"

class testConfig(unittest.TestCase):
    def testLoad(self):
        c=Config()
        c.load_writable_config_file(pathWritable, pathRef)
        
        self.assertEqual(c.get("christmas"), "merry Christmas\nand happy new year")
        self.assertEqual(c.get("newyear"), "champagne")
        
        self.assertEqual(c.get("firstint"), 5)
        self.assertEqual(c.get("sndint"), 8)
        
        self.assertEqual(c.get("liststr"), ["one", "two"])
        self.assertEqual(c.get("listint"), [1, 2, 3])
        
    def testSave(self):
        shutil.copy(pathWritable, pathTemp)
        c=Config()
        c.load_writable_config_file(pathTemp, pathRef)
        c.set("firstint", 666)
        c.set("liststr", ["1", "2", "3"])
        c.set("listint", [666,666])
        c.save()
        c=Config()
        c.load_writable_config_file(pathTemp, pathRef)
        self.assertEqual(c.get("firstint"), 666)
        self.assertEqual(c.get("liststr"), ["1", "2", "3"])
        self.assertEqual(c.get("listint"), [666, 666])
        os.remove(pathTemp)
        
        c=Config()
        c.load_writable_config_file(pathTemp2, pathRef)
        c.set("firstint", 666)
        c.save()
        c.load_writable_config_file(pathTemp2, pathRef)
        self.assertEqual(c.get("firstint"), 666)
        shutil.rmtree("./a")
    
    def testError(self):
        c=Config()
        self.failUnlessRaises(KeyError, lambda :c.set("MAJ", 3))
        self.failUnlessRaises(KeyError, lambda :c.get("MAJ"))

        c.load_writable_config_file(pathWritable, pathRef)
        self.failUnlessRaises(KeyError, lambda :c.get("easter"))


if __name__=="__main__":
    unittest.main()
        

