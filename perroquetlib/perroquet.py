#! /usr/bin/python
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

import sys
import os

from perroquetlib.core import Core
from perroquetlib.gui.gui import Gui

class Perroquet(object):

    def __init__(self):

        self.core = Core()
        self.gui = Gui()

        self.core.setGui(self.gui)
        self.gui.setCore(self.core)
        self.gui.activate("closed")

    def run(self):
        if len(sys.argv) > 1:
            path = os.path.abspath(sys.argv[1])
            self.core.LoadExercise( path )
        elif self.gui.config.get("lastopenfile"):
            print "last open file : " + self.gui.config.get("lastopenfile")
            self.core.LoadExercise(self.gui.config.get("lastopenfile"))

        self.gui.Run()


