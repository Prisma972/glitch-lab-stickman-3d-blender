"""Look module: soft painted 3D + geometric ink. Blender 5.2, EEVEE.
Ink = inverted hull + optional crease tubes, so it takes DOF and motion blur and shows in the viewport.
"""
import bpy, bmesh, math, random
from mathutils import Vector
import kitpath

INK = (0.0035, 0.0028, 0.0028, 1.0)
INK_SCALE = [1.0]
ROOT = kitpath.KIT

MOODS = {
    # the reference keeps the ground warm and fully exposed at dusk: only the sky turns
    'dusk': dict(sun=((1.0, 0.79, 0.58), 3.2, -115, 50, 15.0), top=(0.34, 0.28, 0.30), hor=(0.56, 0.42, 0.38), amb=0.80,
                 fog=(0.30, 0.20, 0.28), fog_a=30.0, fog_b=160.0, fog_max=0.5, sky=((0.30, 0.20, 0.42), (0.10, 0.075, 0.21)),
                 fill=(1.0, 0.84, 0.66, 3.2)),
    # sun colour, strength, azimuth deg, elevation deg, angle deg | sky top, horizon, ambient strength | fog
    'day': dict(sun=((0.92, 0.95, 1.0), 1.7, -115, 50, 15.0), fill=(0.9, 0.92, 1.0, 1.1), top=(0.66, 0.73, 0.78), hor=(0.92, 0.89, 0.78),
                amb=0.62, fog=(0.70, 0.70, 0.60), fog_a=30.0, fog_b=200.0, fog_max=0.45,
                sky=((0.80, 0.74, 0.56), (0.50, 0.50, 0.37))),
    'interior': dict(sun=((1.0, 0.88, 0.70), 1.2, 140, 60, 25.0), top=(0.66, 0.72, 0.84), hor=(0.58, 0.60, 0.68),
                     amb=0.36, fog=(0.8, 0.75, 0.65), fog_a=60.0, fog_b=200.0, fog_max=0.0),
    'night': dict(sun=((0.86, 0.86, 1.0), 2.6, -28, 50, 10.0), top=(0.06, 0.09, 0.32), hor=(0.12, 0.14, 0.44),
                  amb=0.42, fog=(0.035, 0.045, 0.17), fog_a=38.0, fog_b=135.0, fog_max=0.62,
                  sky=((0.20, 0.15, 0.40), (0.09, 0.07, 0.24))),
}
# even room light comes from ambient: walls, desk and floor sit close together in the reference
MOODS['room'] = dict(MOODS['interior'], amb=1.3, top=(0.76, 0.72, 0.66), hor=(0.76, 0.72, 0.66))


def setup(scene, mood='day', w=1080, h=1920, samples=32):
    r = scene.render
    r.engine = 'BLENDER_EEVEE'
    r.resolution_x, r.resolution_y, r.resolution_percentage = w, h, 100
    r.fps = 30
    r.film_transparent = False
    r.image_settings.file_format = 'PNG'
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'None'
    scene.view_settings.exposure = 0.0
    ev = scene.eevee
    try:
        scene.eevee.use_shadow_jitter_viewport = True
    except Exception:
        pass
    for k, v in dict(taa_render_samples=samples, taa_samples=16, use_raytracing=True, use_shadows=True,
                     shadow_ray_count=3, shadow_step_count=8, use_fast_gi=True, fast_gi_method='GLOBAL_ILLUMINATION',
                     fast_gi_ray_count=4, fast_gi_step_count=8, fast_gi_distance=4.0, fast_gi_thickness_near=0.4,
                     bokeh_max_size=60.0).items():
        try:
            setattr(ev, k, v)
        except Exception as e:
            print('eevee opt', k, e)
    try:
        ev.ray_tracing_options.resolution_scale = '1'
    except Exception as e:
        print('rt opt', e)
    scene.view_layers[0].use_pass_z = True
    scene.view_layers[0].use_pass_normal = True
    vl = scene.view_layers[0]
    if 'noink' not in [a.name for a in vl.aovs]:
        a = vl.aovs.add()
        a.name = 'noink'
        a.type = 'VALUE'
    apply_mood(scene, mood)


def apply_mood(scene, mood):
    m = MOODS[mood]
    # world: ambient gradient for lighting, painted paper sky for camera rays
    w = bpy.data.worlds.get('PP_World') or bpy.data.worlds.new('PP_World')
    scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    Lk = nt.links.new
    tc = nt.nodes.new('ShaderNodeTexCoord')
    sp = nt.nodes.new('ShaderNodeSeparateXYZ')
    mr = nt.nodes.new('ShaderNodeMapRange')
    mr.inputs['From Min'].default_value = 0.0
    mr.inputs['From Max'].default_value = 0.6
    mx = nt.nodes.new('ShaderNodeMix')
    mx.data_type = 'RGBA'
    mx.inputs[6].default_value = (*m['hor'], 1)
    mx.inputs[7].default_value = (*m['top'], 1)
    bg = nt.nodes.new('ShaderNodeBackground')
    bg.inputs[1].default_value = m['amb']
    Lk(tc.outputs['Generated'], sp.inputs[0])
    Lk(sp.outputs[2], mr.inputs['Value'])
    Lk(mr.outputs[0], mx.inputs[0])
    Lk(mx.outputs[2], bg.inputs[0])
    # sky seen by camera: two paper tones broken by soft noise
    sk = m.get('sky', (m['hor'], m['top']))
    nz = nt.nodes.new('ShaderNodeTexNoise')
    nz.inputs['Scale'].default_value = 5.0
    nz.inputs['Detail'].default_value = 7.0
    nz.inputs['Roughness'].default_value = 0.62
    Lk(tc.outputs['Generated'], nz.inputs['Vector'])
    gr = nt.nodes.new('ShaderNodeMath'); gr.operation = 'MULTIPLY_ADD'
    gr.inputs[1].default_value = 1.5
    Lk(nz.outputs[0], gr.inputs[0]); Lk(mr.outputs[0], gr.inputs[2])
    cl = nt.nodes.new('ShaderNodeMapRange')
    cl.inputs['From Min'].default_value = 0.3
    cl.inputs['From Max'].default_value = 1.15
    Lk(gr.outputs[0], cl.inputs['Value'])
    mk = nt.nodes.new('ShaderNodeMix')
    mk.data_type = 'RGBA'
    mk.inputs[6].default_value = (*sk[0], 1)
    mk.inputs[7].default_value = (*sk[1], 1)
    Lk(cl.outputs[0], mk.inputs[0])
    bs = nt.nodes.new('ShaderNodeBackground')
    bs.inputs[1].default_value = 1.0
    Lk(mk.outputs[2], bs.inputs[0])
    lp = nt.nodes.new('ShaderNodeLightPath')
    ms = nt.nodes.new('ShaderNodeMixShader')
    Lk(lp.outputs['Is Camera Ray'], ms.inputs[0])
    Lk(bg.outputs[0], ms.inputs[1])
    Lk(bs.outputs[0], ms.inputs[2])
    out = nt.nodes.new('ShaderNodeOutputWorld')
    Lk(ms.outputs[0], out.inputs[0])
    # sun
    sun = bpy.data.objects.get('PP_Sun')
    if sun is None:
        sun = bpy.data.objects.new('PP_Sun', bpy.data.lights.new('PP_Sun', 'SUN'))
        scene.collection.objects.link(sun)
    col, en, az, el, ang = m['sun']
    sun.data.color = col
    sun.data.energy = en
    sun.data.angle = math.radians(ang)
    try:
        sun.data.use_shadow_jitter = True
        sun.data.shadow_jitter_overblur = 0.0
        sun.data.shadow_filter_radius = 3.0
    except Exception as e:
        print('sun jitter', e)
    sun.rotation_euler = (math.radians(90 - el), 0, math.radians(az))
    # soft front fill, casts nothing: keeps faces of coats readable with the key behind them
    fl = bpy.data.objects.get('PP_Fill')
    if fl is None:
        fl = bpy.data.objects.new('PP_Fill', bpy.data.lights.new('PP_Fill', 'SUN'))
        scene.collection.objects.link(fl)
    fl.data.use_shadow = False
    fl.data.angle = math.radians(40)
    fc = m.get('fill', (1, 1, 1, 0.0))
    fl.data.color = fc[:3]
    fl.data.energy = fc[3]
    fl.rotation_euler = (math.radians(68), 0, math.radians(-10))
    fog_group(m)


def fog_group(m=None):
    """Shared group: outputs the fog factor from camera distance and the fog colour."""
    g = bpy.data.node_groups.get('PP_Fog')
    if g is None:
        g = bpy.data.node_groups.new('PP_Fog', 'ShaderNodeTree')
        g.interface.new_socket('Fac', in_out='OUTPUT', socket_type='NodeSocketFloat')
        g.interface.new_socket('Color', in_out='OUTPUT', socket_type='NodeSocketColor')
        o = g.nodes.new('NodeGroupOutput')
        cam = g.nodes.new('ShaderNodeCameraData')
        mr = g.nodes.new('ShaderNodeMapRange')
        mr.name = 'range'
        rgb = g.nodes.new('ShaderNodeRGB')
        rgb.name = 'col'
        g.links.new(cam.outputs['View Distance'], mr.inputs['Value'])
        g.links.new(mr.outputs[0], o.inputs[0])
        g.links.new(rgb.outputs[0], o.inputs[1])
    if m:
        mr = g.nodes['range']
        mr.inputs['From Min'].default_value = m['fog_a']
        mr.inputs['From Max'].default_value = m['fog_b']
        mr.inputs['To Max'].default_value = m['fog_max']
        g.nodes['col'].outputs[0].default_value = (*m['fog'], 1)
    return g


def _finish(m, nt, shader_socket):
    """Fog mix + output."""
    L = nt.links.new
    fg = nt.nodes.new('ShaderNodeGroup')
    fg.node_tree = fog_group()
    em = nt.nodes.new('ShaderNodeEmission')
    L(fg.outputs['Color'], em.inputs['Color'])
    ms = nt.nodes.new('ShaderNodeMixShader')
    L(fg.outputs['Fac'], ms.inputs[0])
    L(shader_socket, ms.inputs[1])
    L(em.outputs[0], ms.inputs[2])
    o = nt.nodes.new('ShaderNodeOutputMaterial')
    L(ms.outputs[0], o.inputs[0])


def _coord(nt, axes='xyz', scale=1.0):
    """Object-space vector, optionally remapped so a facade plane maps to texture XY."""
    tc = nt.nodes.new('ShaderNodeTexCoord')
    src = tc.outputs['Object']
    if axes == 'xyz':
        return src
    sp = nt.nodes.new('ShaderNodeSeparateXYZ')
    cb = nt.nodes.new('ShaderNodeCombineXYZ')
    nt.links.new(src, sp.inputs[0])
    idx = {'x': 0, 'y': 1, 'z': 2}
    nt.links.new(sp.outputs[idx[axes[0]]], cb.inputs[0])
    nt.links.new(sp.outputs[idx[axes[1]]], cb.inputs[1])
    return cb.outputs[0]


def _paint(nt, col_socket, amount=0.08, scale=2.6, seed_w=0.0, detail=5.0, rough=0.6):
    """Painted layer: broad wash plus smaller blotches, slightly warm in the darks."""
    L = nt.links.new
    co = _coord(nt)
    out = col_socket
    for sc_, am in ((scale, amount), (scale * 4.3, amount * 0.75)):
        nz = nt.nodes.new('ShaderNodeTexNoise')
        nz.inputs['Scale'].default_value = sc_
        nz.inputs['Detail'].default_value = detail
        nz.inputs['Roughness'].default_value = rough
        L(co, nz.inputs['Vector'])
        mr = nt.nodes.new('ShaderNodeMapRange')
        mr.inputs['From Min'].default_value = 0.36
        mr.inputs['From Max'].default_value = 0.62
        mr.inputs['To Min'].default_value = 1.0 - am * 1.5
        mr.inputs['To Max'].default_value = 1.0 + am * 0.4
        L(nz.outputs[0], mr.inputs['Value'])
        cb = nt.nodes.new('ShaderNodeCombineColor')
        L(mr.outputs[0], cb.inputs[0])
        L(mr.outputs[0], cb.inputs[1])
        mt = nt.nodes.new('ShaderNodeMath')
        mt.operation = 'MULTIPLY'
        mt.inputs[1].default_value = 0.97
        L(mr.outputs[0], mt.inputs[0])
        L(mt.outputs[0], cb.inputs[2])
        mx = nt.nodes.new('ShaderNodeMix')
        mx.data_type = 'RGBA'
        mx.blend_type = 'MULTIPLY'
        mx.inputs[0].default_value = 1.0
        L(out, mx.inputs[6])
        L(cb.outputs[0], mx.inputs[7])
        out = mx.outputs[2]
    return out


def _bsdf(nt, rough, spec):
    b = nt.nodes.new('ShaderNodeBsdfPrincipled')
    b.inputs['Roughness'].default_value = 1.0      # the reference is fully matte: no sheen anywhere
    b.inputs['Specular IOR Level'].default_value = 0.0
    return b


def _new(name):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.node_tree.nodes.clear()
    return m, m.node_tree


def mat(name, rgb, rough=0.72, spec=0.12, paint=0.10, pscale=2.6, emis=0.0, form=0.0):
    if name in bpy.data.materials and bpy.data.materials[name].get('pp'):
        return bpy.data.materials[name]
    m, nt = _new(name)
    c = nt.nodes.new('ShaderNodeRGB')
    c.outputs[0].default_value = (*rgb[:3], 1)
    col = _paint(nt, c.outputs[0], paint, pscale) if paint else c.outputs[0]
    if form:
        lw = nt.nodes.new('ShaderNodeLayerWeight')
        lw.inputs['Blend'].default_value = 0.5
        fr = nt.nodes.new('ShaderNodeMapRange')
        fr.inputs['From Min'].default_value = 0.2
        fr.inputs['From Max'].default_value = 0.78
        # Facing is 0 toward the camera: centres keep their colour and only the silhouette darkens
        fr.inputs['To Min'].default_value = 1.0 - form
        fr.inputs['To Max'].default_value = (1.0 - form) * 0.85
        nt.links.new(lw.outputs['Facing'], fr.inputs['Value'])
        fc = nt.nodes.new('ShaderNodeCombineColor')
        for i_ in range(3):
            nt.links.new(fr.outputs[0], fc.inputs[i_])
        fm = nt.nodes.new('ShaderNodeMix')
        fm.data_type = 'RGBA'
        fm.blend_type = 'MULTIPLY'
        fm.inputs[0].default_value = 1.0
        nt.links.new(col, fm.inputs[6])
        nt.links.new(fc.outputs[0], fm.inputs[7])
        col = fm.outputs[2]
    b = _bsdf(nt, rough, spec)
    nt.links.new(col, b.inputs['Base Color'])
    if emis:
        nt.links.new(col, b.inputs['Emission Color'])
        b.inputs['Emission Strength'].default_value = emis
    _finish(m, nt, b.outputs[0])
    m['pp'] = 1
    return m


def tex_mat(name, path, rough=0.6, spec=0.2, emis=0.0, axes=None, scale=(1, 1), extension='REPEAT', alpha=False):
    """Image material. axes None = mesh UVs, else planar object coords like 'xz'."""
    if name in bpy.data.materials and bpy.data.materials[name].get('pp'):
        return bpy.data.materials[name]
    m, nt = _new(name)
    L = nt.links.new
    ti = nt.nodes.new('ShaderNodeTexImage')
    ti.image = bpy.data.images.load(path, check_existing=True)
    ti.extension = extension
    ti.interpolation = 'Cubic'
    if axes:
        mp = nt.nodes.new('ShaderNodeMapping')
        mp.inputs['Scale'].default_value = (scale[0], scale[1], 1)
        L(_coord(nt, axes), mp.inputs[0])
        L(mp.outputs[0], ti.inputs[0])
    else:
        uv = nt.nodes.new('ShaderNodeTexCoord')
        L(uv.outputs['UV'], ti.inputs[0])
    b = _bsdf(nt, rough, spec)
    L(ti.outputs[0], b.inputs['Base Color'])
    if emis:
        L(ti.outputs[0], b.inputs['Emission Color'])
        b.inputs['Emission Strength'].default_value = emis
    if alpha:
        L(ti.outputs[1], b.inputs['Alpha'])
    _finish(m, nt, b.outputs[0])
    m['pp'] = 1
    return m


def brick_mat(name, c1, c2, mortar, axes='yz', bw=0.24, bh=0.08, mortar_size=0.009, offset=0.5, rough=0.85, spec=0.1,
              paint=0.17, bias=0.0, pscale=1.1, pdetail=5.0, prough=0.6):
    if name in bpy.data.materials and bpy.data.materials[name].get('pp'):
        return bpy.data.materials[name]
    m, nt = _new(name)
    L = nt.links.new
    t = nt.nodes.new('ShaderNodeTexBrick')
    t.offset = offset
    t.inputs['Color1'].default_value = (*c1, 1)
    t.inputs['Color2'].default_value = (*c2, 1)
    t.inputs['Mortar'].default_value = (*mortar, 1)
    t.inputs['Scale'].default_value = 1.0
    t.inputs['Mortar Size'].default_value = mortar_size
    t.inputs['Mortar Smooth'].default_value = 0.15
    t.inputs['Bias'].default_value = bias
    t.inputs['Brick Width'].default_value = bw
    t.inputs['Row Height'].default_value = bh
    L(_coord(nt, axes), t.inputs['Vector'])
    col = _paint(nt, t.outputs[0], paint, pscale, detail=pdetail, rough=prough)
    b = _bsdf(nt, rough, spec)
    L(col, b.inputs['Base Color'])
    _finish(m, nt, b.outputs[0])
    m['pp'] = 1
    return m


def wood_mat(name, c_light, c_dark, axes='xy', grain=(1.6, 14.0), rough=0.55, spec=0.25, plank=0.0):
    """Painted wood: stretched noise bands, optional plank seams along the first axis."""
    if name in bpy.data.materials and bpy.data.materials[name].get('pp'):
        return bpy.data.materials[name]
    m, nt = _new(name)
    L = nt.links.new
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (grain[0], grain[1], 1)
    L(_coord(nt, axes), mp.inputs[0])
    nz = nt.nodes.new('ShaderNodeTexNoise')
    nz.inputs['Scale'].default_value = 1.0
    nz.inputs['Detail'].default_value = 5.0
    nz.inputs['Distortion'].default_value = 0.4
    L(mp.outputs[0], nz.inputs['Vector'])
    rp = nt.nodes.new('ShaderNodeValToRGB')
    rp.color_ramp.elements[0].position = 0.3
    rp.color_ramp.elements[0].color = (*c_dark, 1)
    rp.color_ramp.elements[1].position = 0.7
    rp.color_ramp.elements[1].color = (*c_light, 1)
    L(nz.outputs[0], rp.inputs[0])
    col = rp.outputs[0]
    if plank:
        bk = nt.nodes.new('ShaderNodeTexBrick')
        bk.offset = 0.35
        bk.inputs['Color1'].default_value = (1, 1, 1, 1)
        bk.inputs['Color2'].default_value = (0.86, 0.84, 0.82, 1)
        bk.inputs['Mortar'].default_value = (0.14, 0.03, 0.02, 1)
        bk.inputs['Scale'].default_value = 1.0
        bk.inputs['Mortar Size'].default_value = 0.004
        bk.inputs['Brick Width'].default_value = 2.4
        bk.inputs['Row Height'].default_value = plank
        L(_coord(nt, axes), bk.inputs['Vector'])
        mx = nt.nodes.new('ShaderNodeMix')
        mx.data_type = 'RGBA'
        mx.blend_type = 'MULTIPLY'
        mx.inputs[0].default_value = 1.0
        L(col, mx.inputs[6])
        L(bk.outputs[0], mx.inputs[7])
        col = mx.outputs[2]
    b = _bsdf(nt, rough, spec)
    L(col, b.inputs['Base Color'])
    _finish(m, nt, b.outputs[0])
    m['pp'] = 1
    return m


def glass_mat(name, rgb=(0.10, 0.20, 0.30), top=(0.50, 0.66, 0.74)):
    """Painted glass: vertical sky gradient, no transparency, reads like a storybook window."""
    if name in bpy.data.materials and bpy.data.materials[name].get('pp'):
        return bpy.data.materials[name]
    m, nt = _new(name)
    L = nt.links.new
    tc = nt.nodes.new('ShaderNodeTexCoord')
    sp = nt.nodes.new('ShaderNodeSeparateXYZ')
    L(tc.outputs['Generated'], sp.inputs[0])
    mx = nt.nodes.new('ShaderNodeMix')
    mx.data_type = 'RGBA'
    mx.inputs[6].default_value = (*rgb, 1)
    mx.inputs[7].default_value = (*top, 1)
    L(sp.outputs[2], mx.inputs[0])
    b = _bsdf(nt, 0.2, 0.5)
    L(mx.outputs[2], b.inputs['Base Color'])
    L(mx.outputs[2], b.inputs['Emission Color'])
    b.inputs['Emission Strength'].default_value = 0.35
    _finish(m, nt, b.outputs[0])
    m['pp'] = 1
    return m


def halo_mat(name, rgb, strength=1.0, radius=1.0, alpha=1.0):
    """Soft radial glow for a flat disc: additive emission falling to nothing at the rim."""
    if name in bpy.data.materials and bpy.data.materials[name].get('pp'):
        return bpy.data.materials[name]
    m, nt = _new(name)
    Lk = nt.links.new
    tc = nt.nodes.new('ShaderNodeTexCoord')
    ln = nt.nodes.new('ShaderNodeVectorMath')
    ln.operation = 'LENGTH'
    Lk(tc.outputs['Object'], ln.inputs[0])
    mr = nt.nodes.new('ShaderNodeMapRange')
    mr.inputs['From Max'].default_value = radius
    mr.inputs['To Min'].default_value = 1.0
    mr.inputs['To Max'].default_value = 0.0
    Lk(ln.outputs['Value'], mr.inputs['Value'])
    p = nt.nodes.new('ShaderNodeMath')
    p.operation = 'POWER'
    p.inputs[1].default_value = 1.6
    Lk(mr.outputs[0], p.inputs[0])
    pa = nt.nodes.new('ShaderNodeMath')
    pa.operation = 'MULTIPLY'
    pa.inputs[1].default_value = alpha
    Lk(p.outputs[0], pa.inputs[0])
    e = nt.nodes.new('ShaderNodeEmission')
    e.inputs['Color'].default_value = (*rgb, 1)
    e.inputs['Strength'].default_value = strength
    t = nt.nodes.new('ShaderNodeBsdfTransparent')
    ms = nt.nodes.new('ShaderNodeMixShader')
    Lk(pa.outputs[0], ms.inputs[0])
    Lk(t.outputs[0], ms.inputs[1])
    Lk(e.outputs[0], ms.inputs[2])
    o = nt.nodes.new('ShaderNodeOutputMaterial')
    Lk(ms.outputs[0], o.inputs[0])
    try:
        m.surface_render_method = 'BLENDED'
    except Exception as ex:
        print('halo', ex)
    m['pp'] = 1
    return m


def glow_mat(name, rgb, strength=3.0):
    if name in bpy.data.materials and bpy.data.materials[name].get('pp'):
        return bpy.data.materials[name]
    m, nt = _new(name)
    e = nt.nodes.new('ShaderNodeEmission')
    e.inputs['Color'].default_value = (*rgb, 1)
    e.inputs['Strength'].default_value = strength
    o = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(e.outputs[0], o.inputs[0])
    m['pp'] = 1
    return m


def ink_mat():
    m = bpy.data.materials.get('PP_Ink')
    if m is None:
        m, nt = _new('PP_Ink')
        e = nt.nodes.new('ShaderNodeEmission')
        e.inputs['Color'].default_value = INK
        _finish(m, nt, e.outputs[0])
        m.use_backface_culling = True
        m.use_backface_culling_shadow = True
    return noink(m)     # the post line pass must not draw a second line along a hull


def soft_ink_mat():
    """See-through looking black: dark grey hull for heads."""
    m = bpy.data.materials.get('PP_InkSoft')
    if m is None:
        m, nt = _new('PP_InkSoft')
        e = nt.nodes.new('ShaderNodeEmission')
        e.inputs['Color'].default_value = (0.022, 0.022, 0.028, 1)
        _finish(m, nt, e.outputs[0])
        m.use_backface_culling = True
        m.use_backface_culling_shadow = True
    return m


def noink(m):
    """Marks a material so the post line pass skips it."""
    if m.get('noink'):
        return m
    a = m.node_tree.nodes.new('ShaderNodeOutputAOV')
    a.aov_name = 'noink'
    a.inputs['Value'].default_value = 1.0
    m['noink'] = 1
    return m


def ink(obj, w=0.008, soft=False, px=None):
    """Inverted hull. World-size width on sets, so lines thin out with distance. px: width in pixels at 1080 wide,
    kept constant on screen by render_frames.py, as on the characters of the reference."""
    if obj.type != 'MESH':
        return obj
    if px:
        obj['ink_px'] = px
    w = w * INK_SCALE[0]
    if 'PP_ink' in obj.modifiers:
        obj.modifiers['PP_ink'].thickness = w
        return obj
    n = len(obj.data.materials)
    obj.data.materials.append(soft_ink_mat() if soft else ink_mat())
    md = obj.modifiers.new('PP_ink', 'SOLIDIFY')
    md.thickness = w
    md.offset = 1
    md.use_flip_normals = True
    md.use_rim = False
    md.material_offset = n
    return obj


def crease(obj, r=0.004, angle=35.0, coll=None):
    """Inner ink: thin curve tubes along the sharp edges of a mesh, parented to it."""
    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.normal_update()
    segs = []
    for e in bm.edges:
        if len(e.link_faces) == 2:
            a = e.link_faces[0].normal.angle(e.link_faces[1].normal, 0.0)
            if a >= math.radians(angle):
                segs.append((e.verts[0].co.copy(), e.verts[1].co.copy()))
        elif len(e.link_faces) == 1:
            segs.append((e.verts[0].co.copy(), e.verts[1].co.copy()))
    bm.free()
    if not segs:
        return None
    cu = bpy.data.curves.new(obj.name + '_cr', 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = r
    cu.bevel_resolution = 0
    cu.use_fill_caps = True
    for a, b in segs:
        s = cu.splines.new('POLY')
        s.points.add(1)
        s.points[0].co = (*a, 1)
        s.points[1].co = (*b, 1)
    cu.materials.append(line_mat())
    o = bpy.data.objects.new(obj.name + '_cr', cu)
    (coll or obj.users_collection[0]).objects.link(o)
    o.parent = obj
    return o


def line_mat():
    m = bpy.data.materials.get('PP_Line')
    if m is None:
        m, nt = _new('PP_Line')
        e = nt.nodes.new('ShaderNodeEmission')
        e.inputs['Color'].default_value = INK
        _finish(m, nt, e.outputs[0])
    return noink(m)


# ------------------------------------------------------------------ mesh helpers
def _link(o, coll):
    (coll or bpy.context.scene.collection).objects.link(o)
    return o


def obj_from_bm(name, bm, m=None, coll=None, smooth=False, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    if smooth:
        me.shade_smooth()
    o = bpy.data.objects.new(name, me)
    _link(o, coll)
    o.location = loc
    o.rotation_euler = rot
    if m is not None:
        me.materials.append(m)
    if parent is not None:
        o.parent = parent
    return o


def box(name, size, loc, m, coll=None, rot=(0, 0, 0), parent=None, w=0.0, bevel=0.0):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=size, verts=bm.verts)
    o = obj_from_bm(name, bm, m, coll, loc=loc, rot=rot, parent=parent)
    if bevel:
        bv = o.modifiers.new('bv', 'BEVEL')
        bv.width = bevel
        bv.segments = 2
        bv.limit_method = 'NONE'
    if w:
        ink(o, w)
    return o


def cyl(name, r, h, loc, m, coll=None, rot=(0, 0, 0), parent=None, seg=24, w=0.0, r2=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=h)
    o = obj_from_bm(name, bm, m, coll, smooth=True, loc=loc, rot=rot, parent=parent)
    o.data.set_sharp_from_angle(angle=math.radians(40))
    if w:
        ink(o, w)
    return o


def sph(name, sc, loc, m, coll=None, rot=(0, 0, 0), parent=None, seg=32, w=0.0):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=max(10, seg // 2), radius=1.0)
    bmesh.ops.scale(bm, vec=sc, verts=bm.verts)
    o = obj_from_bm(name, bm, m, coll, smooth=True, loc=loc, rot=rot, parent=parent)
    if w:
        ink(o, w)
    return o


def lathe(name, prof, m, coll=None, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, seg=48, w=0.0, sy=1.0, smooth=True, sub=0):
    """prof = [(radius, z), ...] bottom to top."""
    bm = bmesh.new()
    rings = []
    for r, z in prof:
        ring = []
        for i in range(seg):
            a = 2 * math.pi * i / seg
            ring.append(bm.verts.new((r * math.cos(a), r * math.sin(a) * sy, z)))
        rings.append(ring)
    for a, b in zip(rings, rings[1:]):
        for i in range(seg):
            j = (i + 1) % seg
            bm.faces.new((a[i], a[j], b[j], b[i]))
    if prof[0][0] > 1e-3:
        bm.faces.new(list(reversed(rings[0])))
    if prof[-1][0] > 1e-3:
        bm.faces.new(rings[-1])
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return_o = obj_from_bm(name, bm, m, coll, smooth=smooth, loc=loc, rot=rot, parent=parent)
    if sub:
        sm = return_o.modifiers.new('sub', 'SUBSURF')
        sm.levels = sm.render_levels = sub
    if w:
        ink(return_o, w)
    return return_o


def empty(name, loc=(0, 0, 0), parent=None, coll=None, rot=(0, 0, 0)):
    o = bpy.data.objects.new(name, None)
    _link(o, coll)
    o.empty_display_size = 0.05
    o.location = loc
    o.rotation_euler = rot
    if parent is not None:
        o.parent = parent
    return o


def collection(name, parent=None):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in [x.name for x in (parent or bpy.context.scene.collection).children]:
        (parent or bpy.context.scene.collection).children.link(c)
    return c


def wipe():
    """Empty the file (only used on the throwaway test scene)."""
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    for b in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.lights, bpy.data.cameras):
        for x in list(b):
            b.remove(x)
    for g in list(bpy.data.node_groups):
        bpy.data.node_groups.remove(g)


def matte_lights():
    for l in bpy.data.lights:
        l.specular_factor = 0.0


def camera(name, pos, target, lens=35.0, roll=0.0, fstop=None, focus=None, coll=None):
    cam = bpy.data.objects.get(name)
    if cam is None:
        cam = bpy.data.objects.new(name, bpy.data.cameras.new(name))
        _link(cam, coll)
    cam.data.lens = lens
    cam.data.sensor_width = 24.0
    cam.data.sensor_fit = 'VERTICAL'
    cam.data.sensor_height = 36.0
    cam.data.clip_end = 900
    cam.location = pos
    d = Vector(target) - Vector(pos)
    q = d.to_track_quat('-Z', 'Y')
    cam.rotation_mode = 'XYZ'
    cam.rotation_euler = q.to_euler()
    cam.rotation_euler.rotate_axis('Z', math.radians(roll))
    cam.data.dof.use_dof = fstop is not None
    if fstop is not None:
        cam.data.dof.aperture_fstop = fstop
        cam.data.dof.focus_distance = (Vector(focus or target) - Vector(pos)).length
    return cam
