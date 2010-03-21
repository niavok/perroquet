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

from xml.dom.minidom import parse
import urllib2
import os
import tempfile
import tarfile
import errno
import shutil
from gettext import gettext as _

from perroquetlib.config import config
from perroquetlib.model.exercise_serializer import ExerciseLoader, ExerciseSaver

from perroquetlib.repository.exercise_repository import ExerciseRepository

class ExerciseRepositoryManager:

    def __init__(self):
        self.config = config

    def get_exercise_repository_list(self):
        repositoryList = []

        repositoryList += self._get_local_exercise_repository_list();
        #repositoryList += _getSystemExerciseRepositoryList();
        repositoryList += self._get_distant_exercise_repository_list();
        repositoryList += self._get_orphan_exercise_repository_list(repositoryList);

        return repositoryList

    def _get_local_exercise_repository_list(self):
        repositoryList = []
        localRepoPath = os.path.join(self.config.get("local_repo_root_dir"),"local")

        if os.path.isdir(localRepoPath):
            repository = ExerciseRepository()
            repository.init_from_path(localRepoPath)
            repository.set_type("local")
            repositoryList.append(repository)

        return repositoryList




    def _get_distant_exercise_repository_list(self):
        repositoryPathList = self.config.get("repository_source_list")
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
                    repository.parse_distant_repository_file(handle)
                    repository.set_url(line)
                    repositoryList.append(repository)
                    repository.generate_description()

        if len(offlineRepoList) > 0:
            repoPathList = os.listdir(self.config.get("local_repo_root_dir"))
            for repoPath in repoPathList:
                repository = ExerciseRepository()
                repoDescriptionPath = os.path.join(self.config.get("local_repo_root_dir"),repoPath,"repository.xml")
                if not os.path.isfile(repoDescriptionPath):
                    continue
                f = open(repoDescriptionPath, 'r')
                dom = parse(f)
                repository.parse_description(dom)
                print "test offline url : " +repository.get_url()
                if repository.get_url() in offlineRepoList:
                    print "add url : " +repository.get_url()
                    repository = ExerciseRepository()
                    repository.init_from_path(os.path.join(self.config.get("local_repo_root_dir"),repoPath))
                    repository.set_type("offline")
                    repositoryList.append(repository)

        return repositoryList



    def get_personal_exercise_repository_list(self):
        repositoryPath = self.config.get("personal_repository_source_path")
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

    def write_personal_exercise_repository_list(self, newRepositoryList):
        #The goal of this methods is to make an inteligent write of config file
        #Line biginning with # are comment and must be keep in place

        repositoryPath = self.config.get("personal_repository_source_path")
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

    def _get_orphan_exercise_repository_list(self,repositoryListIn):
        repoPathList = os.listdir(self.config.get("local_repo_root_dir"))
        repoUsedPath = []
        repositoryList = []
        for repo in repositoryListIn:
            repoUsedPath.append(repo.get_local_path())

        for repoPath in repoPathList:
            path = os.path.join(self.config.get("local_repo_root_dir"), repoPath)
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
            videoPath = os.path.join(sequencePath,os.path.basename(subExo.get_video_path()))
            exercisePath = os.path.join(sequencePath,os.path.basename(subExo.get_exercise_path()))
            translationPath = os.path.join(sequencePath,os.path.basename(subExo.get_translation_path()))

            videoRelPath = os.path.join(localPath,os.path.basename(subExo.get_video_path()))
            exerciseRelPath = os.path.join(localPath,os.path.basename(subExo.get_exercise_path()))
            translationRelPath = os.path.join(localPath,os.path.basename(subExo.get_translation_path()))

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
        saver = ExerciseSaver()
        exercisePackage.set_template(True)
        saver.save(exercisePackage, exercisePackage.get_output_save_path())

        # Create the tar
        tar = tarfile.open(outPath, 'w')
        tar.add(templatePath,"template.perroquet")
        tar.add(dataPath,"data")
        tar.close()

        shutil.rmtree(tempPath)

    def import_package(self, import_path):

        #Verify file existence
        if not os.path.isfile(import_path):
            return _("File not found: ")+import_path + "."

        #Create temporary directory to extract the tar before install it
        tempPath = tempfile.mkdtemp("","perroquet-");

        #Extract tar in temp directory
        tar = tarfile.open(import_path)
        tar.extractall(tempPath)
        tar.close()

        #Check package integrity
        template_path = os.path.join(tempPath,"template.perroquet")
        if not os.path.isfile(template_path):
            shutil.rmtree(tempPath)
            return _("Invalid package, missing template.perroquet.")


        #Find install path
        loader =  ExerciseLoader()
        exercise = loader.load(template_path)
        if exercise.get_name() != '':
            name = exercise.get_name()
        else:
            name = exercise.GetVideoPath()


        localRepoPath = os.path.join(self.config.get("local_repo_root_dir"),"local")
        group_path = os.path.join(localRepoPath,"Imported")
        install_path = os.path.join(group_path,name)

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

        shutil.move(tempPath,install_path )

        return None
