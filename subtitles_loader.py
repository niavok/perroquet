# -*- coding: utf-8 -*-

import re

class SubtitlesLoader(object):
    LOOK_FOR_ID = 0
    LOOK_FOR_TIME = 1
    LOOK_FOR_TEXT = 2

    #def __init__(self):

    def GetSubtitleList(self, path):
        outputList = []
        f = open(path, 'r')
        state = SubtitlesLoader.LOOK_FOR_ID
        for line in f:
            line = line.rstrip()
            
            if state == SubtitlesLoader.LOOK_FOR_ID:
                if len(line) > 0:
                    current = Subtitle()
                    current.SetId(int(line))
                    state = SubtitlesLoader.LOOK_FOR_TIME
            elif state == SubtitlesLoader.LOOK_FOR_TIME:
                 if len(line) > 0:
                    #00:00:06,290 --> 00:00:07,550
                    m = re.search('([0-9]{2}):([0-9]{2}):([0-9]{2}),([0-9]{3}) --> ([0-9]{2}):([0-9]{2}):([0-9]{2}),([0-9]{3})', line)

                    beginTime = int(m.group(1))*1000*3600
                    beginTime += int(m.group(2))*1000*60
                    beginTime += int(m.group(3))*1000
                    beginTime += int(m.group(4))

                    endTime = int(m.group(5))*1000*3600
                    endTime += int(m.group(6))*1000*60
                    endTime += int(m.group(7))*1000
                    endTime += int(m.group(8))

                    current.SetTimeBegin(beginTime)
                    current.SetTimeEnd(endTime)
                    current.SetText('')
                    state = SubtitlesLoader.LOOK_FOR_TEXT
            elif state == SubtitlesLoader.LOOK_FOR_TEXT:
                if len(line) > 0:
                    if len(current.GetText()) == 0:
                        current.SetText(line)
                    else:
                        current.SetText(current.GetText() + " " + line)
                else:
                    state = SubtitlesLoader.LOOK_FOR_ID
                    outputList.append(current)
        return outputList

    def CompactSubtitlesList(self, list):
        outputList = []
        id = 0
        
        for sub in list:
            if id == 0 or current.GetTimeEnd() != sub.GetTimeBegin():
                if id > 0:
                    outputList.append(current)
                id += 1
                current = Subtitle()
                current.SetId(id)
                current.SetText(sub.GetText())
                current.SetTimeBegin(sub.GetTimeBegin())
                current.SetTimeEnd(sub.GetTimeEnd())
            else:
                current.SetText(current.GetText() + " " + sub.GetText())
                current.SetTimeEnd(sub.GetTimeEnd())
        outputList.append(current)
        return outputList

class Subtitle(object):
    def GetText(self):
        return self.text

    def GetTimeBegin(self):
        return self.timeBegin

    def GetTimeEnd(self):
        return self.timeEnd

    def GetId(self):
        return self.id

    def SetText(self,text):
        self.text = text

    def SetTimeBegin(self,timeBegin):
        self.timeBegin = timeBegin

    def SetTimeEnd(self,timeEnd):
        self.timeEnd = timeEnd

    def SetId(self,id):
        self.id = id

