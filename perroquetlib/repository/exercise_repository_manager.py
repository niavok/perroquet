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

import errno
import logging
import os
import shutil
import tarfile
import tempfile
import urllib2
from gettext import gettext as _
from xml.dom.minidom import parse

from perroquetlib.config import config
from perroquetlib.debug import defaultLoggingHandler, defaultLoggingLevel
from perroquetlib.model.exercise_parser import load_exercise, save_exercise
from perroquetlib.repository.exercise_repository import ExerciseRepository

class ExerciseRepositoryManager:
    """This class provide an interface to get a list of exercise repository,
    instance of ExerciseRepository. A repository is a tree of Perroquet
    exercises which can be synchronized with an online image. During
    synchronization, only the exercise's metadatas are downloaded but it's
    possible to install the real exercise then use it.
    A repository contain a list of exercises group. A group contains a list
    of exercises.
    The repositories metadatas are store in a directory tree in the local
    datas of the user. This path is call 'repo root directory'.
    """
    def __init__(self):
        """Constructor"""
        self.logger = logging.Logger("ExerciseRepositoryManager")
        self.logger.setLevel(defaultLoggingLevel)
        self.logger.addHandler(defaultLoggingHandler)

    def get_exercise_repository_list(self):
        """Return the list of all find repositories.
        The list is build from multiple sources:
        - from the list url of repository online description found in the
        main config file
        - from the list url of repository online description found in the
        local config file
        - from the directory present in the repo_root directory whose not
        correspond with an url

        The returned list classify each repository in one of these type:
        - local: if a directory name 'local' is find in the repo_root
        directory, a repository named 'local' is initialized from this path.
        The local repository is not syncronised with distant description but
        contains all manually installed exercises.
        - distant: if an repository url is reachable, a distant repository
        is initialized after syncronization with the distant description
        file.
        - offline: if an repository url is not reachable, an offline
        repository is initialized from the directory created during the
        last syncronization.
        - orphan : an orphan repository is initialized from each directory
        in repo_root which not correspond to any others type of repository.
        An orphan repository car appear is a syncronized exercise
        description is remove from list of url.
        """
        repositoryList = []

        #Add the local repository if exist
        repositoryList += self._get_local_exercise_repository_list()
        #Add the list of distant and offline repository
        repositoryList += self._get_distant_exercise_repository_list()
        #Add the list of orphan repository
        repositoryList += self._get_orphan_exercise_repository_list(repositoryList)

        return repositoryList

    def _get_local_exercise_repository_list(self):
        """Build and return the list of local repority. In fact, this list
        will contain at maximum 1 repository.
        A local repository is added to the list if a directory named 'local'
        exist in the repo root directory"""

        repositoryList = []
        #Build potential local repository path
        localRepoPath = os.path.join(config.get("local_repo_root_dir"), "local")

        # Test local repository existance
        if os.path.isdir(localRepoPath):
            #Repository found so Initialize it from the path and set it as local
            repository = ExerciseRepository()
            repository.init_from_path(localRepoPath)
            repository.set_type("local")
            repositoryList.append(repository)

        return repositoryList




    def _get_distant_exercise_repository_list(self):
        """Build and return a list of distant and offline repositories.
        There is one repository initialized for each url found in the
        config files. If the url is reachable, a distant repository is
        initialized, else an offline repository is created.
        """
        #Get the list of files containing url list
        repositoryPathList = config.get("repository_source_list")
        repositoryList = []
        offlineRepoList = []

        #Fetch repository urls file
        for path in repositoryPathList:
            f = open(path, 'r')
            #Fetch urls of repo description
            for line in f:
                line = line.rstrip()
                if line and line[0] == "#":
                    #Comment line
                    continue
                req = urllib2.Request(line)
                try:
                    #try to download the file headers
                    handle = urllib2.urlopen(req)
                except IOError:
                    #if the download failed store the url in a list of
                    #offline urls
                    self.logger.error("Fail to connection to repository '" + line + "'")
                    offlineRepoList.append(line)
                except ValueError:
                    self.logger.exception("Unknown url type '" + line + "'")
                    offlineRepoList.append(line)
                else:
                    #if the download success, init a repository from the
                    #downloaded file and regenerate the tree
                    self.logger.debug("init distant repo")
                    repository = ExerciseRepository()
                    repository.parse_distant_repository_file(handle)
                    repository.set_url(line)
                    repositoryList.append(repository)
                    repository.generate_description()
        #if the list of url is not empty, add a list of offline repository
        if len(offlineRepoList) > 0:
            repoPathList = os.listdir(config.get("local_repo_root_dir"))
            for repoPath in repoPathList:
                #for eaach directory in the repo root path analyse the
                #description file. If the url of this repo match with one
                #of offline url, then init an offline repository from this
                #path
                repository = ExerciseRepository()
                repoDescriptionPath = os.path.join(config.get("local_repo_root_dir"), repoPath, "repository.xml")
                if not os.path.isfile(repoDescriptionPath):
                    continue
                f = open(repoDescriptionPath, 'r')
                dom = parse(f)
                repository.parse_description(dom)
                self.logger.debug("test offline url : " + repository.get_url())
                if repository.get_url() in offlineRepoList:
                    self.logger.info("add url : " + repository.get_url())
                    repository = ExerciseRepository()
                    repository.init_from_path(os.path.join(config.get("local_repo_root_dir"), repoPath))
                    repository.set_type("offline")
                    repositoryList.append(repository)

        return repositoryList



    def get_personal_exercise_repository_list(self):
        """Return the list of the url of the repository url add by the user"""
        repositoryPath = config.get("personal_repository_source_path")
        repositoryList = []

        if os.path.isfile(repositoryPath):
            f = open(repositoryPath, 'r')
            for line in f:
                line = line.rstrip()
                if line and line[0] == "#":
                    #Comment line
                    continue

                repositoryList.append(line)

        return repositoryList

    def write_personal_exercise_repository_list(self, newRepositoryList):
        """The goal of this methods is to make an inteligent write of
        config file. Lines beginning with # are comment and must be keep
        in place"""

        repositoryPath = config.get("personal_repository_source_path")
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
            self.logger.debug(line)
            f.writelines(line + '\n')

        f.close()

    def _get_orphan_exercise_repository_list(self, repositoryListIn):
        repoPathList = os.listdir(config.get("local_repo_root_dir"))
        repoUsedPath = []
        repositoryList = []
        for repo in repositoryListIn:
            repoUsedPath.append(repo.get_local_path())

        for repoPath in repoPathList:
            path = os.path.join(config.get("local_repo_root_dir"), repoPath)
            if path not in repoUsedPath:
                repository = ExerciseRepository()
                repository.init_from_path(path)
                repository.set_type("orphan")
                repositoryList.append(repository)

        return repositoryList

    def _get_text(self, nodelist):
        rc = ""
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
        rc = rc.strip()
        return rc

    def export_as_package(self, exercise, outPath):
        tempPath = tempfile.mkdtemp("", "perroquet-");

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
        for i, subExo in enumerate(exercisePackage.subExercisesList):

            localPath = os.path.join("data", "sequence_" + str(i))
            #Make sequence directory
            sequencePath = os.path.join(tempPath, localPath)

            if not os.path.isdir(sequencePath):
                try:
                    os.makedirs(sequencePath)
                except OSError, (ErrorNumber, ErrorMessage): # Python <=2.5
                    if ErrorNumber == errno.EEXIST:
                        pass
                    else: raise

            #Copy resources locally
            videoPath = os.path.join(sequencePath, os.path.basename(subExo.get_video_path()))
            exercisePath = os.path.join(sequencePath, os.path.basename(subExo.get_exercise_path()))
            translationPath = os.path.join(sequencePath, os.path.basename(subExo.get_translation_path()))

            videoRelPath = os.path.join(localPath, os.path.basename(subExo.get_video_path()))
            exerciseRelPath = os.path.join(localPath, os.path.basename(subExo.get_exercise_path()))
            translationRelPath = os.path.join(localPath, os.path.basename(subExo.get_translation_path()))

            shutil.copyfile(subExo.get_video_path(), videoPath)
            shutil.copyfile(subExo.get_exercise_path(), exercisePath)
            if subExo.get_translation_path() != '':
                shutil.copyfile(subExo.get_translation_path(), translationPath)


            subExo.set_video_export_path(videoRelPath)
            subExo.set_exercise_export_path(exerciseRelPath)
            if subExo.get_translation_path() != '':
                subExo.set_translation_export_path(translationRelPath)

        templatePath = os.path.join(tempPath, "template.perroquet")

        exercisePackage.set_output_save_path(templatePath)
        exercisePackage.set_template(True)
        save_exercise(exercisePackage, exercisePackage.get_output_save_path())

        # Create the tar
        tar = tarfile.open(outPath, 'w')
        tar.add(templatePath, "template.perroquet")
        tar.add(dataPath, "data")
        tar.close()

        shutil.rmtree(tempPath)

    def import_package(self, import_path):

        #Verify file existence
        if not os.path.isfile(import_path):
            return _("File not found: ") + import_path + "."

        #Create temporary directory to extract the tar before install it
        tempPath = tempfile.mkdtemp("", "perroquet-");

        #Extract tar in temp directory
        tar = tarfile.open(import_path)
        tar.extractall(tempPath)
        tar.close()

        #Check package integrity
        template_path = os.path.join(tempPath, "template.perroquet")
        if not os.path.isfile(template_path):
            shutil.rmtree(tempPath)
            return _("Invalid package, missing template.perroquet.")


        #Find install path
        exercise = load_exercise(template_path)
        if exercise.get_name() != '':
            name = exercise.get_name()
        else:
            name = exercise.GetVideoPath()


        localRepoPath = os.path.join(config.get("local_repo_root_dir"), "local")
        group_path = os.path.join(localRepoPath, "Imported")
        install_path = os.path.join(group_path, name)

        #Copy files
        if not os.path.isdir(group_path):
            try:
                os.makedirs(group_path)
            except OSError, (ErrorNumber, ErrorMessage): # Python <=2.5
                if ErrorNumber == errno.EEXIST:
                    pass
                else: raise

        if os.path.isdir(install_path):
            shutil.rmtree(tempPath)
            return _("Exercise already exist.")

        shutil.move(tempPath, install_path)

        return None
