# -*- coding: utf-8 -*-

import gtk, time

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
        fd.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        #fd.set_policy(gtk.POLICY_NEVER, gtk.POLICY_ALWAYS)

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
        #self.typeLabel.set_wrap_mode(gtk.WRAP_NONE)
        #self.typeLabel.set_wrap_mode(gtk.WRAP_CHAR)
        self.typeLabel.set_wrap_mode(gtk.WRAP_WORD)
        self.typeLabel.set_justification(gtk.JUSTIFY_LEFT)
        #self.typeLabel.set_justification(gtk.JUSTIFY_CENTER)
        #self.typeLabel.set_justification(gtk.JUSTIFY_RIGHT)


        buffer = self.typeLabel.get_buffer()

        """buffer.create_tag("word_to_found",
             foreground_gdk=color,
             background='yellow',
             size_points=24.0)"""

        color_not_found = self.window.get_colormap().alloc_color(0*256, 0*256, 80*256)
        bcolor_not_found = self.window.get_colormap().alloc_color(200*256, 230*256, 250*256)
        color_found = self.window.get_colormap().alloc_color(10*256, 150*256, 10*256)
        """buffer.create_tag("default",
             rise= -4*1024,
             foreground_gdk=color)"""
        buffer.create_tag("default",
             size_points=18.0)
        buffer.create_tag("word_to_found",
             background=bcolor_not_found, foreground=color_not_found, size_points=18.0)
        buffer.create_tag("word_found",
             foreground=color_found, size_points=18.0)



    def keyPressCallback(self,widget, event):
        print "key"
        keyname = gtk.gdk.keyval_name(event.keyval)
        print keyname
        if keyname == "Return":
            self.core.RepeatSequence()
        elif keyname == "space":
            self.core.NextWord()
        elif keyname == "BackSpace":
            self.core.DeletePreviousChar()
        elif keyname == "Delete":
            self.core.DeleteNextChar()
        elif keyname == "Page_Down":
            self.core.PreviousSequence()
        elif keyname == "Page_Up":
            self.core.NextSequence()
        elif keyname == "Right":
            self.core.NextChar()
        elif keyname == "Left":
            self.core.PreviousChar()
        else:
            self.core.WriteCharacter(keyname.lower())


        return True;



    def load(self,w):
        self.core.SetVideoPath("/home/fred/Vidéos/The Big Bang Theory/01x01 - Pilot.avi")

    def GetVideoWindowId(self):
        return self.movie_window.window.xid

    def SetSequence(self, sequence):
        print "SetSequence"
        self.ClearBuffer()
        i = 0
        pos = 1
        cursor_pos = 0
        text = ""
        buffer = self.typeLabel.get_buffer()
        self.AddSymbol(" ")

        for symbol in sequence.GetSymbolList():
            #print "symbol"
            """text += symbol"""
            pos += len(symbol)
            self.AddSymbol(symbol)
            #print "len"
            if i < len(sequence.GetWordList()):
                if sequence.GetActiveWordIndex() == i:
                    cursor_pos = pos
                #print "AddWordFound"
                if len(sequence.GetWorkList()[i]) == 0:
                    self.AddWordToFound(" ")
                    pos += 1
                elif sequence.GetWordList()[i].lower() == sequence.GetWorkList()[i].lower():
                    self.AddWordFound(sequence.GetWordList()[i])
                    pos += len(sequence.GetWordList()[i])
                else:
                    self.AddWordToFound(sequence.GetWorkList()[i])
                    pos += len(sequence.GetWorkList()[i])
                i += 1

        self.window.set_focus(self.typeLabel)
        newCurPos = cursor_pos + sequence.GetActiveWordPos()
        iter = buffer.get_iter_at_offset(newCurPos)
        buffer.place_cursor(iter)

        print "active : " + str(sequence.GetActiveWordIndex()) + " "  + str(sequence.GetActiveWordPos()) + " " + str(cursor_pos) + " " +str(newCurPos)
        """"gtk.gdk.threads_enter()
        buffer = self.typeLabel.get_buffer()
        buffer.set_text(text)
        iter1 = buffer.get_start_iter()
        iter2 = buffer.get_end_iter()
        buffer.apply_tag_by_name("default", iter1, iter2)
        gtk.gdk.threads_leave()"""


    def ClearBuffer(self):
        #print "ClearBuffer"
        #gtk.gdk.threads_enter()
        buffer = self.typeLabel.get_buffer()
        iter1 = buffer.get_start_iter()
        iter2 = buffer.get_end_iter()
        buffer.delete(iter1, iter2)
        #gtk.gdk.threads_leave()
        #print "ClearBuffer end"


    def AddSymbol(self, symbol):
        print "AddSymbol #" + symbol + "#"
        #gtk.gdk.threads_enter()
        symbol
        if len(symbol) == 0:
            return

        buffer = self.typeLabel.get_buffer()
        iter1 = buffer.get_end_iter()
        size = buffer.get_char_count()
        buffer.insert(iter1,symbol)
        iter1 = buffer.get_iter_at_offset(size)
        iter2 = buffer.get_end_iter()
        buffer.apply_tag_by_name("default", iter1, iter2)
        #gtk.gdk.threads_leave()
        #print "AddSymbol end"

    def AddWordToFound(self, word):
        #gtk.gdk.threads_enter()
        buffer = self.typeLabel.get_buffer()
        iter1 = buffer.get_end_iter()
        size = buffer.get_char_count()
        buffer.insert(iter1,word)
        iter1 = buffer.get_iter_at_offset(size)
        iter2 = buffer.get_end_iter()
        buffer.apply_tag_by_name("word_to_found", iter1, iter2)
        #gtk.gdk.threads_leave()

    def AddWordFound(self, word):
        print "AddWordFound"
        #gtk.gdk.threads_enter()
        buffer = self.typeLabel.get_buffer()
        iter1 = buffer.get_end_iter()
        size = buffer.get_char_count()
        buffer.insert(iter1,word)
        iter1 = buffer.get_iter_at_offset(size)
        iter2 = buffer.get_end_iter()
        buffer.apply_tag_by_name("word_found", iter1, iter2)
        #gtk.gdk.threads_leave()
