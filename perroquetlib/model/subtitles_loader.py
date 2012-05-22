# -*- coding: utf-8 -*-

# Copyright (C) 2009-2011 Frédéric Bertolus.
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


import codecs
import logging
import re

from perroquetlib.debug import defaultLoggingHandler, defaultLoggingLevel

class SubtitlesLoader(object):
    LOOK_FOR_ID = 0
    LOOK_FOR_TIME = 1
    LOOK_FOR_TEXT = 2

    sourceFormats = ['utf-8', 'ascii', 'iso-8859-1']
    targetFormat = 'utf-8'
    outputDir = 'converted'

    def __init__(self):
        self.logger = logging.Logger(self.__class__.__name__)
        self.logger.setLevel(defaultLoggingLevel)
        self.logger.addHandler(defaultLoggingHandler)

    def convert_file(self, fileName):
        for format in self.sourceFormats:
            try:
                sourceFile = codecs.open(fileName, 'rU', format)
                convertedFile = []
                for line in sourceFile:
                    convertedFile.append(line.encode("utf-8"))

                return convertedFile
            except UnicodeDecodeError:
                pass
        self.logger.error("Error: failed to convert '" + fileName + "'.")


    def get_subtitle_list(self, path):
        outputList = []
        f = self.convert_file(path)
        #f = open(path, 'r')
        state = SubtitlesLoader.LOOK_FOR_ID
        for line in f:
            line = line.rstrip()
            line = line.decode("utf8")

            if line.startswith(codecs.BOM_UTF8):
                line = line[1:]

            if state == SubtitlesLoader.LOOK_FOR_ID:
                if len(line) > 0:
                    current = Subtitle()
                    try:
                        current.set_id(int(line))
                        state = SubtitlesLoader.LOOK_FOR_TIME
                    except:
                        pass
            elif state == SubtitlesLoader.LOOK_FOR_TIME:
                if len(line) > 0:
                    #00:00:06,290 --> 00:00:07,550
                    regexp = '([0-9]{2}):([0-9]{2}):([0-9]{2}),([0-9]+) --> ([0-9]{2}):([0-9]{2}):([0-9]{2}),([0-9]+)'
                    if re.search(regexp, line):
                        m = re.search(regexp, line)

                        beginMili = m.group(4)
                        while len(beginMili) < 3:
                            beginMili += "0"

                        endMili = m.group(8)
                        while len(endMili) < 3:
                            endMili += "0"

                        beginTime = int(m.group(1)) * 1000 * 3600
                        beginTime += int(m.group(2)) * 1000 * 60
                        beginTime += int(m.group(3)) * 1000
                        beginTime += int(beginMili)

                        endTime = int(m.group(5)) * 1000 * 3600
                        endTime += int(m.group(6)) * 1000 * 60
                        endTime += int(m.group(7)) * 1000
                        endTime += int(endMili)

                        current.set_time_begin(beginTime)
                        current.set_time_end(endTime)
                        current.set_text('')
                        state = SubtitlesLoader.LOOK_FOR_TEXT
            elif state == SubtitlesLoader.LOOK_FOR_TEXT:
                if len(line) > 0:
                    if len(current.get_text()) == 0:
                        current.set_text(line)
                    else:
                        current.set_text(current.get_text() + " " + line)
                else:
                    state = SubtitlesLoader.LOOK_FOR_ID
                    if len(current.get_text()) > 0:
                        outputList.append(current)

        if len(current.get_text()) > 0:
            outputList.append(current)

        return outputList

    def compact_subtitles_list(self, list, timeToMerge, maxTime):
        outputList = []
        id = 0
        current = None
        for sub in list:
            if id == 0 or (sub.get_time_begin() - current.get_time_end() > int(timeToMerge * 1000)) or (sub.get_time_end() - current.get_time_begin() > int(maxTime * 1000)):
                if id > 0:
                    outputList.append(current)
                id += 1
                current = Subtitle()
                current.set_id(id)
                current.set_text(sub.get_text())
                current.set_time_begin(sub.get_time_begin())
                current.set_time_end(sub.get_time_end())
            else:
                current.set_text(current.get_text() + " " + sub.get_text())
                current.set_time_end(sub.get_time_end())
        if current:
            outputList.append(current)
        return outputList

class Subtitle(object):


    def __init__(self):
        self.text = ""

    def get_text(self):
        return self.text

    def get_time_begin(self):
        return self.timeBegin

    def get_time_end(self):
        return self.timeEnd

    def get_id(self):
        return self.id

    def set_text(self, text):
        # | mean new line in some srt files
        text = text.replace("|", "\n")
        #Some subs have <i>...</i> or {]@^\`}. We need to delete them.
        text = re.sub("(<" "[^>]*" ">)"
                      "|"
                      "(\{" "[^\}]*" "\})"
                      , "", text)
        self.text = text


    def set_time_begin(self, timeBegin):
        self.timeBegin = timeBegin

    def set_time_end(self, timeEnd):
        self.timeEnd = timeEnd

    def set_id(self, id):
        self.id = id
