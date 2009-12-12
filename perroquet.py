#!/usr/bin/env python
# -*- coding: utf-8 -*-

from core import Core
from gui import Gui


class Perroquet(object):
    def __init__(self):
        self.core = Core()
        self.gui = Gui()

        self.core.SetGui(self.gui)
        self.gui.SetCore(self.core)

        self.gui.Run()

def main():
    perroquet = Perroquet()

if __name__ == "__main__":
    main()


