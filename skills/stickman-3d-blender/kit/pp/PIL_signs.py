"""Painted shop-sign textures. Works inside Blender (no PIL there): pre-rendered by make_signs.py, this only names the file."""
import re
import kitpath

ROOT = kitpath.TEX + '/signs'


def slug(t):
    return re.sub(r'[^a-z0-9]+', '_', t.lower()).strip('_')


def sign_path(text, w, h, ink, trim):
    return f'{ROOT}/{slug(text)}.png'
