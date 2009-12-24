# -*- coding: utf-8 -*-

import re, gtk, thread, time
from video_player import VideoPlayer
from subtitles_loader import SubtitlesLoader

class Core(object):
    WAIT_BEGIN = 0
    WAIT_END = 1

    def __init__(self):
        self.player = VideoPlayer()
        self.subtitles = SubtitlesLoader()
        
    def SetGui(self, gui):
        self.gui = gui

    def SetPaths(self, videoPath, exercicePath):
        self.subList = self.subtitles.GetSubtitleList(exercicePath)
        for sub in self.subList:
            print str(sub.GetId()) + " " + sub.GetText()

        self.subList = self.subtitles.CompactSubtitlesList(self.subList)
        
        for sub in self.subList:
            print str(sub.GetId()) + " " + sub.GetText()

        #for sub in self.subList:
        #    print str(sub.GetId()) + " " + sub.GetText()

    
        self.player.SetWindowId(self.gui.GetVideoWindowId())
        self.player.Open(videoPath)
        self.InitExercice()
        self.player.Play()
        self.paused = False

    def InitExercice(self):
        print "InitExercice"
        self.player.SetCallback(self.TimeCallback)
        self.sequenceList = []
        self.paused = False
        for sub in self.subList:
            self.sequence = Sequence()
            self.sequence.Load(sub.GetText())
            self.sequenceList.append(self.sequence)
        self.currentSubId = 0
        self.gui.Activate()
        self.ActivateSequence()
        self.timeUpdateThreadId = thread.start_new_thread(self.timeUpdateThread, ())


    def TimeCallback(self):
        if self.state == Core.WAIT_BEGIN:
            self.player.SetNextCallbackTime(self.subList[self.currentSubId].GetTimeEnd() + 500)
            self.state = Core.WAIT_END
        elif self.state == Core.WAIT_END:
            self.state = Core.WAIT_BEGIN
            #self.currentSubId += 1
            #self.player.SetNextCallbackTime(self.subList[self.currentSubId].GetTimeBegin())
            if self.validSequence:
                gtk.gdk.threads_enter()
                self.NextSequence(False)
                gtk.gdk.threads_leave()
            else:
                self.player.Pause()
                
                

    def RepeatSequence(self):
        print "RepeatSequence"
        self.GotoSequenceBegin()
        self.player.Play()
        self.paused = False

    def SelectSequence(self, num, load = True):
        print "SelectSequence " + str(num) + " " + str(self.currentSubId)
        if self.currentSubId == num:
            return
        self.currentSubId = num
        self.ActivateSequence()
        if load:
            self.RepeatSequence()

    def NextSequence(self, load = True):
        print "NextSequence"
        if self.currentSubId < len(self.sequenceList)-1:
            self.currentSubId += 1
        self.ActivateSequence()
        if load:
            self.RepeatSequence()

    def PreviousSequence(self):
        print "PreviousSequence"
        if self.currentSubId > 0:
            self.currentSubId -= 1
        self.ActivateSequence()
        self.RepeatSequence()

    def ActivateSequence(self):
        print "ActivateSequence"
        self.state = Core.WAIT_BEGIN
        self.player.SetNextCallbackTime(self.subList[ self.currentSubId].GetTimeBegin())
        self.sequence = self.sequenceList[self.currentSubId]

        self.validSequence = self.sequence.IsValid()

        print "ActivateSequence: loaded"
        self.gui.SetSequenceNumber(self.currentSubId, len(self.subList)) 
        self.gui.SetSequence(self.sequence)
        print "ActivateSequence: end"

    def ValidateSequence(self):
        if self.sequence.IsValid():
            self.validSequence = True
            self.RepeatSequence()

    def GotoSequenceBegin(self):
        self.state = Core.WAIT_END
        begin_time = self.subList[self.currentSubId].GetTimeBegin() - 1000
        if begin_time < 0:
            begin_time = 0
        self.player.Seek(begin_time)
        self.player.SetNextCallbackTime(self.subList[self.currentSubId].GetTimeEnd())

    def WriteCharacter(self, character):
        if character == "apostrophe":
            character = "'"
        if re.match('^[0-9\'a-zA-Z]$',character):
            self.sequence.WriteCharacter(character)
            self.gui.SetSequence(self.sequence)
            self.ValidateSequence()


    def NextWord(self):
        print "NextWord"
        self.sequence.NextWord(False)
        self.gui.SetSequence(self.sequence)

    def FirstWord(self):
        print "FirstWord"
        while self.sequence.PreviousWord(False):
            continue
        self.gui.SetSequence(self.sequence)

    def LastWord(self):
        print "LastWord"
        while self.sequence.NextWord():
            continue
        self.gui.SetSequence(self.sequence)

    def DeletePreviousChar(self):
        self.sequence.DeletePreviousCharacter()
        self.gui.SetSequence(self.sequence)
        self.ValidateSequence()

    def DeleteNextChar(self):
        self.sequence.DeleteNextCharacter()
        self.gui.SetSequence(self.sequence)
        self.ValidateSequence()

    def PreviousChar(self):
        self.sequence.PreviousCharacter()
        self.gui.SetSequence(self.sequence)

    def NextChar(self):
        self.sequence.NextCharacter()
        self.gui.SetSequence(self.sequence)

    def CompleteWord(self):
        self.sequence.CompleteWord()
        self.gui.SetSequence(self.sequence)
        self.ValidateSequence()

    def TooglePause(self):
        print "TooglePause " + str(self.player.IsPaused()) + " " + str(self.paused)
        if self.player.IsPaused() and self.paused:
            self.player.Play()
            self.paused = False
        elif not self.player.IsPaused() and not self.paused:
            self.player.Pause()
            self.paused = True
    def SeekSequence(self, time):
        begin_time = self.subList[self.currentSubId].GetTimeBegin() - 1000
        if begin_time < 0:
            begin_time = 0
            
        pos = begin_time + time
        self.player.Seek(pos)
        self.player.SetNextCallbackTime(self.subList[self.currentSubId].GetTimeEnd() + 500)
        self.state = Core.WAIT_END
        self.player.Play()
        self.paused = False

    
    def timeUpdateThread(self):
        timeUpdateThreadId = self.timeUpdateThreadId
        #gtk.gdk.threads_enter()
        #self.time_label.set_text("00:00 / 00:00")
        #gtk.gdk.threads_leave()
        while timeUpdateThreadId == self.timeUpdateThreadId:
            time.sleep(0.5)
            pos_int = self.player.GetCurrentTime()
            if pos_int != None:
                end_time = self.subList[self.currentSubId].GetTimeEnd()
                begin_time = self.subList[self.currentSubId].GetTimeBegin() - 1000
                if begin_time < 0:
                    begin_time = 0
                duration =  end_time - begin_time 
                pos = pos_int -begin_time
                self.gui.SetSequenceTime(pos, duration)


class Sequence(object):

    def Load(self, text):
        self.symbolList = []
        self.wordList = []
        self.workList = []
        textToParse = text
        self.activeWordIndex = 0
        self.activeWordPos = 0
        self.helpChar = '~'
        #print textToParse
        while len(textToParse) > 0:
            if re.match('^([0-9\'a-zA-Z]+)[^0-9\'a-zA-Z]', textToParse):
                #print "match"
                m = re.search('^([0-9\'a-zA-Z]+)[^0-9\'a-zA-Z]', textToParse)
                word = m.group(1)
                sizeToCut =  len(word)
                textToParse = textToParse[sizeToCut:]
                if len(self.wordList) == len(self.symbolList) :
                    self.symbolList.append('')
                self.wordList.append(word)
                self.workList.append('')
            elif re.match('^([^0-9\'a-zA-Z]+)[0-9\'a-zA-Z]', textToParse):
                #print "not match"
                m = re.search('^([^0-9\'a-zA-Z]+)[0-9\'a-zA-Z]', textToParse)
                symbol = m.group(1)
                #print symbol
                sizeToCut = len(symbol)
                textToParse = textToParse[sizeToCut:]
                self.symbolList.append(symbol)
            else:
                if re.match('^([0-9\'a-zA-Z]+)', textToParse):
                    self.wordList.append(textToParse)
                    self.workList.append(textToParse)
                else:
                    self.symbolList.append(textToParse)
                break
            #print "while end"
        #print "load end"


    def GetSymbolList(self):
        return self.symbolList

    def GetWordList(self):
        return self.wordList

    def GetWorkList(self):
        return self.workList

    def GetActiveWordIndex(self):
        return self.activeWordIndex

    def SetActiveWordIndex(self, index):
        self.activeWordIndex = index

    def GetActiveWordPos(self):
        return self.activeWordPos

    def SetActiveWordPos(self, index):
        self.activeWordPos = index

    def WriteCharacter(self, character):
        if self.IsValidWord():
            if self.NextWord():
                self.WriteCharacter(character)
        else:
            if self.activeWordPos < len(self.workList[self.activeWordIndex]) and self.workList[self.activeWordIndex][self.activeWordPos] == self.helpChar:
                self.workList[self.activeWordIndex] = self.workList[self.activeWordIndex][:self.activeWordPos] + character + self.workList[self.activeWordIndex][self.activeWordPos+1:]
            else:
                self.workList[self.activeWordIndex] = self.workList[self.activeWordIndex][:self.activeWordPos] + character + self.workList[self.activeWordIndex][self.activeWordPos:]
            self.activeWordPos += 1


    def DeletePreviousCharacter(self):
        if self.IsValidWord():
            if self.PreviousWord():
                self.DeletePreviousCharacter()
        elif len(self.workList[self.activeWordIndex]) == 0:
            if self.PreviousWord():
                self.DeletePreviousCharacter()
        elif self.activeWordPos == 0:
            if self.PreviousWord():
                self.DeletePreviousCharacter()
        else:
            self.workList[self.activeWordIndex] = self.workList[self.activeWordIndex][:self.activeWordPos-1]  + self.workList[self.activeWordIndex][self.activeWordPos:]
            self.activeWordPos -= 1

    def DeleteNextCharacter(self):
        if self.IsValidWord():
            if self.NextWord(False):
                self.DeleteNextCharacter()
        elif len(self.workList[self.activeWordIndex]) == 0:
            if self.NextWord(False):
                self.DeleteNextCharacter()
        elif self.activeWordPos == len(self.workList[self.activeWordIndex]) :
            if self.NextWord(False):
                self.DeleteNextCharacter()
        else:
            self.workList[self.activeWordIndex] = self.workList[self.activeWordIndex][:self.activeWordPos]  + self.workList[self.activeWordIndex][self.activeWordPos+1:]

    def NextWord(self, end = True):
        if self.activeWordIndex < len(self.workList) - 1:
            self.activeWordIndex +=1
            if end:
                self.activeWordPos = len(self.workList[self.activeWordIndex])
            else:
                self.activeWordPos = 0
            if self.IsValidWord():
                return self.NextWord(end)
            else:
                return True
        else:
            if end:
                self.activeWordPos = len(self.workList[self.activeWordIndex])
            else:
                self.activeWordPos = 0
            return False


    def PreviousWord(self, end = True):
        if self.activeWordIndex > 0:
            self.activeWordIndex -=1
            if end:
                self.activeWordPos = len(self.workList[self.activeWordIndex])
            else:
                self.activeWordPos = 0
            if self.IsValidWord():
                return self.PreviousWord()
            else:
                return True
        else:
            if end:
                self.activeWordPos = len(self.workList[self.activeWordIndex])
            else:
                self.activeWordPos = 0
            return False


    def NextCharacter(self):
        if self.activeWordPos >= len(self.workList[self.activeWordIndex]):
            self.NextWord(False)
        else:
            self.activeWordPos += 1

    def PreviousCharacter(self):
        if self.activeWordPos == 0:
            self.PreviousWord()
        else:
            self.activeWordPos -= 1

    def IsValidWord(self):
        if self.workList[self.activeWordIndex].lower() == self.wordList[self.activeWordIndex].lower():
            return True
        else:
            return False

    def IsValid(self):
        valid = True
        id = 0
        for word in self.workList:
            if word.lower() != self.wordList[id].lower():
                valid = False
                break
            id += 1
        print "valid : " + str(valid)
        return valid


    def CompleteWord(self):
        if self.IsValidWord():
            if self.NextWord(False):
                self.CompleteWord()
            return

        currentWord = self.workList[self.activeWordIndex]
        goodWord = self.wordList[self.activeWordIndex]

        outWord = ""
        first_error = -1
        for i in range(0, len(goodWord)):
            if i < len(currentWord) and currentWord[i].lower() == goodWord[i].lower():
                outWord += goodWord[i]
            else:
                outWord += self.helpChar
                if first_error == -1:
                    first_error = i

        if len(currentWord) == len(goodWord) and first_error != -1:
            outWord = outWord[:first_error] + goodWord[first_error] + outWord[first_error+1:]
            self.activeWordPos = first_error+1
        elif first_error != -1:
            self.activeWordPos = first_error
        else:
            self.activeWordPos = 0

        self.workList[self.activeWordIndex] = outWord

