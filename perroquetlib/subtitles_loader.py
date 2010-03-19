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


import re
import os
import sys
import codecs

class SubtitlesLoader(object):
    LOOK_FOR_ID = 0
    LOOK_FOR_TIME = 1
    LOOK_FOR_TEXT = 2

    sourceFormats = ['ascii', 'iso-8859-1']
    targetFormat = 'utf-8'
    outputDir = 'converted'

    def convertFile(self,fileName):
        for format in self.sourceFormats:
            try:
                sourceFile = codecs.open(fileName, 'rU', format)
                convertedFile = []
                for line in sourceFile:
                    convertedFile.append(line.encode( "utf-8" ))

                return convertedFile
            except UnicodeDecodeError:
                pass

        print("Error: failed to convert '" + fileName + "'.")


    def getSubtitleList(self, path):
        outputList = []
        f = self.convertFile(path)
        #f = open(path, 'r')
        state = SubtitlesLoader.LOOK_FOR_ID
        for line in f:
            line = line.rstrip()
            line = line.decode("utf8")

            #Remove BOM of utf-8 : EFBBBF
            if len(line) >=3 and ord(line[0]) == 0xEF and ord(line[1]) == 0xBB and ord(line[2]) == 0xBF:
                line = line[3:]

            if state == SubtitlesLoader.LOOK_FOR_ID:
                if len(line) > 0:
                    current = Subtitle()
                    try:
                        current.setId(int(line))
                        state = SubtitlesLoader.LOOK_FOR_TIME
                    except:
                        pass
            elif state == SubtitlesLoader.LOOK_FOR_TIME:
                 if len(line) > 0:
                    #00:00:06,290 --> 00:00:07,550
                    regexp = '([0-9]{2}):([0-9]{2}):([0-9]{2}),([0-9]+) --> ([0-9]{2}):([0-9]{2}):([0-9]{2}),([0-9]+)'
                    if re.search(regexp,line):
                        m = re.search(regexp, line)

                        beginMili = m.group(4)
                        while len(beginMili) < 3:
                            beginMili += "0"

                        endMili = m.group(8)
                        while len(endMili) < 3:
                            endMili += "0"

                        beginTime = int(m.group(1))*1000*3600
                        beginTime += int(m.group(2))*1000*60
                        beginTime += int(m.group(3))*1000
                        beginTime += int(beginMili)

                        endTime = int(m.group(5))*1000*3600
                        endTime += int(m.group(6))*1000*60
                        endTime += int(m.group(7))*1000
                        endTime += int(endMili)

                        current.setTimeBegin(beginTime)
                        current.setTimeEnd(endTime)
                        current.setText('')
                        state = SubtitlesLoader.LOOK_FOR_TEXT
            elif state == SubtitlesLoader.LOOK_FOR_TEXT:
                if len(line) > 0:
                    if len(current.getText()) == 0:
                        current.setText(line)
                    else:
                        current.setText(current.getText() + " " + line)
                else:
                    state = SubtitlesLoader.LOOK_FOR_ID
                    outputList.append(current)

        if len(current.getText()) > 0:
            outputList.append(current)

        return outputList

    def CompactSubtitlesList(self, list, timeToMerge, maxTime):
        outputList = []
        id = 0
        current = None
        for sub in list:
            if id == 0 or (sub.getTimeBegin() - current.getTimeEnd() > int(timeToMerge*1000)) or (sub.getTimeEnd() - current.getTimeBegin() > int(maxTime*1000)):
                if id > 0:
                    outputList.append(current)
                id += 1
                current = Subtitle()
                current.setId(id)
                current.setText(sub.getText())
                current.setTimeBegin(sub.getTimeBegin())
                current.setTimeEnd(sub.getTimeEnd())
            else:
                current.setText(current.getText() + " " + sub.getText())
                current.setTimeEnd(sub.getTimeEnd())
        if current:
            outputList.append(current)
        return outputList

class Subtitle(object):


    def __init__(self):
        self.text = ""

    def getText(self):
        return self.text

    def getTimeBegin(self):
        return self.timeBegin

    def getTimeEnd(self):
        return self.timeEnd

    def getId(self):
        return self.id

    def setText(self,text):
        # | mean new line in some srt files
        text = text.replace("|","\n")
        #Some subs have <i>...</i> or {]@^\`}. We need to delete them.
        text = re.sub("(<" "[^>]*" ">)"
                      "|"
                      "(\{" "[^\}]*" "\})"
                      , "", text)
        self.text = text


    def setTimeBegin(self,timeBegin):
        self.timeBegin = timeBegin

    def setTimeEnd(self,timeEnd):
        self.timeEnd = timeEnd

    def setId(self,id):
        self.id = id

