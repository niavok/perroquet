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

class ValidWordError(Exception):
    pass
class NoCharPossible(Exception):
    pass
    
def levenshtein(a,b):
    "Calculates the Levenshtein distance between a and b."
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a,b = b,a
        n,m = m,n
    
    text = range(n+1)
    for i in range(1,m+1):
        previous, text = text, [i]+[0]*n
        for j in range(1,n+1):
            add, delete = previous[j]+1, text[j-1]+1
            change = previous[j-1]
            if a[j-1] != b[i-1]:
                change = change + 1
            text[j] = min(add, delete, change)
            
    return text[n]

class Word:
    """A class that implement a word manipulation with a reference
    text    -> the word that is currently written
    valid   -> the word we want to find
    
    NB: texts are stored lowercases"""
    def __init__(self, validText, helpChar="~"):
        if " " in validText:
            raise AttributeError, "validText=' '"
        self._text = ""
        self._valid = validText
        
        self._helpChar = helpChar
        self._pos = 0

    def levenshtein(self):
        return levenshtein(self.getText(), self.getValid())
        
    def getBeginRight(self):
        """Check if the first chars of self.getValid() is self.getText())"""
        return self.getValid()[:len(self.getText(helpChar=False))]==self.getText(helpChar=False)
    
    def getScore(self):
        """Show if we are near the solution.
        return a float from -1 to 1. more is better"""
        #score1 and score2 are between -1 and 1
        score1_ = (2.*len(self.getValid()) - 2*self.levenshtein() - len(self.getText(helpChar=False))) / max(len(self.getValid()), len(self.getText(helpChar=False)))
        score1 = max(score1_, -1)
        score2 = self.getBeginRight()
        return (score1*8+score2*2)/10
    
    def isValid(self):
        return self.getText() == self.getValid()
    
    def isEmpty(self):
        return self.getText() == ""
    
    def complete(self):
        "Reveal the correction"
        self.setText(self.getValid())
    
    def reset(self):
        "RAZ the current word"
        self.setText("")
    
    def writeChar(self, char):
        char = char.lower()
        if len(char)!=1 or char==" ":
            raise AttributeError, "char='"+char+"'"
        if self.isValid():
            raise ValidWordError
        #if replacing an helpChar
        if self.getPos() < len(self.getText()) and self.getText()[self.getPos()] == self._helpChar:
            self.setText(self.getText()[:self.getPos()] + char + self.getText()[self.getPos()+1:])
        else:
            if self._helpChar in self.getText():
                #removing helps chars
                self.setText("".join(c for c in self.getText() if c!=self._helpChar))
            self.setText(self.getText()[:self.getPos()] + char + self.getText()[self.getPos():])
        self._pos += 1

    def showHint(self):
        """Reveal correction for word at cursor in text sequence"""
        outWord = ""
        first_error = -1
        
        for i in range(0, len(self.getValid())):
            if i < len(self.getText()) and self.getText()[i] == self.getValid()[i]:
                outWord += self.getValid()[i]
            else:
                outWord += self._helpChar
                if first_error == -1:
                    first_error = i
        
        # if fist_error != -1 => the first false char is fist_error  
        # else                => The word is valid
        
        if len(self.getText()) == len(self.getValid()) and first_error != -1:
            outWord = outWord[:first_error] + self.getValid()[first_error] + outWord[first_error+1:]
            self.setPos(first_error+1)
        elif first_error != -1:
            self.setPos(first_error)
        else:
            raise ValidWordError
        
        self.setText(outWord)
    
    def deletePreviousChar(self):
        if self.isValid():
            raise ValidWordError
        elif self.getPos() == 0 or self.getText() =="":
            raise NoCharPossible
        else:
            self.setText(self.getText()[:self.getPos()-1]  + self.getText()[self.getPos():])
            self._pos -= 1
    
    def deleteNextChar(self):
        if self.isValid():
            raise ValidWordError
        elif self.getPos() == len(self.getText()) or self.getText() =="":
            raise NoCharPossible
        else:
            self.setText(self.getText()[:self.getPos()]  + self.getText()[self.getPos()+1:])
            
    def setText(self, text):
        if " " in text:
            raise AttributeError
        self._text = text.lower()
        
    def getText(self, helpChar=True):
        if helpChar:
            return self._text.lower()
        else:
            return "".join([i for i in self.getText() if i!=self._helpChar])
        
    def getValid(self, lower=True):
        if lower:
            return self._valid.lower()
        else:
            return self._valid
    
    def setPos(self, pos):
        "if pos=-1, set at the last position"
        if pos > len(self.getText()) or -2 >= pos:
            raise NoCharPossible
        elif pos==-1:
            self._pos = len(self.getText())
        else:
            self._pos = pos
        
    def getPos(self):
        return self._pos
    
    def getLastPos(self):
        return len(self.getText())
    
    def nextChar(self):
        if self.getPos() < self.getLastPos():
            self._pos += 1
        else:
            raise NoCharPossible
    
    def previousChar(self):
        if self.getPos() > 0:
            self._pos -= 1
        else:
            raise NoCharPossible
    
    def __print__(self):
        return str(self.isValid())+" "+self.getText()+" instead of "+self.getValid()
    
    def __repr__(self):
        return self.getText()+" VS "+self.getValid()
