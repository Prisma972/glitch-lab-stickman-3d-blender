"""System Python: python pp/make_signs.py repaints the sign textures used by street.py (and the post box plate of common.postbox)."""
import os
from PIL import Image, ImageDraw, ImageFilter
from fonts import font
from PIL_signs import slug, ROOT

TRIM = {'green': (14, 62, 42), 'plum': (86, 26, 58), 'navy': (20, 44, 92), 'teal': (14, 88, 78)}
SIGNS = [('P. MARROW  FINE TEAS', 'green', (244, 220, 150)), ('PLUM & CRUST BAKERY', 'plum', (250, 214, 184)),
         ('TOLLIVER CLOCKS', 'navy', (234, 224, 178)), ('THE KETTLE ROOM', 'teal', (250, 234, 184)),
         ('ODD BOOKS', 'plum', (244, 220, 150)), ('GRANGER & CO', 'green', (244, 230, 184)),
         ('HAT & GLOVE', 'teal', (244, 234, 188)), ('NINE LANTERNS', 'navy', (234, 224, 178))]
os.makedirs(ROOT, exist_ok=True)
W, H = 2048, 320
for text, trim, ink in SIGNS:
    im = Image.new('RGB', (W, H), TRIM[trim])
    d = ImageDraw.Draw(im)
    d.rectangle((14, 14, W - 15, H - 15), outline=ink, width=6)
    size = 122
    while True:
        f = font('georgiab', size)
        bb = d.textbbox((0, 0), text, font=f)
        if bb[2] - bb[0] < W - 170 or size < 40:
            break
        size -= 6
    x = (W - (bb[2] - bb[0])) / 2 - bb[0]
    y = (H - (bb[3] - bb[1])) / 2 - bb[1]
    d.text((x + 5, y + 6), text, font=f, fill=tuple(int(c * 0.45) for c in TRIM[trim]))
    d.text((x, y), text, font=f, fill=ink)
    im.filter(ImageFilter.GaussianBlur(0.7)).save(f'{ROOT}/{slug(text)}.png')
print('signs ok')

import random
def display(name, wall, shelf, items, seed):
    """Warm shop interior seen through glass: back wall, three shelves, rows of goods."""
    W2, H2 = 1400, 800
    r = random.Random(seed)
    im = Image.new('RGB', (W2, H2), wall)
    d = ImageDraw.Draw(im)
    for y in range(H2):
        t = y / H2
        d.line((0, y, W2, y), fill=tuple(int(c * (0.52 + 0.65 * t)) for c in wall))
    for row, y in enumerate((225, 455, 690)):
        d.rectangle((0, y, W2, y + 26), fill=shelf)
        d.rectangle((0, y + 26, W2, y + 38), fill=tuple(c // 2 for c in shelf))
        x = 30
        while x < W2 - 80:
            w = r.randint(58, 110); h = r.randint(90, 165)
            col = r.choice(items)
            if name == 'cake':
                d.pieslice((x, y - h, x + w + 30, y + h - 40), 180, 360, fill=col, outline=(30, 16, 8), width=5)
            elif name == 'clock':
                d.ellipse((x, y - w - 20, x + w + 20, y), fill=(240, 228, 196), outline=col, width=9)
                cx, cy = x + (w + 20) // 2, y - (w + 20) // 2
                d.line((cx, cy, cx, cy - w // 3), fill=(30, 20, 14), width=5); d.line((cx, cy, cx + w // 4, cy + 6), fill=(30, 20, 14), width=5)
            else:
                d.rounded_rectangle((x, y - h, x + w, y), 12, fill=col, outline=(30, 16, 8), width=5)
                d.rectangle((x + 8, y - h * 0.6, x + w - 8, y - h * 0.3), fill=(236, 224, 190))
            x += w + r.randint(16, 46)
    im.filter(ImageFilter.GaussianBlur(1.6)).save(f'{ROOT}/display_{name}.png')

display('tea', (120, 74, 34), (86, 48, 20), [(170, 40, 34), (30, 92, 70), (204, 150, 40), (40, 66, 120)], 1)
display('cake', (156, 96, 58), (240, 222, 190), [(236, 190, 120), (214, 120, 120), (240, 226, 200), (170, 92, 48)], 2)
display('clock', (72, 56, 62), (60, 36, 20), [(180, 134, 40), (120, 60, 30), (40, 40, 44)], 3)
display('jar', (120, 96, 50), (76, 46, 20), [(200, 70, 60), (220, 170, 60), (90, 150, 110), (220, 120, 170)], 4)

im = Image.new('RGB', (1500, 900), (222, 208, 170))
d = ImageDraw.Draw(im)
f1 = font('impact', 90)
f2 = font('georgiab', 44)
for i, (bg, tx, a, b) in enumerate((((36, 66, 120), (244, 220, 150), 'GRAND', 'REGATTA'), ((186, 60, 44), (250, 236, 200), 'CIRCUS', 'TONIGHT'),
                                    ((24, 96, 80), (246, 226, 160), 'TIDE', 'TABLES'), ((230, 186, 70), (60, 30, 20), 'BRASS', 'BAND'))):
    x = 25 + i * 372
    d.rectangle((x, 60, x + 330, 840), fill=bg, outline=(40, 26, 18), width=6)
    d.text((x + 28, 130), a, font=f1, fill=tx)
    d.text((x + 28, 240), b, font=f1, fill=tx)
    d.ellipse((x + 75, 400, x + 255, 580), fill=tx)
    for k in range(5):
        d.rectangle((x + 40, 630 + k * 34, x + 290 - 30 * (k % 2), 642 + k * 34), fill=tx)
im.filter(ImageFilter.GaussianBlur(1.0)).save(f'{ROOT}/posters.png')

im = Image.new('RGB', (640, 960), (26, 44, 38))
d = ImageDraw.Draw(im)
fc = font('segoepr', 76)
for y, t in ((90, 'TODAY'), (260, 'plum tart'), (400, 'hot tea'), (540, 'good buns')):
    d.text((60, y), t, font=fc, fill=(232, 232, 220))
d.line((60, 210, 560, 200), fill=(232, 232, 220), width=5)
im.filter(ImageFilter.GaussianBlur(1.0)).save(f'{ROOT}/chalk.png')
print('extras ok')

# blade signs and door cards
for i, t in enumerate(('TEA', 'BREAD', 'CLOCKS', 'HATS', 'BOOKS', 'LAMPS')):
    im = Image.new('RGB', (620, 360), (232, 222, 192))
    d = ImageDraw.Draw(im)
    f = font('georgiab', 118)
    bb = d.textbbox((0, 0), t, font=f)
    d.text(((620 - bb[2]) / 2, (360 - bb[3]) / 2 - 12), t, font=f, fill=(44, 34, 30))
    im.filter(ImageFilter.GaussianBlur(0.8)).save(f'{ROOT}/blade{i}.png')
im = Image.new('RGB', (460, 200), (240, 234, 216))
d = ImageDraw.Draw(im)
f = font('arialbd', 96)
bb = d.textbbox((0, 0), 'OPEN', font=f)
d.rectangle((6, 6, 453, 193), outline=(170, 40, 34), width=8)
d.text(((460 - bb[2]) / 2, (200 - bb[3]) / 2 - 10), 'OPEN', font=f, fill=(170, 40, 34))
im.filter(ImageFilter.GaussianBlur(0.7)).save(f'{ROOT}/open.png')
print('blades ok')

# post box plate (common.postbox)
im = Image.new('RGB', (380, 150), (236, 228, 208))
d = ImageDraw.Draw(im)
d.rectangle((7, 7, 372, 142), outline=(60, 30, 26), width=6)
f = font('georgiab', 88)
bb = d.textbbox((0, 0), 'POST', font=f)
d.text(((380 - bb[2]) / 2, (150 - bb[3]) / 2 - 16), 'POST', font=f, fill=(60, 30, 26))
im.filter(ImageFilter.GaussianBlur(0.8)).save(f'{ROOT}/post.png')
print('post plate ok')
