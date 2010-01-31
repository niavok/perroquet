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


import re
from word import *

class CompleteSequenceError(Exception):
    pass

class Sequence(object):
    def __init__(self, aditionnalChars=""):

        # self._symbolList = what is between words (or "")
        # self._wordList = words that we want to find
        # self._workList = words that was writen (or "")
        # self._workValidityList = 1 if the word if good, 0 if it is empty
        #        -levenshtein between it and the normal word otherwise
        #
        # self._activeWordIndex = the word that is currently being edited
        # self._activeWordPos = the position in that word
        #
        # self._helpChar = the char printed when you want a hint
        #
        # Note: self._symbolList, self._wordList, Listself._workList
        # and self._workValidityList have always the same length

        self._symbolList = []
        self._wordList = []
        self._workList = []
        self._workValidityList = []

        self._activeWordIndex = 0
        self._activeWordPos = 0

        self._helpChar = '~'
        
        allChar = "0-9\'a-zA-Z"+aditionnalChars
        self.validChar = "["+allChar+"]"
        self.notValidChar = "[^"+allChar+"]"

    def Load(self, text):
        textToParse = text
        
        #We want swswsw... (s=symbol, w=word)
        #So if the 1st char isn't a symbole, we want an empty symbole
        if re.match(self.validChar, textToParse[0]):
            self._symbolList.append('')    
        while len(textToParse) > 0:
            # if the text begin with a word followed by a not word character
            if re.match('^('+self.validChar+'+)'+self.notValidChar, textToParse):
                m = re.search('^('+self.validChar+'+)'+self.notValidChar, textToParse)
                word = m.group(1)
                sizeToCut =  len(word)
                textToParse = textToParse[sizeToCut:]
                self._wordList.append(word)
                self._workList.append("")
                self._workValidityList.append(0)
            # if the text begin with no word character but followed by a word
            elif re.match('^('+self.notValidChar+'+)'+self.validChar, textToParse):
                m = re.search('^('+self.notValidChar+'+)'+self.validChar, textToParse)
                symbol = m.group(1)
                sizeToCut = len(symbol)
                textToParse = textToParse[sizeToCut:]
                self._symbolList.append(symbol)
            # if there is only one word or one separator
            else:
                # if there is only one word
                if re.match('^('+self.validChar+'+)', textToParse):
                    self._wordList.append(textToParse)
                    self._workList.append("")
                    self._workValidityList.append(0)
                # if there is only one separator
                else:
                    self._symbolList.append(textToParse)
                break

    def GetSymbolList(self):
        return self._symbolList

    def GetWordList(self):
        return self._wordList

    def GetWorkList(self):
        return self._workList

    def GetWordCount(self):
        return len(self._wordList)

    def GetActiveWordIndex(self):
        return self._activeWordIndex

    def SetActiveWordIndex(self, index):
        self._activeWordIndex = index

    def GetActiveWordPos(self):
        return self._activeWordPos

    def SetActiveWordPos(self, index):
        self._activeWordPos = index

    def SelectSequenceWord(self, wordIndex,wordIndexPos):
        self._activeWordPos = wordIndexPos
        self._activeWordIndex = wordIndex

        if self.IsValidWord():
            self.NextWord()

    def WriteCharacter(self, character):
        if self.IsValidWord():
            if self.NextWord():
                self.WriteCharacter(character)
            else:
                raise CompleteSequenceError
        else:
            #if replacing an helpChar
            if self._activeWordPos < len(self._workList[self._activeWordIndex]) and self._workList[self._activeWordIndex][self._activeWordPos] == self._helpChar:
                self._workList[self._activeWordIndex] = self._workList[self._activeWordIndex][:self._activeWordPos] + character + self._workList[self._activeWordIndex][self._activeWordPos+1:]
            else:
                self._workList[self._activeWordIndex] = self._workList[self._activeWordIndex][:self._activeWordPos] + character + self._workList[self._activeWordIndex][self._activeWordPos:]
            self._activeWordPos += 1
            self.WorkChange()


    def DeletePreviousCharacter(self):
        if self.IsValidWord():
            if self.PreviousWord():
                self.DeletePreviousCharacter()
        elif len(self._workList[self._activeWordIndex]) == 0:
            if self.PreviousWord():
                self.DeletePreviousCharacter()
        elif self._activeWordPos == 0:
            if self.PreviousWord():
                self.DeletePreviousCharacter()
        else:
            self._workList[self._activeWordIndex] = self._workList[self._activeWordIndex][:self._activeWordPos-1]  + self._workList[self._activeWordIndex][self._activeWordPos:]
            self._activeWordPos -= 1
            self.WorkChange()

    def DeleteNextCharacter(self):
        if self.IsValidWord():
            if self.NextWord(False):
                self.DeleteNextCharacter()
        elif len(self._workList[self._activeWordIndex]) == 0:
            if self.NextWord(False):
                self.DeleteNextCharacter()
        elif self._activeWordPos == len(self._workList[self._activeWordIndex]) :
            if self.NextWord(False):
                self.DeleteNextCharacter()
        else:
            self._workList[self._activeWordIndex] = self._workList[self._activeWordIndex][:self._activeWordPos]  + self._workList[self._activeWordIndex][self._activeWordPos+1:]
            self.WorkChange()

    def NextWord(self, end = True):
        if self._activeWordIndex < len(self._workList) - 1:
            self._activeWordIndex +=1
            if end:
                self._activeWordPos = len(self._workList[self._activeWordIndex])
            else:
                self._activeWordPos = 0
            if self.IsValidWord():
                return self.NextWord(end)
            else:
                return True
        else:
            if end:
                self._activeWordPos = len(self._workList[self._activeWordIndex])
            else:
                self._activeWordPos = 0
            return False

    def PreviousWord(self, end = True):
        if self._activeWordIndex > 0:
            self._activeWordIndex -=1
            if end:
                self._activeWordPos = len(self._workList[self._activeWordIndex])
            else:
                self._activeWordPos = 0
            if self.IsValidWord():
                return self.PreviousWord()
            else:
                return True
        else:
            if end:
                self._activeWordPos = len(self._workList[self._activeWordIndex])
            else:
                self._activeWordPos = 0
            return False


    def FirstWord(self):
        self._activeWordIndex = 0
        self._activeWordPos = 0
        while self.IsValidWord():
            if not self.NextWord(False):
                break


    def LastWord(self):
        self._activeWordIndex = len(self._workList) -1
        self._activeWordPos = len(self._workList[self._activeWordIndex])
        while self.IsValidWord():
            if not self.PreviousWord(True):
                break

    def NextCharacter(self):
        if self._activeWordPos >= len(self._workList[self._activeWordIndex]):
            self.NextWord(False)
        else:
            self._activeWordPos += 1

    def PreviousCharacter(self):
        if self._activeWordPos == 0:
            self.PreviousWord()
        else:
            self._activeWordPos -= 1

    def IsValidWord(self, i=None):
        if i==None:
            i=self._activeWordIndex
        return self._workList[i].lower() == self._wordList[i].lower()
    
    def IsEmptyWord(self, i=None):
        if i==None:
            i=self._activeWordIndex
        return self._workList[i]==""
        
    def GetValidity(self, index):
        return self._workValidityList[index]

    def IsValid(self):
        return [w.lower() for w in self._workList] == [w.lower() for w in self._wordList]

    def GetWordFound(self):
        found = 0
        id = 0
        for word in self._workList:
            if word.lower() == self._wordList[id].lower():
                found += 1
            id += 1
        return found

    def IsEmpty(self):
        return all(word=="" for word in self._workList)

    def CompleteWord(self):
        """Reveal correction for word at cursor in current sequence"""
        if self.IsValidWord():
            if self.NextWord(False):
                self.CompleteWord()
            return

        currentWord = self._workList[self._activeWordIndex]
        goodWord = self._wordList[self._activeWordIndex]

        outWord = ""
        first_error = -1
        for i in range(0, len(goodWord)):
            if i < len(currentWord) and currentWord[i].lower() == goodWord[i].lower():
                outWord += goodWord[i]
            else:
                outWord += self._helpChar
                if first_error == -1:
                    first_error = i

        if len(currentWord) == len(goodWord) and first_error != -1:
            outWord = outWord[:first_error] + goodWord[first_error] + outWord[first_error+1:]
            self._activeWordPos = first_error+1
            print 1
        elif first_error != -1:
            self._activeWordPos = first_error
            print 2
        else:
            self._activeWordPos = 0
            print 3
            
        self._workList[self._activeWordIndex] = outWord
        self.WorkChange()

    def CompleteAll(self):
        """Reveal all words"""
        for (i, word) in enumerate(self._wordList):
            self._workList[i] = word
            self.ComputeValidity(i)

    def WorkChange(self):
        """Update the validity of the current word"""
        self.ComputeValidity(self._activeWordIndex)

        if not startWith(self._wordList[self._activeWordIndex], self._workList[self._activeWordIndex]):
            #Verify position only if the word isn't at his right place
            #but maybe not fully written
            location = self.CheckLocation(self._activeWordIndex)
            if location != -1:
                self._workList[location] = self._workList[self._activeWordIndex]
                self._workList[self._activeWordIndex] = ""
                self.ComputeValidity(self._activeWordIndex)
                self.ComputeValidity(location)
                self._activeWordPos = 0

    def ComputeValidity(self, index):
        """Compute a score between 1 and 0 and -1 (or less)
        0 if the word is empty
        1 if the word is completed
        negative if the user type a lot of mistake
        20% of the score is given by the lenght and 80% by the good letters"""

        #Global check
        if self._workList[index].lower() == self._wordList[index].lower():
            validity = 1
        elif self._workList[index] == "":
            validity = 0
        else:
            validity = -levenshtein(self._workList[index].lower(), 
                                    self._wordList[index].lower())
            
        self._workValidityList[index] = validity

    def CheckLocation(self, index):
        """Check if the word is correct but at the wrong place."""
        for i in range(1,4):
            if index+i < len(self._wordList) and self.GetValidity(index+i) != 1 and self._workList[index].lower() == self._wordList[index+i].lower():
                return index + i
            if index-i >= 0 and self.GetValidity(index-i) != 1 and self._workList[index].lower() == self._wordList[index-i].lower():
                return index - i

        return -1

    def GetTimeBegin(self):
        return self.beginTime

    def GetTimeEnd(self):
        return self.endTime

    def SetTimeBegin(self, time):
        self.beginTime = time

    def SetTimeEnd(self, time):
        self.endTime = time
