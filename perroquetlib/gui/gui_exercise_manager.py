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


import gtk, time, urllib, re, os, gettext
import locale, thread, textwrap

from perroquetlib.repository.exercise_repository_manager import ExerciseRepositoryManager
from perroquetlib.config import config

_ = gettext.gettext

class GuiExerciseManager:
    def __init__(self, core, parent):

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

    def Run(self):
        self.Load()
        self.dialog.run()
        self.dialog.destroy()
    def Load(self):
        self.play_thread_id = thread.start_new_thread(self.UpdateExerciseListThread, ())
        #self.UpdateExerciseListThread()

    def UpdateExerciseListThread(self):


        self.labelStatus.set_text(_("Updating repositories..."))
        self.repositoryManager = ExerciseRepositoryManager()
        self._updateRepositoryTreeView()


        self.repositoryList = self.repositoryManager.getExerciseRepositoryList()
        self._updateExerciseTreeView()

        self._updateDetailsTreeView()


    def _updateExerciseTreeView(self):
        self.treeStoreExercices = gtk.TreeStore(str,str, str, str, bool, object, str)

        displayOnlyExercises = (self.config.get("repositorymanager.displayonlyexercises") == 1)

        self.availableExoCount = 0
        self.installedExoCount = 0

        for repo in self.repositoryList:

            if not displayOnlyExercises:
                if repo.getType() == "local":
                    type = _("Local repository")
                elif repo.getType() == "distant":
                    type = _("Distant repository")
                elif repo.getType() == "offline":
                    type = _("Offline repository")
                elif repo.getType() == "orphan":
                    type = _("Orphan repository")
                else:
                    type = _("")

                desc = repo.getDescription()
                desc = "<small>"+desc+"</small>"
                type = "<small>"+type+"</small>"
                name = "<b>"+ repo.getName()+"</b>"
                iterRepo = self.treeStoreExercices.append(None,[name, type, desc , "", False, None,""])
            else:
                iterRepo = None

            for group in repo.getGroups():
                if not displayOnlyExercises:

                    desc = group.getDescription()
                    desc = "<small>"+desc+"</small>"
                    name = "<b>"+ group.getName()+"</b>"
                    iterGroup = self.treeStoreExercices.append(iterRepo,[name, _("<small>Group</small>"), desc , "", False, None,""])
                else:
                    iterGroup = None

                for exo in group.getExercises():
                    descList = textwrap.wrap(exo.getDescription(), 40)
                    desc = ""
                    for i, line in enumerate(descList):

                        desc += line
                        if i < len(descList)-1:
                            desc += "\n"

                    desc = "<small>"+desc+"</small>"

                    if exo.getState() == "installed":
                        installStatus = _("Installed")
                        self.installedExoCount += 1
                    elif exo.getState() == "available":
                        installStatus = _("Available")
                        self.availableExoCount += 1
                    elif exo.getState() == "used":
                        installStatus = _("Used")
                        self.installedExoCount += 1
                    elif exo.getState() == "done":
                        installStatus = _("Done")
                        self.installedExoCount += 1


                    name = "<b>"+ exo.getName()+"</b>"

                    if exo.getWordsCount() == 0:
                        words = "-"
                    else:
                        words = str(exo.getWordsCount())

                    iter = self.treeStoreExercices.append(iterGroup,[name, _("<small>Exercise</small>"), desc, installStatus, True, exo, words])
                    exo.setStateChangeCallback(self.exerciceStateChangeListener, iter)


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



        self._updateStatus()

    def _updateRepositoryTreeView(self):
        self.treeStoreRepository = gtk.TreeStore(str,str)

        personnalRepoList = self.repositoryManager.getPersonalExerciseRepositoryList()

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

    def _updateDetailsTreeView(self):
        print "_updateDetailsTreeView"
        self.treeStoreDetails = gtk.TreeStore(str,str)

        #Clean old colomns
        columns = self.treeviewDetails.get_columns()

        for column in columns:
            self.treeviewDetails.remove_column(column)


        if self.selectedExo:
            exo = self.selectedExo
            if exo.getState() == "installed":
                installStatus = _("Installed")
            elif exo.getState() == "available":
                installStatus = _("Available")
            elif exo.getState() == "used":
                installStatus = _("Used")
            elif exo.getState() == "done":
                installStatus = _("Done")

            self.treeStoreDetails.append(None,["<b>"+_("Name")+"</b>",exo.getName()])
            self.treeStoreDetails.append(None,["<b>"+_("Licence")+"</b>",exo.getLicence()])
            self.treeStoreDetails.append(None,["<b>"+_("Description")+"</b>",exo.getDescription()])
            self.treeStoreDetails.append(None,["<b>"+_("Author")+"</b>",exo.getAuthor()])
            self.treeStoreDetails.append(None,["<b>"+_("Author website")+"</b>",exo.getAuthorWebsite()])
            self.treeStoreDetails.append(None,["<b>"+_("Author contact")+"</b>",exo.getAuthorContact()])


            self.treeStoreDetails.append(None,["<b>"+_("Version")+"</b>",exo.getVersion()])
            self.treeStoreDetails.append(None,["<b>"+_("Words count")+"</b>",exo.getWordsCount()])
            self.treeStoreDetails.append(None,["<b>"+_("Language")+"</b>",exo.getLanguage()])
            self.treeStoreDetails.append(None,["<b>"+_("Media type")+"</b>",exo.getMediaType()])
            self.treeStoreDetails.append(None,["<b>"+_("Id")+"</b>",exo.getId()])
            self.treeStoreDetails.append(None,["<b>"+_("Install status")+"</b>",installStatus])


            for translation in exo.getTranslationsList():
                self.treeStoreDetails.append(None,["<b>"+_("Translation")+"</b>",translation])



            self.treeStoreDetails.append(None,["<b>"+_("Packager")+"</b>",exo.getPackager()])
            self.treeStoreDetails.append(None,["<b>"+_("Packager website")+"</b>",exo.getPackagerWebsite()])
            self.treeStoreDetails.append(None,["<b>"+_("Packager contact")+"</b>",exo.getPackagerContact()])

            self.treeStoreDetails.append(None,["<b>"+_("Exercise path")+"</b>",exo.getLocalPath()])
            self.treeStoreDetails.append(None,["<b>"+_("Package path")+"</b>",exo.getFilePath()])
            self.treeStoreDetails.append(None,["<b>"+_("Template path")+"</b>",exo.getTemplatePath()])
            self.treeStoreDetails.append(None,["<b>"+_("Instance path")+"</b>",exo.getInstancePath()])
            self.treeStoreDetails.append(None,["<b>"+_("Done path")+"</b>",exo.getDonePath()])

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


    def on_treeviewExercises_cursor_changed(self,widget,data=None):

        (modele, iter) =  self.treeselectionExercises.get_selected()
        self.iterExo = iter
        if iter == None:
            return

        isExo, exo = modele.get(iter, 4, 5)

        if isExo:
            self.selectedExo = exo
        else:
            self.selectedExo = None

        self._updateActionButton()
        self._updateDetailsTreeView()


    def _updateActionButton(self):
        if self.selectedExo == None:
            self.buttonAction.set_sensitive(False)
            return

        exo = self.selectedExo

        if exo.getState() == "available" or exo.getState() == "corrupted" or exo.getState() == "canceled":
            self.buttonAction.set_label(_("Install"))
            self.action = "install"
            self.buttonAction.set_sensitive(True)
        elif exo.getState() == "downloading":
            self.buttonAction.set_label(_("Cancel install"))
            self.action = "cancel"
            self.buttonAction.set_sensitive(True)
        elif exo.getState() == "installing":
            self.buttonAction.set_label(_("Cancel install"))
            self.action = "cancel"
            self.buttonAction.set_sensitive(False)
        elif exo.getState() == "installed":
            self.buttonAction.set_label(_("Use"))
            self.action = "use"
            self.buttonAction.set_sensitive(True)
        elif exo.getState() == "removing":
            self.buttonAction.set_label(_("Remove"))
            self.action = "remove"
            self.buttonAction.set_sensitive(False)
        elif exo.getState() == "used":
            self.buttonAction.set_label(_("Continue"))
            self.action = "continue"
            self.buttonAction.set_sensitive(True)
        elif exo.getState() == "done":
            self.buttonAction.set_label(_("Remove"))
            self.action = "remove"
            self.buttonAction.set_sensitive(True)

    def on_buttonAction_clicked(self,widget,data=None):
        print "on_buttonAction_activate"
        if self.action == "install":
            self._installSelectedExercise()
        elif self.action == "cancel":
            self._cancelSelectedExercise()
        elif self.action == "use":
            self._useSelectedExercise()
        elif self.action == "continue":
            self._continueSelectedExercise()


    def _installSelectedExercise(self):
        (exo,) = self.treeStoreExercices.get(self.iterExo, 5)
        exo.startInstall()

    def _cancelSelectedExercise(self):
        (exo,) = self.treeStoreExercices.get(self.iterExo, 5)
        exo.cancelInstall()

    def _useSelectedExercise(self):
        (exo,) = self.treeStoreExercices.get(self.iterExo, 5)
        self.core.LoadExercise(exo.getTemplatePath())
        self.core.exercise.setOutputSavePath(exo.getInstancePath())
        self.core.Save()
        self.dialog.response(gtk.RESPONSE_OK)


    def _continueSelectedExercise(self):
        (exo,) = self.treeStoreExercices.get(self.iterExo, 5)
        self.core.LoadExercise(exo.getInstancePath())
        self.dialog.response(gtk.RESPONSE_OK)


    def _updateStatus(self):
        if self.availableExoCount > 1:
            status = _("%d available exercises") % self.availableExoCount
        else:
            status = _("%d available exercise") % self.availableExoCount


        if self.installedExoCount > 1:
            status += _(" and %d installed exercises") % self.installedExoCount
        else:
            status += _(" and %d installed exercise") % self.installedExoCount


        self.labelStatus.set_text(status)

    def exerciceStateChangeListener(self, oldState, iter):
        (exo,) = self.treeStoreExercices.get(iter, 5)
        if oldState == "installed" and exo.getState() != "installed":
            self.availableExoCount += 1
            self.installedExoCount -= 1
        elif oldState != "installed" and exo.getState() == "installed":
            self.availableExoCount -= 1
            self.installedExoCount += 1

        if exo.getState() == "available":
            self.treeStoreExercices.set_value(iter, 3, _("Available"))
        elif exo.getState() == "downloading":
            self.treeStoreExercices.set_value(iter, 3, _("Downloading"))
            thread.start_new_thread(self._downloadExerciseThread, (iter, ))
        elif exo.getState() == "installing":
            self.treeStoreExercices.set_value(iter, 3, _("Installing"))
        elif exo.getState() == "installed":
            self.treeStoreExercices.set_value(iter, 3, _("Installed"))
        elif exo.getState() == "corrupted":
            self.treeStoreExercices.set_value(iter, 3, _("Corrupted"))
        elif exo.getState() == "canceled":
            self.treeStoreExercices.set_value(iter, 3, _("Canceled"))
        elif exo.getState() == "removing":
            self.treeStoreExercices.set_value(iter, 3, _("Removing"))
        elif exo.getState() == "used":
            self.treeStoreExercices.set_value(iter, 3, _("Used"))
        elif exo.getState() == "done":
            self.treeStoreExercices.set_value(iter, 3, _("Done"))

        self._updateStatus()
        self._updateActionButton()

    def _downloadExerciseThread(self, iter):
        (exo,) = self.treeStoreExercices.get(iter, 5)
        while exo.getState() == "downloading":
            self.treeStoreExercices.set_value(iter, 3, _("<small>Downloading ... %d%%</small>") % exo.getDownloadPercent())
            time.sleep(0.5)


    def on_checkbuttonTreeViewMode_toggled(self, widget, data=None):
        checkbuttonTreeViewMode = self.builder.get_object("checkbuttonTreeViewMode")
        if checkbuttonTreeViewMode.props.active:
            self.config.set("repositorymanager.displayonlyexercises",0)
        else:
            self.config.set("repositorymanager.displayonlyexercises",1)
        self._updateExerciseTreeView()


    def on_buttonAddRepo_clicked(self, widget, data=None):
        personnalRepoList = self.repositoryManager.getPersonalExerciseRepositoryList()
        personnalRepoList.append(self.builder.get_object("entryNewRepo").get_text())
        self.builder.get_object("entryNewRepo").set_text("")
        self.repositoryManager.writePersonalExerciseRepositoryList(personnalRepoList)
        self.Load()

    def on_buttonDeleteRepo_clicked(self, widget, data=None):
        personnalRepoList = self.repositoryManager.getPersonalExerciseRepositoryList()
        personnalRepoList.remove(self.builder.get_object("entryNewRepo").get_text())
        self.builder.get_object("entryNewRepo").set_text("")
        self.repositoryManager.writePersonalExerciseRepositoryList(personnalRepoList)
        self.Load()

    def on_treeviewRepositories_cursor_changed(self,widget,data=None):

        (modele, iter) =  self.treeselectionRepositories.get_selected()
        if iter == None:
            return
        (repo,) = self.treeStoreRepository.get(iter, 0)
        self.builder.get_object("entryNewRepo").set_text(repo)

    def on_expanderDetails_activate(self,widget,data=None):
        if self.builder.get_object("box1").get_homogeneous():
            self.builder.get_object("box1").set_homogeneous(False)
        else:
            self.builder.get_object("box1").set_homogeneous(True)
