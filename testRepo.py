#!/usr/bin/env python
# -*- coding: utf-8 -*-

from perroquetlib.exercise_repository_manager import *


if __name__=="__main__":
    manager = ExerciseRepositoryManager()
    list = manager.getExerciseRepositoryList()
    for repo in list:
        print repo.getName()
        print repo.getVersion()
        print repo.getDescription()

        for group in repo.getGroups():
            print group.getName()
            print group.getDescription()
            for exo in group.getExercises():
                print exo.getLicence()
                print exo.getLanguage()
                print exo.getMediaType()
                print exo.getVersion()
                print exo.getAuthor()
                print exo.getAuthorWebsite()
                print exo.getAuthorContact()
                print exo.getPackager()
                print exo.getPackagerWebsite()
                print exo.getPackagerContact()
                print exo.getFilePath()
