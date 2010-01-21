#! /usr/bin/python
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Perroquet.  If not, see <http://www.gnu.org/licenses/>.

from core import Core
from gui import Gui
from perroquetlib.config import Config
import sys, os

class Perroquet(object):

    def __init__(self):

        self.core = Core()
        self.gui = Gui()

        self.core.SetGui(self.gui)
        self.gui.SetCore(self.core)


    def run(self):
        if len(sys.argv) > 1:
            path = os.path.abspath(sys.argv[1])
            self.core.LoadExercice( path )
        else:
            print self.gui.config.Get("lastopenfile")


            self.core.LoadExercice(self.gui.config.Get("lastopenfile"))

        self.gui.Run()


