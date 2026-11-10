"""Workshop interior (original): panelled room, wide desk, lamp pool. Camera looks +Y at the back wall."""
import bpy, math, random
import look as L

T = L.ROOT + '/tex/room'


def _uvbox(o, sx, sy, axes='xz'):
    me = o.data
    uv = me.uv_layers.new(name='UV')
    a, b = {'x': 0, 'y': 1, 'z': 2}[axes[0]], {'x': 0, 'y': 1, 'z': 2}[axes[1]]
    for p in me.polygons:
        for li in p.loop_indices:
            v = me.vertices[me.loops[li].vertex_index].co
            uv.data[li].uv = (v[a] / sx + .5, v[b] / sy + .5)
    return o


def build(night=False):
    c = L.collection('SET_room')
    wall = L.tex_mat('RM_wall', f"{T}/{'wallpaper_night' if night else 'wallpaper'}.png", rough=0.8, spec=0.1, axes='xz', scale=(0.8, 0.8))
    wall2 = L.tex_mat('RM_wall2', f"{T}/{'wallpaper_night' if night else 'wallpaper'}.png", rough=0.8, spec=0.1, axes='yz', scale=(0.8, 0.8))
    pan = L.mat('RM_panel', (0.10, 0.27, 0.21) if not night else (0.13, 0.11, 0.30), rough=0.5, spec=0.3, paint=0.06)
    trim = L.mat('RM_trim', (0.82, 0.76, 0.60), rough=0.5, spec=0.3, paint=0.03)
    floor = L.wood_mat('RM_floor', (0.72, 0.17, 0.07), (0.62, 0.14, 0.06), axes='xy', grain=(0.9, 16.0), plank=0.16)
    desk = L.wood_mat('RM_desk', (0.66, 0.40, 0.15), (0.60, 0.36, 0.13), axes='xy', grain=(0.7, 14.0), plank=0.24)
    deskf = L.wood_mat('RM_deskf', (0.52, 0.30, 0.09), (0.47, 0.27, 0.08), axes='xz', grain=(0.9, 12.0))
    blot = L.mat('RM_blot', (0.105, 0.238, 0.112), rough=0.7, paint=0.08, pscale=5)
    brass = L.mat('RM_brass', (0.85, 0.60, 0.20), rough=0.3, spec=0.6, paint=0.03)
    paper = L.mat('RM_paper', (0.74, 0.71, 0.62), rough=0.7, paint=0.03)
    dark = L.mat('RM_dark', (0.10, 0.06, 0.04), rough=0.5)

    # shell
    L.box('RM_floor', (9, 9, 0.2), (0, 1.0, -0.1), floor, c)
    L.box('RM_back', (9, 0.2, 4.2), (0, 3.2, 2.1), wall, c)
    L.box('RM_left', (0.2, 9, 4.2), (-2.6, 1.0, 2.1), wall2, c)
    L.box('RM_right', (0.2, 9, 4.2), (2.6, 1.0, 2.1), wall2, c)
    L.box('RM_ceil', (9, 9, 0.2), (0, 1.0, 3.5), L.mat('RM_ceil', (0.65, 0.58, 0.44), rough=0.8), c)
    for i in range(5):
        L.box(f'RM_beam{i}', (9, 0.16, 0.2), (0, -1.0 + 1.0 * i, 3.34), deskf, c, w=0.012)
    # dado panelling with raised frames
    L.box('RM_dado', (9, 0.05, 1.05), (0, 3.09, 0.525), pan, c, w=0.012)
    L.box('RM_dadoL', (0.05, 9, 1.05), (-2.49, 1.0, 0.525), pan, c, w=0.012)
    L.box('RM_dadoR', (0.05, 9, 1.05), (2.49, 1.0, 0.525), pan, c, w=0.012)
    L.box('RM_rail', (9, 0.08, 0.07), (0, 3.06, 1.07), trim, c, w=0.01)
    L.box('RM_skirt', (9, 0.08, 0.14), (0, 3.05, 0.07), trim, c, w=0.01)
    for i in range(-3, 4):
        L.box(f'RM_pf{i}', (0.72, 0.03, 0.68), (i * 0.9, 3.05, 0.56), pan, c, w=0.009)

    # window, back wall
    win_sky = L.glow_mat('RM_sky', (0.62, 0.72, 0.76) if not night else (0.10, 0.14, 0.42), 0.55 if not night else 1.2)
    L.box('RM_winbg', (1.2, 0.02, 1.35), (1.42, 3.08, 2.15), win_sky, c)
    for k, (sx, sz, px, pz) in enumerate(((1.36, 0.08, 1.42, 2.84), (1.36, 0.08, 1.42, 1.46), (0.08, 1.46, 0.76, 2.15), (0.08, 1.46, 2.08, 2.15),
                                          (0.04, 1.35, 1.42, 2.15), (1.2, 0.04, 1.42, 2.3))):
        L.box(f'RM_wf{k}', (sx, 0.09, sz), (px, 3.05, pz), trim, c, w=0.012)
    L.box('RM_sill', (1.6, 0.26, 0.07), (1.42, 2.98, 1.4), trim, c, w=0.011)

    # corkboard + calendar
    cork = L.tex_mat('RM_cork', f'{T}/cork.png', rough=0.8, spec=0.1)
    o = L.box('RM_cork', (1.5, 0.03, 1.08), (-0.75, 3.07, 2.25), cork, c)
    _uvbox(o, 1.5, 1.08)
    for k, (sx, sz, px, pz) in enumerate(((1.6, 0.06, -0.75, 2.81), (1.6, 0.06, -0.75, 1.69), (0.06, 1.16, -1.53, 2.25), (0.06, 1.16, 0.03, 2.25))):
        L.box(f'RM_cf{k}', (sx, 0.06, sz), (px, 3.05, pz), deskf, c, w=0.011)
    cal = L.tex_mat('RM_cal', f'{T}/calendar.png', rough=0.7)
    o = L.box('RM_calendar', (0.36, 0.012, 0.48), (0.36, 3.08, 1.78), cal, c, w=0.006)
    _uvbox(o, 0.36, 0.48)

    # shelf with jars on the left wall side
    L.box('RM_shelf', (1.3, 0.3, 0.05), (-1.75, 2.92, 1.5), deskf, c, w=0.01)
    jar_cols = [(0.60, 0.10, 0.08), (0.08, 0.28, 0.40), (0.80, 0.55, 0.12), (0.12, 0.34, 0.20)]
    for i, col in enumerate(jar_cols):
        m = L.mat(f'RM_jar{i}', col, rough=0.3, spec=0.5, paint=0.03)
        L.lathe(f'RM_j{i}', [(0.08, 1.53), (0.09, 1.56), (0.09, 1.72), (0.06, 1.76), (0.06, 1.8), (0, 1.8)], m, c, loc=(-2.2 + i * 0.3, 2.92, 0), seg=16, w=0.008)

    # desk
    dz = 0.74
    L.box('RM_top', (2.7, 1.25, 0.08), (0, -0.55, dz), desk, c, w=0.014)
    L.box('RM_ped1', (0.78, 1.1, dz - 0.04), (-0.94, -0.55, (dz - 0.04) / 2), deskf, c, w=0.013)
    L.box('RM_ped2', (0.78, 1.1, dz - 0.04), (0.94, -0.55, (dz - 0.04) / 2), deskf, c, w=0.013)
    L.box('RM_apron', (1.2, 0.04, 0.14), (0, -1.12, dz - 0.11), deskf, c, w=0.011)
    for s, x in enumerate((-0.94, 0.94)):
        for k in range(2):
            z = 0.2 + k * 0.27
            L.box(f'RM_dr{s}{k}', (0.68, 0.03, 0.22), (x, -1.115, z), desk, c, w=0.01)
            L.sph(f'RM_kn{s}{k}', (0.022, 0.022, 0.022), (x, -1.14, z), brass, c, seg=10, w=0.004)
    # blotter with leather edge
    L.box('RM_blot_edge', (1.42, 0.94, 0.012), (0, -0.68, dz + 0.046), deskf, c, w=0.006)
    L.box('RM_blotter', (1.3, 0.82, 0.014), (0, -0.68, dz + 0.05), blot, c, w=0.003)
    # ledger + tools
    led = L.tex_mat('RM_ledger', f'{T}/ledger.png', rough=0.85, spec=0.05)
    o = L.box('RM_page', (0.46, 0.33, 0.012), (-0.03, -0.68, dz + 0.066), led, c, rot=(0, 0, math.radians(5)), w=0.004)
    _uvbox(o, 0.46, 0.33, 'xy')
    # oil lamp: brass base, glass chimney, glowing wick
    glow = L.glow_mat('RM_flame', (1.0, 0.72, 0.30), 4.0)
    x, y = 0.54, -0.24
    L.lathe('RM_lamp', [(0.13, dz + 0.04), (0.14, dz + 0.06), (0.06, dz + 0.11), (0.10, dz + 0.17), (0.11, dz + 0.22), (0.05, dz + 0.28), (0.055, dz + 0.31)], brass, c, loc=(x, y, 0), seg=24, w=0.008)
    L.lathe('RM_chim', [(0.05, dz + 0.31), (0.09, dz + 0.38), (0.05, dz + 0.56), (0.0, dz + 0.561)], L.glow_mat('RM_chg', (1.0, 0.70, 0.30), 0.85), c, loc=(x, y, 0), seg=20, w=0.006)
    L.sph('RM_flame', (0.022, 0.022, 0.05), (x, y, dz + 0.42), glow, c, seg=10)
    lt = bpy.data.lights.new('RM_lamp', 'POINT')
    lt.energy = 20 if not night else 110
    lt.color = (1.0, 0.78, 0.52) if not night else (1.0, 0.72, 0.42)
    lt.shadow_soft_size = 0.22
    lo = bpy.data.objects.new('RM_lampL', lt)
    c.objects.link(lo)
    lo.location = (x, y - 0.1, dz + 0.5)
    # room key light from above: wide soft fill
    ar = bpy.data.lights.new('RM_fill', 'AREA')
    ar.shape = 'RECTANGLE'
    ar.size, ar.size_y = 4.0, 3.5
    ar.energy = 40 if not night else 34
    ar.color = (1.0, 0.93, 0.82) if not night else (0.55, 0.55, 1.0)
    ao = bpy.data.objects.new('RM_fillL', ar)
    c.objects.link(ao)
    ao.location = (-0.4, -1.6, 3.2)
    ao.rotation_euler = (math.radians(30), 0, 0)
    # pencil jar, mug, ink pot, stamp, scissors-free props
    tin = L.mat('RM_tin', (0.20, 0.33, 0.55), rough=0.35, spec=0.5, paint=0.04)
    L.lathe('RM_tin', [(0.075, dz + 0.04), (0.075, dz + 0.22), (0.07, dz + 0.22), (0.07, dz + 0.06), (0, dz + 0.06)], tin, c, loc=(-0.78, -0.40, 0), seg=20, w=0.007, smooth=True)
    rnd = random.Random(2)
    for i, col in enumerate(((0.85, 0.6, 0.1), (0.7, 0.1, 0.1), (0.1, 0.4, 0.2), (0.86, 0.8, 0.5))):
        L.cyl(f'RM_pc{i}', 0.009, 0.3, (-0.78 + (i - 1.5) * 0.03, -0.40 + (i % 2 - .5) * 0.04, dz + 0.2), L.mat(f'RM_pcm{i}', col, rough=0.4, paint=0), c,
              rot=(rnd.uniform(-.15, .15), rnd.uniform(-.15, .15), 0), seg=6, w=0.003)
    mug = L.mat('RM_mug', (0.88, 0.86, 0.80), rough=0.3, spec=0.5, paint=0.02)
    L.lathe('RM_mug', [(0.065, dz + 0.04), (0.07, dz + 0.16), (0.062, dz + 0.16), (0.062, dz + 0.14), (0, dz + 0.14)], mug, c, loc=(0.46, -0.98, 0), seg=20, w=0.007)
    L.lathe('RM_tea', [(0.061, dz + 0.139), (0, dz + 0.139)], L.mat('RM_teaL', (0.28, 0.12, 0.05), rough=0.15, paint=0), c, loc=(0.46, -0.98, 0), seg=20)
    bm_tor = L.lathe('RM_handle', [(0.03, dz + 0.1)], mug, c, seg=3) if False else None
    for i in range(3):
        L.box(f'RM_book{i}', (0.42, 0.3, 0.05), (-0.66 + 0.01 * i, -0.96, dz + 0.065 + 0.05 * i), L.mat(f'RM_bk{i}', ((0.45, 0.08, 0.08), (0.08, 0.20, 0.34), (0.55, 0.42, 0.14))[i], rough=0.5, paint=0.04), c,
              rot=(0, 0, math.radians(7 * i - 6)), w=0.006)
    # chair back seen behind the character
    L.box('RM_chair', (0.8, 0.07, 1.1), (0, 0.5, 0.55), deskf, c, w=0.012)
    # desk clutter
    plate = L.tex_mat('RM_plate', f'{T}/nameplate.png', rough=0.5)
    o = L.box('RM_nameplate', (0.56, 0.02, 0.12), (-0.52, -0.16, dz + 0.1), plate, c, rot=(math.radians(-16), 0, math.radians(-4)), w=0.006)
    _uvbox(o, 0.56, 0.12)
    L.box('RM_platebase', (0.60, 0.11, 0.04), (-0.52, -0.14, dz + 0.06), deskf, c, rot=(0, 0, math.radians(-4)), w=0.006)
    tray = L.mat('RM_tray', (0.33, 0.20, 0.10), rough=0.7)
    L.box('RM_tray', (0.42, 0.30, 0.018), (0.72, -0.84, dz + 0.05), tray, c, rot=(0, 0, math.radians(8)), w=0.006)
    for s_, (dx, dy) in enumerate(((-0.14, -0.07), (-0.14, 0.06), (0.0, -0.07), (0.0, 0.06), (0.14, 0.0))):
        L.box(f'RM_tr{s_}', (0.42 if s_ % 2 else 0.018, 0.018 if s_ % 2 else 0.30, 0.05), (0.72 + (0 if s_ % 2 else (0.21 if s_ == 2 else -0.21)), -0.84 + (0.15 if s_ == 1 else -0.15 if s_ == 3 else 0), dz + 0.08), tray, c, rot=(0, 0, math.radians(8)), w=0.006)
    for i in range(6):
        L.box(f'RM_env{i}', (0.32, 0.22, 0.008), (0.72 + 0.01 * i, -0.84, dz + 0.075 + 0.009 * i), paper, c, rot=(0, 0, math.radians(8 + 3 * (i % 3) - 3)), w=0.003)
    match = L.mat('RM_match', (0.62, 0.12, 0.08), rough=0.7)
    L.box('RM_matchbox', (0.13, 0.08, 0.035), (0.42, -0.42, dz + 0.058), match, c, rot=(0, 0, math.radians(32)), w=0.005)
    for i in range(5):
        L.cyl(f'RM_stick{i}', 0.005, 0.12, (0.50 + 0.03 * i, -0.50 - 0.015 * i, dz + 0.047), L.mat('RM_matchw', (0.8, 0.62, 0.32), rough=0.7, paint=0), c, rot=(math.pi / 2, 0, math.radians(30 + 28 * i)), seg=6, w=0.002)
    for i, (x_, y_) in enumerate(((-0.46, -0.28), (-0.32, -0.33), (0.28, -0.3))):
        L.cyl(f'RM_coin{i}', 0.04, 0.012, (x_, y_, dz + 0.052), brass, c, seg=20, w=0.003)
    wick = L.mat('RM_wick', (0.82, 0.78, 0.66), rough=0.8)
    for i in range(3):
        L.lathe(f'RM_spool{i}', [(0.05, dz + 0.04), (0.07, dz + 0.045), (0.045, dz + 0.055), (0.045, dz + 0.12), (0.07, dz + 0.13), (0.0, dz + 0.135)], wick, c, loc=(-0.62 + 0.16 * i, -0.22, 0), seg=16, w=0.005)
    # ink pot and pen, spectacles, magnifier, loose keys and tags on the blotter
    glassm = L.mat('RM_inkpot', (0.05, 0.08, 0.16), rough=0.25, spec=0.6, paint=0)
    L.lathe('RM_inkpot', [(0.06, dz + 0.04), (0.065, dz + 0.1), (0.03, dz + 0.13), (0.032, dz + 0.16), (0, dz + 0.16)], glassm, c, loc=(-0.40, -0.36, 0), seg=16, w=0.006)
    L.cyl('RM_pen', 0.008, 0.34, (-0.38, -0.32, dz + 0.27), L.mat('RM_penm', (0.8, 0.72, 0.5), rough=0.5, paint=0), c, rot=(math.radians(16), math.radians(-14), 0), seg=8, w=0.003)
    for sx_ in (-0.05, 0.05):
        L.lathe(f'RM_lens{sx_}', [(0.038, dz + 0.054), (0.045, dz + 0.058), (0.038, dz + 0.062), (0.0, dz + 0.062)], brass, c, loc=(0.28 + sx_, -0.64, 0), seg=16, w=0.002)
    L.box('RM_bridge', (0.03, 0.006, 0.006), (0.28, -0.64, dz + 0.058), brass, c)
    L.cyl('RM_mag', 0.08, 0.012, (-0.36, -0.8, dz + 0.062), L.mat('RM_magg', (0.7, 0.8, 0.86), rough=0.1, spec=0.7, paint=0), c, seg=24, w=0.006)
    L.box('RM_magh', (0.2, 0.03, 0.02), (-0.2, -0.86, dz + 0.062), deskf, c, rot=(0, 0, math.radians(-20)), w=0.004)
    for i, (x_, y_, r_) in enumerate(((0.12, -0.92, 20), (0.2, -0.86, -35), (-0.1, -0.98, 70))):
        L.box(f'RM_tag{i}', (0.1, 0.06, 0.004), (x_, y_, dz + 0.058), paper, c, rot=(0, 0, math.radians(r_)), w=0.003)
    # second shelf row and wall clock
    L.box('RM_shelf2', (1.3, 0.3, 0.05), (-1.75, 2.92, 1.95), deskf, c, w=0.01)
    for i in range(5):
        L.box(f'RM_box{i}', (0.2, 0.2, 0.2 + 0.03 * (i % 3)), (-2.25 + 0.26 * i, 2.92, 2.08), L.mat(f'RM_bx{i % 3}', ((0.55, 0.42, 0.22), (0.3, 0.14, 0.1), (0.2, 0.3, 0.34))[i % 3], rough=0.7), c, w=0.007)
    L.cyl('RM_clock', 0.2, 0.05, (0.42, 3.05, 2.62), L.mat('RM_clockf', (0.9, 0.86, 0.72), rough=0.5, paint=0), c, rot=(math.pi / 2, 0, 0), seg=28, w=0.01)
    L.box('RM_ch1', (0.02, 0.02, 0.13), (0.42, 3.02, 2.68), dark, c)
    L.box('RM_ch2', (0.1, 0.02, 0.02), (0.46, 3.02, 2.62), dark, c)
    # framed poster on the back wall
    pst = L.tex_mat('RM_poster', f'{T}/poster.png', rough=0.7)
    o = L.box('RM_posterP', (0.5, 0.012, 0.72), (-2.0, 3.08, 2.3), pst, c, w=0.008)
    _uvbox(o, 0.5, 0.72)
    pool = bpy.data.lights.new('RM_pool', 'SPOT')
    pool.energy = 60
    pool.color = (1.0, 0.86, 0.68) if not night else (1.0, 0.82, 0.58)
    pool.spot_size = math.radians(95)
    pool.spot_blend = 1.0
    pool.shadow_soft_size = 0.35
    po = bpy.data.objects.new('RM_poolL', pool)
    c.objects.link(po)
    po.location = (-0.25, 0.0, 2.25)
    # tall shelf unit on the right wall behind the desk, full of boxes
    sh = L.wood_mat('RM_shelfw', (0.36, 0.18, 0.08), (0.20, 0.10, 0.05), axes='xz', grain=(1.0, 12.0))
    L.box('RM_case', (0.9, 0.34, 3.0), (2.0, 2.86, 1.5), sh, c, w=0.014)
    rnd = random.Random(4)
    for r in range(5):
        z = 0.4 + r * 0.56
        L.box(f'RM_cs{r}', (0.82, 0.04, 0.04), (2.0, 2.68, z), trim, c, w=0.008)
        x = 1.62
        while x < 2.34:
            w_ = rnd.uniform(0.09, 0.2)
            h_ = rnd.uniform(0.22, 0.4)
            col = rnd.choice(((0.5, 0.1, 0.1), (0.1, 0.2, 0.4), (0.6, 0.42, 0.12), (0.12, 0.3, 0.2), (0.75, 0.68, 0.5)))
            L.box(f'RM_b{r}_{x:.2f}', (w_, 0.2, h_), (x + w_ / 2, 2.67, z + 0.02 + h_ / 2), L.mat(f'RM_bk_{col[0]}', col, rough=0.5, paint=0.04), c, w=0.006)
            x += w_ + 0.02
    # hanging lamp shade over the desk
    L.cyl('RM_cord', 0.012, 1.0, (-0.25, 0.1, 3.0), dark, c, seg=8, w=0.003)
    L.lathe('RM_shade', [(0.36, 2.28), (0.34, 2.32), (0.12, 2.5), (0.05, 2.54), (0, 2.54)], L.mat('RM_shadeM', (0.08, 0.27, 0.20), rough=0.85, spec=0.05), c, loc=(-0.25, 0.1, 0), seg=28, w=0.011)
    return c
