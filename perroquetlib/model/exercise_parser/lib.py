# -*- coding: utf-8 -*-

# Copyright (C) 2009-2010 Frédéric Bertolus.
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Perroquet. If not, see <http://www.gnu.org/licenses/>.

def get_text(nodelist):
    """Extract the text of a node"""
    rc = ""
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc = rc + node.data
    rc = rc.strip()
    return rc


def update_sequence_list(exercise, subExos ):
    "set the sequences empty, partially done or done"
    for subExo, progress in zip(exercise.subExercisesList, subExos):
        sequenceList = subExo.get_sequence_list()

        for (id, state, words) in progress:
            if id >= len(sequenceList):
                break
            sequence = sequenceList[id]
            if state == "done":
                sequence.complete_all()
            elif state == "in_progress":
                i = 0
                for word in words:
                    if id >= sequence.get_word_count():
                        break
                    sequence.get_words()[i].set_text(word)
                    i = i+1
