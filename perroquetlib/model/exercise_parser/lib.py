
def get_text(nodelist):
    ""
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
