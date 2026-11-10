"""Builds the day street set and its three characters in whichever Blender runs it (live, or headless via common.run)."""
import os, sys, importlib, math
import bpy
PP = os.path.join(os.environ['STICKMAN_KIT'], 'pp') if os.environ.get('STICKMAN_KIT') else os.path.dirname(os.path.abspath(__file__))
if PP not in sys.path:
    sys.path.insert(0, PP)
import look, chars, street, PIL_signs
for m in (look, chars, PIL_signs, street):
    importlib.reload(m)
L = look

L.wipe()
sc = bpy.context.scene
L.fog_group()
L.setup(sc, 'day')
L.INK_SCALE[0] = 1.5
chars.HEAD_GLOW[0] = 0.88
chars.GLOVE_GLOW[0] = 0.35
SET, M = street.build()
L.INK_SCALE[0] = 1.0
# the far end of the street keeps a readable line: 5.5 px on roofs, 3.4 px elsewhere at about 55 m
for o in bpy.data.objects:
    if o.name.startswith('ST_end') and 'PP_ink' in o.modifiers:
        o.modifiers['PP_ink'].thickness = 0.17 if o.name.startswith('ST_endr') else 0.11

hero = chars.build('tobin', chars.LAMPLIGHTER, (0.2, 0.0, 0), math.radians(10))
baker = chars.build('mabel', chars.BAKER, (0.95, 1.2, 0), math.radians(-30))
clerk = chars.build('clerk', chars.CLERK, (-1.1, 3.0, 0), math.radians(25))

# hero pose: one hand raised holding something, other on hip

import json
SHOTS = json.load(open(PP + '/shots_street.json'))


def shot(k):
    s = SHOTS[k]
    cam = L.camera('CAM', s['pos'], s['tgt'], s['lens'], s['roll'], s['fstop'], s['focus'])
    sc.camera = cam
    return cam


shot('med')
sc.frame_set(1)
print('built', len(bpy.data.objects), 'objects')
