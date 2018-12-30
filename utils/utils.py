#from subprocess import call as call2
import pickle
from subprocess import check_output
import os
from cv2 import rectangle
import logging
import hashlib
from pathlib import Path
import readline


def rlinput(prompt, prefill=''):
   readline.set_startup_hook(lambda: readline.insert_text(prefill))
   try:
      return input(prompt)
   finally:
      readline.set_startup_hook()

# Filesystem

def ensurePath(p):
    if not os.path.exists(p):
        os.makedirs(p)

def getHome():
    return str(Path.home())


def getExtension(filename):
    return os.path.splitext(filename)[1]
      
# Cache
cacheFolder = "{}/.cache/ebooktoc/".format(getHome())

def getCached(filename):
    cacheFile = cacheFolder + filename
    if os.path.isfile(cacheFile):
        log("Using cache for {}".format(filename))
        with open(cacheFile, "rb") as f:
            return pickle.load(f)
    else:
        return None


def cache(var, filename):
    cacheFile = cacheFolder + filename
    ensurePath(cacheFolder)
    pickle.dump(var, open(cacheFile, "wb"))

# Hashes

def sha1(s):
    return hashlib.sha1(s).hexdigest()


def sha1_file(filename):  # https://stackoverflow.com/questions/1131220/get-md5-hash-of-big-files-in-python
    sha1 = hashlib.sha1()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(128 * sha1.block_size), b""):
            sha1.update(chunk)
    return sha1.hexdigest()

# Logging

def log(text):
    logging.getLogger().debug(text)


def isDebug():
    return logging.getLogger().getEffectiveLevel() == logging.DEBUG

# Processes

def call(command):
    with open(os.devnull, "w") as dn:
        return check_output(command, stderr=dn)

# OpenCV helpers

def drawBox(image, box):
    """
    Draws a pink box on the image
    """
    return drawBox(image, [box])

def drawBoxes(image, boxes):
    """
    Draws pink boxes on the image
    """
    image = image.copy()
    for box in boxes:
        rectangle(image, (box["x"], box["y"]), (box["x"] + box["w"], box["y"] + box["h"]), (255, 0, 255), 2)
    return image


def region(image, block):
    """
    Extract image region
    """
    return image[block["y"] : block["y"]+block["h"], block["x"]: block["x"] + block["w"]]

# Miscellaneous

def isType(s, t):
    """
    Check if variable can be converted to the given type
    """
    try:
        t(s)
        return True
    except:
        return False

def formatDuration(d):
    if d < 60:
        return "{} sec".format(d)
    m = d//60
    if m < 60:
        return "{} min".format(m)
    h, m = divmod(m, 60)
    return "{}h{}min".format(h, m)
