"""The lamplighter: an original 8 s example scene of the kit, the proof that the setup works.
At dusk, Tobin the lamplighter reaches a street lamp and lights it with his pole; Mabel waves to him from the tea room door.
Characters and set come from the kit. One world, three shots joined by flights (the camera grammar of da-bible.md):
  S1 0-70 wide, he arrives | F1 70-90 flight to him | S2 90-150 the lantern lights up | F2 150-170 flight to Mabel | S3 170-239 she waves.
Build: blender -b -P shorts/allumeur/scene.py   (prints 'allumeur ok', writes shorts/allumeur/scene.blend)
Render: python pp/short.py shorts/allumeur/short.json [--preview]
Use it as the model for a new shot file: copy the bootstrap below, build a set with run(), cast, key, film, save.
"""
import sys, os, importlib, math
# find pp/ two folders up (or in STICKMAN_KIT), whatever folder Blender was started from
PP = os.path.join(os.environ.get('STICKMAN_KIT') or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'), 'pp')
PP = os.path.abspath(PP)
if PP not in sys.path:
    sys.path.insert(0, PP)
import common
importlib.reload(common)
from common import *
import acts
importlib.reload(acts)
from mathutils import Quaternion

OUT = P + 'shorts/allumeur/scene.blend'
LAMP = (-2.32, 7.6)                  # ST_lamp1 of the street, glass from z 3.98 to 4.48
TIP_TARGET = (-2.32, 7.6, 3.93)      # under the glass, where the flame goes in
H = (-1.70, 7.95)                    # Tobin at the lamp
START = (-0.95, 11.3)
RZ_WALK = R(-12.6)                   # facing his walk, toward the lens of S1
RZ_UP = R(25.5)                      # three quarters to the S2 lens, the lamp on his right
RZ_MAB = R(125)                      # turned to Mabel for S3
MAB = (2.45, 10.9)
RZ_M = R(-54.6)                      # Mabel faces Tobin
REST = {'L': ((0.272, -0.02, 0.54), (0.335, 0.03, 0.70)), 'R': ((-0.272, -0.02, 0.54), (-0.335, 0.03, 0.70))}
CARRY = ((-0.24, -0.14, 0.66), (-0.33, -0.02, 0.62))     # R hand holds the pole upright at his side
UP = ((-0.33, -0.16, 1.50), (-0.38, -0.04, 1.15))         # R hand high, the pole up to the lantern
GRIP = 0.32                          # pole length below the hand
# late dusk so the lamp matters, and a lamp that really lights the street (env overrides for look tests)
DUSK_K = float(os.environ.get('DUSK_K', 0.42))   # sun and fill
AMB_K = float(os.environ.get('AMB_K', 0.55))     # ambient
LAMP_K = float(os.environ.get('LAMP_K', 1.0))
GLASS_K = float(os.environ.get('GLASS_K', 1.0))
POLE_LEAN = tuple(float(x) for x in os.environ.get('POLE_LEAN', '0.45,-0.10,1.0').split(','))


def smooth(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


def lerp3(a, b, t):
    return tuple(x + (y - x) * t for x, y in zip(a, b))


def build():
    G = run('build_street.py')
    hero, baker, clerk, M, SET = G['hero'], G['baker'], G['clerk'], G['M'], G['SET']
    sc = bpy.context.scene
    L.apply_mood(sc, 'dusk')
    sc.frame_start, sc.frame_end = 0, 239
    cam = sc.camera

    # ---- dusk dressing: shops lit, upper windows dark blue, every lamp still out
    for nd in bpy.data.materials['ST_shop_in'].node_tree.nodes:
        if nd.type == 'EMISSION':
            nd.inputs['Strength'].default_value = 0.95
    mx = next(n for n in bpy.data.materials['ST_glass'].node_tree.nodes if n.type == 'MIX')
    mx.inputs[6].default_value = (0.03, 0.05, 0.12, 1)
    mx.inputs[7].default_value = (0.10, 0.13, 0.26, 1)
    for nd in bpy.data.materials['ST_lampglass'].node_tree.nodes:
        if nd.type == 'EMISSION':
            nd.inputs['Color'].default_value = (0.42, 0.36, 0.26, 1)
            nd.inputs['Strength'].default_value = 0.12
    brick = next(n for n in M['pave'].node_tree.nodes if n.type == 'TEX_BRICK')
    for k in ('Color1', 'Color2'):
        c = brick.inputs[k].default_value
        brick.inputs[k].default_value = (c[0] * 1.3, c[1] * 1.3, c[2] * 1.3, 1)

    # late dusk: an early-dusk street reads as daylight and hides the lamp. Sun, fill and ambient down;
    # the painted sky seen by the camera stays as it is.
    bpy.data.objects['PP_Sun'].data.energy *= DUSK_K
    bpy.data.objects['PP_Fill'].data.energy *= DUSK_K
    for nd in sc.world.node_tree.nodes:
        if nd.type == 'BACKGROUND' and abs(nd.inputs[1].default_value - 1.0) > 1e-3:
            nd.inputs[1].default_value *= AMB_K

    # the poster column stands where he stops: it goes
    for o in bpy.data.objects:
        if o.name.startswith('ST_column'):
            o.hide_render = True
    # ---- the lamp he lights: its own glass, keyed, plus a real light under the cap
    lit = L.glow_mat('T_lampon', (1.0, 0.60, 0.15), 0.12)
    bpy.data.objects['ST_lamp1_glass'].data.materials[0] = lit
    em = next(n for n in lit.node_tree.nodes if n.type == 'EMISSION')
    col = em.inputs['Color']
    # the glass must really glow, not just turn pale yellow, and its light must reach the street
    for f, s, c in ((0, 0.12, (0.42, 0.36, 0.26)), (117, 0.12, (0.42, 0.36, 0.26)), (119, 2.2 * GLASS_K, (1.0, 0.45, 0.06)),
                    (121, 1.1 * GLASS_K, (1.0, 0.38, 0.04)), (124, 1.5 * GLASS_K, (1.0, 0.38, 0.04)), (239, 1.5 * GLASS_K, (1.0, 0.38, 0.04))):
        em.inputs['Strength'].default_value = s
        em.inputs['Strength'].keyframe_insert('default_value', frame=f)
        col.default_value = (*c, 1)
        col.keyframe_insert('default_value', frame=f)
    ld = bpy.data.lights.new('T_lamplight', 'POINT')
    ld.color = (1.0, 0.62, 0.28)
    ld.shadow_soft_size = 0.12
    lo = bpy.data.objects.new('T_lamplight', ld)
    SET.objects.link(lo)
    lo.location = (LAMP[0], LAMP[1], 4.18)
    # the glass and cap of this lamp would shadow the light inside them: nothing would reach the street
    for o in bpy.data.objects:
        if o.name.startswith('ST_lamp1') and o.type == 'MESH':
            o.visible_shadow = False
    ld.shadow_soft_size = 0.06
    for f, e in ((0, 0), (117, 0), (119, 1300 * LAMP_K), (121, 750 * LAMP_K), (124, 1000 * LAMP_K), (239, 1000 * LAMP_K)):
        ld.energy = e
        ld.keyframe_insert('energy', frame=f)

    # ---- cast
    for ch in (hero, baker, clerk):
        for t, (h, e) in REST.items():
            chars.set_arm(ch, t, h, e, (0, 0, 0))
    away(clerk, 0, 239)

    # the pole: an empty on the right wrist, the shaft along its +Z, a brass hook and a small flame at the tip
    hd = hero['joints']['R']['hd']
    pole = L.empty('T_pole', (0, 0, 0), coll=SET)
    pole.parent = hd
    pole.rotation_mode = 'QUATERNION'
    tip_len = (Vector(to_local_at(hero, H, RZ_UP, TIP_TARGET)) - Vector(UP[0])).length
    plen = tip_len + GRIP
    wood = L.mat('T_polewood', (0.16, 0.08, 0.035), paint=0.06, form=0.3)
    brass = L.mat('T_brass', (0.55, 0.38, 0.10), paint=0.04, form=0.3)
    # a thin shaft (1.7 cm) vanishes in the wide shot: 2.6 cm, and a big bright flame with its own small light
    # so it warms his mitt and face on the way up
    L.cyl('T_pole_shaft', 0.026, plen, (0, 0, plen / 2 - GRIP), wood, SET, parent=pole, seg=12, w=0.006)
    L.cyl('T_pole_hook', 0.032, 0.10, (0, 0, tip_len - 0.05), brass, SET, parent=pole, seg=12, w=0.006)
    flame = L.sph('T_pole_flame', (0.055, 0.055, 0.09), (0, 0, tip_len + 0.05), L.glow_mat('T_flame', (1.0, 0.42, 0.06), 3.2), SET, parent=pole, seg=12)
    fd = bpy.data.lights.new('T_flamelight', 'POINT')
    fd.color = (1.0, 0.55, 0.18)
    fd.energy = 25
    fd.shadow_soft_size = 0.05
    fl_o = bpy.data.objects.new('T_flamelight', fd)
    SET.objects.link(fl_o)
    fl_o.parent = pole
    fl_o.location = (0, 0, tip_len + 0.12)
    for o in bpy.data.objects:
        if o.name.startswith('T_pole_'):
            o['ink_px'] = 2.4

    def pole_dir(f, d):
        """Points the shaft along local direction d (wrist space) at frame f."""
        q = Vector((0, 0, 1)).rotation_difference(Vector(d).normalized())
        pole.rotation_quaternion = q
        pole.keyframe_insert('rotation_quaternion', frame=f)

    # ---- S1 0-70: wide, he walks in with the pole, the lamps are out
    anim.walk(hero, 0, 56, (*START, 0), (*H, 0), period=9, bob=0.018, lift=0.08, hold={'R': CARRY})
    anim.stand(hero, 58)
    r = hero['root']
    for f, rz in ((0, RZ_WALK), (56, RZ_WALK), (70, RZ_UP)):
        r.rotation_euler = (0, 0, rz)
        r.keyframe_insert('rotation_euler', frame=f)
    place(hero, 70, 150, (*H, 0), RZ_UP)
    upright = (0, -0.10, 1.0)
    pole_dir(0, upright)
    pole_dir(88, upright)
    s1 = dict(pos=(1.0, 1.0, 1.6), tgt=(-1.2, 9.5, 2.0), lens=30, roll=0)
    end1 = cam_hold(cam, 0, 70, s1, .0022, 9.0)

    # ---- F1 70-90: fly in low, looking up at him and the lantern
    s2 = dict(pos=(-0.15, 3.9, 1.15), tgt=(-2.0, 8.0, 2.35), lens=28, roll=0)   # wider: him from the knees up and the lantern
    focus2 = (*H, 1.4)
    cam_shot(cam, 70, 90, end1, s2, ((H[0], H[1], 1.2), focus2), 8, curve=anim.IN)

    # ---- S2 90-150: up goes the pole, the flame enters the glass, the lantern catches
    up_local = Vector(to_local_at(hero, H, RZ_UP, TIP_TARGET)) - Vector(UP[0])
    keys = [(70, *CARRY)]
    for f in range(88, 111):
        t = smooth((f - 88) / 22)
        keys.append((f, lerp3(CARRY[0], UP[0], t), lerp3(CARRY[1], UP[1], t)))
        pole_dir(f, Vector(upright).lerp(up_local.normalized(), t))
    keys += [(122, *UP), (130, *UP)]
    for f in range(138, 161):                       # back down after the light takes
        t = smooth((f - 138) / 22)
        keys.append((f, lerp3(UP[0], CARRY[0], t), lerp3(UP[1], CARRY[1], t)))
        pole_dir(f, up_local.normalized().lerp(Vector(upright), t))
    key_hand(hero, 'R', keys)
    key_hand(hero, 'L', [(0, *REST['L']), (239, *REST['L'])])
    show(flame, 0, False)
    show(flame, 86, True)
    show(flame, 128, False)                         # the flame stays in the lantern
    show(fl_o, 0, False)
    show(fl_o, 86, True)
    show(fl_o, 128, False)
    head_key(hero, [(0, 0, 0), (92, 0, 0), (106, -20, -24), (140, -20, -24), (158, 0, 0)])
    chars.set_face(hero, 'neutral', 0)
    chars.set_face(hero, 'thinking', 98)
    chars.set_face(hero, 'happy', 122)
    anim.breathe(hero, 58, 239, amp=0.005, head=False)
    end2 = cam_hold(cam, 90, 150, s2, .0024, 3.8, focus=focus2, fstop=5.6)

    # ---- F2 150-170: fly out and round, over his shoulder to Mabel at the tea room door
    s3 = dict(pos=(-3.46, 5.60, 1.62), tgt=(2.45, 10.9, 1.20), lens=35, roll=0)   # behind him on the line to Mabel: his back in the left foreground
    focus3 = (*MAB, 1.3)
    cam_shot(cam, 150, 170, end2, s3, (focus2, focus3), 5, curve=anim.OUT)
    for f in range(150, 171):
        k = anim.OUT((f - 150) / 20)
        r.rotation_euler = (0, 0, RZ_UP + (RZ_MAB - RZ_UP) * k)
        r.keyframe_insert('rotation_euler', frame=f)
    place(hero, 171, 239, (*H, 0), RZ_MAB)

    # ---- S3 170-239: she waves, he nods and lifts the pole to her
    place(baker, 0, 239, (*MAB, 0), RZ_M)
    anim.breathe(baker, 0, 239)
    chars.set_face(baker, 'smile', 0)
    acts.pose(baker, 172, 'rest', face='smile')
    acts.pose(baker, 180, 'wave', face='happy')
    acts.wave(baker, 182, 222)
    acts.pose(baker, 230, 'rest', face='smile')
    lift = (CARRY[0][0], CARRY[0][1], CARRY[0][2] + 0.16)
    key_hand(hero, 'R', [(186, *CARRY), (192, lift, CARRY[1]), (202, lift, CARRY[1]), (210, *CARRY)])
    acts.nod(hero, 194, n=1)
    # upright, the shaft cuts the tea room sign: in S3 it leans on his shoulder, out of the sign
    lean = Vector(upright).lerp(Vector(POLE_LEAN), 1.0)
    pole_dir(160, upright)
    for f in range(160, 175):
        pole_dir(f, Vector(upright).lerp(lean, smooth((f - 160) / 14)))
    pole_dir(239, lean)
    chars.set_face(hero, 'smile', 172)
    cam_hold(cam, 170, 239, s3, .0018, 5.5, focus=focus3, fstop=4)
    cam.data.dof.use_dof = True

    L.matte_lights()
    bpy.ops.wm.save_as_mainfile(filepath=OUT)
    print('allumeur ok')


def to_local_at(ch, loc, rz, w):
    """World point in the root space of a character standing at loc with rotation rz (before the root is keyed there)."""
    v = Vector(w) - Vector((*loc, 0))
    c, s = math.cos(-rz), math.sin(-rz)
    return (v.x * c - v.y * s, v.x * s + v.y * c, v.z)


if __name__ == '__main__':
    build()
