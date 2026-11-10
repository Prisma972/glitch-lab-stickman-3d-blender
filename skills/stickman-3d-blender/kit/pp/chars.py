"""Bean characters: white ball head with painted-on face decal, tapered coat body, stick limbs, mitten gloves.
Limbs are Geometry Nodes bezier tubes driven by empties, so posing = moving empties (animatable, viewport-live).
Units metres. Character faces -Y.
"""
import bpy, bmesh, math, json
from mathutils import Vector
import look as L

FACES = L.ROOT + '/tex/faces'
STICK = (0.022, 0.017, 0.015)
SKIN = (0.95, 0.96, 1.0)
HEAD_R = 0.30
HEAD_GLOW = [0.88]
GLOVE_GLOW = [0.35]
BODY_TOP = 1.04
HIP_Z = 0.40


ATLAS = json.load(open(FACES + '/atlas.json'))      # written by faces.py: families of expressions, tile grid


def head_mat(family='hero'):
    """White ball with the face projected front-on from object XZ. One atlas image per family: the object's 'face'
    property is the tile index, so any number of expressions costs a single texture."""
    name = 'CH_head_' + family
    if name in bpy.data.materials and bpy.data.materials[name].get('pp'):
        return bpy.data.materials[name]
    m, nt = L._new(name)
    lk = nt.links.new

    def op(kind, a, b=None):
        n = nt.nodes.new('ShaderNodeMath')
        n.operation = kind
        for i, x in enumerate((a, b)):
            if x is None:
                continue
            if isinstance(x, (int, float)):
                n.inputs[i].default_value = x
            else:
                lk(x, n.inputs[i])
        return n.outputs[0]

    tc = nt.nodes.new('ShaderNodeTexCoord')
    sp = nt.nodes.new('ShaderNodeSeparateXYZ')
    lk(tc.outputs['Object'], sp.inputs[0])
    u = op('MULTIPLY_ADD', sp.outputs[0], 0.5 / HEAD_R)
    u.node.inputs[2].default_value = 0.5
    v = op('MULTIPLY_ADD', sp.outputs[2], 0.5 / HEAD_R)
    v.node.inputs[2].default_value = 0.5
    at = nt.nodes.new('ShaderNodeAttribute')
    at.attribute_type = 'OBJECT'
    at.attribute_name = 'face'
    cols, rows = ATLAS['cols'], ATLAS['rows']
    col_i = op('MODULO', at.outputs['Fac'], cols)
    row_i = op('FLOOR', op('DIVIDE', at.outputs['Fac'], cols))
    cb = nt.nodes.new('ShaderNodeCombineXYZ')
    lk(op('DIVIDE', op('ADD', u, col_i), cols), cb.inputs[0])
    lk(op('DIVIDE', op('ADD', v, op('SUBTRACT', rows - 1, row_i)), rows), cb.inputs[1])
    ti = nt.nodes.new('ShaderNodeTexImage')
    ti.image = bpy.data.images.load(f'{FACES}/atlas_{family}.png', check_existing=True)
    ti.extension = 'CLIP'
    ti.interpolation = 'Linear'
    lk(cb.outputs[0], ti.inputs[0])
    # only inside this tile, and only on the front of the ball
    inside = op('MULTIPLY', op('MULTIPLY', op('GREATER_THAN', u, 0.0), op('LESS_THAN', u, 1.0)),
                op('MULTIPLY', op('GREATER_THAN', v, 0.0), op('LESS_THAN', v, 1.0)))
    alpha = op('MULTIPLY', op('MULTIPLY', ti.outputs['Alpha'], inside), op('LESS_THAN', sp.outputs[1], 0.0))
    base = nt.nodes.new('ShaderNodeRGB')
    base.outputs[0].default_value = (*SKIN, 1)
    mx = nt.nodes.new('ShaderNodeMix')
    mx.data_type = 'RGBA'
    lk(alpha, mx.inputs[0])
    lk(base.outputs[0], mx.inputs[6])
    lk(ti.outputs['Color'], mx.inputs[7])
    col = mx.outputs[2]
    # the head is lit by paint, not by the scene: a cool grey falls off low on the ball, so cast
    # shadows from the hat can never draw a hard wedge across the face
    sz = nt.nodes.new('ShaderNodeSeparateXYZ')
    lk(tc.outputs['Normal'], sz.inputs[0])
    mr = nt.nodes.new('ShaderNodeMapRange')
    mr.inputs['From Min'].default_value = -0.85
    mr.inputs['From Max'].default_value = 0.6
    lk(sz.outputs[2], mr.inputs['Value'])
    gr = nt.nodes.new('ShaderNodeMix'); gr.data_type = 'RGBA'
    gr.inputs[6].default_value = (0.66, 0.68, 0.74, 1)
    gr.inputs[7].default_value = (1, 1, 1, 1)
    lk(mr.outputs[0], gr.inputs[0])
    sh = nt.nodes.new('ShaderNodeMix'); sh.data_type = 'RGBA'; sh.blend_type = 'MULTIPLY'
    sh.inputs[0].default_value = 1.0
    lk(col, sh.inputs[6]); lk(gr.outputs[2], sh.inputs[7])
    # rim falloff: the ball turns soft grey toward its silhouette
    lw = nt.nodes.new('ShaderNodeLayerWeight')
    lw.inputs['Blend'].default_value = 0.5
    rf = nt.nodes.new('ShaderNodeMapRange')
    rf.inputs['From Min'].default_value = 0.25
    rf.inputs['From Max'].default_value = 0.8
    rf.inputs['To Min'].default_value = 1.0
    rf.inputs['To Max'].default_value = 0.84
    lk(lw.outputs['Facing'], rf.inputs['Value'])
    rc = nt.nodes.new('ShaderNodeCombineColor')
    for i_ in range(3):
        lk(rf.outputs[0], rc.inputs[i_])
    sh2 = nt.nodes.new('ShaderNodeMix'); sh2.data_type = 'RGBA'; sh2.blend_type = 'MULTIPLY'
    sh2.inputs[0].default_value = 1.0
    lk(sh.outputs[2], sh2.inputs[6]); lk(rc.outputs[0], sh2.inputs[7])
    dim = nt.nodes.new('ShaderNodeMix'); dim.data_type = 'RGBA'; dim.blend_type = 'MULTIPLY'
    dim.inputs[0].default_value = 1.0
    dim.inputs[7].default_value = (0.2, 0.2, 0.2, 1)
    lk(col, dim.inputs[6])
    b = L._bsdf(nt, 0.9, 0.0)
    lk(dim.outputs[2], b.inputs['Base Color'])
    lk(sh2.outputs[2], b.inputs['Emission Color'])
    b.inputs['Emission Strength'].default_value = HEAD_GLOW[0]
    L._finish(m, nt, b.outputs[0])
    m['pp'] = 1
    return m


def limb(name, a, b, c, r, m, coll, parent):
    """Bezier tube through three empties. One small node group per limb, objects set on the nodes
    (Blender 5.2 refuses modifier id-props for object inputs)."""
    g = bpy.data.node_groups.new('PP_' + name, 'GeometryNodeTree')
    g.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    go = g.nodes.new('NodeGroupOutput')
    infos = []
    for ob in (a, b, c):
        oi = g.nodes.new('GeometryNodeObjectInfo')
        oi.transform_space = 'RELATIVE'
        oi.inputs['Object'].default_value = ob
        infos.append(oi)
    bz = g.nodes.new('GeometryNodeCurveQuadraticBezier')
    bz.inputs['Resolution'].default_value = 20
    for sock, oi in zip(('Start', 'Middle', 'End'), infos):
        g.links.new(oi.outputs['Location'], bz.inputs[sock])
    circ = g.nodes.new('GeometryNodeCurvePrimitiveCircle')
    circ.inputs['Resolution'].default_value = 10
    circ.inputs['Radius'].default_value = r
    cm = g.nodes.new('GeometryNodeCurveToMesh')
    cm.inputs['Fill Caps'].default_value = True
    g.links.new(bz.outputs[0], cm.inputs['Curve'])
    g.links.new(circ.outputs[0], cm.inputs['Profile Curve'])
    ss = g.nodes.new('GeometryNodeSetShadeSmooth')
    g.links.new(cm.outputs[0], ss.inputs['Geometry'])
    sm = g.nodes.new('GeometryNodeSetMaterial')
    sm.inputs['Material'].default_value = m
    g.links.new(ss.outputs[0], sm.inputs['Geometry'])
    g.links.new(sm.outputs[0], go.inputs[0])
    me = bpy.data.meshes.new(name)
    o = bpy.data.objects.new(name, me)
    coll.objects.link(o)
    o.parent = parent
    md = o.modifiers.new('limb', 'NODES')
    md.node_group = g
    return o


def mitten(name, parent, coll, side, m, w=0.0032):
    """Plain white mitt, no thumb. Very fine outline. Origin at the wrist, hand pointing -Z.
    A pointing finger waits hidden under the palm: acts.point() shows it."""
    f = L.sph(name + '_finger', (0.026, 0.024, 0.066), (0, -0.01, -0.175), m, coll, parent=parent, seg=32)
    L.ink(f, w, soft=True, px=3)
    f.hide_render = True
    L.ink(L.sph(name + '_palm', (0.069, 0.058, 0.071), (0, 0, -0.085), m, coll, parent=parent, seg=48), w, soft=True, px=3)
    L.ink(L.lathe(name + '_cuff', [(0.056, -0.062), (0.064, -0.054), (0.064, -0.004), (0.056, 0.008), (0.0, 0.012)], m, coll, parent=parent, seg=48), w, soft=True, px=3)


def shoe(name, parent, coll, m, w=0.009):
    L.sph(name, (0.072, 0.105, 0.046), (0, -0.03, 0.044), m, coll, parent=parent, seg=22, w=w)['ink_px'] = 4


def coat_body(name, spec, coll, parent):
    p = spec['profile']
    m = spec['coat_mat']
    o = L.lathe(name + '_body', p, m, coll, parent=parent, seg=56, sy=0.86, w=0.0115, sub=2)
    o['ink_px'] = 3.6
    return o


def build(name, spec, loc=(0, 0, 0), rot_z=0.0, coll=None):
    coll = coll or L.collection('CH_' + name)
    root = L.empty(name, loc, coll=coll, rot=(0, 0, rot_z))
    body = L.empty(name + '_torso', (0, 0, 0), root, coll)
    ch = dict(root=root, torso=body, name=name)
    spec = dict(spec)
    spec['coat_mat'] = L.mat('CH_' + name + '_coat', spec['coat'], rough=0.85, spec=0.06, paint=0.07, pscale=2.2, form=0.42)
    trim_m = L.mat('CH_' + name + '_trim', spec.get('trim', spec['coat']), rough=0.65, paint=0.05, form=0.3)
    btn_m = L.noink(L.mat('CH_' + name + '_btn', spec.get('btn', (0.28, 0.16, 0.08)), rough=0.8, spec=0.08, paint=0.0))
    stick = L.noink(L.mat('CH_stick', (0.012, 0.009, 0.008), rough=1.0, spec=0.0, paint=0.0))
    # white mitts belong to the hero only: everyone else wears black ones (measured on two reference videos)
    if spec.get('mitts', 'black') == 'white':
        white = L.noink(L.mat('CH_glove', (0.95, 0.95, 0.96), rough=0.55, paint=0.0, form=0.10, emis=GLOVE_GLOW[0]))
    else:
        white = L.noink(L.mat('CH_glove_black', (0.02, 0.02, 0.022), rough=1.0, spec=0.0, paint=0.0))
    shoe_m = L.mat('CH_' + name + '_shoe', spec.get('shoe', (0.050, 0.018, 0.008)), rough=0.7, spec=0.15, paint=0.08, form=0.35)
    coat_body(name, spec, coll, body)

    # collar flaps, buttons, belt
    zt = BODY_TOP
    if spec.get('collar', True):
        for sd_ in (-1, 1):
            bm = bmesh.new()
            nz_, nx_ = 8, 8
            rows = []
            for i in range(nz_ + 1):
                t = i / nz_
                x_in = 0.018 + 0.03 * t
                x_out = 0.14 + 0.04 * t
                rc = 0.23
                row = []
                for j in range(nx_ + 1):
                    u_ = j / nx_
                    x = sd_ * (x_in + (x_out - x_in) * u_)
                    z = 0.985 - 0.145 * t * (1.0 - 0.08 * u_)
                    rc_ = max(_prof_r(spec['profile'], z) + 0.012, rc)
                    y = -0.86 * math.sqrt(max(rc_ * rc_ - x * x, 0.0004)) + 0.023
                    row.append(bm.verts.new((x, y, z)))
                rows.append(row)
            for a_, b_ in zip(rows, rows[1:]):
                for j in range(nx_):
                    bm.faces.new((a_[j], a_[j + 1], b_[j + 1], b_[j]))
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
            c = L.obj_from_bm(f'{name}_collar{sd_}', bm, trim_m, coll, smooth=True, parent=body)
            sm_ = c.modifiers.new('sd', 'SOLIDIFY')
            sm_.thickness = 0.011
            sm_.offset = 1
            sv_ = c.modifiers.new('sv', 'SUBSURF')
            sv_.levels = sv_.render_levels = 1
            L.ink(c, 0.0065, px=5)
    for i, (x, z) in enumerate(spec.get('buttons', [])):
        bz = z
        # sit the button on the coat surface
        r_here = _prof_r(spec['profile'], bz)
        y = -0.86 * r_here * math.sqrt(max(0.0, 1 - (x / max(r_here, 1e-3)) ** 2)) - 0.004
        L.sph(f'{name}_btn{i}', (0.0155, 0.008, 0.0155), (x, y, bz), btn_m, coll, parent=body, seg=14)
    if spec.get('belt'):
        z = spec['belt']
        r = _prof_r(spec['profile'], z) + 0.002
        belt_m = L.noink(L.mat('CH_' + name + '_belt', tuple(c * 0.68 for c in spec['coat']), rough=0.85, spec=0.06, paint=0.05, form=0.42))
        # a faint thin line that reads by tone, with no ink of its own
        L.lathe(name + '_belt', [(r, z - 0.012), (r + 0.003, z - 0.008), (r + 0.003, z + 0.008), (r, z + 0.012)], belt_m, coll,
                parent=body, seg=48, sy=0.87)
        L.box(name + '_buckle', (0.06, 0.012, 0.045), (0, -0.87 * (r + 0.003) - 0.002, z), trim_m, coll, parent=body, bevel=0.005)
    if spec.get('belt'):
        seam_m = L.noink(L.mat('CH_' + name + '_seam', tuple(c * 0.40 for c in spec['coat']), rough=0.85, paint=0.05))
        L.box(name + '_seam', (0.030, 0.006, 0.20), (0, -0.86 * _prof_r(spec['profile'], 0.43) - 0.002, 0.43), seam_m, coll, parent=body, rot=(math.radians(-8), 0, 0))
    if spec.get('apron'):
        am = L.mat('CH_' + name + '_apron', spec['apron'], rough=0.7, paint=0.05)
        zb, zt2 = 0.36, 0.84
        bm = bmesh.new()
        rows = []
        for i in range(9):
            z = zb + (zt2 - zb) * i / 8
            r = _prof_r(spec['profile'], z)
            hw = (0.72 if i < 6 else 0.72 - 0.12 * (i - 5)) * r
            row = []
            for j in range(9):
                x = -hw + 2 * hw * j / 8
                y = -0.86 * r * math.sqrt(max(0.0, 1 - (x / r) ** 2)) - 0.010
                row.append(bm.verts.new((x, y, z)))
            rows.append(row)
        for a, b in zip(rows, rows[1:]):
            for j in range(8):
                bm.faces.new((a[j], a[j + 1], b[j + 1], b[j]))
        o = L.obj_from_bm(name + '_apron', bm, am, coll, smooth=True, parent=body)
        sd = o.modifiers.new('sd', 'SOLIDIFY'); sd.thickness = 0.008; sd.offset = 1
        L.ink(o, 0.006, px=3.6)

    # head
    head = L.empty(name + '_head', (0, 0, BODY_TOP + 0.20), body, coll)
    ch['head'] = head
    family = spec.get('family', 'plain')
    faces = ATLAS['families'][family]
    sk = L.sph(name + '_skull', (HEAD_R, HEAD_R * 0.97, HEAD_R * 0.96), (0, 0, 0), L.noink(head_mat(family)), coll,
               parent=head, seg=48)
    L.ink(sk, 0.0135, soft=True, px=6)
    sk['face'] = float(faces.index(spec.get('face0', faces[0])))
    ch['skull'] = sk
    ch['faces'] = faces
    hm = L.noink(L.mat('CH_' + name + '_hair', spec.get('hair', (0.05, 0.03, 0.022)), rough=0.38, spec=0.5, paint=0.05))
    _hair(name, head, coll, hm, spec.get('hair_style', 'cap'))
    hat = spec.get('hat')
    if hat == 'flatcap':
        ch['cap'] = _flatcap(name, head, coll, spec)
    elif hat == 'bowler':
        _bowler(name, head, coll, spec)

    # limbs
    ch['joints'] = {}
    for tag, sx in (('L', 1), ('R', -1)):
        sh = L.empty(f'{name}_sh{tag}', (sx * 0.150, 0, 0.87), body, coll)
        el = L.empty(f'{name}_el{tag}', (sx * 0.335, 0.03, 0.70), root, coll)
        hd = L.empty(f'{name}_hd{tag}', (sx * 0.272, -0.02, 0.54), root, coll)
        arm_o = limb(f'{name}_arm{tag}', sh, el, hd, 0.027, stick, coll, root)
        arm_o.visible_shadow = False
        hand = L.empty(f'{name}_hand{tag}', (0, 0, 0), hd, coll)
        mitten(f'{name}_gl{tag}', hand, coll, sx, white)
        hp = L.empty(f'{name}_hp{tag}', (sx * 0.095, 0, HIP_Z + 0.06), body, coll)
        kn = L.empty(f'{name}_kn{tag}', (sx * 0.095, -0.015, 0.17), root, coll)
        ft = L.empty(f'{name}_ft{tag}', (sx * 0.10, 0, 0.0), root, coll)
        ank = L.empty(f'{name}_ank{tag}', (0, 0, 0.044), ft, coll)
        limb(f'{name}_leg{tag}', hp, kn, ank, 0.028, stick, coll, root)
        shoe(f'{name}_shoe{tag}', ft, coll, shoe_m)
        ch['joints'][tag] = dict(sh=sh, el=el, hd=hd, hand=hand, hp=hp, kn=kn, ft=ft)
    return ch


def _prof_r(p, z):
    for (r0, z0), (r1, z1) in zip(p, p[1:]):
        if z0 <= z <= z1 and z1 > z0:
            return r0 + (r1 - r0) * (z - z0) / (z1 - z0)
    return p[-1][0]


def _hair(name, head, coll, m, style):
    R = HEAD_R * 1.022
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=192, v_segments=112, radius=R)
    # cut the sphere along the hairline first: deleting whole faces left a sawtooth edge
    for co, no in (((0, 0, 0.42 * R), (0, 0, 1)), ((0, 0, 0.42 * R), (0, 0.15, 1)), ((0, -0.45 * R, 0), (0, 1, 0.47)),
                   ((0, -0.45 * R, 0), (0, 1, 1.2)), ((0, 0, -0.40 * R), (0, 0, 1))):
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=co, plane_no=Vector(no).normalized())
    kill = []
    for f in bm.faces:
        c = f.calc_center_median()
        # hairline: a dark band hugs the skull under the hat, wider on the upper sides, tapering out at the temple
        lim = -0.45 - 0.47 * max(0.0, c.z / R) + 1.2 * max(0.0, -c.z / R)
        keep = (c.z > 0.42 * R + 0.15 * max(0, -c.y / R) * R) or (c.y > lim * R and c.z > -0.40 * R)
        if not keep:
            kill.append(f)
    bmesh.ops.delete(bm, geom=kill, context='FACES')
    # the shell sinks under the head line at its low end, so the crescent thins into the chin line instead of stopping dead
    for v in bm.verts:
        if v.co.z < 0.1 * R:
            t = min(1, max(0, (v.co.z + 0.45 * R) / (0.55 * R)))
            v.co *= 0.93 + 0.07 * t * t * (3 - 2 * t)
    o = L.obj_from_bm(name + '_hair', bm, m, coll, smooth=True, parent=head)
    sd = o.modifiers.new('sd', 'SOLIDIFY'); sd.thickness = 0.012; sd.offset = 1
    L.ink(o, 0.007, soft=True, px=4)
    if style == 'bun':
        L.sph(name + '_bun', (0.135, 0.13, 0.125), (0, 0.06, HEAD_R + 0.07), m, coll, parent=head, seg=24, w=0.008)
    return o


def _flatcap(name, head, coll, spec):
    """Baker-boy cap: wide soft dome leaning forward, short curved peak. All of it hangs on a hinge at the back
    of the head, so a hand can tip it. Returns the hinge: negative x rotation raises the peak."""
    m = L.mat('CH_' + name + '_hat', spec['hat_col'], rough=0.9, spec=0.04, paint=0.06, pscale=2.2, form=0.38)
    band = L.noink(L.mat('CH_' + name + '_hat2', tuple(c * 0.62 for c in spec['hat_col']), rough=0.7, paint=0.05))
    z0 = 0.19
    hz = z0 - 0.005
    hinge = L.empty(name + '_caphinge', (0, 0.30, hz), head, coll)
    off = (0, -0.30, -hz)
    dome = L.lathe(name + '_cap', [(0.312, z0), (0.335, z0 + 0.018), (0.372, z0 + 0.06), (0.378, z0 + 0.095), (0.33, z0 + 0.142),
                                   (0.22, z0 + 0.178), (0.08, z0 + 0.192), (0.0, z0 + 0.194)], m, coll, loc=off, parent=hinge,
                   rot=(math.radians(-5), 0, 0), seg=56, w=0.0115, sub=2)
    dome['ink_px'] = 4
    L.lathe(name + '_capband', [(0.312, z0 - 0.022), (0.316, z0 - 0.018), (0.316, z0 + 0.016), (0.31, z0 + 0.022)], band, coll, loc=off, parent=hinge,
            rot=(math.radians(-5), 0, 0), seg=56)
    L.sph(name + '_capbtn', (0.024, 0.024, 0.012), (0, 0.012 - 0.30, z0 + 0.197 - hz), band, coll, parent=hinge, seg=14, w=0.003)
    # peak: crescent plate
    bm = bmesh.new()
    n = 24
    outer, inner = [], []
    for i in range(n + 1):
        a = math.radians(-155 + 130 * i / n)
        ro = 0.30 + 0.135 * math.sin(math.pi * i / n) ** 0.8
        outer.append(bm.verts.new((ro * math.cos(a), ro * math.sin(a), -0.03 * math.sin(math.pi * i / n))))
        inner.append(bm.verts.new((0.285 * math.cos(a), 0.285 * math.sin(a), 0.0)))
    for i in range(n):
        bm.faces.new((inner[i], inner[i + 1], outer[i + 1], outer[i]))
    o = L.obj_from_bm(name + '_peak', bm, band, coll, smooth=True, loc=(0, -0.30, z0 - 0.008 - hz), rot=(math.radians(-5), 0, 0), parent=hinge)
    sd = o.modifiers.new('sd', 'SOLIDIFY'); sd.thickness = 0.014; sd.offset = 0
    L.ink(o, 0.006, px=4)
    return hinge


def _bowler(name, head, coll, spec):
    m = L.mat('CH_' + name + '_hat', spec['hat_col'], rough=0.5, paint=0.05)
    z0 = 0.16
    L.lathe(name + '_hat', [(0.30, z0 - 0.015), (0.40, z0 - 0.025), (0.415, z0 - 0.012), (0.40, z0 + 0.006), (0.30, z0 + 0.018), (0.285, z0 + 0.09),
                            (0.262, z0 + 0.20), (0.18, z0 + 0.268), (0.07, z0 + 0.29), (0, z0 + 0.292)], m, coll, parent=head, seg=56, w=0.0115)['ink_px'] = 4


def _fcurves(idb):
    ad = idb.animation_data
    if not ad or not ad.action:
        return []
    try:
        return list(ad.action.fcurves)
    except AttributeError:
        pass
    out = []
    for lay in ad.action.layers:
        for st in lay.strips:
            bag = st.channelbag(ad.action_slot)
            if bag:
                out += list(bag.fcurves)
    return out


# ---------------------------------------------------------------- posing
def set_arm(ch, tag, hand, elbow, hand_rot=None):
    j = ch['joints'][tag]
    j['hd'].location = hand
    j['el'].location = elbow
    if hand_rot is not None:
        j['hand'].rotation_euler = hand_rot


def set_face(ch, face, frame=None):
    """Pick a decal by name. With a frame, keys it (constant, holds until the next key)."""
    sk = ch['skull']
    sk['face'] = float(ch['faces'].index(face))
    if frame is not None:
        sk.keyframe_insert('["face"]', frame=frame)
        for fc in _fcurves(sk):
            for k in fc.keyframe_points:
                k.interpolation = 'CONSTANT'


# the kit's own original cast
# straight fitted torso down to the belt, then the coat skirt flares like a dress
PROF_COAT = [(0.222, 0.31), (0.226, 0.335), (0.215, 0.385), (0.198, 0.48), (0.18, 0.555), (0.192, 0.60), (0.201, 0.63), (0.195, 0.695),
             (0.189, 0.76), (0.18, 0.82), (0.171, 0.885), (0.14, 0.94), (0.09, 1.0), (0.0, 1.04)]
PROF_DRESS = [(0.27, 0.27), (0.275, 0.30), (0.225, 0.42), (0.178, 0.56), (0.172, 0.66), (0.190, 0.80), (0.198, 0.90), (0.17, 0.98),
              (0.11, 1.03), (0.0, 1.05)]
PROF_BEAN = [(0.0, 0.34), (0.13, 0.355), (0.205, 0.41), (0.232, 0.53), (0.232, 0.70), (0.214, 0.86), (0.155, 0.98), (0.07, 1.03), (0.0, 1.05)]

LAMPLIGHTER = dict(profile=PROF_COAT, coat=(0.075, 0.20, 0.215), trim=(0.10, 0.26, 0.28), btn=(0.56, 0.38, 0.12),
                   hat='flatcap', hat_col=(0.46, 0.20, 0.09), belt=0.555, family='hero', face0='sly', mitts='white', hair=(0.045, 0.028, 0.02),
                   buttons=[(-0.058, 0.80), (0.058, 0.80), (-0.058, 0.70), (0.058, 0.70), (-0.058, 0.60), (0.058, 0.60)],
                   shoe=(0.050, 0.018, 0.008))
BAKER = dict(profile=PROF_DRESS, coat=(0.78, 0.46, 0.10), trim=(0.92, 0.78, 0.50), btn=(0.5, 0.2, 0.1), hat=None, collar=False,
             apron=(0.92, 0.90, 0.84), family='plain', face0='calm', hair=(0.24, 0.085, 0.03), hair_style='bun')
PASSER1 = dict(profile=PROF_COAT, coat=(0.26, 0.10, 0.14), trim=(0.34, 0.14, 0.18), btn=(0.5, 0.4, 0.2), hat='bowler', hat_col=(0.12, 0.10, 0.12),
               belt=0.555, family='plain', face0='flatface', buttons=[(-0.058, 0.76), (0.058, 0.76), (-0.058, 0.64), (0.058, 0.64)])
PASSER2 = dict(profile=PROF_DRESS, coat=(0.62, 0.11, 0.10), trim=(0.85, 0.72, 0.60), hat=None, collar=False, family='plain', face0='calm',
               hair=(0.12, 0.05, 0.03), hair_style='bun')
CLERK = dict(profile=PROF_BEAN, coat=(0.40, 0.55, 0.32), collar=False, hat='bowler', hat_col=(0.09, 0.08, 0.09), family='plain', face0='flatface',
             buttons=[(0, 0.82), (0, 0.72), (0, 0.62)], btn=(0.1, 0.08, 0.06))
