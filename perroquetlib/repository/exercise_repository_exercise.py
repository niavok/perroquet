#! /usr/bin/python
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Perroquet.  If not, see <http://www.gnu.org/licenses/>.

import thread
import urllib2
import tempfile
import os
import tarfile
import errno
import gettext
import logging
from xml.dom.minidom import getDOMImplementation, parse
from threading import Lock
from perroquetlib.core import defaultLoggingHandler, defaultLoggingLevel

class ExerciseRepositoryExercise:
    def __init__(self):
        self.id ="no-id"
        self.name ="No name"
        self.description = ""
        self.mutexInstalling = Lock()
        self.downloadPercent = 0
        self.state = "none"
        self.wordsCount = 0
        self.translationList = []
        self.version = None
        self.logger = logging.Logger("ExerciseRepositoryExercise")
        self.logger.setLevel(defaultLoggingLevel)
        self.logger.addHandler(defaultLoggingHandler)

    def is_installed(self):
        return os.path.isfile(self.get_template_path())

    def is_used(self):
        return os.path.isfile(self.get_instance_path())

    def is_done(self):
        return os.path.isfile(self.get_done_path())


    def start_install(self):
        self.mutexInstalling.acquire()
        self.canceled = False
        self.downloadPercent = 0
        self.play_thread_id = thread.start_new_thread(self.install_thread, ())

    def cancel_install(self):
        self.canceled = True

    def wait_install_end(self):
        self.mutexInstalling.acquire()
        self.mutexInstalling.release()

    def download(self):

        f=urllib2.urlopen(self.get_file_path())
        _, tempPath = tempfile.mkstemp("","perroquet-");
        wf = open(tempPath, 'w+b')
        size = f.info().get('Content-Length')
        if size is None:
            size = 0
        else:
            size = int(size)
        count=0
        sizeToRead = 50000
        while not self.canceled:
            data=f.read(sizeToRead)
            wf.write(data)
            if len(data) != sizeToRead:
                break;
            count+=sizeToRead
            self.downloadPercent =  (round((float(count)/float(size))*100))

        self.downloading = False
        return tempPath


    def get_download_percent(self):
        return self.downloadPercent

    def get_state(self):
        #available
        #downloading
        #installing
        #installed
        #corrupted
        #canceled
        #removing
        #used
        #done

        if self.state == "none":
            if self.is_done():
                self.state = "done"
            elif self.is_used():
                self.state = "used"
            elif self.is_installed():
                self.state = "installed"
            else:
                self.state = "available"

        return self.state

    def set_state(self, state):
        oldState = self.state
        self.state = state
        self.notifyStateChange(oldState, self.callbackData)

    def set_state_change_callback(self, callback, callbackData):
        self.notifyStateChange = callback
        self.callbackData = callbackData

    def install_thread(self):
        self.set_state("downloading")
        tmpPath = self.download()
        if self.canceled:
            self.logger.info("remove temp file")
            self.set_state("canceled")
            os.remove(tmpPath)
        else:
            self.set_state("installing")
            tar = tarfile.open(tmpPath)
            outPath = self.get_local_path()
            try:
                os.makedirs(outPath)
            except OSError, (ErrorNumber, ErrorMessage): # Python <=2.5
                if ErrorNumber == errno.EEXIST:
                    pass
                else: raise
            tar.extractall(outPath)
            tar.close()
            os.remove(tmpPath)
            if self.is_installed():
                self.set_state("installed")
            else:
                self.set_state("corrupted")
        self.mutexInstalling.release()

    def get_template_path(self):
        return os.path.join(self.get_local_path(),"template.perroquet")

    def get_instance_path(self):
        return os.path.join(self.get_local_path(),"instance.perroquet")

    def get_done_path(self):
        return os.path.join(self.get_local_path(),"done.perroquet")

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def set_id(self, id):
        self.id = id

    def get_id(self):
        return self.id

    def set_description(self, description):
        self.description = description

    def get_description(self):
        return self.description

    def set_licence(self, licence):
        self.licence = licence

    def get_licence(self):
        return self.licence

    def set_language(self, language):
        self.language = language

    def get_language(self):
        return self.language

    def set_media_type(self, mediaType):
        self.mediaType = mediaType

    def get_media_type(self):
        return self.mediaType

    def set_version(self, version):
        self.version = version

    def get_version(self):
        return self.version

    def set_author(self, author):
        self.author = author

    def get_author(self):
        return self.author

    def set_words_count(self, wordsCount):
        self.wordsCount = wordsCount

    def get_words_count(self):
        return self.wordsCount

    def set_author_website(self, authorWebsite):
        self.authorWebsite = authorWebsite

    def get_author_website(self):
        return self.authorWebsite

    def set_author_contact(self, authorContact):
        self.authorContact = authorContact

    def get_author_contact(self):
        return self.authorContact

    def set_packager(self, packager):
        self.packager = packager

    def get_packager(self):
        return self.packager

    def set_packager_website(self, packagerWebsite):
        self.packagerWebsite = packagerWebsite

    def get_packager_website(self):
        return self.packagerWebsite

    def set_packager_contact(self, packagerContact):
        self.packagerContact = packagerContact

    def get_packager_contact(self):
        return self.packagerContact

    def set_file_path(self, filePath):
        self.filePath = filePath

    def get_file_path(self):
        return self.filePath

    def set_translations_list(self, translationList):
        self.translationList = translationList

    def get_translations_list(self):
        return self.translationList

    def set_parent(self,parent):
        self.parent = parent

    def get_local_path(self):
        if self.version is not None:
            return os.path.join(self.parent.get_local_path(), self.id+"_"+self.version)
        else:
            return os.path.join(self.parent.get_local_path(), self.id)

    def parse_description(self,xml_exercise):
        self.set_name(self._get_text(xml_exercise.getElementsByTagName("name")[0].childNodes))
        self.set_id(self._get_text(xml_exercise.getElementsByTagName("id")[0].childNodes))
        self.set_description(self._get_text(xml_exercise.getElementsByTagName("description")[0].childNodes))
        self.set_licence(self._get_text(xml_exercise.getElementsByTagName("licence")[0].childNodes))
        self.set_language(self._get_text(xml_exercise.getElementsByTagName("language")[0].childNodes))
        self.set_media_type(self._get_text(xml_exercise.getElementsByTagName("media_type")[0].childNodes))
        self.set_version(self._get_text(xml_exercise.getElementsByTagName("exercise_version")[0].childNodes))
        self.set_author(self._get_text(xml_exercise.getElementsByTagName("author")[0].childNodes))
        self.set_author_website(self._get_text(xml_exercise.getElementsByTagName("author_website")[0].childNodes))
        self.set_author_contact(self._get_text(xml_exercise.getElementsByTagName("author_contact")[0].childNodes))
        self.set_packager(self._get_text(xml_exercise.getElementsByTagName("packager")[0].childNodes))
        self.set_packager_website(self._get_text(xml_exercise.getElementsByTagName("packager_website")[0].childNodes))
        self.set_packager_contact(self._get_text(xml_exercise.getElementsByTagName("packager_contact")[0].childNodes))
        if len(xml_exercise.getElementsByTagName("words_count")) > 0:
            self.set_words_count(self._get_text(xml_exercise.getElementsByTagName("words_count")[0].childNodes))
        if len(xml_exercise.getElementsByTagName("file")) > 0:
            self.set_file_path(self._get_text(xml_exercise.getElementsByTagName("file")[0].childNodes))

        if len(xml_exercise.getElementsByTagName("translations")) > 0:
            xml_translations = xml_exercise.getElementsByTagName("translations")[0]
            translationList = []
            for xml_translation in xml_translations.getElementsByTagName("translation"):
                translationList.append(self._get_text(xml_translation.childNodes))

            self.set_translations_list(translationList)

    def generate_description(self):
        self._generate_description()

    def _generate_description(self):

        if not os.path.isdir(self.get_local_path()):
            try:
                os.makedirs(self.get_local_path())
            except OSError, (ErrorNumber, ErrorMessage): # Python <=2.5
                if ErrorNumber == 666: #EEXIST ???
                    pass
                else: raise

        impl = getDOMImplementation()

        newdoc = impl.createDocument(None, "perroquet_exercise", None)
        root_element = newdoc.documentElement

        # Name
        xml_name = newdoc.createElement("name")
        xml_name.appendChild(newdoc.createTextNode(self.get_name()))
        root_element.appendChild(xml_name)

        # Id
        xml_id = newdoc.createElement("id")
        xml_id.appendChild(newdoc.createTextNode(self.get_id()))
        root_element.appendChild(xml_id)

        # Description
        xml_description = newdoc.createElement("description")
        xml_description.appendChild(newdoc.createTextNode(self.get_description()))
        root_element.appendChild(xml_description)

        # Words count
        xml_version = newdoc.createElement("words_count")
        xml_version.appendChild(newdoc.createTextNode(str(self.get_words_count())))
        root_element.appendChild(xml_version)

        # Version
        xml_version = newdoc.createElement("exercise_version")
        xml_version.appendChild(newdoc.createTextNode(self.get_version()))
        root_element.appendChild(xml_version)

        # Licence
        xml_node = newdoc.createElement("licence")
        xml_node.appendChild(newdoc.createTextNode(self.get_licence()))
        root_element.appendChild(xml_node)

        # Language
        xml_node = newdoc.createElement("language")
        xml_node.appendChild(newdoc.createTextNode(self.get_language()))
        root_element.appendChild(xml_node)

        # Media type
        xml_node = newdoc.createElement("media_type")
        xml_node.appendChild(newdoc.createTextNode(self.get_media_type()))
        root_element.appendChild(xml_node)

        # author
        xml_node = newdoc.createElement("author")
        xml_node.appendChild(newdoc.createTextNode(self.get_author()))
        root_element.appendChild(xml_node)

        # author website
        xml_node = newdoc.createElement("author_website")
        xml_node.appendChild(newdoc.createTextNode(self.get_author_website()))
        root_element.appendChild(xml_node)

        # author contact
        xml_node = newdoc.createElement("author_contact")
        xml_node.appendChild(newdoc.createTextNode(self.get_author_contact()))
        root_element.appendChild(xml_node)

        # packager
        xml_node = newdoc.createElement("packager")
        xml_node.appendChild(newdoc.createTextNode(self.get_packager()))
        root_element.appendChild(xml_node)

        # packager website
        xml_node = newdoc.createElement("packager_website")
        xml_node.appendChild(newdoc.createTextNode(self.get_packager_website()))
        root_element.appendChild(xml_node)

        # packager contact
        xml_node = newdoc.createElement("packager_contact")
        xml_node.appendChild(newdoc.createTextNode(self.get_packager_contact()))
        root_element.appendChild(xml_node)

        # template path
        xml_node = newdoc.createElement("template")
        xml_node.appendChild(newdoc.createTextNode(self.get_template_path()))
        root_element.appendChild(xml_node)

        # translation
        #TODO


        xml_string = newdoc.toprettyxml()
        xml_string = xml_string.encode('utf8')

        repoDescriptionPath = os.path.join(self.get_local_path(),"exercise.xml")
        f = open(repoDescriptionPath, 'w')

        f.write(xml_string)
        f.close()



    def init_from_path(self, exercisePath):
        exerciseDescriptionPath = os.path.join(exercisePath,"exercise.xml")
        if os.path.isfile(exerciseDescriptionPath):
            f = open(exerciseDescriptionPath, 'r')
            dom = parse(f)
            self.parse_description(dom)
        else:
            self.id = os.path.basename(exercisePath)
            self.name = self.id
            self.description = gettext.gettext("Imported exercise")

    def _get_text(self, nodelist):
        rc = ""
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
        rc = rc.strip()
        return rc
