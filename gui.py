# -*- coding: utf-8 -*-

import gtk

class Gui(object):
    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("Perroquet")
        self.window.set_default_size(800, 600)
        self.window.connect("destroy", gtk.main_quit, "WM destroy")
        vbox = gtk.VBox()
        self.window.add(vbox)
        hbox = gtk.HBox()
        vbox.pack_start(hbox, False)
        self.entry = gtk.Entry()
        self.entry.set_text("/home/fred/Vidéos/The Big Bang Theory/01x01 - Pilot.avi")
        hbox.add(self.entry)
        self.buttonStart = gtk.Button("Start")
        self.buttonLoad = gtk.Button("Load")
        hbox.pack_start(self.buttonStart, False)
        hbox.pack_start(self.buttonLoad, False)
        #self.buttonStart.connect("clicked", self.start_stop)
        self.buttonLoad.connect("clicked", self.load)
        self.window.connect("key-press-event",self.keyPressCallback)
        self.movie_window = gtk.DrawingArea()
        vbox.pack_start(self.movie_window, True)

        self.initTypeLabel()

        fd = gtk.ScrolledWindow()
        fd.set_policy(gtk.POLICY_NEVER, gtk.POLICY_ALWAYS)

        fd.add(self.typeLabel)
        fd.set_size_request(500, 160)

        vbox.pack_start(fd, False)

    def SetCore(self, core):
        self.core = core

    def Run(self):
        self.window.show_all()
        gtk.gdk.threads_init()
        gtk.main()

    def initTypeLabel(self):
        self.typeLabel = gtk.TextView()
        self.typeLabel.set_editable(False)
        self.typeLabel.set_cursor_visible(True)
        self.typeLabel.set_wrap_mode(gtk.WRAP_WORD)
        self.typeLabel.set_justification(gtk.JUSTIFY_CENTER)


        buffer = self.typeLabel.get_buffer()

        """buffer.create_tag("word_to_found",
             foreground_gdk=color,
             background='yellow',
             size_points=24.0)"""

        color_not_found = self.window.get_colormap().alloc_color(150*256, 150*256, 150*256)
        color_found = self.window.get_colormap().alloc_color(50*256, 255*256, 50*256)
        """buffer.create_tag("default",
             rise= -4*1024,
             foreground_gdk=color)"""
        buffer.create_tag("default",
             size_points=18.0)
        buffer.create_tag("word_to_found",
             background=color_not_found)
        buffer.create_tag("word_found",
             background=color_found)



    def keyPressCallback(self,data,widget):
        print "key"

    def load(self,w):
        self.core.SetVideoPath("/home/fred/Vidéos/The Big Bang Theory/01x01 - Pilot.avi")

    def GetVideoWindowId(self):
        return self.movie_window.window.xid

    def SetSequence(self, sequence):
        #print "SetSequence"
        #self.ClearBuffer()
        i = 0
        text = ""
        for symbol in sequence.GetSymbolList():
            #print "symbol"
            text += symbol
             #self.AddSymbol(symbol)
            #print "len"
            if i < len(sequence.GetWordList()):
                #print "AddWordFound"
                #self.AddWordFound(sequence.GetWordList()[i])
                text += sequence.GetWordList()[i]
                i += 1
        gtk.gdk.threads_enter()
        buffer = self.typeLabel.get_buffer()
        buffer.set_text(text)
        iter1 = buffer.get_start_iter()
        iter2 = buffer.get_end_iter()
        buffer.apply_tag_by_name("default", iter1, iter2)
        gtk.gdk.threads_leave()


    def ClearBuffer(self):
        gtk.gdk.threads_enter()
        buffer = self.typeLabel.get_buffer()
        iter1 = buffer.get_start_iter()
        iter2 = buffer.get_end_iter()
        buffer.delete(iter1, iter2)
        gtk.gdk.threads_leave()


    def AddSymbol(self, symbol):
        print "AddSymbol"
        gtk.gdk.threads_enter()
        buffer = self.typeLabel.get_buffer()
        iter1 = buffer.get_end_iter()
        buffer.insert(iter1,symbol)
        iter2 = buffer.get_end_iter()
        buffer.apply_tag_by_name("default", iter1, iter2)
        gtk.gdk.threads_leave()
        print "AddSymbol end"

    def AddWordToFound(self, word):
        gtk.gdk.threads_enter()
        buffer = self.typeLabel.get_buffer()
        iter1 = buffer.get_end_iter()
        buffer.insert(iter1,word)
        iter2 = buffer.get_end_iter()
        buffer.apply_tag_by_name("word_to_found", iter1, iter2)
        gtk.gdk.threads_leave()

    def AddWordFound(self, word):
        print "AddWordFound"
        gtk.gdk.threads_enter()
        buffer = self.typeLabel.get_buffer()
        iter1 = buffer.get_end_iter()
        buffer.insert(iter1,word)
        iter2 = buffer.get_end_iter()
        buffer.apply_tag_by_name("word_found", iter1, iter2)
        gtk.gdk.threads_leave()
