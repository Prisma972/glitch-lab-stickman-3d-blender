"""Builds the night village (hip-roof houses on a grid) for aerial shots."""
import os, sys, importlib, math, json
import bpy
PP = os.path.join(os.environ['STICKMAN_KIT'], 'pp') if os.environ.get('STICKMAN_KIT') else os.path.dirname(os.path.abspath(__file__))
if PP not in sys.path:
    sys.path.insert(0, PP)
import look, village
for m in (look, village):
    importlib.reload(m)
L = look
L.wipe()
sc = bpy.context.scene
L.fog_group()
L.setup(sc, 'night')
village.build()
SH = json.load(open(PP + '/shots_village.json'))
s = SH['over']
sc.camera = L.camera('CAM', s['pos'], s['tgt'], s['lens'], s['roll'], s.get('fstop'), s.get('focus'))
print('built', len(bpy.data.objects))
