# -*- coding: utf-8 -*-

import gtk, time, urllib

class Gui:
    def __init__(self):
        self.builder = gtk.Builder()
        self.builder.add_from_file("gui.xml")
        self.builder.connect_signals(self)
        self.window = self.builder.get_object("MainWindow")
        self.typeLabel = self.builder.get_object("typeView")

        self.initTypeLabel()

        filefilterSave =self.builder.get_object("filefilterSave")
        filefilterSave.add_pattern("*.perroquet")

    def on_MainWindow_delete_event(self,widget,data=None):
        gtk.main_quit()

    def on_newExerciceButton_clicked(self,widget,data=None):
        self.newExerciceDialog = self.builder.get_object("newExerciceDialog")


        videoChooser = self.builder.get_object("filechooserbuttonVideo")
        exerciceChooser = self.builder.get_object("filechooserbuttonExercice")
        videoChooser.set_filename("/home/fred/Vidéos/elephantsdream-1024-mpeg4-su-ac3.avi")
        #exerciceChooser.set_filename("/media/F14A-2988/The Big Bang Theory/The.Big.Bang.Theory.S01E01.HDTV.XviD-XOR.eng.srt")
        exerciceChooser.set_filename("/home/fred/Vidéos/english_hh.srt")
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
        self.settedSeq = sequenceNumber
        ajustement.configure (sequenceNumber, 1, sequenceCount, 1, 10, 0)
        self.builder.get_object("labelSequenceNumber").set_text(str(sequenceNumber) + "/" + str(sequenceCount))

    def SetSequenceTime(self, sequencePos, sequenceTime):
        if sequencePos > sequenceTime:
            sequencePos = sequenceTime
        if sequencePos < 0:
            sequencePos = 0
        self.settedPos = sequencePos /100
        ajustement = self.builder.get_object("adjustmentSequenceTime")
        ajustement.configure (self.settedPos, 0, sequenceTime/100, 1, 10, 0)
        textTime = round(float(sequencePos)/1000,1)
        textDuration = round(float(sequenceTime)/1000,1)
        self.builder.get_object("labelSequenceTime").set_text(str(textTime) + "/" + str(textDuration) + " s")

    def SetPlaying(self, state):
        self.builder.get_object("toolbuttonPlay").set_sensitive(state)
        self.builder.get_object("toolbuttonPause").set_sensitive(not state)

    def SetCanSave(self, state):
        self.builder.get_object("saveButton").set_sensitive(state)

    def SetWordList(self, wordList):
        buffer = self.builder.get_object("textviewWordList").get_buffer()

        iter1 = buffer.get_start_iter()
        iter2 = buffer.get_end_iter()
        buffer.delete(iter1, iter2)


        formattedWordList = ""

        for word in wordList:
            formattedWordList = formattedWordList + word + "\n"

        iter = buffer.get_end_iter()
        buffer.insert(iter,formattedWordList)


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
                    print sequence.GetWordList()[i]
                    print sequence.GetWorkList()[i]

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

        value = int(self.builder.get_object("adjustmentSequenceNum").get_value())

        if value != self.settedSeq:
            self.core.SelectSequence(value - 1)

    def on_adjustmentSequenceTime_value_changed(self,widget,data=None):
        value = int(self.builder.get_object("adjustmentSequenceTime").get_value())
        if value != self.settedPos:
            self.core.SeekSequence(value*100)
    def on_toolbuttonHint_clicked(self,widget,data=None):
        self.core.CompleteWord()

    def on_toolbuttonPlay_clicked(self,widget,data=None):
        self.core.Play()

    def on_toolbuttonPause_clicked(self,widget,data=None):
        self.core.Pause()

    def on_saveButton_clicked(self, widget, data=None):
        self.core.Save()

    def on_loadButton_clicked(self, widget, data=None):

        loader = OpenFileSelector(self.window)
        result =loader.run()
        if result == None:
            return

        self.core.LoadExercice(result)

    def on_filechooserdialogLoad_confirm_overwrite(self, widget, data=None):
        print "on_filechooserdialogLoad_confirm_overwrite"
        loadChooser = self.builder.get_object("filechooserdialogLoad")
        #loadChooser.emit(gtk.RESPONSE_ACCEPT)
        return gtk.FILE_CHOOSER_CONFIRMATION_ACCEPT_FILENAME

    def on_filechooserdialogLoad_file_activated(self, widget, data=None):
        print "on_filechooserdialogLoad_file_activated"
        loadChooser = self.builder.get_object("filechooserdialogLoad")
        #loadChooser.emit(gtk.RESPONSE_ACCEPT)

    def AskSavePath(self):

        saver = SaveFileSelector(self.window)
        result =saver.run()
        if result == None:
            return

        path = result

        if path == "None" or path == None :
            path = ""
        elif not path.endswith(".perroquet"):
            path = path +".perroquet"
        return path

    def on_buttonSaveExerciceOk_clicked(self, widget, data=None):
        saveChooser = self.builder.get_object("filechooserdialogSave")
        saveChooser.hide()

    def Activate(self):
        self.builder.get_object("hscaleSequenceNum").set_sensitive(True)
        self.builder.get_object("hscaleSequenceTime").set_sensitive(True)
        self.builder.get_object("toolbuttonHint").set_sensitive(True)
        self.builder.get_object("toolbuttonReplaySequence").set_sensitive(True)


    def Run(self):
        gtk.gdk.threads_init()
        self.window.show()
        gtk.main()


EVENT_FILTER            = None


class FileSelector(gtk.FileChooserDialog):
        "A normal file selector"

        def __init__(self, parent, title = None, action = gtk.FILE_CHOOSER_ACTION_OPEN, stockbutton = None):

                if stockbutton is None:
                        if action == gtk.FILE_CHOOSER_ACTION_OPEN:
                                stockbutton = gtk.STOCK_OPEN

                        elif action == gtk.FILE_CHOOSER_ACTION_SAVE:
                                stockbutton = gtk.STOCK_SAVE

                gtk.FileChooserDialog.__init__(
                        self, title, parent, action,
                        ( gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, stockbutton, gtk.RESPONSE_OK )
                )

                self.set_local_only(False)
                self.set_default_response(gtk.RESPONSE_OK)

                self.inputsection = None


        def add_widget(self, title, widget):
                "Adds a widget to the file selection"

                if self.inputsection == None:
                        self.inputsection = ui.InputSection()
                        self.set_extra_widget(self.inputsection)

                self.inputsection.append_widget(title, widget)


        """def get_filename(self):
                "Returns the file URI"

                uri = self.get_filename()

                if uri == None:
                        return None

                else:
                        return urllib.unquote(uri)"""


        def run(self):
                "Displays and runs the file selector, returns the filename"

                self.show_all()

                if EVENT_FILTER != None:
                        self.window.add_filter(EVENT_FILTER)

                response = gtk.FileChooserDialog.run(self)
                filename = self.get_filename()
                self.destroy()

                if response == gtk.RESPONSE_OK:
                        return filename

                else:
                        return None


class OpenFileSelector(FileSelector):
        "A file selector for opening files"

        def __init__(self, parent):
                FileSelector.__init__(
                        self, parent, ('Select File to Open'),
                        gtk.FILE_CHOOSER_ACTION_OPEN, gtk.STOCK_OPEN
                )

                filter = gtk.FileFilter()
                filter.set_name(('Perroquet files'))
                filter.add_pattern("*.perroquet")
                self.add_filter(filter)

                filter = gtk.FileFilter()
                filter.set_name(('All files'))
                filter.add_pattern("*")
                self.add_filter(filter)



class SaveFileSelector(FileSelector):
        "A file selector for saving files"

        def __init__(self, parent):
                FileSelector.__init__(
                        self, parent, ('Select File to Save to'),
                        gtk.FILE_CHOOSER_ACTION_SAVE, gtk.STOCK_SAVE
                )

                filter = gtk.FileFilter()
                filter.set_name(('Perroquet files'))
                filter.add_pattern("*.perroquet")
                self.add_filter(filter)

                filter = gtk.FileFilter()
                filter.set_name(('All files'))
                filter.add_pattern("*")
                self.add_filter(filter)

                self.set_do_overwrite_confirmation(True)
                self.connect("confirm-overwrite", self.__cb_confirm_overwrite)


        def __cb_confirm_overwrite(self, widget, data = None):
                "Handles confirm-overwrite signals"

                try:
                        FileReplace(self, io.file_normpath(self.get_uri())).run()

                except CancelError:
                        return gtk.FILE_CHOOSER_CONFIRMATION_SELECT_AGAIN

                else:
                        return gtk.FILE_CHOOSER_CONFIRMATION_ACCEPT_FILENAME



