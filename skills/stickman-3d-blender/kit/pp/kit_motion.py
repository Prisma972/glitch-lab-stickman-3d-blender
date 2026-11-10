"""Kit motion check: one hero, one locked camera, the actions of acts.py in a row. Frames 0-200, day street.
blender -b -P pp/kit_motion.py -> kit_motion.blend (kit root)"""
import os, sys, importlib, json
PP = os.path.join(os.environ['STICKMAN_KIT'], 'pp') if os.environ.get('STICKMAN_KIT') else os.path.dirname(os.path.abspath(__file__))
if PP not in sys.path:
    sys.path.insert(0, PP)
import common
importlib.reload(common)
from common import *
import acts
importlib.reload(acts)

BEATS = [(0, 'walk in'), (40, 'wave + talk'), (76, 'surprise hop'), (96, 'think + nod'), (124, 'shrug'), (140, 'point'), (166, 'run off')]


def build():
    G = run('build_street.py')
    hero, baker, clerk = G['hero'], G['baker'], G['clerk']
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 0, 200
    cam = sc.camera
    away(clerk, 0, 200)
    away(baker, 0, 200)
    for t, (h, e, r) in acts.POSES['rest'].items():
        chars.set_arm(hero, t, h, e, (0, 0, 0))
    spot = Vector((0.3, 2.2, 0))
    wk = dict(bob=0.018, lift=0.09)
    # walk in toward the lens
    anim.walk(hero, 0, 36, spot + Vector((0, 1.15, 0)), spot, period=8, **wk)
    anim.stand(hero, 38)
    for f in (0, 200):
        hero['root'].rotation_euler = (0, 0, 0)
        anim.key(hero['root'], 'rotation_euler', f)
    acts.pose(hero, 40, 'rest', face='neutral')
    # wave and talk
    acts.pose(hero, 46, 'wave', face='smile')
    acts.wave(hero, 48, 68)
    acts.talk(hero, 50, 66, base='smile')
    acts.pose(hero, 72, 'rest', face='neutral')
    # surprise: a small dip, then the hop with hands up
    acts.pose(hero, 79, 'surprise', mix=0.25, face='neutral_b')
    acts.pose(hero, 83, 'surprise', face='surprised')
    acts.hop(hero, 83)
    acts.pose(hero, 92, 'surprise', face='surprised')
    # think, then nod
    acts.pose(hero, 98, 'think', face='thinking')
    acts.pose(hero, 110, 'think', face='thinking')
    acts.nod(hero, 112, n=1)
    acts.pose(hero, 121, 'think', face='smile')
    # shrug
    acts.pose(hero, 128, 'shrug', face='skeptical')
    acts.pose(hero, 136, 'shrug', face='skeptical')
    # point off frame left
    acts.pose(hero, 143, 'point', face='determined')
    acts.pose(hero, 160, 'point', face='determined')
    acts.pose(hero, 165, 'rest', face='happy')
    # run off to the right
    for f, rz in ((166, 0), (170, 90)):
        hero['root'].rotation_euler = (0, 0, R(rz))
        anim.key(hero['root'], 'rotation_euler', f)
    acts.run(hero, 170, 200, spot, spot + Vector((3.2, -0.3, 0)))
    a = dict(pos=(0.6, -1.7, 1.2), tgt=(0.3, 2.2, 0.85), lens=36, roll=0)
    cam_hold(cam, 0, 200, a, 0.0008, 3.9, focus=spot + Vector((0, 0, 1.0)), fstop=6)
    L.matte_lights()
    bpy.ops.wm.save_as_mainfile(filepath=P + 'kit_motion.blend')
    os.makedirs(P + 'out', exist_ok=True)
    json.dump({str(f): t for f, t in BEATS}, open(P + 'out/kit_motion_beats.json', 'w'))
    print('kit_motion ok')


if __name__ == '__main__':
    build()
