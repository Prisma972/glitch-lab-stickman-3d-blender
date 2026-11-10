"""Fonts by short name, on Windows, macOS or Linux. font('ariblk', 53) -> a PIL font.
Env STICKMAN_FONTS: a folder searched first (drop your own .ttf there, named like the keys below, e.g. ariblk.ttf).
Missing fonts fall back to a bold sans (DejaVu or Liberation), then to Pillow's default font."""
import os
from PIL import ImageFont

WIN = os.environ.get('WINDIR', 'C:/Windows') + '/Fonts/'
MAC = '/System/Library/Fonts/Supplemental/'
LIN = '/usr/share/fonts/truetype/'
BOLD = [LIN + 'dejavu/DejaVuSans-Bold.ttf', LIN + 'liberation/LiberationSans-Bold.ttf', LIN + 'liberation2/LiberationSans-Bold.ttf']
SERIF = [LIN + 'dejavu/DejaVuSerif-Bold.ttf', LIN + 'liberation/LiberationSerif-Bold.ttf']
FILES = {
    'ariblk': [WIN + 'ariblk.ttf', MAC + 'Arial Black.ttf'] + BOLD,        # captions
    'arialbd': [WIN + 'arialbd.ttf', MAC + 'Arial Bold.ttf'] + BOLD,       # labels on boards
    'georgiab': [WIN + 'georgiab.ttf', MAC + 'Georgia Bold.ttf'] + SERIF,  # shop signs, room props
    'georgia': [WIN + 'georgia.ttf', MAC + 'Georgia.ttf', LIN + 'dejavu/DejaVuSerif.ttf'],
    'impact': [WIN + 'impact.ttf', MAC + 'Impact.ttf'] + BOLD,
    'segoepr': [WIN + 'segoepr.ttf', MAC + 'Bradley Hand Bold.ttf', WIN + 'georgiai.ttf', MAC + 'Georgia Italic.ttf'] + SERIF,  # handwriting
}
_CACHE = {}


def path(name):
    if name not in _CACHE:
        own = os.environ.get('STICKMAN_FONTS')
        cands = ([f'{own}/{name}.ttf'] if own else []) + FILES.get(name, BOLD)
        _CACHE[name] = next((c for c in cands if os.path.exists(c)), None)
    return _CACHE[name]


def font(name, size):
    p = path(name)
    if p:
        return ImageFont.truetype(p, size)
    return ImageFont.load_default(size)
