# -*- coding: utf-8 -*-

# Copyright (C) 2009-2011 Frédéric Bertolus.
# Copyright (C) 2009-2011 Matthieu Bizien.
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
import thread
import time
from gettext import gettext as _

import gtk
from debug import defaultLoggingHandler, defaultLoggingLevel
from model.exercise import Exercise
from model.exercise_parser import load_exercise, save_exercise
from model.sequence import NoCharPossible
from perroquetlib.config import config
from perroquetlib.repository.exercise_repository_manager import ExerciseRepositoryManager
from video_player import VideoPlayer

# The Core make the link between the GUI, the vidéo player, the current
# open exercise and all others part of the application
class Core(object):
    WAIT_BEGIN = 0
    WAIT_END = 1

    def __init__(self):
        self.player = None
        self.last_save = False
        self.exercise = None
        self.config = config
        self.logger = logging.Logger("Core")
        self.logger.setLevel(defaultLoggingLevel)
        self.logger.addHandler(defaultLoggingHandler)

    #Call by the main, give an handler to the main gui
    def set_gui(self, gui):
        self.gui_controller = gui

    #Create a new exercice based on paths. load the new exercise and
    #begin to play
    def new_exercise(self, videoPath, exercisePath, translationPath, langId):
        self.exercise = Exercise()
        self.exercise.set_media_change_callback(self.media_change_call_back)
        self.exercise.new()
        self.exercise.set_language_id(langId)
        self._set_paths(videoPath, exercisePath, translationPath)
        self.exercise.initialize()
        self._reload(True);
        self._activate_sequence()
        self.gui_controller.set_title("", True)

    #Configure the paths for the current exercice. Reload subtitles list.
    def _set_paths(self, videoPath, exercisePath, translationPath):
        self.exercise.set_video_path(videoPath)
        self.exercise.set_exercise_path(exercisePath)
        self.exercise.set_translation_path(translationPath)
        self.exercise.initialize()

    #Reload media player and begin to play (if the params is True)
    def _reload(self, load):
        if self.player != None:
            self.player.close()

        self.player = VideoPlayer()
        self.player.set_window_id(self.gui_controller.get_video_window_id())
        self.player.activate_video_callback(self.gui_controller.activate_video_area)
        self.player.open(self.exercise.get_video_path())
        self.player.set_callback(self._time_callback)
        self.paused = False
        self.gui_controller.activate_video_area(False)
        self.gui_controller.activate("loaded")
        self._update_word_list()
        self.timeUpdateThreadId = thread.start_new_thread(self.time_update_thread, ())

        if load and self.exercise.get_repeat_count_limit_by_sequence() == 0:
            #Auto start play only if repeat is not limited
            self.play()
        else:
            self.pause()

    #play the media
    def play(self):
        self.gui_controller.set_playing(True)
        self.player.play()
        self.paused = False

    #pause the media
    def pause(self):
        self.gui_controller.set_playing(False)
        self.player.pause()
        self.paused = True

    #Modify media speed
    def set_speed(self, speed):
        self.gui_controller.set_speed(speed)
        self.player.set_speed(speed)

    #Callback call by video player to notify change of media position.
    #Stop the media at the end of uncompleted sequences
    def _time_callback(self):
        if self.state == Core.WAIT_BEGIN:
            self.player.set_next_callback_time(self.exercise.get_current_sequence().get_time_end() + self.exercise.get_play_margin_after())
            self.state = Core.WAIT_END
        elif self.state == Core.WAIT_END:
            self.state = Core.WAIT_BEGIN
            if self.exercise.get_current_sequence().is_valid():
                gtk.gdk.threads_enter()
                self.next_sequence(False)
                gtk.gdk.threads_leave()
            else:
                self.pause()

    #Repeat the currence sequence
    def repeat_sequence(self):
        if not self.exercise.is_current_sequence_repeat_limit_reach():
            #Repeat limit not reach or no limit
            self.goto_sequence_begin()
            self.play()
            self.exercise.increment_current_sequence_repeat_count()


    #Change the active sequence
    def select_sequence(self, num, load=True):
        if self.exercise.get_current_sequence_id() == num:
            return
        self.exercise.goto_sequence(num)
        self._activate_sequence()
        if load and self.exercise.get_repeat_count_limit_by_sequence() == 0:
            #Auto start play only if repeat is not limited
            self.repeat_sequence()
        self.set_can_save(True)

    #Goto next sequence
    def next_sequence(self, load=True):
        if self.exercise.goto_next_sequence():
            self.set_can_save(True)
        self._activate_sequence()
        if load and self.exercise.get_repeat_count_limit_by_sequence() == 0:
            #Auto start play only if repeat is not limited
            self.repeat_sequence()

    #Goto previous sequence
    def previous_sequence(self, load=True):
        if self.exercise.goto_previous_sequence():
            self.set_can_save(True)
        self._activate_sequence()
        if load and self.exercise.get_repeat_count_limit_by_sequence() == 0:
            #Auto start play only if repeat is not limited
            self.repeat_sequence()

    #Goto next valid sequence
    def next_valid_sequence(self, load=True):
        if self.exercise.goto_next_valid_sequence():
            self.set_can_save(True)
        self._activate_sequence()
        if load and self.exercise.get_repeat_count_limit_by_sequence() == 0:
            #Auto start play only if repeat is not limited
            self.repeat_sequence()

    #Goto previous valid sequence
    def previous_valid_sequence(self, load=True):
        if self.exercise.goto_previous_valid_sequence():
            self.set_can_save(True)
        self._activate_sequence()
        if load and self.exercise.get_repeat_count_limit_by_sequence() == 0:
            #Auto start play only if repeat is not limited
            self.repeat_sequence()

    #Update interface with new sequence. Configure stop media callback
    def _activate_sequence(self):
        self.state = Core.WAIT_BEGIN
        self.set_speed(1)
        self.player.set_next_callback_time(self.exercise.get_current_sequence().get_time_begin())

        self.gui_controller.set_sequence_number(self.exercise.get_current_sequence_id(), self.exercise.get_sequence_count())
        self.gui_controller.set_sequence(self.exercise.get_current_sequence())
        self.__activate_translation()
        self._update_stats()

    #_update displayed translation on new active sequence
    def __activate_translation(self):
        if not self.exercise.get_translation_list():
            self.gui_controller.set_translation("")
        else:
            translation = ""
            currentBegin = self.exercise.get_current_sequence().get_time_begin()
            currentEnd = self.exercise.get_current_sequence().get_time_end()
            for sub in self.exercise.get_translation_list():
                begin = sub.get_time_begin()
                end = sub.get_time_end()
                if (begin >= currentBegin and begin <= currentEnd) or (end >= currentBegin and end <= currentEnd) or (begin <= currentBegin and end >= currentEnd):
                    translation += sub.get_text() + " "

            self.gui_controller.set_translation(translation)

    #Update displayed stats on new active sequence
    def _update_stats(self):
        sequenceCount = self.exercise.get_sequence_count()
        sequenceFound = 0
        wordCount = 0
        wordFound = 0
        for sequence in self.exercise.get_sequence_list():
            wordCount = wordCount + sequence.get_word_count()
            if sequence.is_valid():
                sequenceFound += 1
                wordFound += sequence.get_word_count()
            else:
                wordFound += sequence.get_word_found()
        if wordFound == 0:
            repeatRate = float(0)
        else:
            repeatRate = float(self.exercise.get_repeat_count()) / float(wordFound)
        self.gui_controller.set_statitics(sequenceCount, sequenceFound, wordCount, wordFound, repeatRate)

    def _update(self):
        self.gui_controller.set_sequence(self.exercise.get_current_sequence())
        self.__validate_sequence()

    #Verify if the sequence is complete
    def __validate_sequence(self):
        if self.exercise.get_current_sequence().is_valid():
            if self.exercise.get_repeat_after_completed():
                if self.exercise.get_repeat_count_limit_by_sequence() == 0:
                    #Auto start play only if repeat is not limited
                    self.repeat_sequence()
            else:
                self.next_sequence(False)
                if self.exercise.get_repeat_count_limit_by_sequence() == 0:
                    #Auto start play only if repeat is not limited
                    self.play()


    #Goto beginning of the current sequence. Can start to play as soon
    #as the media player is ready
    def goto_sequence_begin(self, asSoonAsReady=False):
        self.state = Core.WAIT_END
        begin_time = self.exercise.get_current_sequence().get_time_begin() - self.exercise.get_play_margin_before()
        if begin_time < 0:
            begin_time = 0
        if asSoonAsReady:
            self.player.seek_as_soon_as_ready(begin_time)
        else:
            self.player.seek(begin_time)
        self.player.set_next_callback_time(self.exercise.get_current_sequence().get_time_end())


    #Write a char in current sequence at cursor position
    def write_char(self, char):
        if self.exercise.is_character_match(char):
            self.exercise.get_current_sequence().write_char(char)
            self.exercise.get_current_sequence().update_cursor_position()
            self._update()
            self.set_can_save(True)
        else:
            self._update()

    #Goto next word in current sequence
    def next_word(self):
        self.exercise.get_current_sequence().next_word()
        self._update()

    #Goto previous word in current sequence
    def previous_word(self):
        self.exercise.get_current_sequence().previous_word()
        self._update()

    #Choose current word in current sequence
    def select_sequence_word(self, wordIndex, wordIndexPos):
        try:
            self.exercise.get_current_sequence().select_sequence_word(wordIndex, wordIndexPos)
        except NoCharPossible:
            self.exercise.get_current_sequence().select_sequence_word(wordIndex, -1)
        self._update()

    #Goto first word in current sequence
    def first_word(self):
        self.exercise.get_current_sequence().first_word()
        self._update()

    #Goto last word in current sequence
    def last_word(self):
        self.exercise.get_current_sequence().last_word()
        self._update()

    #Delete a char before the cursor in current sequence
    def delete_previous_char(self):
        self.exercise.get_current_sequence().delete_previous_char()
        self._update()
        self.set_can_save(True)

    #Delete a char after the cursor in current sequence
    def delete_next_char(self):
        self.exercise.get_current_sequence().delete_next_char()
        self._update()
        self.set_can_save(True)

    #Goto previous char in current sequence
    def previous_char(self):
        self.exercise.get_current_sequence().previous_char()
        #The sequence don't change but the cursor position is no more up to date
        self._update()

    #Goto next char in current sequence
    def next_char(self):
        self.exercise.get_current_sequence().next_char()
        #The sequence don't change but the cursor position is no more up to date
        self._update()

    #Reveal correction for word at cursor in current sequence
    def complete_word(self):
        self.exercise.get_current_sequence().show_hint()
        self._update()
        self.set_can_save(True)
    
    #Reveal correction for word at cursor in current sequence
    def reveal_word(self):
        self.exercise.get_current_sequence().complete_word()
        self.exercise.get_current_sequence().next_word()
        self._update()
        self.set_can_save(True)

    #Reveal correction for word at cursor in current sequence
    def reveal_sequence(self):
        self.exercise.get_current_sequence().complete_all()
        self._update()
        self.set_can_save(True)

    #reset whole exercise
    def reset_exercise_content(self):
        self.exercise.reset()
        self.exercise.goto_sequence(0) #FIXME
        self._update()
        self.set_can_save(True)
        self.logger.debug("need to stop the current sequence") #FIXME

    #pause or play media
    def toggle_pause(self):
        if self.player.is_paused() and self.paused:
            self.play()
        elif not self.player.is_paused() and not self.paused:
            self.pause()

    #Change position in media and play it
    def seek_sequence(self, time):
        begin_time = self.exercise.get_current_sequence().get_time_begin() - self.exercise.get_play_margin_before()
        if begin_time < 0:
            begin_time = 0

        pos = begin_time + time
        self.player.seek(pos)
        self.player.set_next_callback_time(self.exercise.get_current_sequence().get_time_end() + self.exercise.get_play_margin_after())
        self.state = Core.WAIT_END
        if self.exercise.get_repeat_count_limit_by_sequence() == 0:
            #Auto start play only if repeat is not limited
            self.play()

    #Thread to update slider position in gui
    def time_update_thread(self):
        timeUpdateThreadId = self.timeUpdateThreadId
        while timeUpdateThreadId == self.timeUpdateThreadId:
            time.sleep(0.5)
            pos_int = self.player.get_current_time()
            if pos_int != None:
                end_time = self.exercise.get_current_sequence().get_time_end()
                begin_time = self.exercise.get_current_sequence().get_time_begin() - self.exercise.get_play_margin_before()
                if begin_time < 0:
                    begin_time = 0
                duration = end_time - begin_time
                pos = pos_int -begin_time
                self.gui_controller.set_sequence_time(pos, duration)

    #Save current exercice
    def save(self, saveAs=False):
        if not self.exercise:
            self.logger.error("Save called but no exercise load")
            return

        if saveAs or self.exercise.get_output_save_path() == None:
            outputSavePath = self.gui_controller.ask_save_path()
            if not outputSavePath:
                return
            self.exercise.set_output_save_path(outputSavePath + ".perroquet")

        save_exercise(self.exercise, self.exercise.get_output_save_path())

        self.config.set("lastopenfile", self.exercise.get_output_save_path())

        #lastopenfileS
        l = self.config.get("lastopenfiles")
        path = self.exercise.get_output_save_path()
        name = self.exercise.get_name() or path
        self.config.set("lastopenfiles", [[path, name]] + [p for p in l if p[0] != path][:10])

        self.set_can_save(False)

    #load the exercice at path
    def load_exercise(self, path):
        self.gui_controller.activate("closed")
        if self.exercise:
            self.save()
        try:
            self.exercise = load_exercise(path)
            self.exercise.set_media_change_callback(self.media_change_call_back)
        except IOError:
            self.logger.exception("No file at " + path)
            return
        if not self.exercise:
            return


        validPaths, errorList = self.exercise.is_paths_valid()
        if not validPaths:
            for error in errorList:
                self.gui_controller.signal_exercise_bad_path(error)

            self.set_can_save(False)
            self.gui_controller.activate("load_failed")
            self.gui_controller.ask_properties()
            return

        self._reload(False)
        if self.exercise.get_output_save_path() == None:
            self.set_can_save(True)
        else:
            self.set_can_save(False)
        self._activate_sequence()
        self.goto_sequence_begin(True)
        if self.exercise.get_repeat_count_limit_by_sequence() == 0:
            #Auto start play only if repeat is not limited
            self.play()

    #Change paths of current exercice and reload subtitles and video
    def _update_paths(self, videoPath, exercisePath, translationPath):
        self.exercise.set_video_path(videoPath)
        self.exercise.set_exercise_path(exercisePath)
        self.exercise.set_translation_path(translationPath)

        validPaths, errorList = self.exercise.is_paths_valid()
        if not validPaths:
            for error in errorList:
                self.gui_controller.signal_exercise_bad_path(error)
            self.gui_controller.activate("load_failed")
            self.set_can_save(False)
            return

        self._set_paths(videoPath, exercisePath, translationPath)
        self._reload(True)
        self.set_can_save(True)
        self._activate_sequence()
        self.goto_sequence_begin(True)
        if self.exercise.get_repeat_count_limit_by_sequence() == 0:
            #Auto start play only if repeat is not limited
            self.play()

    def update_properties(self):
        self.exercise.initialize()
        self._reload(True)
        self.set_can_save(True)
        self._activate_sequence()
        self.goto_sequence_begin(True)
        if self.exercise.get_repeat_count_limit_by_sequence() == 0:
            #Auto start play only if repeat is not limited
            self.play()

    #get paths of current exercise
    def get_paths(self):
        return (self.exercise.get_video_path(), self.exercise.get_exercise_path(), self.exercise.get_translation_path())

    #Udpates vocabulary list in interface
    def _update_word_list(self):
        self.gui_controller.set_word_list(self.exercise.extract_word_list())

    #Notify the user use the repeat command (for stats)
    def user_repeat(self):
        self.exercise.increment_repeat_count()
        self.set_can_save(True)

    #Signal to the gui that the exercise has unsaved changes
    def set_can_save(self, save):
        self.gui_controller.set_can_save(save)

        if self.exercise == None:
            title = ""
        elif self.exercise.get_name() != None:
            title = self.exercise.get_name()
        elif self.exercise.get_output_save_path() != None:
            title = self.exercise.get_output_save_path()
        else:
            title = _("Untitled exercise")

        self.last_save = save
        self.gui_controller.set_title(title, save)

    def get_can_save(self):
        return self.last_save

    def get_exercise(self):
        return self.exercise

    def get_player(self):
        return self.player

    def media_change_call_back(self):
        self.logger.info("new media : " + self.exercise.get_video_path())
        """self.Pause()
        self.player.open(self.exercise.get_video_path())
        """
        self._reload(True)
        self._activate_sequence()
        self.goto_sequence_begin(True)
        if self.exercise.get_repeat_count_limit_by_sequence() == 0:
            #Auto start play only if repeat is not limited
            self.play()

    def export_as_template(self):
        self.gui_controller.ask_properties_advanced()
        path = self.gui_controller.ask_export_as_template_path()
        if path:
            self.exercise.set_template(True)
            save_exercise(self.exercise, path)
            self.exercise.set_template(False)

    def export_as_package(self):
        self.gui_controller.ask_properties_advanced()
        path = self.gui_controller.ask_export_as_package_path()
        if path:
            repoManager = ExerciseRepositoryManager()
            repoManager.export_as_package(self.exercise, path)
            self.logger.info("Export done")
        else:
            self.logger.warn("No valid path to export??")


    def import_package(self):
        import_path = self.gui_controller.ask_import_package()

        if import_path is not None:
            repo_manager = ExerciseRepositoryManager()
            error = repo_manager.import_package(import_path)
            if error is None:
                self.gui_controller.display_message(_("Import finish succesfully. Use the exercises manager to use the newly installed exercise."))
            else:
                self.gui_controller.display_message(_("Import failed." + " " + error))
