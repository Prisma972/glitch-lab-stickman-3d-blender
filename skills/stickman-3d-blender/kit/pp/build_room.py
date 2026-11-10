"""Builds the room set (a workshop) with the hero at the desk. NIGHT = True in the globals for the blue night version."""
import sys, importlib, math, os, json
import bpy
PP = os.path.join(os.environ['STICKMAN_KIT'], 'pp') if os.environ.get('STICKMAN_KIT') else os.path.dirname(os.path.abspath(__file__))
if PP not in sys.path:
    sys.path.insert(0, PP)
import look, chars, room
for m in (look, chars, room):
    importlib.reload(m)
L = look
NIGHT = globals().get('NIGHT', False)
L.wipe()
sc = bpy.context.scene
L.fog_group()
L.setup(sc, 'night' if NIGHT else 'room')
sun = bpy.data.objects['PP_Sun']
sun.data.energy = 0.0
L.INK_SCALE[0] = 0.6
chars.HEAD_GLOW[0] = 0.78
chars.GLOVE_GLOW[0] = 0.15
room.build(NIGHT)
L.INK_SCALE[0] = 1.0
# set lines finer than the characters, but the dark band under the desk top stays
bpy.data.objects['RM_top'].modifiers['PP_ink'].thickness = 0.012
bpy.data.objects['RM_apron'].modifiers['PP_ink'].thickness = 0.010
hero = chars.build('tobin', chars.LAMPLIGHTER, (0.0, 0.15, 0.02), 0.0)
# forearms laid on the desk
chars.set_arm(hero, 'L', (0.36, -0.52, 0.84), (0.62, -0.18, 0.66), (math.radians(-80), 0, 0))
chars.set_arm(hero, 'R', (-0.36, -0.52, 0.84), (-0.62, -0.18, 0.66), (math.radians(-80), 0, 0))
SH = json.load(open(PP + '/shots_room.json'))
k = next(iter(SH))
s = SH[k]
sc.camera = L.camera('CAM', s['pos'], s['tgt'], s['lens'], s['roll'], s.get('fstop'), s.get('focus'))
print('built', len(bpy.data.objects))
