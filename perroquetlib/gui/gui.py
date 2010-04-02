# -*- coding: utf-8 -*-

# Copyright (C) 2009-2010 Frédéric Bertolus.
# Copyright (C) 2009-2010 Matthieu Bizien.
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


import gtk
import os
import gettext
import locale
import logging

from perroquetlib.core import defaultLoggingHandler, defaultLoggingLevel
from perroquetlib.config import config
from perroquetlib.model.languages_manager import LanguagesManager

from gui_sequence_properties import GuiSequenceProperties
from gui_sequence_properties_advanced import GuiSequencePropertiesAdvanced
from gui_reset_exercise import GuiResetExercise
from gui_settings import Guisettings
from gui_exercise_manager import GuiExerciseManager
from gui_password_dialog import GuiPasswordDialog

_ = gettext.gettext

class Gui:
    def __init__(self, controller):

        locale.bindtextdomain(config.get("gettext_package"),config.get("localedir"))

        self.logger = logging.Logger("GUI")
        self.logger.setLevel(defaultLoggingLevel)
        self.logger.addHandler(defaultLoggingHandler)
        self.controller = controller
    
        self.builder = gtk.Builder()
        self.builder.set_translation_domain("perroquet")
        self.builder.add_from_file(config.get("ui_path"))
        self.builder.connect_signals(self)
        self.window = self.builder.get_object("MainWindow")
        self.window.set_icon_from_file(config.get("logo_path"))

        self.aboutDialog = self.builder.get_object("aboutdialog")
        icon = gtk.gdk.pixbuf_new_from_file(config.get("logo_path"))
        self.aboutDialog.set_logo(icon)
        self.aboutDialog.set_version(config.get("version"))

        # Sound icon
        self.builder.get_object("imageAudio").set_from_file(config.get("audio_icon"))

        self.typeLabel = self.builder.get_object("typeView")

        self.disable_changed_text_event = False
        self.setted_speed = 100
        self.setted_sequence_number = 0
        self.setted_position = 0
        self.setted_typing_area_text = ""

        self.newExerciseDialog = None
        self.liststoreLanguage = None

        self.disable_correction_event = False

        self._update_last_open_files_tab()

    def signal_exercise_bad_path(self, path):
        dialog = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL,
                                   gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                   _("The file '%s' doesn't exist. Please modify exercise paths") % path)
        dialog.set_title(_("load error"))

        dialog.run()
        dialog.destroy()

    

    def get_video_window_id(self):
        return self.builder.get_object("videoArea").window.xid

    def set_active_video_area(self,state):
        if state:
            self.builder.get_object("videoArea").show()
            self.builder.get_object("imageAudio").hide()
        else:
            self.builder.get_object("videoArea").hide()
            self.builder.get_object("imageAudio").show()

    def set_speed(self, speed):
        self.setted_speed = int(speed*100)
        ajustement = self.builder.get_object("adjustmentSpeed")
        ajustement.configure (self.setted_speed, 75, 100, 1, 10, 0)

    def set_sequence_index_selection(self, sequenceNumber, sequenceCount):
        ajustement = self.builder.get_object("adjustmentSequenceNum")
        self.setted_sequence_number = sequenceNumber
        ajustement.configure (sequenceNumber, 1, sequenceCount, 1, 10, 0)
        self.builder.get_object("labelSequenceNumber").set_text(str(sequenceNumber) + "/" + str(sequenceCount))

    def set_sequence_time_selection(self, sequence_position, sequence_time):
        """Documentation"""
        self.setted_position = sequence_position /100
        ajustement = self.builder.get_object("adjustmentSequenceTime")
        ajustement.configure (self.setted_position, 0, sequence_time/100, 1, 10, 0)
        textTime = round(float(sequence_position)/1000,1)
        textDuration = round(float(sequence_time)/1000,1)
        self.builder.get_object("labelSequenceTime").set_text(str(textTime) + "/" + str(textDuration) + " s")

    def set_word_list(self, word_list):
        """Create a string compose by word separated with \n and update the text field"""
        buffer = self.builder.get_object("textviewWordList").get_buffer()

        iter1 = buffer.get_start_iter()
        iter2 = buffer.get_end_iter()
        buffer.delete(iter1, iter2)

        formattedWordList = ""

        for word in word_list:
            formattedWordList = formattedWordList + word + "\n"

        iter = buffer.get_end_iter()
        buffer.insert(iter,formattedWordList)

    def get_words_filter(self):
        return self.builder.get_object("entryFilter").get_text()

    def set_translation(self, translation):
        textviewTranslation = self.builder.get_object("textviewTranslation").get_buffer()
        textviewTranslation.set_text(translation)

    def set_statitics(self, text):
        labelProgress = self.builder.get_object("labelProgress")
        labelProgress.set_label(text)

    def set_title(self, title):
        self.window.set_title(title)

    def _clear_typing_area(self):
        buffer = self.typeLabel.get_buffer()
        iter1 = buffer.get_start_iter()
        iter2 = buffer.get_end_iter()
        buffer.delete(iter1, iter2)

    def set_typing_area_text(self, formatted_text):
        self.disable_changed_text_event = True
        self._clear_typing_area()
        buffer = self.typeLabel.get_buffer()

        for (text, style) in formatted_text:
            size = buffer.get_char_count()
            iter1 = buffer.get_end_iter()
            buffer.insert(iter1,text)
            iter1 = buffer.get_iter_at_offset(size)
            iter2 = buffer.get_end_iter()
            buffer.apply_tag_by_name(style, iter1, iter2)

        self.setted_typing_area_text = buffer.get_text(buffer.get_start_iter(),buffer.get_end_iter())

        self.disable_changed_text_event = False

    def set_typing_area_cursor_position(self, cursor_position):
        buffer = self.typeLabel.get_buffer()
        iter = buffer.get_iter_at_offset(cursor_position)
        buffer.place_cursor(iter)

    def set_focus_typing_area(self):
        self.window.set_focus(self.typeLabel)

    def set_typing_area_style_list(self,style_list):
        """creates the labels used for the coloration of the text"""
        buffer = self.typeLabel.get_buffer()

        # Remove existing tags
        tag_table = buffer.get_tag_table()
        tag_table.foreach(self._destroy_tag, tag_table)

        for (tag_name,size, foreground_color ,background_color, through) in style_list:
            if foreground_color:
                (red, green, bleu) = foreground_color
                gtk_foreground_color = self.window.get_colormap().alloc_color(
                    red*256,
                    green*256,
                    bleu*256)
            else:
                gtk_foreground_color = None

            if background_color:
                (red, green, bleu) = background_color
                gtk_background_color = self.window.get_colormap().alloc_color(
                    red*256,
                    green*256,
                    bleu*256)
            else:
                gtk_background_color = None

            buffer.create_tag(tag_name,
            background=gtk_background_color,
            foreground=gtk_foreground_color,
            strikethrough=through,
            size_points=size)
      

    def _destroy_tag(text_tag, tag_table):
        tag_table.remove(text_tag)

    def ask_save_path(self):
        saver = SaveFileSelector(self.window)
        path =saver.run()
        return path

    def ask_export_as_template_path(self):
        saver = ExportAsTemplateFileSelector(self.window)
        path =saver.run()
        if path == None:
            return

        if path == "None" or path == None :
            path = ""
        elif not path.endswith(".perroquet"):
            path = path +".perroquet"
        return path

    def ask_export_as_package_path(self):
        saver = ExportAsPackageFileSelector(self.window)
        path =saver.run()
        if path == None:
            return

        if path == "None" or path == None :
            path = ""
        elif not path.endswith(".tar"):
            path = path +".tar"
        return path

    def ask_import_package(self):
        loader = ImportFileSelector(self.window)
        result =loader.run()
        return result

    def ask_properties(self, core):
        dialogExerciseProperties = GuiSequenceProperties(core, self.window)
        dialogExerciseProperties.run()

    def ask_properties_advanced(self, core):
        dialogExerciseProperties = GuiSequencePropertiesAdvanced(core, self.window)
        dialogExerciseProperties.run()

    def ask_settings(self):
        dialogsettings = Guisettings(self.window)
        dialogsettings.run()

    def ask_correction(self):
        dialog_password = GuiPasswordDialog(self.window, "correction")
        return  dialog_password.run()
    
    def run(self):
        gtk.gdk.threads_init()
        self.window.show()
        gtk.main()

    def _update_last_open_files_tab(self):
        #TODO: move part in controller ?
        gtkTree = self.builder.get_object("lastopenfilesTreeView")

        if not gtkTree.get_columns() == []:
            raise Exception

        cell = gtk.CellRendererText()

        treeViewColumn = gtk.TreeViewColumn(_("Path"))
        treeViewColumn.pack_start(cell, False)
        treeViewColumn.add_attribute(cell, 'markup', 0)
        treeViewColumn.set_expand(False)
        gtkTree.append_column(treeViewColumn)


        treeStore = gtk.TreeStore(str)
        for file in config.get("lastopenfiles"):
            treeStore.append(None, [file])

        gtkTree.set_model(treeStore)


    def quit(self):
        gtk.main_quit()

    def ask_confirm_quit_without_save(self):
        dialog = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL,
                                       gtk.MESSAGE_INFO, gtk.BUTTONS_YES_NO,
                                       _("Do you really quit without save ?"))
        dialog.set_title(_("Confirm quit"))

        response = dialog.run()
        dialog.destroy()
        return response == gtk.RESPONSE_YES


    def ask_reset_exercise_content(self):
        dialogExerciseProperties = GuiResetExercise( self.window)
        response = dialogExerciseProperties.run()
        return response

    def display_message(self, message):
        #TODO implemernt message box
        self.logger.warn("display_message TODO:"+ message)

    def set_enable_sequence_index_selection(self, state):
        self.builder.get_object("hscaleSequenceNum").set_sensitive(state)

    def set_enable_sequence_time_selection(self, state):
        self.builder.get_object("hscaleSequenceTime").set_sensitive(state)

    def set_enable_hint(self, state):
        self.builder.get_object("toolbuttonHint").set_sensitive(state)
        self.builder.get_object("imagemenuitemHint").set_sensitive(state)

    def set_enable_replay_sequence(self, state):
        self.builder.get_object("toolbuttonReplaySequence").set_sensitive(state)

    def set_enable_properties(self, state):
        self.builder.get_object("toolbuttonProperties").set_sensitive(state)
        self.builder.get_object("imagemenuitemProperties").set_sensitive(state)

    def set_enable_advanced_properties(self, state):
        self.builder.get_object("imagemenuitemAdvancedProperties").set_sensitive(state)

    def set_enable_translation(self, state):
        self.builder.get_object("toggletoolbuttonShowTranslation").set_sensitive(state)
        self.builder.get_object("checkmenuitemTranslation").set_sensitive(state)

    def set_enable_correction(self, state):
        self.builder.get_object("toolbutton_show_correction").set_sensitive(state)
        self.builder.get_object("checkmenuitem_correction").set_sensitive(state)

    def set_active_translation(self, state):
        self.builder.get_object("toggletoolbuttonShowTranslation").set_active(state)
        self.builder.get_object("checkmenuitemTranslation").set_active(state)

    def set_active_correction(self, state):
        self.disable_correction_event = True
        self.builder.get_object("toolbutton_show_correction").set_active(state)
        self.builder.get_object("checkmenuitem_correction").set_active(state)
        self.disable_correction_event = False

    def set_enable_save_as(self, state):
        self.builder.get_object("imagemenuitemSaveAs").set_sensitive(state)

    def set_enable_save(self, state):
        self.builder.get_object("imagemenuitemSave").set_sensitive(state)
        self.builder.get_object("saveButton").set_sensitive(state)

    def set_enable_export_as_template(self, state):
        self.builder.get_object("imagemenuitemExportAsTemplate").set_sensitive(state)

    def set_enable_export_as_package(self, state):
        self.builder.get_object("imagemenuitemExportAsPackage").set_sensitive(state)

    def set_enable_speed_selection(self, state):
        self.builder.get_object("hscaleSpeed").set_sensitive(state)

    def set_enable_play(self, state):
        self.builder.get_object("toolbuttonPlay").set_sensitive(state)

    def set_enable_pause(self, state):
        self.builder.get_object("toolbuttonPause").set_sensitive(state)

    def set_enable_next_sequence(self, state):
        self.builder.get_object("toolbuttonNextSequence").set_sensitive(state)

    def set_enable_previous_sequence(self, state):
        self.builder.get_object("toolbuttonPreviousSequence").set_sensitive(state)



    def set_visible_play(self, state):
        if state:
            self.builder.get_object("toolbuttonPlay").show()
        else:
            self.builder.get_object("toolbuttonPlay").hide()

    def set_visible_pause(self, state):
        if state:
            self.builder.get_object("toolbuttonPause").show()
        else:
            self.builder.get_object("toolbuttonPause").hide()

    def set_visible_lateral_panel(self, state):
        if state:
            self.builder.get_object("lateralPanel").show()
        else:
            self.builder.get_object("lateralPanel").hide()

    def set_visible_translation_panel(self, state):
        if state:
            self.builder.get_object("scrolledwindowTranslation").show()
        else:
            self.builder.get_object("scrolledwindowTranslation").hide()



    def set_checked_lateral_panel(self, checked):
        self.builder.get_object("checkmenuitemLateralPanel").set_active(checked)


    def ask_new_exercise(self):
        self.newExerciseDialog = self.builder.get_object("newExerciseDialog")

        videoChooser = self.builder.get_object("filechooserbuttonVideo")
        exerciseChooser = self.builder.get_object("filechooserbuttonExercise")
        translationChooser = self.builder.get_object("filechooserbuttonTranslation")
        videoChooser.set_filename("None")
        exerciseChooser.set_filename("None")
        translationChooser.set_filename("None")

        self.liststoreLanguage = gtk.ListStore(str,str)

        languageManager = LanguagesManager()
        languagesList =languageManager.get_languages_list()

        for language in languagesList:
            (langId,langName,chars) = language
            iter = self.liststoreLanguage.append([langName,langId])
            if langId == config.get("default_exercise_language"):
                currentIter = iter

        comboboxLanguage = self.builder.get_object("comboboxLanguage")

        #Clear old values
        comboboxLanguage.clear()

        cell = gtk.CellRendererText()
        comboboxLanguage.set_model(self.liststoreLanguage)
        comboboxLanguage.pack_start(cell, True)
        comboboxLanguage.add_attribute(cell, 'text', 0)

        comboboxLanguage.set_active_iter(currentIter)

        

    def set_visible_new_exercise_dialog(self,state):
        if state:
            self.newExerciseDialog.show()
        else:
           self.newExerciseDialog.hide()

    def ask_load_exercise(self):
        loader = OpenFileSelector(self.window)
        result =loader.run()
        return result

    def display_exercice_manager(self,core):
        dialogExerciseManager = GuiExerciseManager(core, self.window)
        dialogExerciseManager.run()

    #---------------------- Now the functions called directly by the gui--------

    def on_main_window_delete_event(self,widget,data=None):
        # returning True avoids it to signal "destroy-event"
        # returning False makes "destroy-event" be signalled for the window.
        return self.controller.notify_quit()

    def on_new_exercise_button_clicked(self,widget,data=None):
        return self.controller.notify_new_exercise()


    def on_button_new_exercise_ok_clicked(self,widget,data=None):

        videoChooser = self.builder.get_object("filechooserbuttonVideo")
        videoPath = videoChooser.get_filename()
        exerciseChooser = self.builder.get_object("filechooserbuttonExercise")
        exercisePath = exerciseChooser.get_filename()
        translationChooser = self.builder.get_object("filechooserbuttonTranslation")
        translationPath = translationChooser.get_filename()
        if videoPath == "None" or videoPath == None:
            videoPath = ""
        if exercisePath == "None" or exercisePath == None:
            exercisePath = ""
        if translationPath == "None" or translationPath == None:
            translationPath = ""

        comboboxLanguage = self.builder.get_object("comboboxLanguage")
        self.liststoreLanguage.get_iter_first()
        iter = comboboxLanguage.get_active_iter()
        langId = self.liststoreLanguage.get_value(iter,1)

        self.controller.notify_new_exercise_create(videoPath,exercisePath, translationPath, langId)
        
    def on_newExerciseDialog_delete_event(self,widget,data=None):
        self.controller.notify_new_exercise_cancel()
        return True #True for stop event propagation

    def on_button_new_exercise_cancel_clicked(self,widget,data=None):
        self.controller.notify_new_exercise_cancel()

    def on_imagemenuitem_export_as_template_activate(self,widget,data=None):
        self.controller.notify_export_as_template()

    def on_imagemenuitem_export_as_package_activate(self,widget,data=None):
        self.controller.notify_export_as_package()

    def on_imagemenuitem_import_activate(self,widget,data=None):
        self.controller.notify_import_package()

    def on_textbuffer_view_changed(self,widget):

        if self.disable_changed_text_event:
           return False;

        buffer = self.typeLabel.get_buffer()
        oldText = self.setted_typing_area_text
        newText = buffer.get_text(buffer.get_start_iter(),buffer.get_end_iter())
        index = self.typeLabel.get_buffer().props.cursor_position

        newText= newText.decode("utf-8")
        oldText= oldText.decode("utf-8")

        newLength = len(newText) - len(oldText)
        newString = newText[index-newLength:index]

        return self.controller.notify_typing(newString)
        
        

    def on_type_view_key_press_event(self,widget, event):
        keyname = gtk.gdk.keyval_name(event.keyval)
        return self.controller.notify_key_press(keyname)
        
    def on_toolbutton_next_sequence_clicked(self,widget,data=None):
        self.controller.notify_next_sequence()

    def on_toolbutton_previous_sequence_clicked(self,widget,data=None):
        self.controller.notify_previous_sequence()

    def on_toolbutton_replay_sequence_clicked(self,widget,data=None):
        self.controller.notify_repeat_sequence()

    def on_adjustment_sequence_num_value_changed(self,widget,data=None):

        value = int(self.builder.get_object("adjustmentSequenceNum").get_value())

        if value != self.setted_sequence_number:
            self.controller.notify_select_sequence_number(value - 1)

    def on_adjustment_sequence_time_value_changed(self,widget,data=None):
        value = int(self.builder.get_object("adjustmentSequenceTime").get_value())
        if value != self.setted_position:
            self.controller.notify_select_sequence_time(value*100)

    def on_adjustment_speed_value_changed(self,widget,data=None):
        value = int(self.builder.get_object("adjustmentSpeed").get_value())
        if value != self.setted_speed:
            self.controller.notify_select_speed(float(value)/100)

    def on_toolbutton_hint_clicked(self,widget,data=None):
        self.controller.notify_hint()

    def on_toolbutton_play_clicked(self,widget,data=None):
        self.controller.notify_play()

    def on_toolbutton_pause_clicked(self,widget,data=None):
        self.controller.notify_pause()

    def on_save_button_clicked(self, widget, data=None):
        self.controller.notify_save()

    def on_load_button_clicked(self, widget, data=None):
        self.controller.notify_load()
        
    def on_button_save_exercise_ok_clicked(self, widget, data=None):
        #TODO : use controller
        saveChooser = self.builder.get_object("filechooserdialogSave")
        saveChooser.hide()

    def on_entry_filter_changed(self, widget, data=None):
        self.controller.notify_filter_change()

    def on_toggletoolbutton_show_translation_toggled(self, widget, data=None):
        toggletoolbuttonShowTranslation = self.builder.get_object("toggletoolbuttonShowTranslation")
        self.controller.notify_toogle_translation(toggletoolbuttonShowTranslation.props.active)

    def on_checkmenuitem_correction_toggled(self, widget, data=None):
        if self.disable_correction_event:
            return False
        toolbutton_show_correction = self.builder.get_object("toolbutton_show_correction")
        self.controller.notify_toogle_correction(not toolbutton_show_correction.props.active)

    def on_toolbutton_show_correction_toggled(self, widget, data=None):
        if self.disable_correction_event:
            return False
        toolbutton_show_correction = self.builder.get_object("toolbutton_show_correction")
        self.controller.notify_toogle_correction(toolbutton_show_correction.props.active)


    def on_type_view_move_cursor(self, textview, step_size, count, extend_selection):

        if step_size == gtk.MOVEMENT_VISUAL_POSITIONS:
            if count == -1:
                self.controller.notify_move_cursor("previous_char")
            elif count == 1:
                self.controller.notify_move_cursor("next_char")
        elif step_size == gtk.MOVEMENT_DISPLAY_LINE_ENDS:
            if count == -1:
                self.controller.notify_move_cursor("first_word")
            elif count == 1:
                self.controller.notify_move_cursor("last_word")
        elif step_size == gtk.MOVEMENT_WORDS:
            if count == -1:
                self.controller.notify_move_cursor("previous_word")
            elif count == 1:
                self.controller.notify_move_cursor("next_word")

        return True

    def on_type_view_button_release_event(self, widget, data=None):
        index = self.typeLabel.get_buffer().props.cursor_position
        return self.controller.notify_move_cursor(index)

    def on_toolbutton_properties_clicked(self, widget, data=None):
        self.controller.notify_properties()

    def on_imagemenuitem_exercice_manager_activate(self, widget, data=None):
        self.controller.notify_exercise_manager()

    def on_imagemenuitem_about_activate(self,widget,data=None):
        self.builder.get_object("aboutdialog").show()

    def on_imagemenuitem_hint_activate(self,widget,data=None):
        self.controller.notify_hint()

    def on_checkmenuitem_lateral_panel_toggled(self,widget,data=None):
        self.controller.toggle_lateral_panel()

    def on_checkmenuitem_translation_toggled(self,widget,data=None):
        checkmenuitemTranslation = self.builder.get_object("checkmenuitemTranslation")
        self.controller.notify_toogle_translation(checkmenuitemTranslation.props.active)
        
    def on_imagemenuitem_properties_activate(self,widget,data=None):
        self.controller.notify_properties()

    def on_imagemenuitem_advanced_properties_activate(self,widget,data=None):
        self.controller.notify_properties_advanced()

    def on_imagemenuitem_settings_activate(self,widget,data=None):
        self.controller.notify_settings()

    def on_imagemenuitem_quit_activate(self,widget,data=None):
        return self.controller.notify_quit()

    def on_imagemenuitem_save_as_activate(self,widget,data=None):
        self.controller.notify_save_as()

    def on_imagemenuitem_save_activate(self,widget,data=None):
        self.controller.notify_save()

    def on_imagemenuitem_open_activate(self,widget,data=None):
        self.controller.notify_load()

    def on_imagemenuitem_new_activate(self,widget,data=None):
        self.controller.notify_new_exercise()

    def on_filechooserbutton_video_file_set(self,widget,data=None):

        videoChooser = self.builder.get_object("filechooserbuttonVideo")
        exerciseChooser = self.builder.get_object("filechooserbuttonExercise")
        translationChooser = self.builder.get_object("filechooserbuttonTranslation")

        fileName = videoChooser.get_filename()
        if fileName and os.path.isfile(fileName):
            filePath = os.path.dirname(fileName)
            if not exerciseChooser.get_filename() or not os.path.isfile(exerciseChooser.get_filename()):
                exerciseChooser.set_current_folder(filePath)
            if not translationChooser.get_filename() or not os.path.isfile(translationChooser.get_filename()):
                translationChooser.set_current_folder(filePath)

    def on_aboutdialog_delete_event(self,widget,data=None):
        self.builder.get_object("aboutdialog").hide()
        return True

    def on_aboutdialog_response(self,widget,data=None):
        self.builder.get_object("aboutdialog").hide()
        return True

    def on_menuitem_reset_progress_activate(self, widget, data=None):
        self.controller.notify_reset_exercise_content()

    def on_reset_exercise_content_clicked(self, widget, data=None):
        self.controller.notify_reset_exercise_content()

    def on_lastopenfilesTreeView_cursor_changed(self, widget, data=None):
        gtkTree = self.builder.get_object("lastopenfilesTreeView")
        gtkSelection = gtkTree.get_selection()
        (modele, iter) =  gtkSelection.get_selected()
        path = modele.get(iter, 0)[0]
        self.controller.notify_load_path(path)
        
EVENT_FILTER = None


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


        #FIXME unused
        def add_widget(self, title, widget):
                "Adds a widget to the file selection"

                if self.inputsection == None:
                        self.inputsection = ui.InputSection() #FIXME ui ???
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
                        self, parent, _('Select File to open'),
                        gtk.FILE_CHOOSER_ACTION_OPEN, gtk.STOCK_OPEN
                )

                filter = gtk.FileFilter()
                filter.set_name(_('Perroquet files'))
                filter.add_pattern("*.perroquet")
                self.add_filter(filter)

                filter = gtk.FileFilter()
                filter.set_name(_('All files'))
                filter.add_pattern("*")
                self.add_filter(filter)

class ImportFileSelector(FileSelector):
        "A file selector for import files"

        def __init__(self, parent):
                FileSelector.__init__(
                        self, parent, _('Select package to import'),
                        gtk.FILE_CHOOSER_ACTION_OPEN, gtk.STOCK_OPEN
                )

                filter = gtk.FileFilter()
                filter.set_name(_('Perroquet package files'))
                filter.add_pattern("*.tar")
                self.add_filter(filter)

                filter = gtk.FileFilter()
                filter.set_name(_('All files'))
                filter.add_pattern("*")
                self.add_filter(filter)

class SaveFileSelector(FileSelector):
        "A file selector for saving files"

        def __init__(self, parent):
                FileSelector.__init__(
                        self, parent, _('Select File to Save to'),
                        gtk.FILE_CHOOSER_ACTION_SAVE, gtk.STOCK_SAVE
                )

                filter = gtk.FileFilter()
                filter.set_name(_('Perroquet files'))
                filter.add_pattern("*.perroquet")
                self.add_filter(filter)

                filter = gtk.FileFilter()
                filter.set_name(_('All files'))
                filter.add_pattern("*")
                self.add_filter(filter)

                self.set_do_overwrite_confirmation(True)

class ExportAsTemplateFileSelector(FileSelector):
        "A file selector for saving files"

        def __init__(self, parent):
                FileSelector.__init__(
                        self, parent, _('Select File to Export to'),
                        gtk.FILE_CHOOSER_ACTION_SAVE, gtk.STOCK_SAVE
                )

                filter = gtk.FileFilter()
                filter.set_name(_('Perroquet template files'))
                filter.add_pattern("*.perroquet")
                self.add_filter(filter)

                filter = gtk.FileFilter()
                filter.set_name(_('All files'))
                filter.add_pattern("*")
                self.add_filter(filter)

                self.set_do_overwrite_confirmation(True)

class ExportAsPackageFileSelector(FileSelector):
        "A file selector for saving files"

        def __init__(self, parent):
                FileSelector.__init__(
                        self, parent, _('Select File to Export to'),
                        gtk.FILE_CHOOSER_ACTION_SAVE, gtk.STOCK_SAVE
                )

                filter = gtk.FileFilter()
                filter.set_name(_('Perroquet package files'))
                filter.add_pattern("*.tar")
                self.add_filter(filter)

                filter = gtk.FileFilter()
                filter.set_name(_('All files'))
                filter.add_pattern("*")
                self.add_filter(filter)

                self.set_do_overwrite_confirmation(True)


