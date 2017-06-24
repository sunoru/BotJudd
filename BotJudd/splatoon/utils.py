import json
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
def jsonload(filename):
    with open(os.path.join(BASE_DIR, filename)) as fi:
        ret = json.load(fi)
    return ret

def textload(filename):
    with open(os.path.join(BASE_DIR, filename)) as fi:
        ret = fi.read()
    return ret
