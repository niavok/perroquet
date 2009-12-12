# -*- coding: utf-8 -*-

import re
from video_player import VideoPlayer
from subtitles_loader import SubtitlesLoader

class Core(object):
    WAIT_BEGIN = 0
    WAIT_END = 1

    def __init__(self):
        self.player = VideoPlayer()
        self.subtitles = SubtitlesLoader()
        self.subList = self.subtitles.GetSubtitleList('/home/fred/Vidéos/The Big Bang Theory/The.Big.Bang.Theory.S01E01.HDTV.XviD-XOR.eng.srt')
        self.subList = self.subtitles.CompactSubtitlesList(self.subList)
        for sub in self.subList:
            print str(sub.GetId()) + " " + sub.GetText()

    def SetGui(self, gui):
        self.gui = gui

    def SetVideoPath(self, path):
        self.player.SetWindowId(self.gui.GetVideoWindowId())
        self.player.Open(path)
        self.InitExercice()
        self.player.Play()

    def InitExercice(self):
        self.player.SetCallback(self.TimeCallback)
        self.player.SetNextCallbackTime(self.subList[0].GetTimeBegin())
        self.currentSubId = 0
        self.state = Core.WAIT_BEGIN

    def TimeCallback(self):
        if self.state == Core.WAIT_BEGIN:
            self.player.SetNextCallbackTime(self.subList[self.currentSubId].GetTimeEnd())
            print "load"
            self.sequence = Sequence()

            self.sequence.Load(self.subList[self.currentSubId].GetText())
            print "load2"
            self.gui.SetSequence(self.sequence)
            print self.subList[self.currentSubId].GetText()
            self.state = Core.WAIT_END
        elif self.state == Core.WAIT_END:
            self.state = Core.WAIT_BEGIN
            self.currentSubId += 1
            self.player.SetNextCallbackTime(self.subList[self.currentSubId].GetTimeBegin())
            #self.player.Pause()


class Sequence(object):

    def Load(self, text):
        self.symbolList = []
        self.wordList = []
        textToParse = text

        while len(textToParse) > 0:
            print textToParse
            if re.match('^([0-9\'a-zA-Z]+)[^0-9\'a-zA-Z]', textToParse):
                print "match"
                m = re.search('^([0-9\'a-zA-Z]+)[^0-9\'a-zA-Z]', textToParse)
                word = m.group(1)
                sizeToCut =  len(word)
                textToParse = textToParse[sizeToCut:]
                if len(self.wordList) == len(self.symbolList) :
                    symbolList.append("")
                self.wordList.append(word)
            elif re.match('^([^0-9\'a-zA-Z]+)[0-9\'a-zA-Z]', textToParse):
                print "not match"
                m = re.search('^([^0-9\'a-zA-Z]+)[0-9\'a-zA-Z]', textToParse)
                symbol = m.group(1)
                print symbol
                sizeToCut = len(symbol)
                textToParse = textToParse[sizeToCut:]
                self.symbolList.append(symbol)
            else:
                if re.match('^([0-9\'a-zA-Z]+)', textToParse):
                    self.wordList.append(textToParse)
                else:
                    self.symbolList.append(textToParse)
                break
            print "while end"
        print "laod end"


    def GetSymbolList(self):
        return self.symbolList

    def GetWordList(self):
        return self.wordList
