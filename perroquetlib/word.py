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
    
    current = range(n+1)
    for i in range(1,m+1):
        previous, current = current, [i]+[0]*n
        for j in range(1,n+1):
            add, delete = previous[j]+1, current[j-1]+1
            change = previous[j-1]
            if a[j-1] != b[i-1]:
                change = change + 1
            current[j] = min(add, delete, change)
            
    return current[n]

def startWith(w1, w2):
    """Check if the first chars of w1 is w2)"""
    return w1[:len(w2)]==w2


class Word:
    def __init__(self, validText, helpChar="~"):
        self._current = ""
        self._valid = validText
        
        self._helpChar = helpChar
        self._pos = 0

    def levenshtein(self):
        return levenshtein(self._current, self._valid)
    
    def score(self):
        return 2*len(self._valid) - 2*self.levenshtein() - len(self._current)
    
    def isValid(self):
        return self._current == self._valid
    
    def isEmpty(self):
        return self._current == ""
    
    def complete(self):
        "Reveal the correction"
        self._current = self._valid
    
    def writeChar(self, char):
        if len(char)>1:
            raise AttributeError
        if self.isValid():
            raise Comp
        #if replacing an helpChar
        if self._pos < len(self._current) and self._current[self._pos] == self._helpChar:
            self._current = self._current[:self._pos] + char + self._current[self._pos+1:]
        else:
            self._current = self._current[:self._pos] + char + self._current[self._pos:]
        self._pos += 1

    def showHint(self):
        """Reveal correction for word at cursor in current sequence"""
        outWord = ""
        first_error = -1
        
        for i in range(0, len(self._valid)):
            if i < len(self._current) and self._current[i].lower() == self._valid[i].lower():
                outWord += self._valid[i]
            else:
                outWord += self._helpChar
                if first_error == -1:
                    first_error = i
        
        # if fist_error != -1 => the first false char is fist_error  
        # else                => The word is valid
        
        if len(self._current) == len(self._valid) and first_error != -1:
            outWord = outWord[:first_error] + self._valid[first_error] + outWord[first_error+1:]
            self._pos = first_error+1
        elif first_error != -1:
            self._pos = first_error
        else:
            #The word is valid
            raise ValidWordError
        
        self._current = outWord
    
    def deletePreviousChar(self):
        if self.isValid():
            raise ValidWordError
        elif self._pos == 0 or self._current =="":
            raise NoCharPossible
        else:
            self._current = self._current[:self._pos-1]  + self._current[self._pos:]
    
    def deleteNextChar(self):
        if self.isValid():
            raise ValidWordError
        elif self._pos == len(self._current) or self._current =="":
            raise NoCharPossible
        else:
            self._current = self._current[:self._pos]  + self._current[self._pos+1:]
            
    
    def setCurrent(self, current):
        self._current = current
        
    def getCurrent(self):
        return self._current
        
    def getValid(self):
        return self._valid
    
    def setPos(self, pos):
        "if pos=-1, set at the last position"
        if pos > len(self._current) or -2 >= pos:
            raise NoCharPossible
        elif pos==-1:
            self._pos = len(self._current)
        else:
            self._pos = pos
        
    def getPos(self):
        return self._pos
