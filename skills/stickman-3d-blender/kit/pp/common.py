"""Shared helpers for shot files (shorts/<slug>/<clip>.py): `from common import *`.
Gives bpy, Vector, look as L, chars, anim, R (degrees to radians), P (the kit root with a trailing slash),
run() to build a set, and the placement, visibility, hand, head, camera and prop helpers below.
Example: shorts/allumeur/scene.py.
"""
import os, sys, importlib, math
import bpy, bmesh
from mathutils import Vector
import kitpath
PP = kitpath.PP
P = kitpath.KIT + '/'
T = kitpath.TEX + '/signs'
import look, chars, anim
for m in (look, chars, anim):
    importlib.reload(m)
L = look
R = math.radians


def run(build):
    """run('build_street.py'): builds a set of pp/ in the open scene and returns its globals (hero, baker, clerk, SET, M...)."""
    path = f'{PP}/{build}'
    G = {'__name__': '__main__', '__file__': path}
    exec(compile(open(path, encoding='utf-8').read(), path, 'exec'), G)
    return G


def place(ch, f0, f1, loc, rz=0.0):
    r = ch['root']
    for f in (f0, f1):
        r.location = loc
        r.rotation_euler = (0, 0, rz)
        r.keyframe_insert('location', frame=f)
        r.keyframe_insert('rotation_euler', frame=f)


def away(ch, f0, f1):
    place(ch, f0, f1, (0, 0, -60))


def show(o, f, on):
    """Children too: hide_render does not inherit, and a hidden prop would leave its parts floating."""
    for x in (o, *o.children_recursive):
        x.hide_render = not on
        x.keyframe_insert('hide_render', frame=f)


def to_local(ch, w):
    loc = ch['root'].location
    rz = ch['root'].rotation_euler.z
    v = Vector(w) - loc
    c, s = math.cos(-rz), math.sin(-rz)
    return (v.x * c - v.y * s, v.x * s + v.y * c, v.z)


def key_hand(ch, tag, keys):
    """keys: [(frame, hand_loc, elbow_loc)]"""
    j = ch['joints'][tag]
    for f, h, e in keys:
        j['hd'].location = h
        j['el'].location = e
        j['hd'].keyframe_insert('location', frame=f)
        j['el'].keyframe_insert('location', frame=f)


def head_key(ch, keys):
    for f, rx, rz in keys:
        ch['head'].rotation_euler = (R(rx), 0, R(rz))
        ch['head'].keyframe_insert('rotation_euler', frame=f)


def wallet(name, coll, parent=None, loc=(0, 0, 0), rot=(0, 0, 0)):
    m = L.mat('T_wallet', (0.27, 0.12, 0.05), paint=0.08, form=0.3)
    o = L.box(name, (0.15, 0.03, 0.2), loc, m, coll, rot=rot, parent=parent, w=0.0012, bevel=0.012)
    o['ink_px'] = 2.4
    L.box(name + '_st', (0.12, 0.034, 0.008), (0, 0, 0.078), L.mat('T_wstitch', (0.70, 0.52, 0.28), paint=0), coll, parent=o)
    return o


def plane_uv(name, w, h, loc, m, coll, rot=(0, 0, 0), parent=None):
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new()
    vs = [bm.verts.new((x * w / 2, y * h / 2, 0)) for x, y in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    f = bm.faces.new(vs)
    for l, c in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
        l[uv].uv = c
    return L.obj_from_bm(name, bm, m, coll, loc=loc, rot=rot, parent=parent)


def postbox(c, loc, rz=R(45)):
    red = L.mat('T_red', (0.56, 0.035, 0.03), paint=0.05, form=0.32)
    blk = L.mat('T_blk', (0.02, 0.02, 0.025), paint=0)
    root = L.empty('T_box', (*loc, 0), coll=c, rot=(0, 0, rz))
    L.lathe('T_bx_base', [(0.43, 0), (0.43, 0.1), (0.36, 0.17), (0.34, 0.2)], blk, c, parent=root, seg=40, w=0.012)
    L.cyl('T_bx_body', 0.335, 1.26, (0, 0, 0.82), red, c, parent=root, seg=48, w=0.012)
    L.lathe('T_bx_cap', [(0.36, 1.44), (0.385, 1.47), (0.385, 1.51), (0.33, 1.56), (0.19, 1.64), (0.06, 1.69), (0, 1.71)], red, c, parent=root, seg=48, w=0.012)
    L.lathe('T_bx_band', [(0.35, 1.39), (0.35, 1.43)], blk, c, parent=root, seg=48, w=0.004)
    L.box('T_bx_slotp', (0.08, 0.5, 0.15), (-0.325, 0, 1.28), red, c, parent=root, w=0.01)
    L.box('T_bx_hood', (0.16, 0.54, 0.05), (-0.36, 0, 1.365), red, c, parent=root, w=0.01)
    L.box('T_bx_slot', (0.03, 0.4, 0.05), (-0.366, 0, 1.285), blk, c, parent=root)
    L.box('T_bx_door', (0.03, 0.4, 0.56), (-0.335, 0, 0.74), red, c, parent=root, w=0.009)
    pl = L.tex_mat('T_postplate', f'{T}/post.png')
    plane_uv('T_bx_plate', 0.3, 0.12, (-0.356, 0, 0.92), pl, c, rot=(R(90), 0, R(-90)), parent=root)
    return root


def key_reveal(o, frames):
    for f, v in frames:
        o['reveal'] = float(v)
        o.keyframe_insert('["reveal"]', frame=f)


def note_mat(name, path):
    m, nt = L._new(name)
    lk = nt.links.new
    tc = nt.nodes.new('ShaderNodeTexCoord')
    ti = nt.nodes.new('ShaderNodeTexImage')
    ti.image = bpy.data.images.load(path, check_existing=True)
    ti.extension = 'CLIP'
    lk(tc.outputs['UV'], ti.inputs[0])
    sp = nt.nodes.new('ShaderNodeSeparateXYZ')
    lk(tc.outputs['UV'], sp.inputs[0])
    at = nt.nodes.new('ShaderNodeAttribute')
    at.attribute_type = 'OBJECT'
    at.attribute_name = 'reveal'
    lt = nt.nodes.new('ShaderNodeMath')
    lt.operation = 'LESS_THAN'
    lk(sp.outputs[0], lt.inputs[0])
    lk(at.outputs['Fac'], lt.inputs[1])
    mu = nt.nodes.new('ShaderNodeMath')
    mu.operation = 'MULTIPLY'
    lk(lt.outputs[0], mu.inputs[0])
    lk(ti.outputs[1], mu.inputs[1])
    em = nt.nodes.new('ShaderNodeEmission')
    lk(ti.outputs[0], em.inputs[0])
    tr = nt.nodes.new('ShaderNodeBsdfTransparent')
    ms = nt.nodes.new('ShaderNodeMixShader')
    lk(mu.outputs[0], ms.inputs[0])
    lk(tr.outputs[0], ms.inputs[1])
    lk(em.outputs[0], ms.inputs[2])
    o = nt.nodes.new('ShaderNodeOutputMaterial')
    lk(ms.outputs[0], o.inputs[0])
    m.surface_render_method = 'BLENDED'
    return m


def _fstop(cam, f0, f1, fstop):
    cam.data.dof.use_dof = fstop is not None
    if fstop:
        cam.data.dof.aperture_fstop = fstop
        cam.data.dof.keyframe_insert('aperture_fstop', frame=f0)
        cam.data.dof.keyframe_insert('aperture_fstop', frame=f1)


def cam_shot(cam, f0, f1, a, b=None, focus=None, fstop=None, curve=None, aim=None):
    """Move from pose a to pose b. focus: (point at a, point at b). curve: anim.ease, lin, IN or OUT. Returns the end pose."""
    b = b or a
    _fstop(cam, f0, f1, fstop)
    return anim.camera_move(cam, f0, f1, a, b, focus[0] if focus else None, focus[1] if focus else None, curve=curve or anim.ease, aim=aim)


def cam_hold(cam, f0, f1, a, rate, dist, push=None, focus=None, fstop=None):
    """Locked creep from pose a, see anim.hold. Returns the last pose, the start of the next move."""
    _fstop(cam, f0, f1, fstop)
    return anim.hold(cam, f0, f1, a, rate, dist, push, focus)


def key_ink(names, keys):
    """Hull width per shot, held constant between keys. keys: [(frame, width)]."""
    for n in names:
        o = bpy.data.objects.get(n)
        md = o.modifiers.get('PP_ink') if o else None
        if md is None:
            continue
        for f, w in keys:
            md.thickness = w
            md.keyframe_insert('thickness', frame=f)
        for fc in chars._fcurves(o):
            if 'thickness' in fc.data_path:
                for k in fc.keyframe_points:
                    k.interpolation = 'CONSTANT'
