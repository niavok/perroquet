# -*- coding: utf-8 -*-

import gtk, time

class Gui:
    def __init__(self):
        self.builder = gtk.Builder()
        self.builder.add_from_file("gui.xml")
        self.builder.connect_signals(self)
        self.window = self.builder.get_object("MainWindow")
        self.typeLabel = self.builder.get_object("typeView")
        
        self.initTypeLabel()

   
    def on_MainWindow_delete_event(self,widget,data=None):
        gtk.main_quit()

    def on_newExerciceButton_clicked(self,widget,data=None):
        self.newExerciceDialog = self.builder.get_object("newExerciceDialog")
        

        videoChooser = self.builder.get_object("filechooserbuttonVideo")
        exerciceChooser = self.builder.get_object("filechooserbuttonExercice")
        videoChooser.set_filename("/media/F14A-2988/The Big Bang Theory/01x01 - Pilot.avi")
        exerciceChooser.set_filename("/media/F14A-2988/The Big Bang Theory/The.Big.Bang.Theory.S01E01.HDTV.XviD-XOR.eng.srt")
        self.newExerciceDialog.show() 
       
    def on_buttonNewExerciceOk_clicked(self,widget,data=None):
        videoChooser = self.builder.get_object("filechooserbuttonVideo")
        videoPath = videoChooser.get_filename()
        exerciceChooser = self.builder.get_object("filechooserbuttonExercice")
        exercicePath = exerciceChooser.get_filename()
        if videoPath == "None":
            videoPath = ""
        if exercicePath == "None":
            exercicePath = ""    
        print videoPath
        print exercicePath
        self.core.SetPaths(videoPath,exercicePath)
        self.newExerciceDialog.hide()

    def monclic(self, source=None, event=None):
        self.widgets.get_widget('label1').set_text('Vous avez cliqué !')
        
        return True

    def SetCore(self, core):
        self.core = core

    def GetVideoWindowId(self):
        return self.builder.get_object("videoArea").window.xid
        
    def SetSequenceNumber(self, sequenceNumber, sequenceCount):
        ajustement = self.builder.get_object("adjustmentSequenceNum")
        sequenceNumber = sequenceNumber + 1
        ajustement.configure (sequenceNumber, 1, sequenceCount, 1, 10, 0)
        self.builder.get_object("labelSequenceNumber").set_text(str(sequenceNumber) + "/" + str(sequenceCount))
                                                        
    def SetSequenceTime(self, sequencePos, sequenceTime):
        if sequencePos > sequenceTime:
            sequencePos = sequenceTime
        self.settedPos = sequencePos /100
        ajustement = self.builder.get_object("adjustmentSequenceTime")
        ajustement.configure (self.settedPos, 0, sequenceTime/100, 1, 10, 0)
        textTime = round(float(sequencePos)/1000,1)
        textDuration = round(float(sequenceTime)/1000,1)
        self.builder.get_object("labelSequenceTime").set_text(str(textTime) + "/" + str(textDuration) + " s")
      
                                                        
    def SetSequence(self, sequence):
        #print "SetSequence"
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
        #print "AddSymbol #" + symbol + "#"
        #gtk.gdk.threads_enter()
        if len(symbol) == 0:
            #print "AddSymbol abord"
            return
        buffer = self.typeLabel.get_buffer()
        size = buffer.get_char_count()
        iter1 = buffer.get_end_iter()
        buffer.insert(iter1,symbol)
        iter1 = buffer.get_iter_at_offset(size)
        iter2 = buffer.get_end_iter()
        buffer.apply_tag_by_name("default", iter1, iter2)
        #gtk.gdk.threads_leave()
        #print "AddSymbol end"
    
    def AddWordToFound(self, word):
        #print "AddWordFound"
        #gtk.gdk.threads_enter()
        buffer = self.typeLabel.get_buffer()
        iter1 = buffer.get_end_iter()
        size = buffer.get_char_count()
        buffer.insert(iter1,word)
        iter1 = buffer.get_iter_at_offset(size)
        iter2 = buffer.get_end_iter()
        buffer.apply_tag_by_name("word_to_found", iter1, iter2)
        #gtk.gdk.threads_leave()
        #print "AddWordFound end"
        
    def AddWordFound(self, word):
        #print "AddWordFound"
        #gtk.gdk.threads_enter()
        buffer = self.typeLabel.get_buffer()
        iter1 = buffer.get_end_iter()
        size = buffer.get_char_count()
        buffer.insert(iter1,word)
        iter1 = buffer.get_iter_at_offset(size)
        iter2 = buffer.get_end_iter()
        buffer.apply_tag_by_name("word_found", iter1, iter2)
        #gtk.gdk.threads_leave()


    def initTypeLabel(self):
    #    self.typeLabel = gtk.TextView()
     #   self.typeLabel.set_editable(False)
     #   self.typeLabel.set_cursor_visible(True)
        #self.typeLabel.set_wrap_mode(gtk.WRAP_NONE)
        #self.typeLabel.set_wrap_mode(gtk.WRAP_CHAR)
     #   self.typeLabel.set_wrap_mode(gtk.WRAP_WORD)
     #   self.typeLabel.set_justification(gtk.JUSTIFY_LEFT)
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


    def on_typeView_key_press_event(self,widget, event):
        #print "key"
        keyname = gtk.gdk.keyval_name(event.keyval)
        #print keyname
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
        elif keyname == "Home":
            self.core.FirstWord()
        elif keyname == "End":
            self.core.LastWord()
        elif keyname == "F1":
            self.core.CompleteWord()
        elif keyname == "Pause":
            self.core.TooglePause()
        else:
            self.core.WriteCharacter(keyname.lower())


        return True;

    def on_toolbuttonNextSequence_clicked(self,widget,data=None):
        self.core.NextSequence()

    def on_toolbuttonPreviousSequence_clicked(self,widget,data=None):
        self.core.PreviousSequence()

    def on_toolbuttonReplaySequence_clicked(self,widget,data=None):
        self.core.RepeatSequence()
    
    def on_adjustmentSequenceNum_value_changed(self,widget,data=None):
        print "on_adjustmentSequenceNum_value_changed " + str(int(self.builder.get_object("adjustmentSequenceNum").get_value()))
        self.core.SelectSequence(int(self.builder.get_object("adjustmentSequenceNum").get_value()) - 1)
    
    def on_adjustmentSequenceTime_value_changed(self,widget,data=None):
        value = int(self.builder.get_object("adjustmentSequenceTime").get_value())
        if value != self.settedPos:
            self.core.SeekSequence(value*100)
    
    def Activate(self):
        self.builder.get_object("hscaleSequenceNum").set_sensitive(True)
        self.builder.get_object("hscaleSequenceTime").set_sensitive(True)
    
    def Run(self):
        gtk.gdk.threads_init()
        self.window.show()
        gtk.main()
