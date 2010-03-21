#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys

from lib import apply_to_file

def set_blanks_lines(string):
    #no more than one blank lines between methods
    string = re.sub(r'((\n|^) *def(.|\n)*?)(\n *)*\n(?= +def)',
        r'\1\n\n', string)
    #two blancks lines between class definition
    string = re.sub(r'((\n|^) *class(.|\n)*?)( *\n)*(?= *class)',
        r'\1\n\n\n', string)
    #two blancks lines between def definition
    string = re.sub(r'((\n|^)def(.|\n)*?)( *\n)*(?=def)',
        r'\1\n\n\n', string)
    #no blank line afted def or class
    string = re.sub(r'((\n|^) *((def)|(class)).*\n)( *\n)*',
        r'\1', string)
    return string

#Set the functions names lowercase with underscores (aka loweru)

def find_function_names(string):
    "find the functions with a name not lowercase with underscores"
    #get the list of functions that aren't good
    return [s[1] for s in 
            re.findall("(def (\w*[A-Z]\w*))", string)]

def set_loweru(string):
    def aux(s):
        return "_"+s.group(1).lower()
    string = string[0].lower() + string[1:]
    return re.sub("(?!^)_?([A-Z])", aux, string)

def replace_words(list_tuple, string):
    for w1, w2 in list_tuple:
        string = re.sub("(?<!\w)"+w1+"(?!\w)", w2, string)
    return string

def set_function_names_loweru(paths):
    for path in paths:
        string = open(path).read()
        tuples = [(name, set_loweru(name)) for name 
                 in find_function_names(string)]
        for path2 in paths: #must apply in path
            apply_to_file(path2, lambda s: replace_words(tuples, s))
    
if __name__=="__main__":
    paths = sys.argv[2:]
    if len(sys.argv)<=2:
        pass
    elif sys.argv[1]=="blank":
        for path in paths:
            apply_to_file(path, set_blanks_lines)
    elif sys.argv[1]=="names":
        set_function_names_loweru(paths)
