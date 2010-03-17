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

from xml.dom.minidom import getDOMImplementation, parse
import urllib2, os, tempfile, tarfile, errno, shutil

from perroquetlib.config import config
from perroquetlib.exercise_serializer import ExerciseSaver
from perroquetlib.repository.exercise_repository import ExerciseRepository
from perroquetlib.repository.exercise_repository_group import ExerciseRepositoryGroup
from perroquetlib.repository.exercise_repository_exercise import ExerciseRepositoryExercise


class ExerciseRepositoryManager:

    def __init__(self):
        self.config = config

    def getExerciseRepositoryList(self):
        repositoryPathList = self.config.Get("repository_source_list")
        repositoryList = []

        repositoryList += self._getLocalExerciseRepositoryList();
        #repositoryList += _getSystemExerciseRepositoryList();
        repositoryList += self._getDistantExerciseRepositoryList();
        repositoryList += self._getOrphanExerciseRepositoryList(repositoryList);

        return repositoryList

    def _getLocalExerciseRepositoryList(self):
        repositoryList = []
        localRepoPath = os.path.join(self.config.Get("local_repo_root_dir"),"local")

        if os.path.isdir(localRepoPath):
            repository = ExerciseRepository()
            repository.initFromPath(localRepoPath)
            repository.setType("local")
            repositoryList.append(repository)

        return repositoryList




    def _getDistantExerciseRepositoryList(self):
        repositoryPathList = self.config.Get("repository_source_list")
        repositoryList = []
        offlineRepoList = []

        for path in repositoryPathList:
            f = open(path, 'r')
            for line in f:
                line = line.rstrip()
                if line[0] == "#":
                    #Comment line
                    continue

                req = urllib2.Request(line)
                try:
                    handle = urllib2.urlopen(req)
                except IOError:
                    print "Fail to connection to repository '"+line+"'"
                    offlineRepoList.append(line)
                except ValueError:
                    print "Unknown url type '"+line+"'"
                    offlineRepoList.append(line)
                else:
                    print "init distant repo"
                    repository = ExerciseRepository()
                    repository.parseDistantRepositoryFile(handle)
                    repository.setUrl(line)
                    repositoryList.append(repository)
                    repository.generateDescription()

        if len(offlineRepoList) > 0:
            repoPathList = os.listdir(self.config.Get("local_repo_root_dir"))
            for repoPath in repoPathList:
                repository = ExerciseRepository()
                repoDescriptionPath = os.path.join(self.config.Get("local_repo_root_dir"),repoPath,"repository.xml")
                if not os.path.isfile(repoDescriptionPath):
                    continue
                f = open(repoDescriptionPath, 'r')
                dom = parse(f)
                repository.parseDescription(dom)
                print "test offline url : " +repository.getUrl()
                if repository.getUrl() in offlineRepoList:
                    print "add url : " +repository.getUrl()
                    repository = ExerciseRepository()
                    repository.initFromPath(os.path.join(self.config.Get("local_repo_root_dir"),repoPath))
                    repository.setType("offline")
                    repositoryList.append(repository)

        return repositoryList



    def getPersonalExerciseRepositoryList(self):
        repositoryPath = self.config.Get("personal_repository_source_path")
        repositoryList = []

        if os.path.isfile(repositoryPath):
            f = open(repositoryPath, 'r')
            for line in f:
                line = line.rstrip()
                if line[0] == "#":
                    #Comment line
                    continue

                repositoryList.append(line)

        return repositoryList

    def writePersonalExerciseRepositoryList(self, newRepositoryList):
        #The goal of this methods is to make an inteligent write of config file
        #Line biginning with # are comment and must be keep in place

        repositoryPath = self.config.Get("personal_repository_source_path")
        repositoryList = []

        if os.path.isfile(repositoryPath):
            f = open(repositoryPath, 'r')
            for line in f:
                line = line.rstrip()
                if line[0] == "#":
                    #Comment line, set as keep
                    repositoryList.append(line)
                elif line in newRepositoryList:
                    repositoryList.append(line)
                    newRepositoryList.remove(line)
            f.close()

        for newRepo in newRepositoryList:
            repositoryList.append(newRepo)

        f = open(repositoryPath, 'w')
        for line in repositoryList:
            print line
            f.writelines(line+'\n')

        f.close()

    def _getOrphanExerciseRepositoryList(self,repositoryListIn):
        repoPathList = os.listdir(self.config.Get("local_repo_root_dir"))
        repoUsedPath = []
        repositoryList = []
        for repo in repositoryListIn:
            repoUsedPath.append(repo.getLocalPath())

        for repoPath in repoPathList:
            path = os.path.join(self.config.Get("local_repo_root_dir"), repoPath)
            if path not in repoUsedPath:
                repository = ExerciseRepository()
                repository.initFromPath(path)
                repository.setType("orphan")
                repositoryList.append(repository)

        return repositoryList

    def _getText(self, nodelist):
        rc = ""
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
        rc = rc.strip()
        return rc

    def exportAsPackage(self, exercise, outPath):
        tempPath = tempfile.mkdtemp("","perroquet-");

        exercisePackage = exercise

        #Make data directory
        dataPath = os.path.join(tempPath, "data")

        if not os.path.isdir(dataPath):
            try:
                os.makedirs(dataPath)
            except OSError, (ErrorNumber, ErrorMessage): # Python <=2.5
                if ErrorNumber == errno.EEXIST:
                    pass
                else: raise

        #Exercise - SubExercises
        for i,subExo in enumerate(exercisePackage.subExercisesList):

            localPath = os.path.join("data", "sequence_"+str(i))
            #Make sequence directory
            sequencePath = os.path.join(tempPath,localPath)

            if not os.path.isdir(sequencePath):
                try:
                    os.makedirs(sequencePath)
                except OSError, (ErrorNumber, ErrorMessage): # Python <=2.5
                    if ErrorNumber == errno.EEXIST:
                        pass
                    else: raise

            #Copy resources locally
            videoPath = os.path.join(sequencePath,os.path.basename(subExo.GetVideoPath()))
            exercisePath = os.path.join(sequencePath,os.path.basename(subExo.GetExercisePath()))
            translationPath = os.path.join(sequencePath,os.path.basename(subExo.GetTranslationPath()))

            videoRelPath = os.path.join(localPath,os.path.basename(subExo.GetVideoPath()))
            exerciseRelPath = os.path.join(localPath,os.path.basename(subExo.GetExercisePath()))
            translationRelPath = os.path.join(localPath,os.path.basename(subExo.GetTranslationPath()))

            shutil.copyfile(subExo.GetVideoPath(), videoPath)
            shutil.copyfile(subExo.GetExercisePath(), exercisePath)
            if subExo.GetTranslationPath() != '':
                shutil.copyfile(subExo.GetTranslationPath(), translationPath)


            subExo.SetVideoExportPath(videoRelPath)
            subExo.SetExerciseExportPath(exerciseRelPath)
            if subExo.GetTranslationPath() != '':
                subExo.SetTranslationExportPath(translationRelPath)

        templatePath = os.path.join(tempPath, "template.perroquet")

        exercisePackage.setOutputSavePath(templatePath)
        saver = ExerciseSaver()
        exercisePackage.setTemplate(True)
        saver.Save(exercisePackage, exercisePackage.getOutputSavePath())

        # Create the tar
        tar = tarfile.open(outPath, 'w')
        tar.add(templatePath,"template.perroquet")
        tar.add(dataPath,"data")
        tar.close()

        shutil.rmtree(tempPath)
