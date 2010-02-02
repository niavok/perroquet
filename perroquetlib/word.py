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

def startWith(w1, w2):
    """Check if the first chars of w1 is w2)"""
    return w1[:len(w2)]==w2


class Word:
    """A class that implement a word manipulation with a reference
    text    -> the word that is currently written
    valid   -> the word we want to find"""
    def __init__(self, validText, helpChar="~"):
        if " " in validText:
            raise AttributeError, "validText=' '"
        self._text = ""
        self._valid = validText
        
        self._helpChar = helpChar
        self._pos = 0

    def levenshtein(self):
        return levenshtein(self._text, self._valid)
    
    def getScore(self):
        return 2*len(self._valid) - 2*self.levenshtein() - len(self._text)
    
    def isValid(self):
        return self._text == self._valid
    
    def isEmpty(self):
        return self._text == ""
    
    def complete(self):
        "Reveal the correction"
        self._text = self._valid
    
    def writeChar(self, char):
        if len(char)!=1 or char==" ":
            raise AttributeError, "char='"+char+"'"
        if self.isValid():
            raise ValidWordError
        #if replacing an helpChar
        if self._pos < len(self._text) and self._text[self._pos] == self._helpChar:
            self._text = self._text[:self._pos] + char + self._text[self._pos+1:]
        else:
            if self._helpChar in self._text:
                self._text="".join(c for c in self._text if c!=self._helpChar)
            self._text = self._text[:self._pos] + char + self._text[self._pos:]
        self._pos += 1

    def showHint(self):
        """Reveal correction for word at cursor in text sequence"""
        outWord = ""
        first_error = -1
        
        for i in range(0, len(self._valid)):
            if i < len(self._text) and self._text[i].lower() == self._valid[i].lower():
                outWord += self._valid[i]
            else:
                outWord += self._helpChar
                if first_error == -1:
                    first_error = i
        
        # if fist_error != -1 => the first false char is fist_error  
        # else                => The word is valid
        
        if len(self._text) == len(self._valid) and first_error != -1:
            outWord = outWord[:first_error] + self._valid[first_error] + outWord[first_error+1:]
            self._pos = first_error+1
        elif first_error != -1:
            self._pos = first_error
        else:
            #The word is valid
            raise ValidWordError
        
        self._text = outWord
    
    def deletePreviousChar(self):
        if self.isValid():
            raise ValidWordError
        elif self._pos == 0 or self._text =="":
            raise NoCharPossible
        else:
            self._text = self._text[:self._pos-1]  + self._text[self._pos:]
            self._pos -= 1
    
    def deleteNextChar(self):
        if self.isValid():
            raise ValidWordError
        elif self._pos == len(self._text) or self._text =="":
            raise NoCharPossible
        else:
            self._text = self._text[:self._pos]  + self._text[self._pos+1:]
            
    
    def setText(self, text):
        if " " in text:
            raise AttributeError
        self._text = text
        
    def getText(self):
        return self._text
        
    def getValid(self):
        return self._valid
    
    def setPos(self, pos):
        "if pos=-1, set at the last position"
        if pos > len(self._text) or -2 >= pos:
            raise NoCharPossible
        elif pos==-1:
            self._pos = len(self._text)
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
