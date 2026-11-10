"""Finish a rendered frame: soft bloom, gentle halation, vignette, slight softness, optional caption.
python post.py in.png out.png ["caption"]   (also imported by the batch finisher)
"""
import sys
import numpy as np
import cv2
from fonts import font
from PIL import Image, ImageDraw, ImageFilter


# grades per place and time: dk dusk street, wl warm insert, st day street, rm room, vl night village. Add your own.
SCENES = {
    'dk': dict(con=0.2, sat=1.0, tint=(1.0, 1.0, 0.98), gain=1.12, lift=0.004),
    'wl': dict(con=0.2, sat=1.0, tint=(1.0, 1.0, 0.98), gain=1.22, lift=0.004, bloom=0.5),
    'st': dict(con=0.26, sat=0.95, tint=(1.0, 1.0, 0.975), gain=1.25, lift=0.004),
    'rm': dict(con=0.2, sat=1.08, tint=(0.98, 1.0, 0.96), gain=1.16, lift=0.004, bloom=0.5, thr=0.7),
    'vl': dict(con=0.24, sat=1.0, tint=(0.97, 0.97, 1.05), gain=0.86, lift=0.008),
}


def finish(rgb, bloom=0.42, thr=0.62, soft=0.5, sat=1.04, con=0.28, tint=(1, 1, 1), gain=1.0, lift=0.0, nobloom=None):
    """rgb float32 0..1, display-referred."""
    h, w = rgb.shape[:2]
    s = h / 1920.0
    lum = rgb @ np.array([.2126, .7152, .0722], np.float32)
    hi = rgb * np.clip((lum - thr) / (1 - thr), 0, 1)[..., None]
    if nobloom is not None:     # heads and mitts feed no glow: it would wash their own outline
        hi = hi * (1 - nobloom)[..., None]
    b1 = cv2.GaussianBlur(hi, (0, 0), 10 * s)
    b2 = cv2.GaussianBlur(hi, (0, 0), 44 * s)
    # bloom never screens over ink: the head line stays the darkest stroke on the figure
    t = np.clip((lum - 0.08) / 0.22, 0, 1)
    t = t * t * (3 - 2 * t)
    out = 1 - (1 - rgb) * (1 - bloom * (0.6 * b1 + 0.8 * b2) * t[..., None])
    if soft:
        out = cv2.GaussianBlur(out, (0, 0), soft * s)
    g = out @ np.array([.2126, .7152, .0722], np.float32)
    out = g[..., None] + (out - g[..., None]) * sat
    out = out * np.array(tint, np.float32) * gain
    # highlight shoulder: whites roll off instead of clipping, so heads keep their shading
    k = 0.88
    out = np.where(out > k, k + (1 - k) * (1 - np.exp(-(out - k) / (1 - k))) * 0.97, out)
    # gentle S-curve for the deep painted midtones
    x_ = np.clip(out, 0, 1)
    out = x_ + con * (x_ * x_ * (3 - 2 * x_) - x_)
    # vignette fixed to the screen, measured on flat surfaces of the reference: strong to top and bottom, light to the sides
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    dx = (x / w - .5) * 2
    dy = (y / h - .5) * 2
    a = np.where(dy > 0, 0.55, 0.50)
    v = (1 - a * np.abs(dy) ** 1.75) * (1 - 0.23 * np.abs(dx) ** 1.93)
    out = out * v[..., None]
    out = lift + out * (1 - lift)
    return np.clip(out, 0, 1)


def far_blur(img, z, near=75.0, far=190.0, r=3.5):
    """Town falls away: blur grows with distance from the depth pass."""
    s = img.shape[0] / 1920.0
    b = cv2.GaussianBlur(img, (0, 0), r * s)
    a = np.clip((np.clip(z, 0, 900) - near) / (far - near), 0, 1)
    a[z > 280] = 0.0      # sky, moon and hills stay crisp
    a = a[..., None]
    return img * (1 - a) + b * a


def caption(im, text, sc=1.0):
    """White heavy word, hard black stroke, tight shadow, on one fixed baseline at every size. sc: pop scale, 1.0 at rest."""
    w, h = im.size
    k = h / 1920
    f = font('ariblk', 53 * k * sc)
    X, Y = w / 2, (1357 + 15 * sc) * k
    st = max(1, round(6 * k * sc))
    shadow = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).text((X, Y + 2.5 * k), text, font=f, anchor='ms', fill=(0, 0, 0, 100), stroke_width=st, stroke_fill=(0, 0, 0, 100))
    shadow = shadow.filter(ImageFilter.GaussianBlur(2 * k))
    lay = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(lay).text((X, Y), text, font=f, anchor='ms', fill=(255, 255, 255, 255), stroke_width=st, stroke_fill=(8, 8, 10, 255))
    return Image.alpha_composite(Image.alpha_composite(im.convert('RGBA'), shadow), lay).convert('RGB')


def main():
    src, dst = sys.argv[1], sys.argv[2]
    a = np.asarray(Image.open(src).convert('RGB'), np.float32) / 255
    im = Image.fromarray((finish(a) * 255 + .5).astype(np.uint8))
    if len(sys.argv) > 3:
        im = caption(im, sys.argv[3])
    im.save(dst, quality=95)


if __name__ == '__main__':
    main()
