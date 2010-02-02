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
