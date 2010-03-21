#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

from lib import ls_rec

def clean(directory):
    files = [f for f in ls_rec(directory)
            if f.endswith(".pyc") or
               f.endswith("~")]
    for f in files:
        os.remove(f)
    return files

if __name__=="__main__":
    if len(sys.argv)>=2:
        dirs = sys.argv[1:]
    else:
        dirs = [os.path.abspath("./")] #perroquet/
        print dirs
    
    print "REMOVED FILES:"
    for directory in dirs:
        print "\n".join(clean(directory))
