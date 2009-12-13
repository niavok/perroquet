# -*- coding: utf-8 -*-


import gst
import gtk
import thread, time, traceback, sys


class VideoPlayer(object):

    def __init__(self):
        self.player = gst.element_factory_make("playbin2", "player")
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect("message", self.on_message)
        bus.connect("sync-message::element", self.on_sync_message)

        self.time_format = gst.Format(gst.FORMAT_TIME)


    def on_message(self, bus, message):
        t = message.type
        if t == gst.MESSAGE_EOS:
            self.player.set_state(gst.STATE_NULL)
            #self.buttonStart.set_label("Start")
        elif t == gst.MESSAGE_ERROR:
            self.player.set_state(gst.STATE_NULL)
            err, debug = message.parse_error()
            print "Error: %s" % err, debug
            #self.buttonStart.set_label("Start")

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
            imagesink.set_xwindow_id(self.windowId)
            gtk.gdk.threads_leave()

    def Open(self,path):
        self.player.set_property("uri", "file://" + path)
        self.play_thread_id = thread.start_new_thread(self.play_thread, ())
        self.playing = False
    def Play(self):
        print "Play"
        self.player.set_state(gst.STATE_PLAYING)
        self.playing = True

    def Pause(self):
        print "Pause"
        self.player.set_state(gst.STATE_PAUSED)
        self.playing = False

    def IsPaused(self):
        return not self.playing

    def Seek(self, time):
        print "Seek"
        #self.player.set_state(gst.STATE_PAUSED)
        #00:17:55,760
        value = int(time * 1000000 )
        self.player.seek_simple(gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH,value)

    def SetCallback(self, callback):
        self.callback = callback

    def SetNextCallbackTime(self, nextCallbackTime):
        self.nextCallbackTime = nextCallbackTime

    def SetWindowId(self, windowId):
        self.windowId = windowId

    def play_thread(self):
        play_thread_id = self.play_thread_id
        #gtk.gdk.threads_enter()
        #self.time_label.set_text("00:00 / 00:00")
        #gtk.gdk.threads_leave()
        while play_thread_id == self.play_thread_id:
            time.sleep(0.1)
            pos_int = -1
            try:
                pos_int = self.player.query_position(self.time_format, None)[0]
            except:
                pass
            if pos_int != -1 and self.nextCallbackTime != -1 and pos_int > self.nextCallbackTime *1000000:
                self.nextCallbackTime = -1
                self.callback()




