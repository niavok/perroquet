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
import logging

from perroquetlib.core import Core, defaultLoggingHandler, defaultLoggingLevel
from perroquetlib.gui.gui_controller import GuiController
from perroquetlib.config.perroquet_config import config

class Perroquet(object):

    def __init__(self):

        self.core = Core()
        self.gui = GuiController()

        self.core.set_gui(self.gui)
        self.gui.set_core(self.core)
        self.gui.activate("closed")
        self.logger = logging.Logger(self.__class__.__name__)
        self.logger.setLevel(defaultLoggingLevel)
        self.logger.addHandler(defaultLoggingHandler)

    def run(self):
        if len(sys.argv) > 1:
            path = os.path.abspath(sys.argv[1])
            self.core.load_exercise( path )
        elif config.get("lastopenfile"):
            self.logger.info("last open file : " + config.get("lastopenfile"))
            self.core.load_exercise(config.get("lastopenfile"))

        self.gui.run()


