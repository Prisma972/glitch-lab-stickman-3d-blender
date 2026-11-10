"""Poses and small actions for the bean characters. Everything is keyed on the rig empties, in the character's root space
(x to his left, -y in front of him, z up). Hands hang from the wrist along -Z; hand rotations turn that.
Use with anim.walk and anim.breathe(head=False) when the head is keyed here."""
import math
from mathutils import Vector
import chars

R = math.radians


def _m(p):
    """Mirror a left-side point to the right side."""
    return (-p[0], p[1], p[2])


def _mr(r):
    return (r[0], -r[1], -r[2])


def sym(hand, elbow, rot=(0, 0, 0)):
    return {'L': (hand, elbow, rot), 'R': (_m(hand), _m(elbow), _mr(rot))}


REST = sym((0.272, -0.02, 0.54), (0.335, 0.03, 0.70))
# name: {side: (wrist, elbow, hand rotation deg)}, plus optional torso (rx, ry, rz deg), head (rx, rz deg), lift (torso z)
POSES = {
    'rest': dict(REST),
    'hips': sym((0.235, 0.0, 0.60), (0.40, 0.06, 0.74), (0, -40, 0)),
    'behind': sym((0.12, 0.24, 0.58), (0.27, 0.14, 0.70)),
    'carry': sym((0.14, -0.31, 0.72), (0.29, -0.10, 0.68), (-55, 0, 20)),
    'shrug': dict(sym((0.42, -0.14, 0.86), (0.33, 0.02, 0.72), (0, -105, 0)), head=(0, 8), lift=0.015),
    'surprise': dict(sym((0.36, -0.12, 1.22), (0.40, 0.0, 0.92), (165, 0, -20)), torso=(6, 0, 0), head=(-8, 0)),
    'cheer': dict(sym((0.30, -0.06, 1.62), (0.33, 0.0, 1.22), (180, 0, 0)), head=(-10, 0)),
    'scared': dict(sym((0.16, -0.34, 1.0), (0.32, -0.12, 0.80), (170, 0, 0)), torso=(-6, 0, 0), head=(6, 0), lift=-0.03),
    'cross': {'L': ((-0.10, -0.26, 0.76), (0.26, -0.16, 0.75), (0, 90, 0)), 'R': ((0.10, -0.27, 0.79), (-0.26, -0.16, 0.77), (0, -90, 0))},
    'point': {'L': REST['L'], 'R': ((-0.30, -0.44, 1.00), (-0.24, -0.20, 0.92), (-90, 0, 0))},
    'wave': {'L': REST['L'], 'R': ((-0.40, -0.06, 1.32), (-0.42, 0.02, 0.98), (180, 0, 0))},
    'think': dict({'L': ((-0.08, -0.26, 0.70), (0.22, -0.16, 0.72), (0, 90, 0)), 'R': ((-0.05, -0.33, 0.86), (-0.22, -0.22, 0.72), (180, 0, 0))}, head=(-6, 10)),
    'facepalm': dict({'L': REST['L'], 'R': ((-0.08, -0.40, 1.06), (-0.30, -0.25, 0.82), (160, 0, 0))}, head=(12, 0), torso=(-4, 0, 0)),
    'reach': dict({'L': REST['L'], 'R': ((-0.16, -0.52, 0.56), (-0.22, -0.30, 0.78), (-30, 0, 0))}, torso=(-14, 0, 0), head=(10, 0)),
    'beckon': {'L': REST['L'], 'R': ((-0.22, -0.38, 0.92), (-0.30, -0.12, 0.76), (-120, 0, 0))},
}


def _key(o, attr, f):
    o.keyframe_insert(attr, frame=f)


def pose(ch, f, name, face=None, mix=1.0, base='rest'):
    """Keys a whole pose at frame f. mix < 1 blends it with `base`, for in-betweens."""
    p, b = POSES[name], POSES[base]
    J = ch['joints']
    for t in 'LR':
        h, e, r = p.get(t, b[t])
        h0, e0, r0 = b[t]
        J[t]['hd'].location = Vector(h0).lerp(Vector(h), mix)
        J[t]['el'].location = Vector(e0).lerp(Vector(e), mix)
        J[t]['hand'].rotation_euler = tuple(R(a0 + (a - a0) * mix) for a, a0 in zip(r, r0))
        _key(J[t]['hd'], 'location', f)
        _key(J[t]['el'], 'location', f)
        _key(J[t]['hand'], 'rotation_euler', f)
    tx, ty, tz = p.get('torso', (0, 0, 0))
    ch['torso'].rotation_euler = (R(tx * mix), R(ty * mix), R(tz * mix))
    ch['torso'].location = (0, 0, p.get('lift', 0.0) * mix)
    _key(ch['torso'], 'rotation_euler', f)
    _key(ch['torso'], 'location', f)
    hx, hz = p.get('head', (0, 0))
    ch['head'].rotation_euler = (R(hx * mix), 0, R(hz * mix))
    _key(ch['head'], 'rotation_euler', f)
    finger(ch, 'R', f, name == 'point' and mix > 0.5)
    if face:
        chars.set_face(ch, face, f)


def finger(ch, tag, f, on):
    """Shows the index finger of that mitt from frame f."""
    for o in ch['joints'][tag]['hand'].children_recursive:
        if o.name.endswith('_finger'):
            o.hide_render = not on
            o.keyframe_insert('hide_render', frame=f)


def wave(ch, f0, f1, period=8, amp=0.07):
    """Hand waves side to side from the wrist, R arm, on top of the 'wave' pose."""
    J = ch['joints']['R']
    h0 = Vector(POSES['wave']['R'][0])
    for f in range(f0, f1 + 1, 2):
        s = math.sin(2 * math.pi * (f - f0) / period)
        J['hd'].location = h0 + Vector((amp * s, 0, 0.02 * abs(s)))
        J['hand'].rotation_euler = (R(180), R(14 * s), 0)
        _key(J['hd'], 'location', f)
        _key(J['hand'], 'rotation_euler', f)


def nod(ch, f, n=2, deg=12, period=8):
    for i in range(n * 2 + 1):
        ch['head'].rotation_euler.x = R(deg if i % 2 else 0)
        _key(ch['head'], 'rotation_euler', f + i * period // 2)


def shake(ch, f, n=2, deg=16, period=8):
    for i in range(n * 2 + 1):
        ch['head'].rotation_euler.z = R(0 if i in (0, n * 2) else deg * (1 if i % 2 else -1))
        _key(ch['head'], 'rotation_euler', f + i * period // 2)


def hop(ch, f, height=0.14):
    """Surprise hop: dip 3 frames before, off the ground 4 frames, a small squash on landing."""
    r, t = ch['root'], ch['torso']
    z0 = r.location.z
    for df, rz, tz in ((-4, 0, 0), (-1, 0, -0.04), (2, height, 0.0), (4, height * 0.7, 0.0), (6, 0, -0.03), (9, 0, 0)):
        r.location.z = z0 + rz
        t.location.z = tz
        _key(r, 'location', f + df)
        _key(t, 'location', f + df)


def run(ch, f0, f1, start, end, **k):
    """A run is a fast walk: shorter period, higher feet, more swing and a forward lean."""
    import anim
    anim.walk(ch, f0, f1, start, end, period=k.pop('period', 6), lift=k.pop('lift', 0.15), arm=k.pop('arm', 0.20), bob=k.pop('bob', 0.03), **k)
    for f in range(f0, f1 + 1):
        ch['torso'].rotation_euler.x = R(-12)
        _key(ch['torso'], 'rotation_euler', f)


def sit(ch, f, seat=0.42):
    """Knees forward, feet under them, body on the seat. The coat hides most of the chair."""
    J = ch['joints']
    for t, sx in (('L', 1), ('R', -1)):
        J[t]['kn'].location = (sx * 0.10, -0.24, seat)
        J[t]['ft'].location = (sx * 0.10, -0.30, 0)
        _key(J[t]['kn'], 'location', f)
        _key(J[t]['ft'], 'location', f)
    ch['torso'].location = (0, 0, seat - chars.HIP_Z - 0.06 + 0.04)
    _key(ch['torso'], 'location', f)


def talk(ch, f0, f1, base='neutral', shapes=('talk_a', 'neutral', 'talk_o', 'talk_a', 'neutral'), every=3):
    """Mouth flaps over a spoken span; ends on base."""
    for i, f in enumerate(range(f0, f1, every)):
        chars.set_face(ch, shapes[i % len(shapes)], f)
    chars.set_face(ch, base, f1)
