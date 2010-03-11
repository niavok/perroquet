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

import thread, urllib2, tempfile, os, tarfile, errno
from xml.dom.minidom import getDOMImplementation, parse
from multiprocessing import Lock

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

    def isInstalled(self):
        return os.path.isfile(self.getTemplatePath())

    def isUsed(self):
        return os.path.isfile(self.getInstancePath())

    def isDone(self):
        return os.path.isfile(self.getDonePath())


    def startInstall(self):
        self.mutexInstalling.acquire()
        self.canceled = False
        self.downloadPercent = 0
        self.play_thread_id = thread.start_new_thread(self.installThread, ())

    def cancelInstall(self):
        self.canceled = True

    def waitInstallEnd(self):
        self.mutexInstalling.acquire()
        self.mutexInstalling.release()

    def download(self):

        f=urllib2.urlopen(self.getFilePath())
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


    def getDownloadPercent(self):
        return self.downloadPercent

    def getState(self):
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
            if self.isDone():
                self.state = "done"
            elif self.isUsed():
                self.state = "used"
            elif self.isInstalled():
                self.state = "installed"
            else:
                self.state = "available"

        return self.state

    def setState(self, state):
        oldState = self.state
        self.state = state
        self.notifyStateChange(oldState, self.callbackData)

    def setStateChangeCallback(self, callback, callbackData):
        self.notifyStateChange = callback
        self.callbackData = callbackData

    def installThread(self):
        self.setState("downloading")
        tmpPath = self.download()
        if self.canceled:
            print "remove temp file"
            self.setState("canceled")
            os.remove(tmpPath)
        else:
            self.setState("installing")
            tar = tarfile.open(tmpPath)
            outPath = self.getLocalPath()
            try:
                os.makedirs(outPath)
            except OSError as exc: # Python >2.5
                if exc.errno == errno.EEXIST:
                    pass
                else: raise
            tar.extractall(outPath)
            tar.close()
            os.remove(tmpPath)
            if self.isInstalled():
                self.setState("installed")
            else:
                self.setState("corrupted")
        self.mutexInstalling.release()

    def getTemplatePath(self):
        return os.path.join(self.getLocalPath(),"template.perroquet")

    def getInstancePath(self):
        return os.path.join(self.getLocalPath(),"instance.perroquet")

    def getDonePath(self):
        return os.path.join(self.getLocalPath(),"done.perroquet")

    def setName(self, name):
        self.name = name

    def getName(self):
        return self.name

    def setId(self, id):
        self.id = id

    def getId(self):
        return self.id

    def setDescription(self, description):
        self.description = description

    def getDescription(self):
        return self.description

    def setLicence(self, licence):
        self.licence = licence

    def getLicence(self):
        return self.licence

    def setLanguage(self, language):
        self.language = language

    def getLanguage(self):
        return self.language

    def setMediaType(self, mediaType):
        self.mediaType = mediaType

    def getMediaType(self):
        return self.mediaType

    def setVersion(self, version):
        self.version = version

    def getVersion(self):
        return self.version

    def setAuthor(self, author):
        self.author = author

    def getAuthor(self):
        return self.author

    def setWordsCount(self, wordsCount):
        self.wordsCount = wordsCount

    def getWordsCount(self):
        return self.wordsCount

    def setAuthorWebsite(self, authorWebsite):
        self.authorWebsite = authorWebsite

    def getAuthorWebsite(self):
        return self.authorWebsite

    def setAuthorContact(self, authorContact):
        self.authorContact = authorContact

    def getAuthorContact(self):
        return self.authorContact

    def setPackager(self, packager):
        self.packager = packager

    def getPackager(self):
        return self.packager

    def setPackagerWebsite(self, packagerWebsite):
        self.packagerWebsite = packagerWebsite

    def getPackagerWebsite(self):
        return self.packagerWebsite

    def setPackagerContact(self, packagerContact):
        self.packagerContact = packagerContact

    def getPackagerContact(self):
        return self.packagerContact

    def setFilePath(self, filePath):
        self.filePath = filePath

    def getFilePath(self):
        return self.filePath

    def setTranslationsList(self, translationList):
        self.translationList = translationList

    def getTranslationsList(self):
        return self.translationList

    def setParent(self,parent):
        self.parent = parent

    def getLocalPath(self):
        return os.path.join(self.parent.getLocalPath(), self.id+"_"+self.version)

    def parseDescription(self,xml_exercise):
        self.setName(self._getText(xml_exercise.getElementsByTagName("name")[0].childNodes))
        self.setId(self._getText(xml_exercise.getElementsByTagName("id")[0].childNodes))
        self.setDescription(self._getText(xml_exercise.getElementsByTagName("description")[0].childNodes))
        self.setLicence(self._getText(xml_exercise.getElementsByTagName("licence")[0].childNodes))
        self.setLanguage(self._getText(xml_exercise.getElementsByTagName("language")[0].childNodes))
        self.setMediaType(self._getText(xml_exercise.getElementsByTagName("media_type")[0].childNodes))
        self.setVersion(self._getText(xml_exercise.getElementsByTagName("exercise_version")[0].childNodes))
        self.setAuthor(self._getText(xml_exercise.getElementsByTagName("author")[0].childNodes))
        self.setAuthorWebsite(self._getText(xml_exercise.getElementsByTagName("author_website")[0].childNodes))
        self.setAuthorContact(self._getText(xml_exercise.getElementsByTagName("author_contact")[0].childNodes))
        self.setPackager(self._getText(xml_exercise.getElementsByTagName("packager")[0].childNodes))
        self.setPackagerWebsite(self._getText(xml_exercise.getElementsByTagName("packager_website")[0].childNodes))
        self.setPackagerContact(self._getText(xml_exercise.getElementsByTagName("packager_contact")[0].childNodes))
        if len(xml_exercise.getElementsByTagName("words_count")) > 0:
            self.setWordsCount(self._getText(xml_exercise.getElementsByTagName("words_count")[0].childNodes))
        if len(xml_exercise.getElementsByTagName("file")) > 0:
            self.setFilePath(self._getText(xml_exercise.getElementsByTagName("file")[0].childNodes))

        if len(xml_exercise.getElementsByTagName("translations")) > 0:
            xml_translations = xml_exercise.getElementsByTagName("translations")[0]
            translationList = []
            for xml_translation in xml_translations.getElementsByTagName("translation"):
                translationList.append(self._getText(xml_translation.childNodes))

            self.setTranslationsList(translationList)

    def generateDescription(self):
        self._generateDescription()

    def _generateDescription(self):

        if not os.path.isdir(self.getLocalPath()):
            try:
                os.makedirs(self.getLocalPath())
            except OSError as exc: # Python >2.5
                if exc.errno == errno.EEXIST:
                    pass
                else: raise

        impl = getDOMImplementation()

        newdoc = impl.createDocument(None, "perroquet_exercise", None)
        root_element = newdoc.documentElement

        # Name
        xml_name = newdoc.createElement("name")
        xml_name.appendChild(newdoc.createTextNode(self.getName()))
        root_element.appendChild(xml_name)

        # Id
        xml_id = newdoc.createElement("id")
        xml_id.appendChild(newdoc.createTextNode(self.getId()))
        root_element.appendChild(xml_id)

        # Description
        xml_description = newdoc.createElement("description")
        xml_description.appendChild(newdoc.createTextNode(self.getDescription()))
        root_element.appendChild(xml_description)

        # Words count
        xml_version = newdoc.createElement("words_count")
        xml_version.appendChild(newdoc.createTextNode(str(self.getWordsCount())))
        root_element.appendChild(xml_version)

        # Version
        xml_version = newdoc.createElement("exercise_version")
        xml_version.appendChild(newdoc.createTextNode(self.getVersion()))
        root_element.appendChild(xml_version)

        # Licence
        xml_node = newdoc.createElement("licence")
        xml_node.appendChild(newdoc.createTextNode(self.getLicence()))
        root_element.appendChild(xml_node)

        # Language
        xml_node = newdoc.createElement("language")
        xml_node.appendChild(newdoc.createTextNode(self.getLanguage()))
        root_element.appendChild(xml_node)

        # Media type
        xml_node = newdoc.createElement("media_type")
        xml_node.appendChild(newdoc.createTextNode(self.getMediaType()))
        root_element.appendChild(xml_node)

        # author
        xml_node = newdoc.createElement("author")
        xml_node.appendChild(newdoc.createTextNode(self.getAuthor()))
        root_element.appendChild(xml_node)

        # author website
        xml_node = newdoc.createElement("author_website")
        xml_node.appendChild(newdoc.createTextNode(self.getAuthorWebsite()))
        root_element.appendChild(xml_node)

        # author contact
        xml_node = newdoc.createElement("author_contact")
        xml_node.appendChild(newdoc.createTextNode(self.getAuthorContact()))
        root_element.appendChild(xml_node)

        # packager
        xml_node = newdoc.createElement("packager")
        xml_node.appendChild(newdoc.createTextNode(self.getPackager()))
        root_element.appendChild(xml_node)

        # packager website
        xml_node = newdoc.createElement("packager_website")
        xml_node.appendChild(newdoc.createTextNode(self.getPackagerWebsite()))
        root_element.appendChild(xml_node)

        # packager contact
        xml_node = newdoc.createElement("packager_contact")
        xml_node.appendChild(newdoc.createTextNode(self.getPackagerContact()))
        root_element.appendChild(xml_node)

        # template path
        xml_node = newdoc.createElement("template")
        xml_node.appendChild(newdoc.createTextNode(self.getTemplatePath()))
        root_element.appendChild(xml_node)

        # translation
        #TODO


        xml_string = newdoc.toprettyxml()
        xml_string = xml_string.encode('utf8')

        repoDescriptionPath = os.path.join(self.getLocalPath(),"exercise.xml")
        f = open(repoDescriptionPath, 'w')

        f.write(xml_string)
        f.close()



    def initFromPath(self, exercisePath):
        exerciseDescriptionPath = os.path.join(exercisePath,"exercise.xml")
        if os.path.isfile(exerciseDescriptionPath):
            exercise = ExerciseRepositoryExercise()
            f = open(exerciseDescriptionPath, 'r')
            dom = parse(f)
            self.parseDescription(dom)






    def _getText(self, nodelist):
        rc = ""
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
        rc = rc.strip()
        return rc
