#! /usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2009-2011 Frédéric Bertolus.
# Copyright (C) 2009-2011 Matthieu Bizien.
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

import logging
import sys

from perroquetlib.config import config

# Build some logger related objects
defaultLoggingHandler = logging.StreamHandler(sys.stdout)
defaultLoggingHandler.setFormatter(logging.Formatter("%(asctime)s.%(msecs)d-[%(name)s::%(levelname)s] %(message)s", "%a %H:%M:%S"))
defaultLoggingLevel = logging.DEBUG
defaultLoggingLevel = logging._levelNames[config.get("default_debug_level")]
