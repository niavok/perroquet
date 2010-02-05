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
from word import *

class Sequence(object):
    def __init__(self, aditionnalChars=""):

        # self._symbolList = what is between words (or "")
        # self._wordList = a list of Words items that we want to find
        # self._workValidityList = 1 if the word if good, 0 if it is empty
        #        -levenshtein between it and the normal word otherwise
        #
        # self._activeWordIndex = the word that is currently being edited
        # self.getActiveWord().getPos() = the position in that word
        #
        # self._helpChar = the char printed when you want a hint
        #
        # Note: self._symbolList, self._wordList
        #  have always the same length

        self._symbolList = []
        self._wordList = []

        self._activeWordIndex = 0

        self._helpChar = '~'
        
        allChar = "0-9\'a-zA-Z"+aditionnalChars
        self.validChar = "["+allChar+"]"
        self.notValidChar = "[^"+allChar+"]"

    def load(self, text):
        #TODO FIXME
        textToParse = text
        #We want swswsw... (s=symbol, w=word)
        #So if the 1st char isn't a symbole, we want an empty symbole
        if re.match(self.validChar, textToParse[0]):
            self._symbolList.append('')
        while len(textToParse) > 0:
            # if the text begin with a word followed by a not word char
            if re.match('^('+self.validChar+'+)'+self.notValidChar, textToParse):
                m = re.search('^('+self.validChar+'+)'+self.notValidChar, textToParse)
                word = m.group(1)
                sizeToCut =  len(word)
                textToParse = textToParse[sizeToCut:]
                self._wordList.append(Word(word))
            # if the text begin with no word char but followed by a word
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
                    self._wordList.append(Word(textToParse))
                # if there is only one separator
                else:
                    self._symbolList.append(textToParse)
                break
        
    def getSymbols(self):
        return self._symbolList

    def getWords(self):
        return self._wordList
    
    def getWordCount(self):
        return len(self._wordList)

    def getActiveWordIndex(self):
        return self._activeWordIndex

    def setActiveWordIndex(self, index):
        if index==-1:
            index=self.getWordCount()
            
        if index<0 or index>self.getWordCount():
            raise AttributeError, str(index)
            
        self._activeWordIndex = index
    
    def getLastIndex(self):
        return len(self._wordList) - 1

    def getActiveWord(self):
        return self.getWords()[self.getActiveWordIndex()]
    
    def GetWordFound(self):
        return len([w for w in self.getWords() if w.isValid()])
        
    def nextWord(self, loop=False):
        "go to the next word"
        if self.getActiveWordIndex() < self.getLastIndex():
            self._activeWordIndex +=1
            self.getActiveWord().setPos(0)
        else:
            if not loop:
                pass
            else:
                raise NotImplemented
            
    def nextFalseWord(self, loop=False):
        "go to the next non valid word"
        if loop:
            raise NotImplemented
        if self.getActiveWord().isValid():
            if self.isValid() or self.getActiveWordIndex() == self.getLastIndex():
                return
            self.nextWord()
            self.nextFalseWord()
    
    def previousWord(self, loop=False):
        "go to the previous word"
        if self.getActiveWordIndex() > 0:
            self._activeWordIndex -= 1
            self.getActiveWord().setPos(self.getActiveWord().getLastPos())
        else:
            if not loop:
                pass
            else:
                raise NotImplemented
            
    def previousFalseWord(self, loop=False):
        "go to the previous non valid word"
        if loop:
            raise NotImplemented
        if self.getActiveWord().isValid():
            if self.isValid() or self.getActiveWordIndex() == 0:
                return
            self.previousWord()
            self.previousFalseWord()

    def selectSequenceWord(self, wordIndex,wordIndexPos):
        self.getActiveWord().setPos(wordIndexPos)
        self.setActiveWordIndex(wordIndex)

        self.nextFalseWord()

    def writeChar(self, char):
        try:
            self.getActiveWord().writeChar(char)
            if self.getActiveWord().isValid():
                self.nextChar()
        except ValidWordError:
            self.nextWord()
            self.nextFalseWord()
            self.writeChar(char)
        self.updateAfterWrite()
    
    def _writeSentence(self, sentence):
        """write many chars. a ' ' mean next word.
        Only for tests"""
        for char in sentence:
            if char==" ":
                pass
            elif char=="+":
                self.nextWord()
                self.nextFalseWord()
            else:
                self.writeChar(char)
    
    def deleteNextChar(self):
        self.previousFalseWord()
        try:
            self.getActiveWord().deleteNextChar()
        except NoCharPossible:
            if self.getActiveWordIndex() < self.getWordCount():
                self.previousWord()
                self.deleteNextChar()
        self.updateAfterWrite()

    def deletePreviousChar(self):
        self.previousFalseWord()
        try:
            self.getActiveWord().deletePreviousChar()
        except NoCharPossible:
            if self.getActiveWordIndex() > 0:
                self.previousWord()
                self.deletePreviousChar()
        except ValidWordError:
            if self.getActiveWordIndex() > 0:
                self.previousWord()
                self.deletePreviousChar()
            
        self.updateAfterWrite()

    def firstFalseWord(self):
        self._activeWordIndex = 0
        self.getActiveWord().setPos(0)
        self.nextFalseWord()

    def lastFalseWord(self):
        self._activeWordIndex = self.getLastIndex()
        self.getActiveWord().setPos(self.getActiveWord().getLastPos())
        self.previousFalseWord()
        
    def nextChar(self):
        try:
            self.getActiveWord().nextChar()
        except NoCharPossible:
            self.nextWord()
            self.nextFalseWord()
            self.getActiveWord().setPos(0)

    def previousChar(self):
        try:
            self.getActiveWord().previousChar()
        except NoCharPossible:
            self.previousWord()
            self.previousFalseWord()
            self.getActiveWord().setPos(-1)

    def isValid(self):
        return all(w.isValid() for w in self.getWords())

    def isEmpty(self):
        return all(w.isEmpty() for w in self.getWords())
        
    def completeAll(self):
        """Reveal all words"""
        for w in self.getWords():
            w.complete()
    
    def updateAfterWrite(self):
        "update after a modification of the text"
        self._checkLocation()
    
    def _checkLocation(self):
        """Check if a word is correct but at a wrong place."""
        for w1 in self.getWords():
            for j, w2 in enumerate(self.getWords()):
                if w1.getScore()<=0 and w1.getText()==w2.getValid() and not w2.isValid():
                    w2.setText(w1.getText())
                    w1.setText("")
                    self.setActiveWordIndex(j)
                    self.nextFalseWord()

    def getTimeBegin(self):
        return self.beginTime

    def getTimeEnd(self):
        return self.endTime

    def setTimeBegin(self, time):
        self.beginTime = time

    def setTimeEnd(self, time):
        self.endTime = time
    
    def showHint(self): 
        try:
            self.getActiveWord().showHint()
        except ValidWordError:
            if self.getActiveWordIndex()==self.getWordCount()-1:
                return
            else:
                self.nextWord()
                self.showHint()
    
    def __print__(self):
        return "-".join(w.getText() for w in self.getWords())+" VS "+"-".join(w.getValid() for w in self.getWords())
    
    def __repr__(self):
        return self.__print__()
