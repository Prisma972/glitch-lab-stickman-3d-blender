"""System Python: python pp/make_room.py paints room textures (wallpaper, corkboard, paper notes, map, calendar)."""
import os, random
from PIL import Image, ImageDraw, ImageFilter
from fonts import font
import kitpath

R = kitpath.TEX + '/room'
os.makedirs(R, exist_ok=True)
rnd = random.Random(3)

# wallpaper: dusty teal with small darker sprigs
W = 1024
im = Image.new('RGB', (W, W), (148, 186, 166))
d = ImageDraw.Draw(im)
for j in range(8):
    for i in range(8):
        x = i * 128 + (64 if j % 2 else 0) + 32
        y = j * 128 + 40
        c = (112, 150, 134)
        d.ellipse((x - 10, y - 10, x + 10, y + 10), fill=c)
        d.line((x, y + 8, x, y + 34), fill=c, width=5)
        d.ellipse((x - 16, y + 18, x - 2, y + 28), fill=c)
        d.ellipse((x + 2, y + 18, x + 16, y + 28), fill=c)
for x in range(0, W, 256):
    d.rectangle((x, 0, x + 5, W), fill=(132, 170, 150))
im.filter(ImageFilter.GaussianBlur(1.2)).save(f'{R}/wallpaper.png')

# lilac night variant
im = Image.new('RGB', (W, W), (96, 88, 150))
d = ImageDraw.Draw(im)
for j in range(8):
    for i in range(8):
        x = i * 128 + (64 if j % 2 else 0) + 32
        y = j * 128 + 40
        c = (66, 58, 118)
        d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=c)
        d.line((x, y + 8, x, y + 30), fill=c, width=4)
im.filter(ImageFilter.GaussianBlur(1.2)).save(f'{R}/wallpaper_night.png')

# corkboard
im = Image.new('RGB', (1200, 900), (176, 128, 74))
px = im.load()
for _ in range(60000):
    x, y = rnd.randrange(1200), rnd.randrange(900)
    v = rnd.randint(-30, 26)
    r, g, b = px[x, y]
    px[x, y] = (max(0, r + v), max(0, g + v), max(0, b + v))
d = ImageDraw.Draw(im)
f = font('georgiab', 34)
fs = font('georgia', 22)
notes = [(70, 60, 380, 300, (238, 230, 206), 'TIDES', 'high 6:40'), (480, 50, 760, 330, (236, 222, 170), 'ORDERS', 'twelve wicks'),
         (840, 90, 1130, 300, (222, 232, 226), 'OIL', 'two barrels'), (110, 400, 420, 760, (240, 232, 214), 'ROUTE', 'Quay to Hill'),
         (520, 430, 840, 800, (232, 224, 196), 'WATCH', 'every lamp'), (900, 400, 1140, 700, (236, 214, 190), 'NOTE', 'buy matches')]
for x0, y0, x1, y1, c, a, b in notes:
    d.rectangle((x0 + 7, y0 + 7, x1 + 7, y1 + 7), fill=(112, 76, 40))
    d.rectangle((x0, y0, x1, y1), fill=c, outline=(120, 100, 76), width=2)
    d.text((x0 + 24, y0 + 24), a, font=f, fill=(44, 34, 28))
    d.text((x0 + 24, y0 + 74), b, font=fs, fill=(70, 60, 52))
    for k in range(4):
        yy = y0 + 124 + k * 30
        if yy < y1 - 24:
            d.line((x0 + 24, yy, x1 - 30 - 20 * (k % 2), yy), fill=(150, 140, 126), width=3)
    d.ellipse(((x0 + x1) / 2 - 11, y0 - 8, (x0 + x1) / 2 + 11, y0 + 14), fill=(190, 46, 40), outline=(60, 20, 18), width=2)
im.filter(ImageFilter.GaussianBlur(0.9)).save(f'{R}/cork.png')

# ledger page
im = Image.new('RGB', (900, 640), (196, 188, 164))
d = ImageDraw.Draw(im)
fh = font('segoepr', 56)
d.text((70, 120), 'All lamps lit.', font=fh, fill=(70, 80, 120))
d.text((70, 300), 'Nothing missing.', font=fh, fill=(70, 80, 120))
d.line((70, 240, 820, 232), fill=(150, 150, 170), width=3)
d.line((70, 420, 820, 412), fill=(150, 150, 170), width=3)
im.filter(ImageFilter.GaussianBlur(0.8)).save(f'{R}/ledger.png')

# wall calendar
im = Image.new('RGB', (500, 660), (238, 232, 216))
d = ImageDraw.Draw(im)
d.rectangle((0, 0, 500, 180), fill=(176, 52, 46))
f3 = font('georgiab', 72)
d.text((70, 48), 'MARCH', font=f3, fill=(246, 236, 214))
for j in range(5):
    for i in range(7):
        d.rectangle((26 + i * 66, 214 + j * 84, 76 + i * 66, 264 + j * 84), fill=(198, 186, 170) if (i + j * 7) % 9 else (176, 52, 46))
im.filter(ImageFilter.GaussianBlur(0.8)).save(f'{R}/calendar.png')
# brass-edged desk nameplate
im = Image.new('RGB', (900, 200), (40, 26, 16))
d = ImageDraw.Draw(im)
d.rectangle((10, 10, 889, 189), outline=(214, 170, 80), width=7)
fn = font('georgiab', 92)
bb = d.textbbox((0, 0), 'T. TOBIN', font=fn)
d.text(((900 - bb[2]) / 2, (200 - bb[3]) / 2 - 10), 'T. TOBIN', font=fn, fill=(232, 196, 110))
im.filter(ImageFilter.GaussianBlur(0.8)).save(f'{R}/nameplate.png')

# wall poster
im = Image.new('RGB', (500, 720), (232, 222, 196))
d = ImageDraw.Draw(im)
fb = font('georgiab', 58)
d.rectangle((14, 14, 485, 705), outline=(50, 40, 34), width=6)
d.text((46, 50), 'KEEP THE', font=fb, fill=(40, 34, 30))
d.text((46, 118), 'LAMPS LIT', font=fb, fill=(160, 44, 40))
d.polygon([(250, 240), (340, 420), (160, 420)], fill=(226, 170, 60), outline=(40, 30, 24))
d.rectangle((210, 420, 290, 610), fill=(60, 66, 62))
for k in range(3):
    d.rectangle((60, 640 + k * 18, 440 - k * 60, 648 + k * 18), fill=(90, 80, 70))
im.filter(ImageFilter.GaussianBlur(0.9)).save(f'{R}/poster.png')
print('room ok')
