"""Kit check blend: every expression on the hero and on a plain character, every pose on the hero, in the day street.
blender -b -P pp/kit_board.py  ->  kit.blend (kit root), labels in out/kit_labels.json. Frames: faces hero 0-21, faces plain 30-51, poses 60-74. See BOARD for labels."""
import os, sys, importlib, json
PP = os.path.join(os.environ['STICKMAN_KIT'], 'pp') if os.environ.get('STICKMAN_KIT') else os.path.dirname(os.path.abspath(__file__))
if PP not in sys.path:
    sys.path.insert(0, PP)
import common
importlib.reload(common)
from common import *
import acts
importlib.reload(acts)

EXPR = [n for n in chars.ATLAS['families']['hero'][6:]]
POSE_FACE = [('rest', 'neutral'), ('hips', 'determined'), ('behind', 'sly'), ('carry', 'neutral'), ('shrug', 'skeptical'), ('surprise', 'surprised'),
             ('cheer', 'happy'), ('scared', 'scared'), ('cross', 'angry'), ('point', 'determined'), ('wave', 'smile'), ('think', 'thinking'),
             ('facepalm', 'embarrassed'), ('reach', 'worried'), ('beckon', 'sly')]
BOARD = {}


def build():
    G = run('build_street.py')
    hero, baker, clerk = G['hero'], G['baker'], G['clerk']
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 0, 74
    cam = sc.camera
    away(clerk, 0, 74)
    spot = (0.3, 2.2, 0)
    for ch in (hero, baker):
        for t, (h, e, r) in acts.POSES['rest'].items():
            chars.set_arm(ch, t, h, e, (0, 0, 0))
    close = dict(pos=(0.3, 0.35, 1.22), tgt=(0.3, 2.2, 1.14), lens=48, roll=0)
    wide = dict(pos=(0.75, -1.4, 1.15), tgt=(0.3, 2.2, 0.82), lens=40, roll=0)
    # hero faces
    place(hero, 0, 21, spot)
    away(baker, 0, 21)
    for i, n in enumerate(EXPR):
        chars.set_face(hero, n, i)
        BOARD[i] = 'hero ' + n
    # plain faces on the baker
    away(hero, 30, 51)
    place(baker, 30, 51, spot)
    for i, n in enumerate(EXPR):
        chars.set_face(baker, n, 30 + i)
        BOARD[30 + i] = 'plain ' + n
    # poses
    place(hero, 60, 74, spot, R(-12))
    away(baker, 60, 74)
    for i, (p, fc) in enumerate(POSE_FACE):
        acts.pose(hero, 60 + i, p, face=fc)
        BOARD[60 + i] = f'pose {p} / {fc}'
    for f in range(0, 75):
        a = close if f < 60 else wide
        anim._key_cam(cam, f, Vector(a['pos']), Vector(a['tgt']), a['lens'], 0, Vector(spot) + Vector((0, 0, 1.2 if f < 60 else 0.9)))
    cam.data.dof.use_dof = True
    cam.data.dof.aperture_fstop = 5.6
    for o in (hero['root'], baker['root'], cam):
        for fc in chars._fcurves(o):
            for k in fc.keyframe_points:
                k.interpolation = 'CONSTANT'
    L.matte_lights()
    bpy.ops.wm.save_as_mainfile(filepath=P + 'kit.blend')
    os.makedirs(P + 'out', exist_ok=True)
    json.dump(BOARD, open(P + 'out/kit_labels.json', 'w'), indent=0)
    print('kit ok')


if __name__ == '__main__':
    build()
