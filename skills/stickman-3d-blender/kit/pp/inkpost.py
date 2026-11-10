"""Hand-inked line layer from depth + normal passes. Reads Blender multilayer EXR.
Plane-safe edges: Laplacian of inverse depth is zero on flat surfaces, so ground and walls stay clean.
Lines get a fixed screen-space wobble, noise-varied width, thin out with distance but never vanish,
and blur with the lens so they sit inside the depth of field."""
import numpy as np
import cv2
import OpenEXR

INK = np.array([0.0035, 0.0028, 0.0028], np.float32)
_NOISE = {}
LAST = {}


def load(path):
    f = OpenEXR.File(path, separate_channels=True)
    P = {p.name(): p.channels for p in f.parts}
    c = P['ViewLayer.Combined']
    rgb = np.dstack([c[f'ViewLayer.Combined.{k}'].pixels for k in 'RGB']).astype(np.float32)
    z = P['ViewLayer.Depth']['ViewLayer.Depth.Z'].pixels.astype(np.float32)
    n = P['ViewLayer.Normal']
    nrm = np.dstack([n[f'ViewLayer.Normal.{k}'].pixels for k in 'XYZ']).astype(np.float32)
    LAST['noink'] = None
    for nm, ch in P.items():
        if 'noink' in nm:
            LAST['noink'] = list(ch.values())[0].pixels.astype(np.float32)
    LAST['vec'] = None
    if 'ViewLayer.Vector' in P:
        v = P['ViewLayer.Vector']
        LAST['vec'] = np.dstack([v[f'ViewLayer.Vector.{k}'].pixels for k in 'XYZW']).astype(np.float32)
    return rgb, z, nrm


def to_srgb(x):
    x = np.clip(x, 0, 1)
    return np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(x, 1 / 2.4) - 0.055).astype(np.float32)


def _field(h, w, seed, cell):
    k = (h, w, seed, cell)
    if k not in _NOISE:
        r = np.random.RandomState(seed)
        a = r.rand(h // cell + 3, w // cell + 3).astype(np.float32)
        _NOISE[k] = cv2.resize(a, (w, h), interpolation=cv2.INTER_CUBIC) * 2 - 1
    return _NOISE[k]


def lines(z, nrm, depth_t=0.02, normal_t=0.42, width=1.0, focus=None, fstop=None, lens=35.0, fade=(7, 60, 0.22)):
    """Returns line alpha 0..1."""
    h, w = z.shape
    s = h / 1920.0
    D = np.clip(z, 0.15, 900.0)
    inv = 1.0 / D
    k = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]], np.float32)
    lap = np.abs(cv2.filter2D(inv, -1, k))
    de = lap * D
    e_d = np.clip((de - depth_t) / depth_t, 0, 1)
    # normal break between neighbours
    def nb(k):
        return np.maximum(np.abs(np.roll(nrm, k, 1) - np.roll(nrm, -k, 1)).sum(2), np.abs(np.roll(nrm, k, 0) - np.roll(nrm, -k, 0)).sum(2))
    # a break must hold over two offsets: a sub-pixel sliver between two faces beats with the pixel grid and draws dashes
    e_n = np.clip((np.minimum(nb(1), nb(2)) - normal_t) / normal_t, 0, 1)
    # smooth curved forms should not ink: only keep sharp normal jumps
    E = np.maximum(e_d, e_n)
    E[D > 700] *= 0.0
    # width by distance: near about 3.5 px wide, far about 2 px
    d1 = cv2.dilate(E, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
    mid = np.clip((5 - D) / 3, 0, 1)
    W = E * (1 - mid) + d1 * mid
    # hand wobble: displace the whole line layer by smooth fixed noise
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    amp = 0.22 * s * width
    dx = _field(h, w, 3, 90) * amp + _field(h, w, 5, 24) * amp * 0.55
    dy = _field(h, w, 4, 90) * amp + _field(h, w, 6, 24) * amp * 0.55
    W = cv2.remap(W, xx + dx, yy + dy, cv2.INTER_LINEAR)
    # variable width: soft threshold whose level drifts along the stroke
    B = cv2.GaussianBlur(W, (0, 0), 0.9 * s)
    th = 0.60 + 0.02 * _field(h, w, 7, 60)
    L = np.clip((B - th) / 0.32 + 0.5, 0, 1)
    # lens blur on the lines themselves
    if focus and fstop:
        f = lens / 1000.0
        coc_m = (f * f / fstop) * np.abs(D - focus) / (D * max(focus - f, 0.05))
        coc = coc_m * 1000.0 / 36.0 * h          # pixels across
        L1 = cv2.GaussianBlur(L, (0, 0), 5 * s)
        L2 = cv2.GaussianBlur(L, (0, 0), 14 * s)
        a = np.clip(coc / 12, 0, 1)
        b = np.clip((coc - 12) / 22, 0, 1)
        L = L * (1 - a) + L1 * a * 1.15
        L = L * (1 - b) + L2 * b * 1.3
    # arms, gloves and heads carry no post line
    mk = LAST.get('noink')
    if mk is not None:
        L *= 1 - np.clip(cv2.GaussianBlur(cv2.dilate(mk, np.ones((7, 7), np.uint8)), (0, 0), 1.2 * s), 0, 1)
    # keep far lines present but lighter
    L *= np.clip(1.0 - (D - 5) / 40, 0.6, 1.0)
    return np.clip(L, 0, 1)


def apply(img, L, strength=0.8):
    """Tinted line: multiplies the local colour down, so set lines keep a little of what they cross."""
    a = (L * strength)[..., None]
    return img * (1 - a) + (img * 0.10 + INK * 0.2) * a


def _spread(vx, vy, tile=32):
    """A fast object must smear over what is next to it, not only inside its own silhouette:
    a pixel takes the fastest vector around it when that is much faster than its own."""
    h, w = vx.shape
    th, tw = -(-h // tile), -(-w // tile)
    pad = ((0, th * tile - h), (0, tw * tile - w))
    ax, ay = np.pad(vx, pad), np.pad(vy, pad)
    sp = np.hypot(ax, ay).reshape(th, tile, tw, tile).transpose(0, 2, 1, 3).reshape(th, tw, -1)
    i = sp.argmax(2)[..., None]
    tx = np.take_along_axis(ax.reshape(th, tile, tw, tile).transpose(0, 2, 1, 3).reshape(th, tw, -1), i, 2)[..., 0]
    ty = np.take_along_axis(ay.reshape(th, tile, tw, tile).transpose(0, 2, 1, 3).reshape(th, tw, -1), i, 2)[..., 0]
    best, bx, by = np.hypot(tx, ty), tx.copy(), ty.copy()
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            sx, sy = np.roll(tx, (dy, dx), (0, 1)), np.roll(ty, (dy, dx), (0, 1))
            m = np.hypot(sx, sy) > best
            best, bx, by = np.where(m, np.hypot(sx, sy), best), np.where(m, sx, bx), np.where(m, sy, by)
    ux = cv2.resize(bx, (tw * tile, th * tile), interpolation=cv2.INTER_LINEAR)[:h, :w]
    uy = cv2.resize(by, (tw * tile, th * tile), interpolation=cv2.INTER_LINEAR)[:h, :w]
    # soft weight: a hard switch between own and tile vector drew the tile grid into fast flights
    k = np.clip(1.5 - 2 * np.hypot(vx, vy) / np.maximum(np.hypot(ux, uy), 1e-3), 0, 1)
    k = cv2.GaussianBlur(k, (0, 0), tile / 3)
    return vx + (ux - vx) * k, vy + (uy - vy) * k


def motion_blur(img, shutter=0.4, side=0, step=3.0):
    """Smears colour and ink together along the Vector pass of the last load().
    Measured on two frames: in array coordinates, (-Z, +W) points to the next frame and (+X, -Y) to the previous one.
    side: 0 both, -1 previous only (last frame of a shot), 1 next only (first frame), because the other
    vector crosses the cut. One tap per `step` px of travel, so a 2 px line never strobes."""
    v = LAST.get('vec')
    if v is None or not shutter:
        return img
    s = img.shape[0] / v.shape[0]
    nx, ny = -v[..., 2] * s, v[..., 3] * s
    bx, by = v[..., 0] * s, -v[..., 1] * s
    if side < 0:
        nx, ny = -bx, -by
    elif side > 0:
        bx, by = -nx, -ny
    fast = max(float(np.percentile(np.hypot(nx, ny), 99.9)), float(np.percentile(np.hypot(bx, by), 99.9)))
    taps = int(min(96, np.ceil(fast * shutter / step)))
    if taps < 3:
        return img
    nx, ny = _spread(nx, ny)
    bx, by = _spread(bx, by)
    h, w = img.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    acc = np.zeros_like(img)
    for i in range(taps):
        t = ((i + .5) / taps - .5) * shutter
        dx, dy = (nx, ny) if t > 0 else (bx, by)
        acc += cv2.remap(img, xx + dx * abs(t), yy + dy * abs(t), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    return acc / taps
