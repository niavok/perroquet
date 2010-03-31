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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Perroquet. If not, see <http://www.gnu.org/licenses/>.
import logging
from xml.dom.minidom import parse

from perroquetlib.model.exercise import Exercise
from perroquetlib.core import defaultLoggingHandler, defaultLoggingLevel

from lib import get_text
from parser_v1_1_0 import load as load_v1_1_0, save as save_v1_1_0
from parser_v1_0_0 import load as load_v1_0_0, save as save_v1_0_0

def load_exercise(path):
    """Load a perroquet exercise."""
    exercise = Exercise()
    logger = logging.Logger("load_exercise")
    logger.setLevel(defaultLoggingLevel)
    logger.addHandler(defaultLoggingHandler)

    dom = parse(path)
    if len(dom.getElementsByTagName("version")) > 0:
        version = get_text(dom.getElementsByTagName("version")[0].childNodes)

        if version >= "1.1.0":
            load_v1_1_0(exercise, dom, path)
        elif version >= "1.0.0":
            raise NotImplemented
            load_v1_0_0(exercise, dom, path)
        else:
            logger.error("Unknown file version: "+version)
            exercise = None
    else:
        logger.error("Invalid perroquet file")
        exercise = None

    dom.unlink()

    return exercise

def save_exercise(exercise, outputPath):
    """Save a perroquet exercise.
    exercise must be an empty perroquet Exercise or inherited"""
    save_v1_1_0(exercise, outputPath)
