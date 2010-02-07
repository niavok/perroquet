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
        print "Load"
        self.play_thread_id = thread.start_new_thread(self.UpdateExerciseListThread, ())
        #self.UpdateExerciseListThread()
    def UpdateExerciseListThread(self):
        self.labelStatus.set_text(_("Updating repositories..."))
        self.repositoryManager = ExerciseRepositoryManager()
        print "Get repository list"
        self.repositoryList = self.repositoryManager.getExerciseRepositoryList()
        print "get repository list"

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



                    self.treeStoreExercices.append(iterGroup,[name, _("<small>Exercise</small>"), desc, installStatus, True, exo])


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
        print "on_treeviewExercises_cursor_changed"

        (modele, iter) =  self.treeselectionExercises.get_selected()
        self.iterExo = iter
        if iter == None:
            return

        isExo, exo = modele.get(iter, 4, 5)

        if isExo:
            self.selectedExo = exo
            self.buttonAction.set_sensitive(True)
            if exo.isInstalling():
                self.buttonAction.set_label(_("Cancel install"))
                self.action = "cancel"
            elif exo.isInstalled():
                self.buttonAction.set_label(_("Use"))
                self.action = "use"
            else:
                self.buttonAction.set_label(_("Install"))
                self.action = "install"

            print "is exo selected"
        else:
            print "is not exo selected"
            self.buttonAction.set_sensitive(False)
            self.selectedExo = None
            self.action = "none"

    def on_buttonAction_clicked(self,widget,data=None):
        print "on_buttonAction_activate"
        if self.action == "install":
            self._installSelectedExercise()

    def _installSelectedExercise(self):

        idThread = thread.start_new_thread(self._installSelectedExerciseThread, (self.iterExo, ))
        #self._installSelectedExerciseThread(self.iterExo)

    def _installSelectedExerciseThread(self, iter):
        (exo,) = self.treeStoreExercices.get(iter, 5)
        print "start install"
        exo.startInstall()
        self.on_treeviewExercises_cursor_changed(None)
        print "set label to downlowding"
        self.treeStoreExercices.set_value(iter, 3, _("<small>Downloading ... %d%%</small>") % exo.getDownloadPercent() )
        print "wait download end"
        while exo.isDownloading():
            self.treeStoreExercices.set_value(iter, 3, _("<small>Downloading ... %d%%</small>") % exo.getDownloadPercent())
            time.sleep(0.5)
        print "download end"
        self.treeStoreExercices.set_value(iter, 3, _("Installing ... "))
        exo.waitInstallEnd()
        if exo.isInstalled():
            self.treeStoreExercices.set_value(iter, 3, _("Installed"))
        else:
            self.treeStoreExercices.set_value(iter, 3, _("Corrupted"))
        self.on_treeviewExercises_cursor_changed(None)
        print "isntall end"
        self.availableExoCount -= 1
        self.installedExoCount += 1
        self._updateStatus()

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


