# -*- coding: utf-8 -*-

# Copyright (C) 2009-2011 Frédéric Bertolus.
#
# This file is part of Perroquet.
#
# Perroquet is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Perroquet is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Perroquet. If not, see <http://www.gnu.org/licenses/>.

import logging
import sys
import thread
import time

import gst
import gtk
# Build some logger related objects
defaultLoggingHandler = logging.StreamHandler(sys.stdout)
defaultLoggingHandler.setFormatter(logging.Formatter("%(asctime)s.%(msecs)d-[%(name)s::%(levelname)s] %(message)s", "%a %H:%M:%S"))
defaultLoggingLevel = logging.DEBUG
from gettext import gettext as _
from perroquetlib.config import config

class VideoPlayer:
    def __init__(self):

        self.player = gst.Pipeline()
        self.playbin = gst.element_factory_make("playbin2", "player")

        # Disable the subtitle display if there is embeded subtitles
        # (for example, in mkv files)
        #
        # Flags activates some things
        # (1 << 0) : video
        # (1 << 1) : audio
        # (1 << 4) : software volume
        #
        # The default value is 0, 1, 2, 4. (1 << 2) display the subtitles
        #
        # For more details, see the doc
        # http://www.gstreamer.net/data/doc/gstreamer/head/gst-plugins-base-plugins/html/gst-plugins-base-plugins-playbin2.html#GstPlayFlags
        # http://www.gstreamer.net/data/doc/gstreamer/head/gst-plugins-base-plugins/html/gst-plugins-base-plugins-playbin2.html#GstPlayBin2--flags
        self.playbin.set_property("flags", (1 << 0)|(1 << 1)|(1 << 4))
        self.playbin.set_property("current-audio", 0)


        self.player.add(self.playbin)
        self.logger = logging.Logger("VideoPlayer")
        self.logger.setLevel(defaultLoggingLevel)
        self.logger.addHandler(defaultLoggingHandler)
        #Audio
        audiobin = gst.Bin("audio-speed-bin")
        try:
            self.audiospeedchanger = gst.element_factory_make("pitch")
            self.canChangeSpeed = True
        except gst.ElementNotFoundError:
            self.logger.warn(_(u"You need to install the gstreamer soundtouch elements to "
                             "use slowly play feature."))
            self.canChangeSpeed = False

        #Try to use the pitch element only if it is available
        if self.canChangeSpeed and config.get("interface_use_speed_change"):
            audiobin.add(self.audiospeedchanger)

            self.audiosink = gst.element_factory_make("autoaudiosink")

            audiobin.add(self.audiosink)
            convert = gst.element_factory_make("audioconvert")
            audiobin.add(convert)
            gst.element_link_many(self.audiospeedchanger, convert, self.audiosink)
            sink_pad = gst.GhostPad("sink", self.audiospeedchanger.get_pad("sink"))
            audiobin.add_pad(sink_pad)
            self.playbin.set_property("audio-sink", audiobin)

        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect("message", self.on_message)
        bus.connect("sync-message::element", self.on_sync_message)

        self.time_format = gst.Format(gst.FORMAT_TIME)
        self.timeToSeek = -1
        self.speed = 1.0
        self.nextCallbackTime = -1

    def on_message(self, bus, message):
        t = message.type
        if t == gst.MESSAGE_EOS:
            self.player.set_state(gst.STATE_NULL)
        elif t == gst.MESSAGE_ERROR:
            self.player.set_state(gst.STATE_NULL)
            err, debug = message.parse_error()
            self.logger.error("Error: %s, %s" % (err, debug))

    def on_sync_message(self, bus, message):
        if message.structure is None:
            return
        message_name = message.structure.get_name()
        if message_name == "prepare-xwindow-id":
            gtk.gdk.threads_enter()
            gtk.gdk.display_get_default().sync()
            imagesink = message.src
            imagesink.set_property("force-aspect-ratio", True)
            imagesink.set_xwindow_id(self.windowId)
            self.activate_video_area(True)
            gtk.gdk.threads_leave()

    def open(self, path):
        self.playbin.set_property("uri", "file://" + path)
        self.play_thread_id = thread.start_new_thread(self.play_thread, ())
        self.player.set_state(gst.STATE_PAUSED)
        self.playing = False
    def play(self):
        self.player.set_state(gst.STATE_PLAYING)
        self.playing = True

    def set_speed(self, speed):
        if self.canChangeSpeed:
            self.audiospeedchanger.set_property("tempo", speed)
            if self.nextCallbackTime != -1:
                self.nextCallbackTime = self.nextCallbackTime * speed / self.speed
            self.speed = speed


    def pause(self):
        self.player.set_state(gst.STATE_PAUSED)
        self.playing = False

    def is_paused(self):
        return not self.playing

    def is_speed_changeable(self):
        return self.canChangeSpeed

    def seek(self, time):
        value = int(time * 1000000)
        self.playbin.seek_simple(gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH, value)

    def get_seek(self):
        pos_int = -1
        try:
            pos_int = self.player.query_position(self.time_format, None)[0]
        except:
            pass
        return (self.speed * pos_int) / 1000000

    def seek_as_soon_as_ready(self, time):
        self.timeToSeek = time

    def set_callback(self, callback):
        self.callback = callback

    def set_next_callback_time(self, nextCallbackTime):
        self.nextCallbackTime = nextCallbackTime

    def set_window_id(self, windowId):
        self.windowId = windowId

    def activate_video_callback(self, activate_video):
        self.activate_video_area = activate_video

    def get_current_time(self):
        pos_int = -1
        try:
            pos_int = self.playbin.query_position(self.time_format, None)[0]
        except:
            pass
        if pos_int != -1:
            return int(self.speed * pos_int / 1000000)
        else:
            return None

    def play_thread(self):
        play_thread_id = self.play_thread_id

        while play_thread_id == self.play_thread_id:
            time.sleep(0.1)
            pos_int = -1
            try:
                pos_int = self.player.query_position(self.time_format, None)[0]
            except:
                pass

            if pos_int != -1 and self.nextCallbackTime != -1 and self.speed * pos_int > self.nextCallbackTime * 1000000:
                self.nextCallbackTime = -1

                self.callback()

            if pos_int != -1 and self.timeToSeek != -1:
                self.seek(self.timeToSeek)
                self.timeToSeek = -1

    def close(self):
        self.player.set_state(gst.STATE_NULL)
