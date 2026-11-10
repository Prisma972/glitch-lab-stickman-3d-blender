"""Night village (original): rows of gabled houses climbing to a ridge, a lighthouse, moon, layered hills."""
import bpy, bmesh, math, random
import look as L


def _house_meshes(name, w, d, h, rh, wall, roof, lit, door, mats):
    """Two meshes per house so the roof can carry a heavy ink line and the walls a fine one.
    Wide two-storey front: three windows up, door and two down, white frames, dark sills, plinth, step."""
    bm = bmesh.new()
    W_, LIT, DARK, DOOR, FRAME, SILL, PLINTH = range(7)

    def add(b_, sx, sy, sz, c, mi):
        res = bmesh.ops.create_cube(b_, size=1.0)
        vs = res['verts']
        bmesh.ops.scale(b_, vec=(sx, sy, sz), verts=vs)
        bmesh.ops.translate(b_, vec=c, verts=vs)
        for f in {f for v in vs for f in v.link_faces}:
            f.material_index = mi

    hw, hd = w / 2, d / 2
    add(bm, w, d, h, (0, 0, h / 2), W_)
    add(bm, w + 0.1, d + 0.1, 0.22, (0, 0, 0.11), PLINTH)
    fy = -hd - 0.012
    fl = (h * 0.30, h * 0.74)

    def win(x, z, on):
        add(bm, 0.56, 0.03, 0.72, (x, fy, z), FRAME)
        add(bm, 0.44, 0.04, 0.60, (x, fy - 0.006, z), LIT if on else DARK)
        add(bm, 0.035, 0.05, 0.60, (x, fy - 0.01, z), FRAME)
        add(bm, 0.44, 0.05, 0.035, (x, fy - 0.01, z), FRAME)
        add(bm, 0.72, 0.09, 0.05, (x, fy - 0.03, z - 0.40), SILL)

    xs = (-w * 0.31, 0.0, w * 0.31)
    for i, x in enumerate(xs):
        win(x, fl[1], (lit >> i) & 1)
    win(xs[0], fl[0], (lit >> 3) & 1)
    win(xs[2], fl[0], (lit >> 4) & 1)
    add(bm, 0.62, 0.04, 1.14, (0, fy, 0.62), DOOR)
    add(bm, 0.86, 0.12, 0.07, (0, fy - 0.04, 1.24), SILL)
    add(bm, 1.0, 0.34, 0.13, (0, fy - 0.17, 0.065), PLINTH)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    body = bpy.data.meshes.new(name + 'b')
    bm.to_mesh(body)
    bm.free()
    for m in (mats[wall], mats['win_lit'], mats['win_dark'], mats['door'], mats['frame'], mats['sill'], mats['plinth']):
        body.materials.append(m)
    body['door'] = door

    # hip roof with a thick eave
    br = bmesh.new()
    o = 0.26
    ex, ey = hw + o, hd + o
    t = 0.16
    rx = hw * 0.62
    lo = [br.verts.new(p) for p in ((-ex, -ey, h), (ex, -ey, h), (ex, ey, h), (-ex, ey, h))]
    up = [br.verts.new((p.co.x, p.co.y, h + t)) for p in lo]
    r = [br.verts.new(p) for p in ((-rx, 0, h + t + rh), (rx, 0, h + t + rh))]
    br.faces.new((lo[3], lo[2], lo[1], lo[0]))
    for i in range(4):
        j = (i + 1) % 4
        br.faces.new((lo[i], lo[j], up[j], up[i]))
    br.faces.new((up[0], up[1], r[1], r[0]))
    br.faces.new((up[2], up[3], r[0], r[1]))
    br.faces.new((up[1], up[2], r[1]))
    br.faces.new((up[3], up[0], r[0]))
    add(br, 0.36, 0.36, rh + 0.5, (hw * 0.52, hd * 0.25, h + rh * 0.55 + 0.3), 1)
    bmesh.ops.recalc_face_normals(br, faces=br.faces)
    rm = bpy.data.meshes.new(name + 'r')
    br.to_mesh(rm)
    br.free()
    rm.materials.append(mats[roof])
    rm.materials.append(mats['chim'])
    return body, rm


def build():
    c = L.collection('SET_village')
    rnd = random.Random(9)
    walls = {'w1': (0.98, 0.84, 0.84), 'w2': (0.82, 0.90, 0.80), 'w3': (1.0, 0.92, 0.80), 'w4': (0.86, 0.86, 0.92), 'w5': (0.98, 0.94, 0.88)}
    roofs = {'r1': (0.25, 0.22, 0.23), 'r2': (0.05, 0.30, 0.31), 'r3': (0.33, 0.15, 0.16), 'r4': (0.20, 0.11, 0.38), 'r5': (0.22, 0.16, 0.15)}
    mats = {k: L.mat('VL_' + k, v, paint=0.05) for k, v in {**walls, **roofs}.items()}
    mats['win_lit'] = L.glow_mat('VL_lit', (1.0, 0.74, 0.34), 2.0)
    mats['win_dark'] = L.mat('VL_dark', (0.09, 0.11, 0.22), paint=0.0)
    mats['frame'] = L.mat('VL_frame', (0.92, 0.91, 0.92), paint=0.0)
    mats['sill'] = L.mat('VL_sill', (0.03, 0.03, 0.05), paint=0.0)
    mats['plinth'] = L.mat('VL_plinth', (0.80, 0.78, 0.80), paint=0.0)
    mats['chim'] = L.mat('VL_chim', (0.30, 0.12, 0.11))
    door_cols = [L.mat('VL_d1', (0.42, 0.06, 0.06), paint=0.03), L.mat('VL_d2', (0.36, 0.24, 0.07), paint=0.03), L.mat('VL_d3', (0.05, 0.22, 0.22), paint=0.03)]
    variants = []
    for i in range(16):
        w = rnd.uniform(4.5, 5.0)
        mats['door'] = door_cols[i % 3]
        variants.append(_house_meshes(f'VLH{i}', w, rnd.uniform(3.5, 3.9), rnd.uniform(3.1, 3.4), rnd.uniform(1.5, 1.9),
                                      f'w{rnd.randint(1, 5)}', f'r{rnd.randint(1, 5)}', rnd.choice((0, 0, 0, 0, 0, 1, 2, 8, 16, 4)), None, mats))
    ground = L.mat('VL_ground', (0.012, 0.02, 0.13), rough=0.8, paint=0.08, pscale=0.3)
    # terraced hillside: ground rises with distance
    bm = bmesh.new()
    nx, ny = 30, 40
    pts = {}
    for j in range(ny + 1):
        for i in range(nx + 1):
            x = -110 + 220 * i / nx
            y = -12 + 260 * j / ny
            pts[i, j] = bm.verts.new((x, y, _terrain(x, y)))
    for j in range(ny):
        for i in range(nx):
            bm.faces.new((pts[i, j], pts[i + 1, j], pts[i + 1, j + 1], pts[i, j + 1]))
    L.obj_from_bm('VL_ground', bm, ground, c, smooth=True)
    n = 0
    for row in range(24):
        y = row * 8.8
        for col in range(-10, 11):
            x = col * 8.4 + rnd.uniform(-0.25, 0.25) + (4.2 if row % 2 else 0)
            if rnd.random() < 0.07:
                continue
            vb, vr = variants[rnd.randrange(16)]
            o = bpy.data.objects.new(f'VLh{n}', vb)
            c.objects.link(o)
            y2 = y + rnd.uniform(-0.3, 0.3)
            o.location = (x, y2, _terrain(x, y2) - 0.05)
            o.rotation_euler = (0, 0, rnd.uniform(-0.02, 0.02))
            k_ = rnd.uniform(1.25, 1.42)
            o.scale = (k_, k_, k_)
            L.ink(o, 0.006)
            ro = bpy.data.objects.new(f'VLr{n}', vr)
            c.objects.link(ro)
            ro.parent = o
            L.ink(ro, 0.05)
            n += 1
    # hills
    cols = [(0.012, 0.018, 0.22), (0.009, 0.013, 0.17), (0.006, 0.01, 0.12)]
    for i, col in enumerate(cols):
        m = L.mat(f'VL_hill{i}', col, rough=0.9, paint=0.0)
        bm = bmesh.new()
        prev = None
        y = 330 - i * 40
        ks = []
        for k in range(61):
            x = -360 + 12 * k
            z = 48 - i * 9 + 18 * math.sin(k * 0.55 + i * 2.1) + 9 * math.sin(k * 1.7 + i)
            ks.append((bm.verts.new((x, y, -5)), bm.verts.new((x, y, z))))
        for a, b in zip(ks, ks[1:]):
            bm.faces.new((a[0], b[0], b[1], a[1]))
        L.obj_from_bm(f'VL_ridge{i}', bm, m, c)
    # lighthouse on the ridge
    lx, ly = 24.0, 118.0
    lz = _terrain(lx, ly)
    wh = L.mat('VL_lh1', (0.84, 0.82, 0.92), rough=0.6, paint=0.04)
    rd = L.mat('VL_lh2', (0.50, 0.08, 0.10), rough=0.6, paint=0.04)
    for i in range(5):
        z0 = lz + i * 6.5
        r0, r1 = 5.0 - i * 0.62, 5.0 - (i + 1) * 0.62
        L.lathe(f'VL_lhs{i}', [(r0, z0), (r1, z0 + 6.5)], wh if i % 2 == 0 else rd, c, loc=(lx, ly, 0), seg=28, w=0.06)
    top = lz + 32.5
    L.lathe('VL_lhgal', [(1.9, top), (2.7, top + 0.3), (2.7, top + 0.8), (1.5, top + 0.8)], mats['r5'], c, loc=(lx, ly, 0), seg=24, w=0.05)
    L.lathe('VL_lhlamp', [(1.2, top + 0.8), (1.2, top + 3.2), (0, top + 3.2)], L.glow_mat('VL_beam', (1.0, 0.84, 0.48), 6.0), c, loc=(lx, ly, 0), seg=12, smooth=False, w=0.05)
    L.lathe('VL_lhroof', [(1.6, top + 3.2), (0.1, top + 5.0), (0, top + 5.2)], rd, c, loc=(lx, ly, 0), seg=16, w=0.05)
    # moon with soft halo
    mo = L.sph('VL_moon', (13, 1, 13), (-52, 360, 118), L.glow_mat('VL_moonm', (1.0, 0.95, 0.72), 1.6), c, seg=40)
    hal = L.halo_mat('VL_halo', (0.52, 0.56, 0.86), 0.9, 1.0)
    h = L.sph('VL_halo', (1, 1, 1), (-52, 365, 118), hal, c, seg=40)
    h.scale = (46, 1, 46)
    return c


def _terrain(x, y):
    return 0.03 * max(y, 0) ** 1.42 * 0.5 + 0.8 * math.sin(x * 0.05) * (y > 0)
