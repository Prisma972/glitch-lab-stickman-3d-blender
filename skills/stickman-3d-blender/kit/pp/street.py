"""Day street set (original layout): pavement along +Y, shops on the right, road and far shops on the left."""
import bpy, math, random
from mathutils import Vector
import look as L
from PIL_signs import sign_path


def _mats():
    M = {}
    M['pave'] = L.brick_mat('ST_pave', (0.47, 0.47, 0.44), (0.42, 0.42, 0.40), (0.21, 0.20, 0.19), axes='xy', bw=0.74, bh=0.74,
                            mortar_size=0.006, offset=0.0, rough=0.78, spec=0.14, paint=0.17, pscale=0.35, pdetail=2.0, prough=0.45)
    M['curb'] = L.mat('ST_curb', (0.50, 0.49, 0.46), rough=0.8)
    M['road'] = L.brick_mat('ST_road', (0.30, 0.30, 0.31), (0.21, 0.21, 0.23), (0.055, 0.05, 0.05), axes='xy', bw=0.30, bh=0.20,
                            mortar_size=0.016, rough=0.6, spec=0.3, paint=0.10)
    M['brick_a'] = L.brick_mat('ST_brickA', (0.27, 0.13, 0.10), (0.21, 0.10, 0.08), (0.42, 0.38, 0.33), axes='yz')
    M['brick_b'] = L.brick_mat('ST_brickB', (0.25, 0.10, 0.075), (0.20, 0.08, 0.065), (0.40, 0.34, 0.29), axes='yz')
    M['brick_c'] = L.brick_mat('ST_brickC', (0.46, 0.25, 0.12), (0.38, 0.20, 0.10), (0.56, 0.48, 0.38), axes='yz')
    M['plaster'] = L.mat('ST_plaster', (0.80, 0.72, 0.58), rough=0.8, paint=0.08, pscale=1.3)
    M['plaster2'] = L.mat('ST_plaster2', (0.45, 0.58, 0.60), rough=0.8, paint=0.08, pscale=1.3)
    M['cream'] = L.mat('ST_cream', (0.86, 0.80, 0.68), rough=0.6, paint=0.04)
    M['teal'] = L.mat('ST_teal', (0.035, 0.26, 0.22), rough=0.45, spec=0.35, paint=0.06)
    M['green'] = L.mat('ST_green', (0.05, 0.20, 0.12), rough=0.45, spec=0.35, paint=0.06)
    M['navy'] = L.mat('ST_navy', (0.03, 0.09, 0.26), rough=0.45, spec=0.35, paint=0.06)
    M['plum'] = L.mat('ST_plum', (0.16, 0.07, 0.11), rough=0.45, spec=0.35, paint=0.06)
    M['iron'] = L.mat('ST_iron', (0.03, 0.055, 0.05), rough=0.42, spec=0.4, paint=0.03)
    M['gold'] = L.mat('ST_gold', (0.85, 0.57, 0.14), rough=0.35, spec=0.5, paint=0.03)
    M['glass'] = L.glass_mat('ST_glass')
    M['shop_in'] = L.glow_mat('ST_shop_in', (1.0, 0.72, 0.36), 1.25)
    M['roof'] = L.mat('ST_roof', (0.20, 0.17, 0.17), rough=0.7)
    M['stripeW'] = L.mat('ST_stripeW', (0.90, 0.87, 0.78), rough=0.7, paint=0.04)
    M['wood'] = L.wood_mat('ST_wood', (0.62, 0.40, 0.19), (0.36, 0.20, 0.08), axes='xz', grain=(1.2, 12.0))
    M['crate'] = L.wood_mat('ST_crate', (0.68, 0.46, 0.24), (0.42, 0.25, 0.11), axes='xz', grain=(1.4, 15.0))
    return M


DISP = {'green': 'tea', 'plum': 'cake', 'navy': 'clock', 'teal': 'jar'}


def window(c, name, M, y, z, w, h, x, frame='cream', face=-1, sill=True, mullion=(1, 2), ow=0.012):
    """Sash window on a facade plane at world x, centre (y, z). face = outward x sign."""
    d = 0.08
    L.box(f'{name}_gl', (0.02, w, h), (x + face * 0.01, y, z), M['glass'], c)
    fw = 0.055
    fm = M[frame]
    for sgn in (-1, 1):
        L.box(f'{name}_fv{sgn}', (d, fw, h + fw), (x + face * 0.03, y + sgn * w / 2, z), fm, c, w=ow)
        L.box(f'{name}_fh{sgn}', (d, w + fw * 2, fw), (x + face * 0.03, y, z + sgn * h / 2), fm, c, w=ow)
    for i in range(1, mullion[0] + 1):
        yy = y - w / 2 + w * i / (mullion[0] + 1)
        L.box(f'{name}_mv{i}', (0.03, 0.022, h), (x + face * 0.025, yy, z), fm, c, w=ow * 0.5)
    for i in range(1, mullion[1] + 1):
        zz = z - h / 2 + h * i / (mullion[1] + 1)
        L.box(f'{name}_mh{i}', (0.03, w, 0.022), (x + face * 0.025, y, zz), fm, c, w=ow * 0.5)
    if sill:
        L.box(f'{name}_sill', (0.16, w + 0.22, 0.06), (x + face * 0.06, y, z - h / 2 - 0.05), M['cream'], c, w=ow)


def shop(c, name, M, y0, width, height, x=3.0, face=-1, wall='brick_a', trim='teal', sign=None, sign_ink=None, floors=2, awning=None):
    """One shop unit, facade on plane x, spanning y0..y0+width."""
    yc = y0 + width / 2
    depth = 6.0
    # building mass
    L.box(f'{name}_mass', (depth, width, height), (x - face * depth / 2, yc, height / 2), M[wall], c, w=0.016)
    # cornice
    L.box(f'{name}_cor', (0.42, width + 0.1, 0.22), (x + face * 0.13, yc, height), M['cream'], c, w=0.014)
    L.box(f'{name}_cor2', (0.26, width + 0.04, 0.10), (x + face * 0.06, yc, height - 0.2), M['cream'], c, w=0.01)
    # shopfront
    sf_h = 3.35
    L.box(f'{name}_sf', (0.24, width - 0.12, sf_h), (x + face * 0.12, yc, sf_h / 2), M[trim], c, w=0.014)
    # fascia with painted sign
    fas_h = 0.72
    if sign:
        sm = L.tex_mat(f'ST_sign_{name}', sign_path(sign, width, fas_h, sign_ink or (0.95, 0.85, 0.55), trim), rough=0.4, spec=0.3)
        o = L.box(f'{name}_fas', (0.10, width - 0.25, fas_h), (x + face * 0.30, yc, sf_h - 0.15), M[trim], c, w=0.012)
        p = _plane(f'{name}_signp', width - 0.34, fas_h - 0.10, (x + face * 0.352, yc, sf_h - 0.15), sm, c, face)
    # glazing: warm interior with mullions
    gw = width - 1.75
    door_w = 0.95
    gy = y0 + 0.28 + gw / 2
    dm = L.tex_mat(f'ST_disp{DISP[trim]}', f'{L.ROOT}/tex/signs/display_{DISP[trim]}.png', rough=0.25, spec=0.5, emis=0.42)
    _plane(f'{name}_shopwin', gw, 1.95, (x + face * 0.245, gy, 1.65), dm, c, face)
    for i in range(0, 4):
        yy = gy - gw / 2 + gw * i / 3
        L.box(f'{name}_wm{i}', (0.06, 0.05, 1.98), (x + face * 0.26, yy, 1.65), M[trim], c, w=0.008)
    L.box(f'{name}_wb', (0.06, gw, 0.05), (x + face * 0.26, gy, 2.1), M[trim], c, w=0.007)
    L.box(f'{name}_stall', (0.16, gw + 0.1, 0.66), (x + face * 0.30, gy, 0.33), M['cream'] if trim != 'teal' else M[trim], c, w=0.012)
    # door
    dy = y0 + width - 0.3 - door_w / 2
    L.box(f'{name}_door', (0.06, door_w, 2.3), (x + face * 0.26, dy, 1.15), M[trim], c, w=0.012)
    L.box(f'{name}_dgl', (0.02, door_w - 0.26, 1.15), (x + face * 0.295, dy, 1.62), M['glass'], c, w=0.008)
    L.cyl(f'{name}_knob', 0.038, 0.06, (x + face * 0.31, dy - door_w / 2 + 0.11, 1.05), M['gold'], c, rot=(0, math.pi / 2, 0), seg=12, w=0.005)
    # upper windows
    nwin = max(2, int(width / 1.7))
    for fl in range(floors):
        z = sf_h + 1.28 + fl * 2.35
        if z + 0.9 > height:
            break
        for i in range(nwin):
            yy = y0 + width * (i + 0.5) / nwin
            window(c, f'{name}_w{fl}{i}', M, yy, z, 0.9, 1.45, x + face * 0.0, face=face)
    if awning:
        _awning(c, name, M, y0 + 0.1, gw + 0.4, x, face, awning)


def _plane(name, w, h, loc, m, coll, face):
    """Plane facing world +-X with proper UVs."""
    import bmesh
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new()
    sg = 1 if face < 0 else -1
    vs = [bm.verts.new((0, sg * w / 2 * s1, h / 2 * s2)) for s1, s2 in ((1, -1), (-1, -1), (-1, 1), (1, 1))]
    f = bm.faces.new(vs)
    for l, (u, v) in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
        l[uv].uv = (u, v)
    return L.obj_from_bm(name, bm, m, coll, loc=loc)


def _awning(c, name, M, y0, length, x, face, col):
    """Striped sloped awning."""
    n = max(6, int(length / 0.42))
    w = length / n
    drop, out = 0.72, 1.45
    for i in range(n):
        y = y0 + w * (i + 0.5)
        m = M['stripeW'] if i % 2 == 0 else M[col]
        ang = math.atan2(drop, out)
        L.box(f'{name}_aw{i}', (math.hypot(out, drop), w, 0.03), (x + face * (0.32 + out / 2), y, 3.02 - drop / 2), m, c,
              rot=(0, -face * ang * -1, 0), w=0.007)
        # scalloped valance
        L.box(f'{name}_av{i}', (0.025, w, 0.18), (x + face * (0.32 + out + 0.012), y, 3.02 - drop - 0.09), m, c, w=0.006)


def lamp(c, name, M, loc):
    x, y = loc
    L.lathe(name + '_base', [(0.2, 0), (0.2, 0.12), (0.12, 0.2), (0.085, 0.65), (0.06, 0.72)], M['iron'], c, loc=(x, y, 0), seg=20, w=0.012)
    L.cyl(name + '_post', 0.05, 3.3, (x, y, 2.3), M['iron'], c, seg=14, w=0.012, r2=0.038)
    L.lathe(name + '_ring', [(0.09, 3.9), (0.1, 3.95), (0.06, 4.0)], M['iron'], c, loc=(x, y, 0), seg=16, w=0.008)
    gl = L.glow_mat('ST_lampglass', (1.0, 0.9, 0.62), 0.9)
    L.lathe(name + '_glass', [(0.11, 3.98), (0.21, 4.48), (0.0, 4.5)], gl, c, loc=(x, y, 0), seg=6, smooth=False, w=0.012)
    L.lathe(name + '_cap', [(0.25, 4.48), (0.26, 4.5), (0.05, 4.72), (0.0, 4.82)], M['iron'], c, loc=(x, y, 0), seg=6, smooth=False, w=0.012)


def bench_stall(c, name, M, loc, rot=0.0):
    """Fruit stall: trestle with crates of apples and oranges under a small canopy."""
    root = L.empty(name, (*loc, 0), coll=c, rot=(0, 0, rot))
    L.box(name + '_top', (1.8, 0.8, 0.07), (0, 0, 0.82), M['wood'], c, parent=root, w=0.011)
    for sx in (-1, 1):
        for sy in (-1, 1):
            L.box(f'{name}_leg{sx}{sy}', (0.07, 0.07, 0.8), (sx * 0.8, sy * 0.32, 0.4), M['wood'], c, parent=root, w=0.01)
    apple = L.mat('ST_apple', (0.62, 0.05, 0.05), rough=0.3, spec=0.5, paint=0.05)
    orange = L.mat('ST_orange', (0.88, 0.40, 0.04), rough=0.4, spec=0.4, paint=0.05)
    pear = L.mat('ST_pear', (0.52, 0.60, 0.12), rough=0.4, spec=0.4, paint=0.05)
    rnd = random.Random(7)
    for i, (cx, fm) in enumerate(((-0.58, apple), (0.0, orange), (0.58, pear))):
        L.box(f'{name}_cr{i}', (0.54, 0.62, 0.2), (cx, 0, 0.96), M['crate'], c, parent=root, w=0.009)
        for k in range(16):
            px = cx + (k % 4 - 1.5) * 0.118 + rnd.uniform(-.01, .01)
            py = (k // 4 - 1.5) * 0.135 + rnd.uniform(-.01, .01)
            L.sph(f'{name}_f{i}_{k}', (0.066, 0.066, 0.062), (px, py, 1.09 + rnd.uniform(0, 0.03)), fm, c, parent=root, seg=12, w=0.004)
    return root


def bin_(c, name, M, loc):
    L.lathe(name, [(0.2, 0.0), (0.26, 0.86), (0.275, 0.9), (0.275, 0.94), (0.0, 0.95)], M['green'], c, loc=(*loc, 0), seg=24, w=0.011)


def barrel_flowers(c, name, M, loc):
    x, y = loc
    L.lathe(name, [(0.27, 0), (0.33, 0.3), (0.27, 0.62), (0.0, 0.62)], M['crate'], c, loc=(x, y, 0), seg=20, w=0.01)
    for i, z in enumerate((0.12, 0.5)):
        L.lathe(f'{name}_h{i}', [(0.305 + 0.02 * (1 - i), z - 0.02), (0.315 + 0.02 * (1 - i), z), (0.305 + 0.02 * (1 - i), z + 0.02)], M['iron'], c, loc=(x, y, 0), seg=20)
    leaf = L.mat('ST_leaf', (0.10, 0.30, 0.09), rough=0.6, paint=0.14, pscale=9)
    pet = [L.mat('ST_pet1', (0.85, 0.15, 0.25), rough=0.6), L.mat('ST_pet2', (0.92, 0.72, 0.10), rough=0.6), L.mat('ST_pet3', (0.88, 0.88, 0.85), rough=0.6)]
    rnd = random.Random(int(abs(x * 13 + y)))
    for i in range(14):
        a = rnd.uniform(0, 6.28); r = rnd.uniform(0, 0.24)
        L.sph(f'{name}_l{i}', (0.09, 0.09, 0.075), (x + r * math.cos(a), y + r * math.sin(a), 0.68 + rnd.uniform(0, 0.13)), leaf, c, seg=10, w=0.005)
    for i in range(10):
        a = rnd.uniform(0, 6.28); r = rnd.uniform(0, 0.27)
        L.sph(f'{name}_p{i}', (0.05, 0.05, 0.04), (x + r * math.cos(a), y + r * math.sin(a), 0.78 + rnd.uniform(0, 0.12)), pet[i % 3], c, seg=8, w=0.004)


def litter(c, n=170, x0=-2.3, x1=2.6, y0=-5, y1=26):
    """Confetti of leaves and paper on the pavement, one mesh."""
    import bmesh
    cols = [(0.72, 0.28, 0.14), (0.86, 0.60, 0.16), (0.82, 0.50, 0.42), (0.90, 0.86, 0.72)]
    rnd = random.Random(21)
    for ci, col in enumerate(cols):
        bm = bmesh.new()
        for i in range(n // len(cols)):
            x = rnd.uniform(x0, x1); y = rnd.uniform(y0, y1)
            a = rnd.uniform(0, 6.28); s = rnd.uniform(0.03, 0.065)
            vs = []
            for k in range(5):
                t = a + k * 6.283 / 5
                r = s * (1 + 0.5 * math.sin(k * 2.2 + a))
                vs.append(bm.verts.new((x + r * math.cos(t), y + r * 0.7 * math.sin(t), 0.004)))
            bm.faces.new(vs)
        L.obj_from_bm(f'ST_litter{ci}', bm, L.mat(f'ST_lit{ci}', col, rough=0.8, paint=0.0), c)


def build():
    c = L.collection('SET_street')
    M = _mats()
    # ground
    L.box('ST_pavement', (5.4, 120, 0.3), (0.0, 40, -0.15), M['pave'], c)
    L.box('ST_curbstone', (0.32, 120, 0.32), (-2.86, 40, -0.14), M['curb'], c, w=0.012)
    L.box('ST_road', (4.9, 120, 0.3), (-5.3, 40, -0.28), M['road'], c)
    L.box('ST_farpave', (1.8, 120, 0.3), (-8.6, 40, -0.15), M['pave'], c)
    L.box('ST_farcurb', (0.3, 120, 0.32), (-7.7, 40, -0.14), M['curb'], c, w=0.012)
    L.box('ST_endwall', (60, 1, 0.1), (0, 400, 0), M['curb'], c)

    # right side, far to near
    y = -8.0
    specs = [
        (6.2, 10.2, 'brick_a', 'green', 'P. MARROW  FINE TEAS', (0.96, 0.86, 0.60), 'green'),
        (5.0, 9.4, 'plaster', 'plum', 'PLUM & CRUST BAKERY', (0.98, 0.84, 0.72), 'plum'),
        (5.6, 11.6, 'brick_b', 'navy', 'TOLLIVER CLOCKS', (0.92, 0.88, 0.70), None),
        (5.2, 9.6, 'brick_c', 'teal', 'THE KETTLE ROOM', (0.98, 0.92, 0.72), 'teal'),
        (6.0, 10.8, 'brick_a', 'plum', 'ODD BOOKS', (0.96, 0.86, 0.60), None),
        (5.4, 10.0, 'plaster2', 'green', 'GRANGER & CO', (0.96, 0.90, 0.72), 'green'),
        (6.2, 11.2, 'brick_b', 'teal', 'HAT & GLOVE', (0.96, 0.92, 0.74), None),
        (5.6, 9.8, 'plaster', 'navy', 'NINE LANTERNS', (0.92, 0.88, 0.70), 'navy'),
    ]
    for i, (w, h, wall, trim, sign, ink, aw) in enumerate(specs):
        shop(c, f'R{i}', M, y, w, h, x=3.0, face=-1, wall=wall, trim=trim, sign=sign, sign_ink=ink, awning=aw)
        y += w
    # far side of the road, facing +x
    y = -14.0
    far = [('brick_c', 'teal', 7.0, 12.5), ('plaster', 'green', 6.0, 10.5), ('brick_a', 'navy', 8.0, 13.5), ('plaster2', 'plum', 6.5, 11.0),
           ('brick_b', 'green', 7.5, 12.0), ('brick_c', 'navy', 6.5, 10.8), ('plaster', 'teal', 7.5, 12.8), ('brick_a', 'green', 8.0, 11.5),
           ('plaster2', 'navy', 7.0, 12.0)]
    for i, (wall, trim, w, h) in enumerate(far):
        shop(c, f'L{i}', M, y, w, h * 0.56, x=-9.5, face=1, wall=wall, trim=trim, floors=1)
        y += w

    # hills and end of street
    # the street ends on a terrace of buildings, never on open sky
    bx = {'a': L.brick_mat('ST_brickXa', (0.33, 0.10, 0.06), (0.25, 0.075, 0.05), (0.46, 0.39, 0.32), axes='xz'),
          'b': L.brick_mat('ST_brickXb', (0.46, 0.25, 0.12), (0.38, 0.20, 0.10), (0.56, 0.48, 0.38), axes='xz'),
          'c': L.mat('ST_plasterX', (0.62, 0.66, 0.60), rough=0.8, paint=0.08, pscale=1.3)}
    for i, (x, w_, h_, k, tm) in enumerate(((-14, 8.5, 12.5, 'a', 'navy'), (-5.6, 8.5, 15.0, 'c', 'green'), (2.8, 8.5, 12.0, 'b', 'teal'), (11.2, 8.5, 14.0, 'a', 'plum'))):
        L.box(f'ST_end{i}', (w_, 6, h_), (x, 58, h_ / 2), bx[k], c, w=0.03)
        L.box(f'ST_endc{i}', (w_ + 0.3, 0.5, 0.4), (x, 54.9, h_), M['cream'], c, w=0.03)
        L.box(f'ST_endr{i}', (w_ + 0.1, 5.6, 2.2), (x, 58, h_ + 1.1), M['roof'], c, w=0.03)
        L.box(f'ST_ends{i}', (w_ - 0.2, 0.3, 3.3), (x, 54.9, 1.65), M[tm], c, w=0.03)
        L.box(f'ST_endd{i}', (w_ - 2.4, 0.1, 1.7), (x, 54.72, 1.75), M['shop_in'], c, w=0.02)
        for r in range(int((h_ - 4.5) / 2.9)):
            for q in range(3):
                wx, wz = x - 2.6 + q * 2.6, 5.2 + r * 2.9
                L.box(f'ST_endw{i}{r}{q}', (1.3, 0.12, 1.8), (wx, 54.94, wz), M['cream'], c, w=0.02)
                L.box(f'ST_endg{i}{r}{q}', (1.05, 0.14, 1.55), (wx, 54.92, wz), M['glass'], c)
    # street furniture
    for i, y in enumerate((-3.6, 7.6, 18.8, 30.0, 41.2)):
        lamp(c, f'ST_lamp{i}', M, (-2.32, y))
    bench_stall(c, 'ST_stall', M, (1.85, 8.3), rot=math.radians(-90))
    bin_(c, 'ST_bin', M, (-2.2, 3.2))
    barrel_flowers(c, 'ST_barrel1', M, (2.2, 2.5))
    barrel_flowers(c, 'ST_barrel2', M, (2.25, 14.0))
    for i in range(3):
        L.box(f'ST_crateS{i}', (0.6, 0.6, 0.5), (2.25 - 0.05 * i, 5.3 + 0.1 * i, 0.25 + 0.5 * (i == 2)), M['crate'], c,
              rot=(0, 0, 0.1 * i), w=0.01) if i != 1 else None
    litter(c, n=340)
    cracks(c)
    stains(c)
    for i, (y, side) in enumerate(((1.4, 0), (6.4, 1), (12.2, 0), (17.5, 1), (22.6, 0), (28.0, 1))):
        blade_sign(c, f'ST_blade{i}', M, y, ('teal', 'plum', 'green', 'navy', 'teal', 'plum')[i])
    poster_column(c, 'ST_column', M, (-1.95, 8.2))
    tram(c, 'ST_tram', M, (-4.4, 15.5))
    for i, y in enumerate((4.5, 13.0, 23.0, 33.0)):
        bunting(c, f'ST_bunt{i}', M, y)
    a_board(c, 'ST_board', M, (2.05, -0.8), math.radians(-70))
    dress_street(c, M)
    return c, M


def cracks(c, n=70):
    """Ink cracks across the slabs: flat ribbons on the ground, so the line pass leaves them thin."""
    import bmesh
    bm = bmesh.new()
    rnd = random.Random(5)
    for i in range(n):
        x, y = rnd.uniform(-2.5, 2.5), rnd.uniform(-5, 24)
        a = rnd.uniform(0, 6.28)
        prev = None
        sg = 1
        pts = rnd.randint(12, 20)
        for k in range(pts):
            # stair-stepped, with short side twigs. Widened across y to cancel the ground foreshortening
            w = rnd.uniform(0.005, 0.007) * (1 - 0.8 * abs(k - pts / 2) / (pts / 2))
            nx, ny = -math.sin(a) * w, math.cos(a) * w * 3
            cur = (bm.verts.new((x + nx, y + ny, 0.0015)), bm.verts.new((x - nx, y - ny, 0.0015)))
            if prev:
                bm.faces.new((prev[0], prev[1], cur[1], cur[0]))
            prev = cur
            if rnd.random() < 0.3:
                ta = a + rnd.choice((-1, 1)) * rnd.uniform(0.9, 1.4)
                tl = rnd.uniform(0.04, 0.09)
                tip = bm.verts.new((x + tl * math.cos(ta), y + tl * math.sin(ta), 0.0015))
                bm.faces.new((cur[0], tip, cur[1]))
            a += sg * rnd.uniform(0.7, 1.3)
            sg = -sg
            st = rnd.uniform(0.03, 0.08)
            x += st * math.cos(a); y += st * math.sin(a)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        if f.normal.z < 0:
            f.normal_flip()
    L.obj_from_bm('ST_cracks', bm, L.line_mat(), c)


def stains(c, n=40):
    """Dark oil and water marks: irregular flat discs."""
    import bmesh
    rnd = random.Random(11)
    st = L.mat('ST_stain', (0.30, 0.30, 0.29), rough=0.5, spec=0.3, paint=0.2, pscale=3.0)
    bm = bmesh.new()
    for i in range(n):
        x, y = rnd.uniform(-2.5, 2.5), rnd.uniform(-5, 26)
        r = rnd.uniform(0.03, 0.12)
        vs = []
        for k in range(24):
            t = k * 6.283 / 24
            rr = r * (1 + 0.15 * math.sin(k * 0.8 + i))
            vs.append(bm.verts.new((x + rr * math.cos(t) * 1.4, y + rr * math.sin(t), 0.002)))
        bm.faces.new(vs)
    L.obj_from_bm('ST_stains', bm, st, c)


def blade_sign(c, name, M, y, col):
    """Projecting bracket sign on the right-hand facades."""
    x = 3.0
    L.box(name + '_arm', (1.15, 0.05, 0.05), (x - 0.58, y, 4.3), M['iron'], c, w=0.008)
    L.box(name + '_arm2', (0.9, 0.04, 0.04), (x - 0.45, y, 3.62), M['iron'], c, rot=(0, math.radians(-30), 0), w=0.006)
    L.box(name + '_board', (0.82, 0.06, 0.56), (x - 0.72, y, 3.95), M[col], c, w=0.012)
    L.box(name + '_bin', (0.62, 0.075, 0.36), (x - 0.72, y, 3.95), M['cream'], c, w=0.006)
    t = L.tex_mat(f'ST_blade_{name[-1]}', f'{L.ROOT}/tex/signs/blade{name[-1]}.png', rough=0.6)
    import bmesh
    for sgn in (-1, 1):
        bm = bmesh.new()
        uv = bm.loops.layers.uv.new()
        vs = [bm.verts.new((-sgn * 0.3 * a_, 0, 0.17 * b_)) for a_, b_ in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        f_ = bm.faces.new(vs if sgn < 0 else list(reversed(vs)))
        for l_, (u_, v_) in zip(f_.loops, ((0, 0), (1, 0), (1, 1), (0, 1)) if sgn < 0 else ((0, 1), (1, 1), (1, 0), (0, 0))):
            l_[uv].uv = (u_, v_)
        L.obj_from_bm(f'{name}_t{sgn}', bm, t, c, loc=(x - 0.72, y + sgn * 0.04, 3.95))


def poster_column(c, name, M, loc):
    x, y = loc
    pm = L.tex_mat('ST_posters', f'{L.ROOT}/tex/signs/posters.png', rough=0.6, spec=0.2)
    L.lathe(name + '_base', [(0.5, 0), (0.5, 0.25), (0.42, 0.32)], M['green'], c, loc=(x, y, 0), seg=28, w=0.012)
    col = L.cyl(name + '_body', 0.42, 2.5, (x, y, 1.57), pm, c, seg=32, w=0.012)
    L.lathe(name + '_cap', [(0.46, 2.82), (0.54, 2.86), (0.54, 2.94), (0.28, 3.18), (0.05, 3.3), (0, 3.42)], M['green'], c, loc=(x, y, 0), seg=28, w=0.012)
    _uv_cyl(col)


def _uv_cyl(o):
    me = o.data
    uv = me.uv_layers.new(name='UV')
    for poly in me.polygons:
        for li in poly.loop_indices:
            v = me.vertices[me.loops[li].vertex_index].co
            uv.data[li].uv = (math.atan2(v.y, v.x) / 6.2832 * 3 + .5, v.z / 2.5 + .5)


def tram(c, name, M, loc):
    """Cream and maroon single-deck tram on the road, seen end-on from down the street."""
    x, y = loc
    mr = L.mat('ST_tram1', (0.32, 0.055, 0.075), rough=0.4, spec=0.45, paint=0.05)
    cr = L.mat('ST_tram2', (0.84, 0.76, 0.56), rough=0.4, spec=0.4, paint=0.04)
    L.box(name + '_low', (2.1, 9.0, 1.15), (x, y, 1.0), mr, c, w=0.016, bevel=0.06)
    L.box(name + '_up', (2.0, 8.8, 1.15), (x, y, 2.15), cr, c, w=0.016, bevel=0.05)
    L.box(name + '_roof', (2.2, 9.1, 0.18), (x, y, 2.82), mr, c, w=0.016, bevel=0.06)
    L.box(name + '_vent', (1.0, 7.0, 0.16), (x, y, 2.98), cr, c, w=0.01, bevel=0.03)
    for i in range(6):
        L.box(f'{name}_win{i}', (0.03, 1.1, 0.8), (x + 1.01, y - 3.6 + 1.44 * i, 2.15), M['glass'], c, w=0.01)
    L.box(name + '_endw', (1.5, 0.03, 0.8), (x, y - 4.41, 2.15), M['glass'], c, w=0.01)
    for sx in (-0.75, 0.75):
        for yy in (-3, 3):
            L.cyl(f'{name}_wh{sx}{yy}', 0.3, 0.1, (x + sx, y + yy, 0.28), M['iron'], c, rot=(0, math.pi / 2, 0), seg=16, w=0.008)
    L.sph(name + '_lamp', (0.13, 0.05, 0.13), (x, y - 4.53, 1.2), L.glow_mat('ST_tl', (1, 0.86, 0.55), 1.2), c, w=0.01)
    L.box(name + '_pole', (0.04, 3.2, 0.04), (x, y + 1.2, 3.8), M['iron'], c, rot=(math.radians(28), 0, 0), w=0.004)
    L.box(name + '_wire', (0.012, 120, 0.012), (x, 40, 4.55), M['iron'], c)
    for sx in (-0.72, 0.72):
        L.box(f'{name}_rail{sx}', (0.07, 120, 0.02), (x + sx, 40, -0.125), L.mat('ST_rail', (0.45, 0.43, 0.42), rough=0.3, spec=0.6), c)


def a_board(c, name, M, loc, rot):
    bm = L.tex_mat('ST_chalk', f'{L.ROOT}/tex/signs/chalk.png', rough=0.8)
    root = L.empty(name, (*loc, 0), coll=c, rot=(0, 0, rot))
    for s in (-1, 1):
        L.box(f'{name}_fr{s}', (0.72, 0.04, 1.05), (0, s * 0.17, 0.52), M['wood'], c, parent=root, rot=(s * math.radians(9), 0, 0), w=0.01)
    pl = L.box(name + '_face', (0.58, 0.01, 0.88), (0, -0.197, 0.53), bm, c, parent=root, rot=(math.radians(-9), 0, 0))
    me = pl.data
    uv = me.uv_layers.new(name='UV')
    for poly in me.polygons:
        for li in poly.loop_indices:
            v = me.vertices[me.loops[li].vertex_index].co
            uv.data[li].uv = (v.x / 0.58 + .5, v.z / 0.88 + .5)


def bunting(c, name, M, y):
    """String of small flags across the street, sagging between the facades."""
    import bmesh
    x0, x1, z0, sag = -9.3, 2.9, 6.1, 1.0
    pts = []
    n = 26
    for i in range(n + 1):
        t = i / n
        pts.append((x0 + (x1 - x0) * t, y, z0 - sag * 4 * t * (1 - t)))
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = 0.012
    s = cu.splines.new('POLY')
    s.points.add(len(pts) - 1)
    for p, q in zip(s.points, pts):
        p.co = (*q, 1)
    cu.materials.append(L.line_mat())
    o = bpy.data.objects.new(name, cu)
    c.objects.link(o)
    cols = [M['stripeW'], M['plum'], M['teal'], M['gold']]
    for k, m in enumerate(cols):
        bm = bmesh.new()
        for i in range(k, n, 4):
            x, _, z = pts[i]
            vs = [bm.verts.new(v) for v in ((x - 0.17, y, z), (x + 0.17, y, z), (x, y, z - 0.42))]
            bm.faces.new(vs)
        fl = L.obj_from_bm(f'{name}_f{k}', bm, m, c)
        sd = fl.modifiers.new('sd', 'SOLIDIFY')
        sd.thickness = 0.012
        L.ink(fl, 0.012)


def ground_pools(c, n=14):
    """Big blurred shadow pools lying on the pavement."""
    rnd = random.Random(19)
    m = L.halo_mat('ST_pool', (0.03, 0.03, 0.05), 1.0, 1.0, 0.5)
    for i in range(n):
        o = L.sph(f'ST_pool{i}', (1, 1, 0.002), (rnd.uniform(-2.6, 2.7), rnd.uniform(-6, 30), 0.004), m, c, rot=(0, 0, rnd.uniform(0, 3.14)), seg=20)
        k = rnd.uniform(0.7, 2.0)
        o.scale = (k * rnd.uniform(1.0, 1.9), k * 0.62, 1)


def shade_blobs(c):
    """Unseen canopy high up: only casts broad soft shadow pools across the pavement."""
    rnd = random.Random(14)
    m = L.mat('ST_blob', (0.2, 0.2, 0.2), paint=0.0)
    h = 5.2
    d = h / math.tan(math.radians(48))
    for i in range(30):
        gx, gy = rnd.uniform(-2.6, 2.8), rnd.uniform(-6, 26)
        r = rnd.uniform(0.35, 0.95)
        o = L.sph(f'ST_blob{i}', (r * 1.7, r, 0.2), (gx - d * 0.906, gy + d * 0.42, h), m, c, seg=12)
        o.visible_camera = False


def drainpipe(c, name, M, y, h):
    L.cyl(name, 0.05, h, (2.93, y, h / 2), M['iron'], c, seg=10, w=0.008)
    for k in range(int(h / 2.2)):
        L.box(f'{name}_b{k}', (0.1, 0.13, 0.04), (2.94, y, 1.1 + k * 2.2), M['iron'], c, w=0.004)


def _foliage(c, name, x, y, z, rx, ry, seed):
    rnd = random.Random(seed)
    leaf = L.mat('ST_leaf2', (0.09, 0.27, 0.10), rough=0.7, paint=0.12, pscale=6)
    pet = [L.mat('ST_pet1', (0.85, 0.15, 0.25), rough=0.6), L.mat('ST_pet2', (0.92, 0.72, 0.10), rough=0.6), L.mat('ST_pet3', (0.88, 0.88, 0.85), rough=0.6)]
    for i in range(9):
        L.sph(f'{name}_l{i}', (0.11, 0.11, 0.09), (x + rnd.uniform(-rx, rx), y + rnd.uniform(-ry, ry), z + rnd.uniform(0, 0.12)), leaf, c, seg=8, w=0.005)
    for i in range(7):
        L.sph(f'{name}_p{i}', (0.05, 0.05, 0.04), (x + rnd.uniform(-rx, rx), y + rnd.uniform(-ry, ry), z + 0.09 + rnd.uniform(0, 0.12)), pet[i % 3], c, seg=8, w=0.003)


def window_box(c, name, M, y, z, i):
    L.box(name, (0.26, 1.15, 0.2), (2.84, y, z), M['crate'], c, w=0.009)
    _foliage(c, name, 2.84, y, z + 0.12, 0.1, 0.5, i)


def basket(c, name, M, x, y):
    """Hanging basket on a lamp bracket."""
    L.box(name + '_arm', (0.7, 0.03, 0.03), (x + 0.35, y, 3.55), M['iron'], c, w=0.004)
    L.lathe(name, [(0.03, 2.92), (0.2, 3.0), (0.26, 3.14), (0.26, 3.18), (0.0, 3.18)], M['crate'], c, loc=(x + 0.66, y, 0), seg=14, w=0.007)
    for k, (dx, dy) in enumerate(((-0.1, 0), (0.1, 0), (0, 0.1))):
        L.box(f'{name}_ch{k}', (0.012, 0.012, 0.42), (x + 0.66 + dx * 0.6, y + dy * 0.6, 3.36), M['iron'], c)
    _foliage(c, name, x + 0.66, y, 3.18, 0.17, 0.17, int(y * 7) + 3)


def bench(c, name, M, loc, rot):
    root = L.empty(name, (*loc, 0), coll=c, rot=(0, 0, rot))
    for k in range(3):
        L.box(f'{name}_s{k}', (1.5, 0.11, 0.04), (0, -0.14 + k * 0.14, 0.47), M['wood'], c, parent=root, w=0.007)
    for k in range(3):
        L.box(f'{name}_b{k}', (1.5, 0.04, 0.1), (0, 0.24, 0.62 + k * 0.13), M['wood'], c, parent=root, w=0.007)
    for sx in (-0.68, 0.68):
        L.box(f'{name}_f{sx}', (0.06, 0.5, 0.05), (sx, 0.03, 0.44), M['iron'], c, parent=root, w=0.006)
        L.box(f'{name}_l{sx}', (0.06, 0.05, 0.46), (sx, -0.2, 0.23), M['iron'], c, parent=root, w=0.006)
        L.box(f'{name}_k{sx}', (0.06, 0.05, 0.86), (sx, 0.26, 0.43), M['iron'], c, parent=root, w=0.006)


def bollard(c, name, M, loc):
    L.lathe(name, [(0.1, 0), (0.09, 0.1), (0.07, 0.18), (0.07, 0.72), (0.09, 0.78), (0.05, 0.86), (0, 0.88)], M['iron'], c, loc=(*loc, 0), seg=14, w=0.008)


def manhole(c, name, M, loc):
    L.cyl(name, 0.36, 0.012, (*loc, 0.005), M['iron'], c, seg=28, w=0.008)
    L.cyl(name + '_in', 0.29, 0.016, (*loc, 0.007), L.mat('ST_mh', (0.10, 0.11, 0.10), rough=0.5), c, seg=24, w=0.004)


def sack_pile(c, name, M, loc):
    sk = L.mat('ST_sack', (0.62, 0.50, 0.32), rough=0.85, paint=0.12, pscale=5)
    x, y = loc
    for k, (dx, dy, z) in enumerate(((0, 0, 0.2), (0.42, 0.06, 0.2), (0.2, 0.05, 0.54))):
        L.sph(f'{name}{k}', (0.27, 0.2, 0.2), (x + dx, y + dy, z), sk, c, seg=14, w=0.008)


def open_sign(c, name, y, face=-1):
    m = L.tex_mat('ST_open', f'{L.ROOT}/tex/signs/open.png', rough=0.5)
    _plane(name, 0.46, 0.2, (2.66, y, 1.62), m, c, face)


def dress_street(c, M):
    y = -8.0
    for i, w in enumerate((6.2, 5.0, 5.6, 5.2, 6.0, 5.4, 6.2, 5.6)):
        drainpipe(c, f'ST_pipe{i}', M, y + w - 0.03, 9.0)
        y += w
    # flower boxes under first-floor windows, in the part of the street the camera sees
    for i, yy in enumerate((-0.2, 1.8, 5.3, 8.0, 10.7, 13.9, 16.1)):
        window_box(c, f'ST_wb{i}', M, yy, 4.28, i)
    for i, yy in enumerate((-3.6, 7.6, 18.8, 30.0)):
        basket(c, f'ST_bask{i}', M, -2.32, yy)
    bench(c, 'ST_bench', M, (2.42, 4.2), math.radians(-90))
    for i, yy in enumerate((-1.0, 1.4, 3.8, 6.2, 9.8, 12.2, 14.6, 17.0)):
        bollard(c, f'ST_boll{i}', M, (-2.5, yy))
    manhole(c, 'ST_mh1', M, (-0.9, 1.6))
    manhole(c, 'ST_mh2', M, (1.0, 7.4))
    sack_pile(c, 'ST_sacks', M, (1.85, 0.9))
    for i, yy in enumerate((3.4, 8.7, 14.4, 19.5)):
        open_sign(c, f'ST_open{i}', yy)
