#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2009-2011 Frédéric Bertolus.
# Copyright (C) 2009-2011 Matthieu Bizien.
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

from perroquetlib.repository.exercise_repository_manager import ExerciseRepositoryManager


if __name__=="__main__":
    manager = ExerciseRepositoryManager()
    print "get repository list"
    list = manager.get_exercise_repository_list()
    print str(len(list)) +" repository found:"
    for repo in list:
        print "/////////////////////////"
        print repo.get_id()
        print repo.get_name()
        print repo.get_local_path()
        print repo.get_version()
        print repo.get_description()
        print repo.get_type()
        print repo.get_url()

        for group in repo.get_groups():
            print "  "+group.get_name()
            print "  "+group.get_description()
            for exo in group.get_exercises():
                print "    "+exo.get_licence()
                print "    "+exo.get_language()
                print "    "+exo.get_media_type()
                print "    "+exo.get_version()
                print "    "+exo.get_author()
                print "    "+exo.get_author_website()
                print "    "+exo.get_author_contact()
                print "    "+exo.get_packager()
                print "    "+exo.get_packager_website()
                print "    "+exo.get_packager_contact()
                print "    "+exo.get_file_path()
                if not exo.is_installed():
                    print "    "+"Not installed"
                    """exo.start_install()
                    print "    "+"Install started"
                    exo.wait_install_end()
                    print "    "+"Install ended"""
                else:
                    print "    "+"Already installed"
