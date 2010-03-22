# -*- coding: utf-8 -*-

import os

def ls_rec(directory, hidden=False):
    files = []
    if hidden:
        l = os.listdir(directory)
    else:
        l = [f for f in os.listdir(directory) if not f.startswith(".")]
    for f in l:
        path = os.path.join(directory, f)
        if os.path.isdir(path):
            files += ls_rec(path)
        else:
            files.append(path)
    return files

def lspy(directory):
    return [f for f in ls_rec(directory) if f.endswith("py")]

def apply_to_file(path, function):
    s=open(path).read()
    f=open(path, "w")
    f.write(function(s))
    f.close

if __name__=="__main__":
    pass
    
