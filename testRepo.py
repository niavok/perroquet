#!/usr/bin/env python
# -*- coding: utf-8 -*-

from perroquetlib.exercise_repository_manager import *


if __name__=="__main__":
    manager = ExerciseRepositoryManager()
    print "Get repository list"
    list = manager.getExerciseRepositoryList()
    print str(len(list)) +" repository found:"
    for repo in list:
        print "/////////////////////////"
        print repo.getId()
        print repo.getName()
        print repo.getLocalPath()
        print repo.getVersion()
        print repo.getDescription()
        print repo.getType()
        print repo.getUrl()

        for group in repo.getGroups():
            print "  "+group.getName()
            print "  "+group.getDescription()
            for exo in group.getExercises():
                print "    "+exo.getLicence()
                print "    "+exo.getLanguage()
                print "    "+exo.getMediaType()
                print "    "+exo.getVersion()
                print "    "+exo.getAuthor()
                print "    "+exo.getAuthorWebsite()
                print "    "+exo.getAuthorContact()
                print "    "+exo.getPackager()
                print "    "+exo.getPackagerWebsite()
                print "    "+exo.getPackagerContact()
                print "    "+exo.getFilePath()
                if not exo.isInstalled():
                    print "    "+"Not installed"
                    """exo.startInstall()
                    print "    "+"Install started"
                    exo.waitInstallEnd()
                    print "    "+"Install ended"""
                else:
                    print "    "+"Already installed"
