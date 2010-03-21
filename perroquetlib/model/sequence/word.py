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
        return levenshtein(self.get_text(), self.get_valid())
        
    def get_begin_right(self):
        """Check if the first chars of self.get_valid() is self.get_text())"""
        return self.get_valid()[:len(self.get_text(helpChar=False))]==self.get_text(helpChar=False)
    
    def get_score(self):
        """Show if we are near the solution.
        return a float from -1 to 1. more is better"""
        #score1 and score2 are between -1 and 1
        score1_ = (2.*len(self.get_valid()) - 2*self.levenshtein() - len(self.get_text(helpChar=False))) / max(len(self.get_valid()), len(self.get_text(helpChar=False)))
        score1 = max(score1_, -1)
        score2 = self.get_begin_right()
        return (score1*8+score2*2)/10
    
    def is_valid(self):
        return self.get_text() == self.get_valid()
    
    def is_empty(self):
        return self.get_text() == ""
    
    def complete(self):
        "Reveal the correction"
        self.set_text(self.get_valid())
    
    def reset(self):
        "RAZ the current word"
        self.set_text("")
    
    def write_char(self, char):
        char = char.lower()
        if len(char)!=1 or char==" ":
            raise AttributeError, "char='"+char+"'"
        if self.is_valid():
            raise ValidWordError
        #if replacing an helpChar
        if self.get_pos() < len(self.get_text()) and self.get_text()[self.get_pos()] == self._helpChar:
            self.set_text(self.get_text()[:self.get_pos()] + char + self.get_text()[self.get_pos()+1:])
        else:
            if self._helpChar in self.get_text():
                #removing helps chars
                self.set_text("".join(c for c in self.get_text() if c!=self._helpChar))
            self.set_text(self.get_text()[:self.get_pos()] + char + self.get_text()[self.get_pos():])
        self._pos += 1

    def show_hint(self):
        """Reveal correction for word at cursor in text sequence"""
        outWord = ""
        first_error = -1
        
        for i in range(0, len(self.get_valid())):
            if i < len(self.get_text()) and self.get_text()[i] == self.get_valid()[i]:
                outWord += self.get_valid()[i]
            else:
                outWord += self._helpChar
                if first_error == -1:
                    first_error = i
        
        # if fist_error != -1 => the first false char is fist_error  
        # else                => The word is valid
        
        if len(self.get_text()) == len(self.get_valid()) and first_error != -1:
            outWord = outWord[:first_error] + self.get_valid()[first_error] + outWord[first_error+1:]
            self.set_pos(first_error+1)
        elif first_error != -1:
            self.set_pos(first_error)
        else:
            raise ValidWordError
        
        self.set_text(outWord)
    
    def delete_previous_char(self):
        if self.is_valid():
            raise ValidWordError
        elif self.get_pos() == 0 or self.get_text() =="":
            raise NoCharPossible
        else:
            self.set_text(self.get_text()[:self.get_pos()-1]  + self.get_text()[self.get_pos():])
            self._pos -= 1
    
    def delete_next_char(self):
        if self.is_valid():
            raise ValidWordError
        elif self.get_pos() == len(self.get_text()) or self.get_text() =="":
            raise NoCharPossible
        else:
            self.set_text(self.get_text()[:self.get_pos()]  + self.get_text()[self.get_pos()+1:])
            
    def set_text(self, text):
        if " " in text:
            raise AttributeError
        self._text = text.lower()
        
    def get_text(self, helpChar=True):
        if helpChar:
            return self._text.lower()
        else:
            return "".join([i for i in self.get_text() if i!=self._helpChar])
        
    def get_valid(self, lower=True):
        if lower:
            return self._valid.lower()
        else:
            return self._valid
    
    def set_pos(self, pos):
        "if pos=-1, set at the last position"
        if pos > len(self.get_text()) or -2 >= pos:
            raise NoCharPossible
        elif pos==-1:
            self._pos = len(self.get_text())
        else:
            self._pos = pos
        
    def get_pos(self):
        return self._pos
    
    def get_last_pos(self):
        return len(self.get_text())
    
    def next_char(self):
        if self.get_pos() < self.get_last_pos():
            self._pos += 1
        else:
            raise NoCharPossible
    
    def previous_char(self):
        if self.get_pos() > 0:
            self._pos -= 1
        else:
            raise NoCharPossible
    
    def __print__(self):
        return str(self.is_valid())+" "+self.get_text()+" instead of "+self.get_valid()
    
    def __repr__(self):
        return self.get_text()+" VS "+self.get_valid()
