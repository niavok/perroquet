# -*- coding: utf-8 -*-

# Copyright (C) 2009-2010 Frédéric Bertolus.
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
import time
import gettext
import thread
import textwrap
import logging

from perroquetlib.core import defaultLoggingHandler, defaultLoggingLevel
from perroquetlib.repository.exercise_repository_manager import ExerciseRepositoryManager
from perroquetlib.config import config
import perroquetlib

_ = gettext.gettext

class GuiExerciseManager:
    def __init__(self, core, parent):

        self.logger = logging.Logger("GuiExerciseManager")
        self.logger.setLevel(defaultLoggingLevel)
        self.logger.addHandler(defaultLoggingHandler)
        self.core = core
        self.config = config
        self.parent = parent

        self.builder = gtk.Builder()
        self.builder.set_translation_domain("perroquet")
        self.builder.add_from_file(self.config.get("ui_exercise_manager_path"))
        self.builder.connect_signals(self)
        self.dialog = self.builder.get_object("dialogExerciseManager")
        self.dialogDetails = self.builder.get_object("dialogDetails")
        self.labelStatus = self.builder.get_object("labelStatus")
        self.treeviewExercises = self.builder.get_object("treeviewExercises")
        self.treeviewRepositories = self.builder.get_object("treeviewRepositories")
        self.buttonAction = self.builder.get_object("buttonAction")

        self.dialog.set_modal(True)
        self.dialog.set_transient_for(self.parent)
        #self.dialog.set_functions (gtk.gdk.FUNC_RESIZE | gtk.gdk.FUNC_MOVE | gtk.gdk.FUNC_MINIMIZE |gtk.gdk.FUNC_MAXIMIZE)

        checkbuttonTreeViewMode = self.builder.get_object("checkbuttonTreeViewMode")
        checkbuttonTreeViewMode.props.active = (self.config.get("repositorymanager.displayonlyexercises") != 1)

        self.treeviewDetails = self.builder.get_object("treeviewDetails")

        self.selectedExo = None

    def run(self):
        self.load()
        self.dialog.run()
        self.dialog.destroy()
    def load(self):
        self.play_thread_id = thread.start_new_thread(self.update_exercise_list_thread, ())
        #Use the following line to debug crash in the thread
        #self.update_exercise_list_thread()

    def update_exercise_list_thread(self):


        self.labelStatus.set_text(_("Updating repositories..."))
        self.repositoryManager = ExerciseRepositoryManager()
        self._update_repository_tree_view()


        self.repositoryList = self.repositoryManager.get_exercise_repository_list()
        self._update_exercise_tree_view()

        self._update_details_tree_view()


    def _update_exercise_tree_view(self):
        self.treeStoreExercices = gtk.TreeStore(str,str, str, str, bool, object, str)

        displayOnlyExercises = (self.config.get("repositorymanager.displayonlyexercises") == 1)

        self.availableExoCount = 0
        self.installedExoCount = 0

        for repo in self.repositoryList:

            if not displayOnlyExercises:
                if repo.get_type() == "local":
                    type = _("Local repository")
                elif repo.get_type() == "distant":
                    type = _("Distant repository")
                elif repo.get_type() == "offline":
                    type = _("Offline repository")
                elif repo.get_type() == "orphan":
                    type = _("Orphan repository")
                else:
                    type = _("")

                desc = repo.get_description()
                desc = "<small>"+desc+"</small>"
                type = "<small>"+type+"</small>"
                name = "<b>"+ repo.get_name()+"</b>"
                iterRepo = self.treeStoreExercices.append(None,[name, type, desc , "", False, None,""])
            else:
                iterRepo = None

            for group in repo.get_groups():
                if not displayOnlyExercises:

                    desc = group.get_description()
                    desc = "<small>"+desc+"</small>"
                    name = "<b>"+ group.get_name()+"</b>"
                    iterGroup = self.treeStoreExercices.append(iterRepo,[name, _("<small>Group</small>"), desc , "", False, None,""])
                else:
                    iterGroup = None

                for exo in group.get_exercises():
                    descList = textwrap.wrap(exo.get_description(), 40)
                    desc = ""
                    for i, line in enumerate(descList):

                        desc += line
                        if i < len(descList)-1:
                            desc += "\n"

                    desc = "<small>"+desc+"</small>"

                    if exo.get_state() == "installed":
                        installStatus = _("Installed")
                        self.installedExoCount += 1
                    elif exo.get_state() == "available":
                        installStatus = _("Available")
                        self.availableExoCount += 1
                    elif exo.get_state() == "used":
                        installStatus = _("Used")
                        self.installedExoCount += 1
                    elif exo.get_state() == "done":
                        installStatus = _("Done")
                        self.installedExoCount += 1


                    name = "<b>"+ exo.get_name()+"</b>"

                    if exo.get_words_count() == 0:
                        words = "-"
                    else:
                        words = str(exo.get_words_count())

                    iter = self.treeStoreExercices.append(iterGroup,[name, _("<small>Exercise</small>"), desc, installStatus, True, exo, words])
                    exo.set_state_change_callback(self.exercice_state_change_listener, iter)


        cell = gtk.CellRendererText()
        pix = gtk.CellRendererPixbuf()

        treeviewcolumnName = gtk.TreeViewColumn(_("Name"))
        treeviewcolumnName.pack_start(cell, False)
        treeviewcolumnName.add_attribute(cell, 'markup', 0)
        treeviewcolumnName.set_expand(False)

        treeviewcolumnType = gtk.TreeViewColumn(_("Type"),)
        treeviewcolumnType.pack_start(cell, False)
        treeviewcolumnType.add_attribute(cell, 'markup', 1)
        treeviewcolumnType.set_expand(False)

        treeviewcolumnDescription = gtk.TreeViewColumn(_("Description"))
        treeviewcolumnDescription.pack_start(cell, True)
        treeviewcolumnDescription.add_attribute(cell, 'markup', 2)
        treeviewcolumnDescription.set_expand(True)

        treeviewcolumnStatus = gtk.TreeViewColumn(_("Status"))
        treeviewcolumnStatus.pack_start(cell, False)
        treeviewcolumnStatus.add_attribute(cell, 'markup', 3)
        treeviewcolumnStatus.set_expand(False)

        treeviewcolumnWordsCount = gtk.TreeViewColumn(_("Words count"))
        treeviewcolumnWordsCount.pack_start(cell, False)
        treeviewcolumnWordsCount.add_attribute(cell, 'markup', 6)
        treeviewcolumnWordsCount.set_expand(False)

        columns = self.treeviewExercises.get_columns()

        for column in columns:
            self.treeviewExercises.remove_column(column)

        if not displayOnlyExercises:
            self.treeviewExercises.append_column(treeviewcolumnType)
        self.treeviewExercises.append_column(treeviewcolumnName)
        self.treeviewExercises.append_column(treeviewcolumnDescription)

        if displayOnlyExercises:
            self.treeviewExercises.append_column(treeviewcolumnWordsCount)
        self.treeviewExercises.append_column(treeviewcolumnStatus)

        self.treeviewExercises.set_expander_column(treeviewcolumnName)



        self.treeviewExercises.set_model(self.treeStoreExercices)
        self.treeselectionExercises = self.treeviewExercises.get_selection()



        self._update_status()

    def _update_repository_tree_view(self):
        self.treeStoreRepository = gtk.TreeStore(str,str)

        personnalRepoList = self.repositoryManager.get_personal_exercise_repository_list()

        for repo in personnalRepoList:
            #self.treeStoreRepository.append(None,["<small>"+repo+"</small>", repo])
            self.treeStoreRepository.append(None,[repo, repo])


        cell = gtk.CellRendererText()

        treeviewcolumnPath = gtk.TreeViewColumn(_("Path"))
        treeviewcolumnPath.pack_start(cell, True)
        treeviewcolumnPath.add_attribute(cell, 'markup', 0)
        treeviewcolumnPath.set_expand(True)

        columns = self.treeviewRepositories.get_columns()

        for column in columns:
            self.treeviewRepositories.remove_column(column)

        self.treeviewRepositories.append_column(treeviewcolumnPath)


        self.treeviewRepositories.set_model(self.treeStoreRepository)
        self.treeselectionRepositories = self.treeviewRepositories.get_selection()

    def _update_details_tree_view(self):
        self.logger.debug("_update_details_tree_view")
        self.treeStoreDetails = gtk.TreeStore(str,str)

        #Clean old colomns
        columns = self.treeviewDetails.get_columns()

        for column in columns:
            self.treeviewDetails.remove_column(column)


        if self.selectedExo:
            exo = self.selectedExo
            if exo.get_state() == "installed":
                installStatus = _("Installed")
            elif exo.get_state() == "available":
                installStatus = _("Available")
            elif exo.get_state() == "used":
                installStatus = _("Used")
            elif exo.get_state() == "done":
                installStatus = _("Done")

            self.treeStoreDetails.append(None,["<b>"+_("Name")+"</b>",exo.get_name()])
            self.treeStoreDetails.append(None,["<b>"+_("Licence")+"</b>",exo.get_licence()])
            self.treeStoreDetails.append(None,["<b>"+_("Description")+"</b>",exo.get_description()])
            self.treeStoreDetails.append(None,["<b>"+_("Author")+"</b>",exo.get_author()])
            self.treeStoreDetails.append(None,["<b>"+_("Author website")+"</b>",exo.get_author_website()])
            self.treeStoreDetails.append(None,["<b>"+_("Author contact")+"</b>",exo.get_author_contact()])


            self.treeStoreDetails.append(None,["<b>"+_("Version")+"</b>",exo.get_version()])
            self.treeStoreDetails.append(None,["<b>"+_("Words count")+"</b>",exo.get_words_count()])
            self.treeStoreDetails.append(None,["<b>"+_("Language")+"</b>",exo.get_language()])
            self.treeStoreDetails.append(None,["<b>"+_("Media type")+"</b>",exo.get_media_type()])
            self.treeStoreDetails.append(None,["<b>"+_("Id")+"</b>",exo.get_id()])
            self.treeStoreDetails.append(None,["<b>"+_("Install status")+"</b>",installStatus])


            for translation in exo.get_translations_list():
                self.treeStoreDetails.append(None,["<b>"+_("Translation")+"</b>",translation])



            self.treeStoreDetails.append(None,["<b>"+_("Packager")+"</b>",exo.get_packager()])
            self.treeStoreDetails.append(None,["<b>"+_("Packager website")+"</b>",exo.get_packager_website()])
            self.treeStoreDetails.append(None,["<b>"+_("Packager contact")+"</b>",exo.get_packager_contact()])

            self.treeStoreDetails.append(None,["<b>"+_("Exercise path")+"</b>",exo.get_local_path()])
            self.treeStoreDetails.append(None,["<b>"+_("Package path")+"</b>",exo.get_file_path()])
            self.treeStoreDetails.append(None,["<b>"+_("Template path")+"</b>",exo.get_template_path()])
            self.treeStoreDetails.append(None,["<b>"+_("Instance path")+"</b>",exo.get_instance_path()])
            self.treeStoreDetails.append(None,["<b>"+_("Finished exercise  path")+"</b>",exo.get_done_path()])

        cell = gtk.CellRendererText()

        treeviewcolumnName = gtk.TreeViewColumn(_("Name"))
        treeviewcolumnName.pack_start(cell, False)
        treeviewcolumnName.add_attribute(cell, 'markup', 0)
        treeviewcolumnName.set_expand(False)

        treeviewcolumnValue = gtk.TreeViewColumn(_("Value"))
        treeviewcolumnValue.pack_start(cell, True)
        treeviewcolumnValue.add_attribute(cell, 'markup', 1)
        treeviewcolumnValue.set_expand(True)



        self.treeviewDetails.append_column(treeviewcolumnName)
        self.treeviewDetails.append_column(treeviewcolumnValue)


        self.treeviewDetails.set_model(self.treeStoreDetails)


    def on_treeview_exercises_cursor_changed(self,widget,data=None):

        (modele, iter) =  self.treeselectionExercises.get_selected()
        self.iterExo = iter
        if iter == None:
            return

        isExo, exo = modele.get(iter, 4, 5)

        if isExo:
            self.selectedExo = exo
        else:
            self.selectedExo = None

        self._update_action_button()
        self._update_details_tree_view()


    def _update_action_button(self):
        if self.selectedExo == None:
            self.buttonAction.set_sensitive(False)
            return

        exo = self.selectedExo

        if exo.get_state() == "available" or exo.get_state() == "corrupted" or exo.get_state() == "canceled":
            self.buttonAction.set_label(_("Install"))
            self.action = "install"
            self.buttonAction.set_sensitive(True)
        elif exo.get_state() == "downloading":
            self.buttonAction.set_label(_("Cancel install"))
            self.action = "cancel"
            self.buttonAction.set_sensitive(True)
        elif exo.get_state() == "installing":
            self.buttonAction.set_label(_("Cancel install"))
            self.action = "cancel"
            self.buttonAction.set_sensitive(False)
        elif exo.get_state() == "installed":
            self.buttonAction.set_label(_("Use"))
            self.action = "use"
            self.buttonAction.set_sensitive(True)
        elif exo.get_state() == "removing":
            self.buttonAction.set_label(_("Remove"))
            self.action = "remove"
            self.buttonAction.set_sensitive(False)
        elif exo.get_state() == "used":
            self.buttonAction.set_label(_("Continue"))
            self.action = "continue"
            self.buttonAction.set_sensitive(True)
        elif exo.get_state() == "done":
            self.buttonAction.set_label(_("Remove"))
            self.action = "remove"
            self.buttonAction.set_sensitive(True)

    def on_button_action_clicked(self,widget,data=None):
        self.logger.debug("on_buttonAction_activate")
        if self.action == "install":
            self._install_selected_exercise()
        elif self.action == "cancel":
            self._cancel_selected_exercise()
        elif self.action == "use":
            self._use_selected_exercise()
        elif self.action == "continue":
            self._continue_selected_exercise()


    def _install_selected_exercise(self):
        (exo,) = self.treeStoreExercices.get(self.iterExo, 5)
        exo.start_install()

    def _cancel_selected_exercise(self):
        (exo,) = self.treeStoreExercices.get(self.iterExo, 5)
        exo.cancel_install()

    def _use_selected_exercise(self):
        (exo,) = self.treeStoreExercices.get(self.iterExo, 5)
        self.core.load_exercise(exo.get_template_path())
        self.core.exercise.set_output_save_path(exo.get_instance_path())
        self.core.save()
        self.dialog.response(gtk.RESPONSE_OK)


    def _continue_selected_exercise(self):
        (exo,) = self.treeStoreExercices.get(self.iterExo, 5)
        self.core.load_exercise(exo.get_instance_path())
        self.dialog.response(gtk.RESPONSE_OK)


    def _update_status(self):
        if self.availableExoCount > 1:
            status = _("%d available exercises") % self.availableExoCount
        else:
            status = _("%d available exercise") % self.availableExoCount


        if self.installedExoCount > 1:
            status += _(" and %d installed exercises") % self.installedExoCount
        else:
            status += _(" and %d installed exercise") % self.installedExoCount


        self.labelStatus.set_text(status)

    def exercice_state_change_listener(self, oldState, iter):
        (exo,) = self.treeStoreExercices.get(iter, 5)
        if oldState == "installed" and exo.get_state() != "installed":
            self.availableExoCount += 1
            self.installedExoCount -= 1
        elif oldState != "installed" and exo.get_state() == "installed":
            self.availableExoCount -= 1
            self.installedExoCount += 1

        if exo.get_state() == "available":
            self.treeStoreExercices.set_value(iter, 3, _("Available"))
        elif exo.get_state() == "downloading":
            self.treeStoreExercices.set_value(iter, 3, _("Downloading"))
            thread.start_new_thread(self._download_exercise_thread, (iter, ))
        elif exo.get_state() == "installing":
            self.treeStoreExercices.set_value(iter, 3, _("Installing"))
        elif exo.get_state() == "installed":
            self.treeStoreExercices.set_value(iter, 3, _("Installed"))
        elif exo.get_state() == "corrupted":
            self.treeStoreExercices.set_value(iter, 3, _("Corrupted"))
        elif exo.get_state() == "canceled":
            self.treeStoreExercices.set_value(iter, 3, _("Canceled"))
        elif exo.get_state() == "removing":
            self.treeStoreExercices.set_value(iter, 3, _("Removing"))
        elif exo.get_state() == "used":
            self.treeStoreExercices.set_value(iter, 3, _("Used"))
        elif exo.get_state() == "done":
            self.treeStoreExercices.set_value(iter, 3, _("Done"))

        self._update_status()
        self._update_action_button()

    def _download_exercise_thread(self, iter):
        (exo,) = self.treeStoreExercices.get(iter, 5)
        while exo.get_state() == "downloading":
            self.treeStoreExercices.set_value(iter, 3, _("<small>Downloading ... %d%%</small>") % exo.get_download_percent())
            time.sleep(0.5)


    def on_checkbutton_tree_view_mode_toggled(self, widget, data=None):
        checkbuttonTreeViewMode = self.builder.get_object("checkbuttonTreeViewMode")
        if checkbuttonTreeViewMode.props.active:
            self.config.set("repositorymanager.displayonlyexercises",0)
        else:
            self.config.set("repositorymanager.displayonlyexercises",1)
        self._update_exercise_tree_view()


    def on_button_add_repo_clicked(self, widget, data=None):
        personnalRepoList = self.repositoryManager.get_personal_exercise_repository_list()
        personnalRepoList.append(self.builder.get_object("entryNewRepo").get_text())
        self.builder.get_object("entryNewRepo").set_text("")
        self.repositoryManager.write_personal_exercise_repository_list(personnalRepoList)
        self.load()

    def on_button_delete_repo_clicked(self, widget, data=None):
        personnalRepoList = self.repositoryManager.get_personal_exercise_repository_list()
        personnalRepoList.remove(self.builder.get_object("entryNewRepo").get_text())
        self.builder.get_object("entryNewRepo").set_text("")
        self.repositoryManager.write_personal_exercise_repository_list(personnalRepoList)
        self.load()

    def on_treeview_repositories_cursor_changed(self,widget,data=None):

        (modele, iter) =  self.treeselectionRepositories.get_selected()
        if iter == None:
            return
        (repo,) = self.treeStoreRepository.get(iter, 0)
        self.builder.get_object("entryNewRepo").set_text(repo)

    def on_expander_details_activate(self,widget,data=None):
        if self.builder.get_object("box1").get_homogeneous():
            self.builder.get_object("box1").set_homogeneous(False)
        else:
            self.builder.get_object("box1").set_homogeneous(True)
