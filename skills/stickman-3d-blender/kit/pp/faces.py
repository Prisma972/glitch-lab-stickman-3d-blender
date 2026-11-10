"""Face decals (RGBA). Run with system Python: python pp/faces.py
Layout measured on reference shorts, fractions of head height from the top:
brows 0.34, eyes 0.48, moustache 0.65, mouth 0.70 (mouth sits right under the moustache).
Eye: straight lid, big half-ellipse pupil hanging below it. Coordinates: x, y in head radii / 1.1, y up.
"""
import os
import math
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter
import kitpath

OUT = kitpath.TEX + '/faces'
S = 2048
G = (122, 122, 126, 255)    # pupils
BROW = (96, 96, 99, 255)    # the darkest large mark on the face
D = (50, 50, 56, 255)       # lids, moustache, mouth line
MOUTH = (52, 50, 54, 255)
TEETH = (246, 246, 244, 255)

EYE_Y, BROW_Y, STACHE_Y, MOUTH_Y = 0.035, 0.275, -0.285, -0.36
EYE_X = 0.26


def C(x, y):
    return (S / 2 + x * 1.1 * S / 2, S / 2 - y * 1.1 * S / 2)


def stroke(d, pts, width, col, taper=0.32):
    """Tapered stroke through points."""
    n = 80
    P = [pts[0]] + list(pts) + [pts[-1]]
    path = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            f = lambda a, b, c, e: 0.5 * ((2 * b) + (-a + c) * t + (2 * a - 5 * b + 4 * c - e) * t * t + (-a + 3 * b - 3 * c + e) * t ** 3)
            path.append((f(p0[0], p1[0], p2[0], p3[0]), f(p0[1], p1[1], p2[1], p3[1])))
    path.append(pts[-1])
    m = len(path)
    for i, (x, y) in enumerate(path):
        u = i / (m - 1)
        r = width / 2 * (taper + (1 - taper) * math.sin(math.pi * u) ** 0.7)
        d.ellipse((x - r, y - r, x + r, y + r), fill=col)


def lidded_eye(im, d, cx, cy=EYE_Y, w=0.185, tilt=0.0, look=0.0):
    """Lid line with a big pupil hanging below it."""
    rx, ry = w * 0.74, w * 1.0
    ix = cx + look * w * 0.3
    layer = Image.new('L', (S, S), 0)
    ImageDraw.Draw(layer).ellipse((*C(ix - rx, cy + ry), *C(ix + rx, cy - ry)), fill=255)
    cut = Image.new('L', (S, S), 255)
    x0, y0 = C(cx - w * 2, cy + tilt * 2 * w)
    x1, y1 = C(cx + w * 2, cy - tilt * 2 * w)
    ImageDraw.Draw(cut).polygon([(x0, y0), (x1, y1), (x1, 0), (x0, 0)], fill=0)
    im.paste(G[:3] + (255,), (0, 0), ImageChops.multiply(layer, cut))
    stroke(d, [C(cx - w * 1.2, cy + tilt * w * 1.2), C(cx, cy), C(cx + w * 1.2, cy - tilt * w * 1.2)], S * 0.026, D, taper=0.5)


def wide_eye(d, cx, cy=EYE_Y + 0.03, w=0.15):
    d.ellipse((*C(cx - w, cy + w * 1.15), *C(cx + w, cy - w * 1.15)), outline=D, width=int(S * 0.016))
    r = w * 0.5
    d.ellipse((*C(cx - r, cy + r), *C(cx + r, cy - r)), fill=D)


def brow(d, cx, cy=BROW_Y, w=0.19, tilt=0.0, arch=0.02):
    stroke(d, [C(cx - w, cy + tilt * w), C(cx, cy + arch), C(cx + w, cy - tilt * w)], S * 0.05, BROW, taper=0.45)


def moustache(d, y=STACHE_Y):
    """Thin wavy line each side, tips lifting a little, like a drawn pencil moustache."""
    for s in (-1, 1):
        stroke(d, [C(s * 0.02, y - 0.006), C(s * 0.13, y + 0.012), C(s * 0.25, y - 0.008), C(s * 0.33, y - 0.03)], S * 0.024, D, taper=0.4)


def smirk(d, y=MOUTH_Y):
    stroke(d, [C(-0.15, y + 0.012), C(-0.02, y - 0.026), C(0.1, y - 0.016), C(0.19, y + 0.02)], S * 0.022, G)


def smile(d, y=MOUTH_Y):
    stroke(d, [C(-0.19, y + 0.03), C(0, y - 0.03), C(0.19, y + 0.03)], S * 0.022, G)


def flat(d, y=MOUTH_Y):
    stroke(d, [C(-0.19, y), C(0, y - 0.012), C(0.19, y)], S * 0.024, D)


def open_mouth(im, cy=-0.31, w=0.3, h=0.3):
    """Laugh: half-ellipse mouth under the moustache, teeth bar along the top."""
    box = (*C(-w, cy + h), *C(w, cy - h))
    mask = Image.new('L', (S, S), 0)
    ImageDraw.Draw(mask).pieslice(box, 0, 180, fill=255)
    im.paste(MOUTH[:3] + (255,), (0, 0), mask)
    t = Image.new('L', (S, S), 0)
    ImageDraw.Draw(t).rectangle((*C(-w, cy), *C(w, cy - 0.075)), fill=255)
    im.paste(TEETH[:3] + (255,), (0, 0), ImageChops.multiply(t, mask))


def oh(d, y=-0.42):
    r = 0.08
    d.ellipse((*C(-r, y + 0.03), *C(r, y - 0.13)), fill=MOUTH)


def closed_eyes(d):
    for s in (-1, 1):
        stroke(d, [C(s * EYE_X - 0.2, EYE_Y + 0.02), C(s * EYE_X, EYE_Y - 0.035), C(s * EYE_X + 0.2, EYE_Y + 0.02)], S * 0.03, D)


def happy_eyes(d):
    for s in (-1, 1):
        stroke(d, [C(s * EYE_X - 0.15, EYE_Y - 0.02), C(s * EYE_X, EYE_Y + 0.09), C(s * EYE_X + 0.15, EYE_Y - 0.02)], S * 0.03, D)


FACES = {}


def face(fn):
    FACES[fn.__name__] = fn
    return fn


@face
def sly(im, d):
    brow(d, -EYE_X, BROW_Y - 0.01, tilt=0.05)
    brow(d, EYE_X, BROW_Y + 0.03, tilt=-0.07)
    lidded_eye(im, d, -EYE_X, tilt=0.03, look=0.4)
    lidded_eye(im, d, EYE_X, tilt=-0.03, look=0.4)
    moustache(d)
    smirk(d)


@face
def sly_b(im, d):
    brow(d, -EYE_X, BROW_Y - 0.04, tilt=0.05)
    brow(d, EYE_X, BROW_Y, tilt=-0.07)
    closed_eyes(d)
    moustache(d)
    smirk(d)


@face
def sly_w(im, d):
    brow(d, -EYE_X, BROW_Y - 0.05, tilt=0.12)
    brow(d, EYE_X, BROW_Y + 0.08, tilt=-0.16)
    stroke(d, [C(-EYE_X - 0.2, EYE_Y - 0.02), C(-EYE_X, EYE_Y + 0.07), C(-EYE_X + 0.2, EYE_Y - 0.02)], S * 0.03, D)
    lidded_eye(im, d, EYE_X, tilt=-0.03, look=0.2)
    moustache(d)
    smile(d)


@face
def laugh_m(im, d):
    brow(d, -EYE_X, BROW_Y + 0.08, tilt=-0.16)
    brow(d, EYE_X, BROW_Y + 0.08, tilt=0.16)
    happy_eyes(d)
    open_mouth(im)
    moustache(d, -0.235)


@face
def shock_m(im, d):
    brow(d, -EYE_X, BROW_Y + 0.12, tilt=-0.18)
    brow(d, EYE_X, BROW_Y + 0.12, tilt=0.18)
    wide_eye(d, -EYE_X)
    wide_eye(d, EYE_X)
    moustache(d)
    oh(d)


@face
def calm_m(im, d):
    brow(d, -EYE_X, tilt=-0.05)
    brow(d, EYE_X, tilt=0.05)
    lidded_eye(im, d, -EYE_X)
    lidded_eye(im, d, EYE_X)
    moustache(d)
    smile(d)


@face
def calm(im, d):
    brow(d, -EYE_X, tilt=-0.05)
    brow(d, EYE_X, tilt=0.05)
    lidded_eye(im, d, -EYE_X)
    lidded_eye(im, d, EYE_X)
    smile(d, -0.3)


@face
def calm_b(im, d):
    brow(d, -EYE_X, BROW_Y - 0.03, tilt=-0.05)
    brow(d, EYE_X, BROW_Y - 0.03, tilt=0.05)
    closed_eyes(d)
    smile(d, -0.3)


@face
def laugh(im, d):
    brow(d, -EYE_X, BROW_Y + 0.08, tilt=-0.16)
    brow(d, EYE_X, BROW_Y + 0.08, tilt=0.16)
    happy_eyes(d)
    open_mouth(im, -0.24)


@face
def shock(im, d):
    brow(d, -EYE_X, BROW_Y + 0.12, tilt=-0.18)
    brow(d, EYE_X, BROW_Y + 0.12, tilt=0.18)
    wide_eye(d, -EYE_X)
    wide_eye(d, EYE_X)
    oh(d, -0.34)


@face
def flatface(im, d):
    brow(d, -EYE_X)
    brow(d, EYE_X)
    lidded_eye(im, d, -EYE_X)
    lidded_eye(im, d, EYE_X)
    flat(d, -0.3)


@face
def flatface_b(im, d):
    brow(d, -EYE_X, BROW_Y - 0.03)
    brow(d, EYE_X, BROW_Y - 0.03)
    closed_eyes(d)
    flat(d, -0.3)


# ================================================================ expressions from parts
# Any expression = eyes + brows + mouth (+ the moustache on the 'hero' family, always drawn last so it never disappears).
# side: -1 is the character's right eye, on the left of the picture.

def eye(im, d, side, kind='lid', look=(0.0, 0.0), w=0.185):
    cx, cy = side * EYE_X, EYE_Y
    lx = look[0] * w * 0.55
    if kind in ('lid', 'sad', 'angry', 'squint', 'open'):
        tilt = {'lid': 0.0, 'squint': 0.0, 'open': 0.0, 'sad': side * 0.32, 'angry': -side * 0.32}[kind]
        rx, ry = w * 0.74, w * 1.0
        lid = cy
        py = cy + look[1] * w * 0.25
        if kind == 'open':          # lid lifted: most of the pupil shows, still cut flat on top
            lid, rx, ry, py = cy + 0.42 * w, w * 0.64, w * 0.82, cy + 0.04 * w + look[1] * w * 0.2
        if kind == 'squint':
            ry = w * 0.62
        layer = Image.new('L', (S, S), 0)
        ImageDraw.Draw(layer).ellipse((*C(cx + lx - rx, py + ry), *C(cx + lx + rx, py - ry)), fill=255)
        cut = Image.new('L', (S, S), 255)
        x0, y0 = C(cx - w * 2, lid + tilt * 2 * w)
        x1, y1 = C(cx + w * 2, lid - tilt * 2 * w)
        ImageDraw.Draw(cut).polygon([(x0, y0), (x1, y1), (x1, 0), (x0, 0)], fill=0)
        im.paste(G[:3] + (255,), (0, 0), ImageChops.multiply(layer, cut))
        arch = 0.05 * w if kind == 'open' else 0.0
        stroke(d, [C(cx - w * 1.2, lid + tilt * w * 1.2), C(cx, lid + arch), C(cx + w * 1.2, lid - tilt * w * 1.2)], S * 0.026, D, taper=0.5)
        if kind == 'squint':         # a lower lid closes in under the pupil
            stroke(d, [C(cx - w * 0.9, cy - 0.55 * w), C(cx, cy - 0.68 * w), C(cx + w * 0.9, cy - 0.55 * w)], S * 0.018, D, taper=0.5)
    elif kind == 'wide':
        r = w * 0.82
        y = cy + 0.03
        d.ellipse((*C(cx - r, y + r * 1.15), *C(cx + r, y - r * 1.15)), outline=D, width=int(S * 0.016))
        p = r * 0.42
        d.ellipse((*C(cx + lx - p, y + p), *C(cx + lx + p, y - p)), fill=D)
    elif kind == 'closed':
        stroke(d, [C(cx - 0.2, cy + 0.02), C(cx, cy - 0.035), C(cx + 0.2, cy + 0.02)], S * 0.03, D)
    elif kind == 'happy':
        stroke(d, [C(cx - 0.15, cy - 0.02), C(cx, cy + 0.09), C(cx + 0.15, cy - 0.02)], S * 0.03, D)


def brows(d, kind='flat'):
    for side in (-1, 1):
        cx = side * EYE_X
        cy, tilt, arch = BROW_Y, 0.0, 0.02
        if kind == 'smug':
            cy, tilt = (BROW_Y - 0.01, 0.05) if side < 0 else (BROW_Y + 0.03, -0.07)
        elif kind == 'raised':
            cy, arch = BROW_Y + 0.08, 0.05
        elif kind == 'worried':
            cy, tilt = BROW_Y + 0.03, side * 0.30
        elif kind == 'sad':
            cy, tilt = BROW_Y - 0.01, side * 0.24
        elif kind == 'angry':
            cy, tilt = BROW_Y - 0.03, -side * 0.30
        elif kind == 'skeptic':
            cy, tilt, arch = (BROW_Y - 0.03, 0.0, 0.01) if side < 0 else (BROW_Y + 0.08, -0.05, 0.05)
        elif kind == 'relaxed':
            cy, arch = BROW_Y - 0.03, 0.03
        brow(d, cx, cy, tilt=tilt, arch=arch)


def mouth(im, d, kind, y):
    if kind == 'smirk':
        smirk(d, y)
    elif kind == 'smile':
        smile(d, y)
    elif kind == 'grin':
        stroke(d, [C(-0.24, y + 0.05), C(0, y - 0.05), C(0.24, y + 0.05)], S * 0.024, G)
    elif kind == 'flat':
        flat(d, y)
    elif kind == 'frown':
        stroke(d, [C(-0.17, y - 0.035), C(0, y + 0.02), C(0.17, y - 0.035)], S * 0.022, G)
    elif kind == 'side':            # small mouth pushed to one side, for thinking
        stroke(d, [C(0.02, y - 0.005), C(0.10, y + 0.005), C(0.17, y + 0.02)], S * 0.022, G)
    elif kind == 'wavy':
        stroke(d, [C(-0.17, y), C(-0.085, y + 0.02), C(0, y - 0.01), C(0.085, y + 0.02), C(0.17, y - 0.005)], S * 0.02, G, taper=0.6)
    elif kind == 'o':
        r = 0.055
        d.ellipse((*C(-r, y + 0.02), *C(r, y - 0.10)), fill=MOUTH)
    elif kind == 'talk_a':
        open_mouth(im, cy=y + 0.025, w=0.15, h=0.13)
    elif kind == 'talk_o':
        r = 0.075
        d.ellipse((*C(-r, y + 0.03), *C(r, y - 0.12)), fill=MOUTH)
    elif kind == 'laugh':
        open_mouth(im, cy=y + 0.05, w=0.26, h=0.26)
    elif kind == 'teeth':           # clenched grimace: a white bar with a dark outline and tooth gaps
        x0, x1, y0, y1 = -0.19, 0.19, y + 0.035, y - 0.065
        d.rounded_rectangle((*C(x0, y0), *C(x1, y1)), radius=int(S * 0.02), fill=TEETH, outline=D, width=int(S * 0.012))
        for x in (-0.095, 0.0, 0.095):
            d.line((*C(x, y0), *C(x, y1)), fill=D, width=int(S * 0.008))


# name: (eyes kind, look, brows kind, mouth kind). Eyes may be a pair (right, left) for winks and asymmetric looks.
EXPR = {
    'neutral': ('lid', (0, 0), 'flat', 'flat'),
    'neutral_b': ('closed', (0, 0), 'flat', 'flat'),
    'smile': ('open', (0, 0), 'relaxed', 'smile'),
    'smile_b': ('closed', (0, 0), 'relaxed', 'smile'),
    'happy': ('happy', (0, 0), 'raised', 'grin'),
    'surprised': ('open', (0, 0.2), 'raised', 'o'),
    'worried': ('open', (0, -0.2), 'worried', 'wavy'),
    'worried_b': ('closed', (0, 0), 'worried', 'wavy'),
    'sad': ('sad', (0, -0.4), 'sad', 'frown'),
    'sad_b': ('closed', (0, 0), 'sad', 'frown'),
    'angry': ('angry', (0, 0), 'angry', 'frown'),
    'angry_b': ('closed', (0, 0), 'angry', 'frown'),
    'skeptical': ('lid', (0.6, 0), 'skeptic', 'flat'),
    'scared': ('wide', (0, 0), 'worried', 'teeth'),
    'thinking': ('lid', (0.8, 0.6), 'skeptic', 'side'),
    'sleepy': ('squint', (0, 0), 'relaxed', 'flat'),
    'determined': ('angry', (0, 0), 'flat', 'flat'),
    'embarrassed': ('happy', (0, 0), 'worried', 'wavy'),
    'talk_a': ('lid', (0, 0), 'flat', 'talk_a'),
    'talk_o': ('lid', (0, 0), 'flat', 'talk_o'),
    'look_l': ('lid', (-1.0, 0), 'smug', 'smirk'),
    'look_r': ('lid', (1.0, 0), 'smug', 'smirk'),
}
# the old hand-drawn faces keep their names, so shots built on them do not change
LEGACY = {'hero': ['sly', 'sly_b', 'sly_w', 'laugh_m', 'shock_m', 'calm_m'],
          'plain': ['flatface', 'flatface_b', 'calm', 'calm_b', 'laugh', 'shock']}
FAMILIES = {f: LEGACY[f] + list(EXPR) for f in LEGACY}
COLS, ROWS, TILE = 8, 4, 1024


def draw_expr(im, d, name, family):
    eyes_, look, brows_, mouth_ = EXPR[name]
    for i, side in enumerate((-1, 1)):
        eye(im, d, side, eyes_ if isinstance(eyes_, str) else eyes_[i], look)
    brows(d, brows_)
    if family == 'hero':
        mouth(im, d, mouth_, MOUTH_Y)
        moustache(d)
    else:
        mouth(im, d, mouth_, -0.30)


def render(fn):
    im = Image.new('RGBA', (S, S), (255, 255, 255, 0))
    fn(im, ImageDraw.Draw(im))
    return im.resize((TILE, TILE), Image.LANCZOS).filter(ImageFilter.GaussianBlur(2.2))


def main():
    import json
    os.makedirs(OUT, exist_ok=True)
    for n, fn in FACES.items():
        render(fn).save(f'{OUT}/{n}.png')
    for fam, names in FAMILIES.items():
        assert len(names) <= COLS * ROWS, (fam, len(names))
        atlas = Image.new('RGBA', (COLS * TILE, ROWS * TILE), (255, 255, 255, 0))
        for i, n in enumerate(names):
            if n in FACES:
                tile = Image.open(f'{OUT}/{n}.png')
            else:
                tile = render(lambda im, d, n=n: draw_expr(im, d, n, fam))
                tile.save(f'{OUT}/{fam}_{n}.png')
            atlas.paste(tile, ((i % COLS) * TILE, (i // COLS) * TILE))
        atlas.save(f'{OUT}/atlas_{fam}.png', optimize=True)
        # a light preview of the whole family, white ball behind each face
        prev = Image.new('RGB', (COLS * 256, ROWS * 280), (40, 40, 44))
        dr = ImageDraw.Draw(prev)
        for i, n in enumerate(names):
            x, y = (i % COLS) * 256, (i // COLS) * 280
            dr.ellipse((x + 8, y + 8, x + 248, y + 248), fill=(242, 242, 240))
            prev.paste(atlas.crop(((i % COLS) * TILE, (i // COLS) * TILE, (i % COLS + 1) * TILE, (i // COLS + 1) * TILE)).resize((256, 256)), (x, y),
                       atlas.crop(((i % COLS) * TILE, (i // COLS) * TILE, (i % COLS + 1) * TILE, (i // COLS + 1) * TILE)).resize((256, 256)))
            dr.text((x + 6, y + 256), n, fill=(255, 230, 90))
        prev.save(f'{OUT}/preview_{fam}.jpg', quality=88)
    json.dump(dict(families=FAMILIES, cols=COLS, rows=ROWS), open(f'{OUT}/atlas.json', 'w'), indent=1)
    print('ok', {f: len(v) for f, v in FAMILIES.items()})


if __name__ == '__main__':
    main()
