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
from perroquetlib.config import Config
import thread, urllib2, tempfile, os, tarfile, errno
from multiprocessing import Lock

class ExerciseRepository:

    def __init__(self):
        self.name =""
        self.description = ""
        self.version = ""
        self.exercisesGroupList = []
        self.config = Config()

    def setName(self, name):
        self.name = name

    def setDescription(self, description):
        self.description = description

    def setVersion(self, version):
        self.version = version

    def setName(self, name):
        self.name = name

    def getName(self):
        return self.name

    def setId(self, id):
        self.id = id

    def getId(self):
        return self.id

    def getDescription(self):
        return self.description

    def getVersion(self):
        return self.version

    def addGroup(self, group):
        self.exercisesGroupList.append(group)
        group.setParent(self)

    def getGroups(self):
        return self.exercisesGroupList

    def getLocalPath(self):
        print self.config.Get("local_repo_root_dir")
        print self.id
        return os.path.join(self.config.Get("local_repo_root_dir"), self.id)

    class ExercisesGroup:
        def __init__(self):
            self.name =""
            self.description = ""
            self.exercisesList = []

        def setName(self, name):
            self.name = name

        def setDescription(self, description):
            self.description = description

        def getName(self):
            return self.name

        def getDescription(self):
            return self.description

        def setId(self, id):
            self.id = id

        def getId(self):
            return self.id

        def addExercise(self, exercise):
            self.exercisesList.append(exercise)
            exercise.setParent(self)

        def getExercises(self):
            return self.exercisesList

        def setParent(self,parent):
            self.parent = parent

        def getLocalPath(self):
            return os.path.join(self.parent.getLocalPath(), self.id)

    class Exercise:
        def __init__(self):
            self.name =""
            self.description = ""
            self.mutexInstalling = Lock()

        def isInstalled(self):
            return False

        def startInstall(self):
            self.mutexInstalling.acquire()
            self.play_thread_id = thread.start_new_thread(self.installThread, ())

        def cancelInstall(self):
            print "TODO"

        def waitInstallEnd(self):
            self.mutexInstalling.acquire()
            self.mutexInstalling.release()

        def download(self):
            print "Start download"
            f=urllib2.urlopen('http://perroquet.b219.org/ressources/elephant_dream_en.tar.gz')
            print "Url open" + str(f.info())
            _, tempPath = tempfile.mkstemp("","perroquet-");
            wf = open(tempPath, 'w+b')
            print "File open"
            size = f.info().get('Content-Length')
            if size is None:
                size = 0
            else:
                size = int(size)
            print "size " +str(size)
            count=0
            sizeToRead = 50000
            while True:
                data=f.read(sizeToRead)
                wf.write(data)
                if len(data) != sizeToRead:
                    break;
                count+=sizeToRead
                print "%d%% complete" % (round((float(count)/float(size))*100))

            return tempPath

        def installThread(self):
            tmpPath = self.download()

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
            self.mutexInstalling.release()

        def getTemplatePath(self):
            print "TODO"


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
            return os.path.join(self.parent.getLocalPath(), self.id)
