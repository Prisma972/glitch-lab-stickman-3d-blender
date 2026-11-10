"""Where the kit and Blender are. Every path in the kit comes from here, so the kit folder can live anywhere.

KIT      the kit root (the folder holding pp/, tex/, shorts/). Env STICKMAN_KIT overrides; default: the parent of this file.
BLENDER  the Blender executable. Env BLENDER overrides; default: `blender` on PATH, then the usual install folders.
"""
import glob
import os
import shutil


def _p(x):
    return os.path.abspath(x).replace('\\', '/')


KIT = _p(os.environ.get('STICKMAN_KIT') or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
PP = KIT + '/pp'
TEX = KIT + '/tex'
OUT = KIT + '/out'


def find_blender():
    b = os.environ.get('BLENDER')
    if b:
        return b
    b = shutil.which('blender')
    if b:
        return b
    pats = ['C:/Program Files/Blender Foundation/Blender*/blender.exe',
            '/Applications/Blender.app/Contents/MacOS/Blender',
            '/usr/bin/blender', '/usr/local/bin/blender', '/snap/bin/blender']
    for pat in pats:
        hits = sorted(glob.glob(pat))
        if hits:
            return hits[-1]
    return 'blender'


BLENDER = find_blender()
