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
from perroquetlib.exercise_repository_manager import *
from perroquetlib.config import Config
_ = gettext.gettext

class GuiExerciseManager:
    def __init__(self, core, parent):

        self.core = core
        self.config = Config()
        self.parent = parent

        self.builder = gtk.Builder()
        self.builder.set_translation_domain("perroquet")
        self.builder.add_from_file(self.config.Get("ui_exercise_manager_path"))
        self.builder.connect_signals(self)
        self.dialog = self.builder.get_object("dialogExerciseManager")
        self.labelStatus = self.builder.get_object("labelStatus")
        self.treeviewExercises = self.builder.get_object("treeviewExercises")
        self.buttonAction = self.builder.get_object("buttonAction")

        self.dialog.set_modal(True)
        self.dialog.set_transient_for(self.parent)
        #self.dialog.set_functions (gtk.gdk.FUNC_RESIZE | gtk.gdk.FUNC_MOVE | gtk.gdk.FUNC_MINIMIZE |gtk.gdk.FUNC_MAXIMIZE)



    def Run(self):
        self.Load()
        self.dialog.run()
        self.dialog.destroy()
    def Load(self):
        self.play_thread_id = thread.start_new_thread(self.UpdateExerciseListThread, ())
        
    def UpdateExerciseListThread(self):
        self.labelStatus.set_text(_("Updating repositories..."))
        self.repositoryManager = ExerciseRepositoryManager()
        self.repositoryList = self.repositoryManager.getExerciseRepositoryList()
        
        self.treeStoreExercices = gtk.TreeStore(str,str, str, str, bool, object)

        self.availableExoCount = 0
        self.installedExoCount = 0

        for repo in self.repositoryList:

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
            iterRepo = self.treeStoreExercices.append(None,[name, type, desc , "", False, None])

            for group in repo.getGroups():
                desc = group.getDescription()
                desc = "<small>"+desc+"</small>"
                name = "<b>"+ group.getName()+"</b>"
                iterGroup = self.treeStoreExercices.append(iterRepo,[name, _("<small>Group</small>"), desc , "", False, None])

                for exo in group.getExercises():
                    descList = textwrap.wrap(exo.getDescription(), 40)
                    desc = ""
                    for i, line in enumerate(descList):

                        desc += line
                        if i < len(descList)-1:
                            desc += "\n"

                    desc = "<small>"+desc+"</small>"

                    if exo.isInstalled():
                        installStatus = _("Installed")
                        self.installedExoCount += 1
                    else:
                        installStatus = _("Available")
                        self.availableExoCount += 1

                    name = "<b>"+ exo.getName()+"</b>"



                    iter = self.treeStoreExercices.append(iterGroup,[name, _("<small>Exercise</small>"), desc, installStatus, True, exo])
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

        self.treeviewExercises.append_column(treeviewcolumnType)
        self.treeviewExercises.append_column(treeviewcolumnName)
        self.treeviewExercises.append_column(treeviewcolumnDescription)
        self.treeviewExercises.append_column(treeviewcolumnStatus)

        self.treeviewExercises.set_expander_column(treeviewcolumnName)



        self.treeviewExercises.set_model(self.treeStoreExercices)
        self.treeselectionExercises = self.treeviewExercises.get_selection()



        self._updateStatus()


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
        print "_installSelectedExerciseThread"
        while exo.getState() == "downloading":
            print " while exo.getState() == downloading:"
            self.treeStoreExercices.set_value(iter, 3, _("<small>Downloading ... %d%%</small>") % exo.getDownloadPercent())
            time.sleep(0.5)



