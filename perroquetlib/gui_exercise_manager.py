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

        self.dialog.set_modal(True)
        self.dialog.set_transient_for(self.parent)



    def Run(self):
        self.Load()
        self.dialog.run()
        self.dialog.destroy()
    def Load(self):
        print "Load"
        #self.play_thread_id = thread.start_new_thread(self.UpdateExerciseListThread, ())
        self.UpdateExerciseListThread()
    def UpdateExerciseListThread(self):
        self.labelStatus.set_text(_("Updating repositories..."))
        self.repositoryManager = ExerciseRepositoryManager()
        print "Get repository list"
        self.repositoryList = self.repositoryManager.getExerciseRepositoryList()
        print "get repository list"

        self.treeStoreExercices = gtk.TreeStore(str,str, str, str)

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

            iterRepo = self.treeStoreExercices.append(None,[repo.getName(), type, repo.getDescription(), ""])

            for group in repo.getGroups():
                iterGroup = self.treeStoreExercices.append(iterRepo,[group.getName(), _("Group"), group.getDescription(), ""])

                for exo in group.getExercises():
                    descList = textwrap.wrap(exo.getDescription())
                    desc = ""
                    for i, line in enumerate(descList):

                        desc += line
                        if i < len(descList)-1:
                            desc += "\n"


                    if exo.isInstalled():
                        installStatus = _("Installed")
                    else:
                        installStatus = _("Available")

                    self.treeStoreExercices.append(iterGroup,[exo.getName(), _("Exercise"), desc, installStatus])


        cell = gtk.CellRendererText()

        treeviewcolumnName = gtk.TreeViewColumn(_("Name"))
        treeviewcolumnName.pack_start(cell, False)
        treeviewcolumnName.add_attribute(cell, 'text', 0)

        treeviewcolumnType = gtk.TreeViewColumn(_("Type"),)
        treeviewcolumnType.pack_start(cell, False)
        treeviewcolumnType.add_attribute(cell, 'text', 1)

        treeviewcolumnDescription = gtk.TreeViewColumn(_("Description"))
        treeviewcolumnDescription.pack_start(cell, True)
        treeviewcolumnDescription.add_attribute(cell, 'markup', 2)

        treeviewcolumnStatus = gtk.TreeViewColumn(_("Status"))
        treeviewcolumnStatus.pack_start(cell, False)
        treeviewcolumnStatus.add_attribute(cell, 'text', 3)




        self.treeviewExercises.append_column(treeviewcolumnName)
        self.treeviewExercises.append_column(treeviewcolumnType)
        self.treeviewExercises.append_column(treeviewcolumnDescription)
        self.treeviewExercises.append_column(treeviewcolumnStatus)


        self.treeviewExercises.set_model(self.treeStoreExercices)


        self.labelStatus.set_text(_("Ready"))



    def on_buttonExercisePropOk_clicked(self,widget,data=None):

       self.dialog.response(gtk.RESPONSE_OK)

    def on_buttonExercisePropCancel_clicked(self,widget,data=None):
        self.dialog.response(gtk.RESPONSE_CANCEL)
