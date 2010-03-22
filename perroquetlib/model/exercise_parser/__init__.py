
from xml.dom.minidom import parse

from perroquetlib.model.exercise import Exercise

from lib import get_text
from parser_v1_1_0 import load as load_v1_1_0, save as save_v1_1_0
from parser_v1_0_0 import load as load_v1_0_0, save as save_v1_0_0

def load(path):
    "load a perroquet exercise"
    exercise = Exercise()

    dom = parse(path)
    if len(dom.getElementsByTagName("version")) > 0:
        version = get_text(dom.getElementsByTagName("version")[0].childNodes)

        if version >= "1.1.0":
            load_v1_1_0(exercise, dom, path)
        elif version >= "1.0.0":
            raise NotImplemented
            load_v1_0_0(exercise, dom, path)
        else:
            print "Unknown file version: "+version
            exercise = None
    else:
        print "Invalid perroquet file"
        exercise = None

    dom.unlink()

    return exercise

def save(*args):
    save_v1_1_0(*args)
