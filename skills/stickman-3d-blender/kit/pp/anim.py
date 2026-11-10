"""Character and camera motion.
Walk: planted feet, 60/40 stance, head dips on contact. Camera grammar measured on reference shorts:
holds are a constant dolly toward frame centre, shots join by real flights (IN ramps up late, OUT snaps early and glides)."""
import math
import bpy
from mathutils import Vector
import chars
import look as L


def key(o, attr, f):
    o.keyframe_insert(attr, frame=f)


def ease(t):
    return t * t * t * (t * (6 * t - 15) + 10)


def lin(t):
    return t


def _table(tb):
    n = len(tb) - 1

    def c(x):
        x = min(max(x, 0.0), 1.0) * n
        i = min(int(x), n - 1)
        return tb[i] + (tb[i + 1] - tb[i]) * (x - i)
    return c


# flight profiles measured from the reference
IN = _table([0, .01, .03, .06, .12, .21, .38, .57, .72, .86, .95, .99, 1])
OUT = _table([0, .04, .11, .32, .48, .63, .77, .85, .91, .95, .97, .99, 1])


def rest_pose(ch):
    """Arm pose the walk swings around. Captured once, so a walk never inherits the last swung frame of the previous one."""
    if 'rest' not in ch:
        J = ch['joints']
        ch['rest'] = {t: (J[t]['hd'].location.copy(), J[t]['el'].location.copy()) for t in 'LR'}
    return ch['rest']


def walk(ch, f0, f1, start, end, period=26, lift=0.085, arm=0.10, bob=0.016, hold=None, release=None, curve=None):
    """Root travels start -> end in a straight line; feet stay planted during stance.
    hold: {tag: (hand, elbow)} pins that hand on the body with a small sway.
    release: (fa, fb) the held hand goes back to the free swing between these frames.
    curve: optional time curve for the root, for a walk carried by a flight."""
    root, torso, J = ch['root'], ch['torso'], ch['joints']
    start, end = Vector(start), Vector(end)
    n = max(1, f1 - f0)
    v = (end - start).length / n
    amp = v * period * 0.6 / 2          # half stance length in root-local Y
    rest = rest_pose(ch)
    hz = chars.BODY_TOP + 0.20
    for f in range(f0, f1 + 1):
        t = (f - f0) / n
        root.location = start.lerp(end, curve(t) if curve else t)
        key(root, 'location', f)
        ph = (f - f0) / period
        w = 2 * math.pi * ph
        for tag, off in (('L', 0.0), ('R', 0.5)):
            u = (ph + off) % 1.0
            j = J[tag]
            sx = 1 if tag == 'L' else -1
            if u < 0.6:                 # stance: foot slides back in root space
                y = -amp + 2 * amp * (u / 0.6)
                z = 0.0
            else:                       # swing: lifts and passes forward
                s = (u - 0.6) / 0.4
                y = amp - 2 * amp * (s * s * (3 - 2 * s))
                z = lift * math.sin(math.pi * s)
            j['ft'].location = (sx * 0.10, y, z)
            j['ft'].rotation_euler = (math.radians(14) * math.sin(math.pi * max(0, (u - 0.6) / 0.4)) * -1, 0, 0)
            key(j['ft'], 'location', f)
            key(j['ft'], 'rotation_euler', f)
            j['kn'].location = (sx * 0.10, y * 0.55 - 0.03, 0.22 + z * 0.75)
            key(j['kn'], 'location', f)
            # free arm: swings against the leg on the same side, out and up on the back swing, so it reads from the front
            sw = math.cos(2 * math.pi * (ph + off))
            h = rest[tag][0].copy()
            e = rest[tag][1].copy()
            h.y += sw * arm
            h.z += 0.07 * sw
            h.x += sx * 0.058 * sw
            e.y += sw * arm * 0.45
            e.x += sx * 0.03 * sw
            if hold and tag in hold:
                ph_, pe_ = Vector(hold[tag][0]), Vector(hold[tag][1])
                ph_ = ph_ + Vector((0.02 * math.sin(w), 0.0, 0.012 * math.cos(w)))
                k = 0.0
                if release:
                    k = min(max((f - release[0]) / max(1, release[1] - release[0]), 0.0), 1.0)
                    k = k * k * (3 - 2 * k)
                h = ph_.lerp(h, k)
                e = pe_.lerp(e, k)
            j['hd'].location = h
            j['el'].location = e
            key(j['hd'], 'location', f)
            key(j['el'], 'location', f)
        # lowest on contact, highest at passing. The head out-bobs the coat a little
        torso.location = (0.0, 0.0, -bob * math.cos(2 * w) - bob)
        torso.rotation_euler = (math.radians(-3), math.radians(1.8) * math.sin(w), math.radians(4) * math.sin(w))
        key(torso, 'location', f)
        key(torso, 'rotation_euler', f)
        # the -3.2 z term cancels the torso yaw, so the face stays flat to the lens
        ch['head'].rotation_euler = (math.radians(2.0) * math.cos(2 * w), math.radians(-1.6) * math.sin(w), math.radians(-3.2) * math.sin(w))
        key(ch['head'], 'rotation_euler', f)
        ch['head'].location.z = hz - 0.007 * math.cos(2 * w)
        key(ch['head'], 'location', f)


def stand(ch, f, head=True):
    """Both feet on the ground, side by side, body at rest. Call at the end of a walk."""
    J = ch['joints']
    for tag, sx in (('L', 1), ('R', -1)):
        j = J[tag]
        j['ft'].location = (sx * 0.10, 0, 0)
        j['ft'].rotation_euler = (0, 0, 0)
        j['kn'].location = (sx * 0.095, -0.015, 0.17)
        key(j['ft'], 'location', f)
        key(j['ft'], 'rotation_euler', f)
        key(j['kn'], 'location', f)
    ch['torso'].location = (0, 0, 0)
    ch['torso'].rotation_euler = (0, 0, 0)
    key(ch['torso'], 'location', f)
    key(ch['torso'], 'rotation_euler', f)
    if head:
        ch['head'].location.z = chars.BODY_TOP + 0.20
        key(ch['head'], 'location', f)


def blinks(ch, frames, open_face=None, closed_face=None):
    a = open_face or ch['faces'][0]
    b = closed_face or ch['faces'][1]
    chars.set_face(ch, a, 0)
    for f in frames:
        chars.set_face(ch, b, f)
        chars.set_face(ch, a, f + 4)


def breathe(ch, f0, f1, amp=0.010, period=70, head=True, yaw=0.0):
    """Idle: slow chest rise and a small head drift, so no hold is frozen.
    head=False leaves the head curve free for head keys: mixing both makes the head twitch between keys.
    yaw turns the head (degrees) for the length of the idle."""
    for f in range(f0, f1 + 1, 4):
        w = 2 * math.pi * (f - f0) / period
        ch['torso'].location.z = amp * math.sin(w)
        key(ch['torso'], 'location', f)
        if head:
            ch['head'].rotation_euler = (math.radians(1.2) * math.sin(w * 0.7), 0, math.radians(yaw) + math.radians(1.8) * math.sin(w * 0.5))
            key(ch['head'], 'rotation_euler', f)


def _key_cam(cam, f, p, g, lens, roll, focus=None):
    q = (g - p).to_track_quat('-Z', 'Y')
    cam.location = p
    cam.rotation_euler = q.to_euler()
    cam.rotation_euler.rotate_axis('Z', math.radians(roll))
    cam.data.lens = lens
    key(cam, 'location', f)
    key(cam, 'rotation_euler', f)
    cam.data.keyframe_insert('lens', frame=f)
    if focus is not None:
        cam.data.dof.focus_distance = (Vector(focus) - p).length
        cam.data.dof.keyframe_insert('focus_distance', frame=f)


def _aimed(p, g, aim):
    p, g = Vector(p), Vector(g)
    return p + (g - p).normalized() * (Vector(aim) - p).length


def camera_move(cam, f0, f1, a, b, focus_a=None, focus_b=None, curve=ease, aim=None):
    """a, b: dicts pos/tgt/lens/roll, keyed on every frame. Returns b.
    aim: the targets are first moved to the subject's distance, so a lerp sweeps around the subject
    instead of swinging past it. curve: ease, lin, IN, OUT or any 0..1 function."""
    n = max(1, f1 - f0)
    ga = _aimed(a['pos'], a['tgt'], aim) if aim else Vector(a['tgt'])
    gb = _aimed(b['pos'], b['tgt'], aim) if aim else Vector(b['tgt'])
    for f in range(f0, f1 + 1):
        t = curve((f - f0) / n)
        p = Vector(a['pos']).lerp(Vector(b['pos']), t)
        g = ga.lerp(gb, t)
        r = a['roll'] + (b['roll'] - a['roll']) * t
        focus = None
        if focus_a is not None:
            focus = Vector(focus_a).lerp(Vector(focus_b or focus_a), t)
        _key_cam(cam, f, p, g, a['lens'] + (b['lens'] - a['lens']) * t, r, focus)
    return b


def hold(cam, f0, f1, a, rate, dist, push=None, focus=None):
    """A locked shot: straight constant dolly toward frame centre, no pan, no roll change, full speed from f0.
    The image scale grows by rate per frame at the subject's distance dist. push: scale steps that replace
    the last frames, for the acceleration into a hard cut. Returns the last pose, which starts the next move."""
    pos, tgt = Vector(a['pos']), Vector(a['tgt'])
    v = (tgt - pos).normalized()
    push = list(push or [])
    s = 1.0
    p, g = pos, tgt
    for i, f in enumerate(range(f0, f1 + 1)):
        if i:
            left = f1 - f
            s *= 1 + (push[len(push) - 1 - left] if left < len(push) else rate)
        off = v * dist * (1 - 1 / s)
        p, g = pos + off, tgt + off
        _key_cam(cam, f, p, g, a['lens'], a['roll'], focus)
    return dict(pos=tuple(p), tgt=tuple(g), lens=a['lens'], roll=a['roll'])
