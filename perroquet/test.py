#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
import pygtk, gtk, gobject
import pygst
pygst.require("0.10")
import gst

class GTK_Main:

    def __init__(self):
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_title("Video-Player")
        window.set_default_size(500, 400)
        window.connect("destroy", gtk.main_quit, "WM destroy")
        vbox = gtk.VBox()
        window.add(vbox)
        hbox = gtk.HBox()
        vbox.pack_start(hbox, False)
        self.entry = gtk.Entry()
        self.entry.set_text("/home/fred/Vidéos/The Big Bang Theory/01x01 - Pilot.avi")
        hbox.add(self.entry)
        self.buttonStart = gtk.Button("Start")
        self.buttonPause = gtk.Button("Pause")
        hbox.pack_start(self.buttonStart, False)
        hbox.pack_start(self.buttonPause, False)
        self.buttonStart.connect("clicked", self.start_stop)
        self.buttonPause.connect("clicked", self.pause)
        self.movie_window = gtk.DrawingArea()
        vbox.add(self.movie_window)
        window.show_all()

        self.player = gst.element_factory_make("playbin2", "player")
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect("message", self.on_message)
        bus.connect("sync-message::element", self.on_sync_message)

    def start_stop(self, w):
        if self.buttonStart.get_label() == "Start":
            filepath = self.entry.get_text()
            if os.path.isfile(filepath):
                self.buttonStart.set_label("Stop")
                self.player.set_property("uri", "file://" + filepath)
                print "plop1"
                self.player.set_state(gst.STATE_PLAYING)
                print "plop2"
        else:
            self.player.set_state(gst.STATE_NULL)
            self.buttonStart.set_label("Start")

    def pause(self, w):
        print "pause"
        #self.player.set_state(gst.STATE_PAUSED)
        #00:17:55,760
        value = int(gst.SECOND * (17*60 +55 )+ 760 * 1000000 )
        self.player.seek_simple(gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH,value)



    def on_message(self, bus, message):
        t = message.type
        if t == gst.MESSAGE_EOS:
            self.player.set_state(gst.STATE_NULL)
            self.buttonStart.set_label("Start")
        elif t == gst.MESSAGE_ERROR:
            self.player.set_state(gst.STATE_NULL)
            err, debug = message.parse_error()
            print "Error: %s" % err, debug
            self.buttonStart.set_label("Start")

    def on_sync_message(self, bus, message):
        print "plip"
        if message.structure is None:
            return
        message_name = message.structure.get_name()
        print message_name
        if message_name == "prepare-xwindow-id":
            gtk.gdk.threads_enter()
            gtk.gdk.display_get_default().sync()
            imagesink = message.src
            imagesink.set_property("force-aspect-ratio", True)
            imagesink.set_xwindow_id(self.movie_window.window.xid)
            gtk.gdk.threads_leave()

GTK_Main()
gtk.gdk.threads_init()
gtk.main()
