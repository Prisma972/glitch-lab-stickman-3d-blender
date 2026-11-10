"""python pp/board.py OUTDIR TAG frames NAME : labelled grid of finished frames (fNNNN_f.jpg), 7 per row. Labels from out/kit_labels.json."""
import json
import os
import sys
from PIL import Image, ImageDraw
from fonts import font as _font
import kitpath

O, tag, fr, name = sys.argv[1], sys.argv[2], [int(x) for x in sys.argv[3].split(',') if x], sys.argv[4]
LABELS = kitpath.OUT + '/kit_labels.json'
lab = json.load(open(LABELS)) if os.path.exists(LABELS) else {}
cols = 7
W, H = 300, 533
rows = -(-len(fr) // cols)
sheet = Image.new('RGB', (W * cols, H * rows), (20, 20, 22))
font = _font('arialbd', 17)
for i, f in enumerate(fr):
    im = Image.open(f'{O}/{tag}/f{f:04d}_f.jpg').convert('RGB').resize((W, H), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    t = lab.get(str(f), str(f))
    d.rectangle((0, H - 26, W, H), fill=(0, 0, 0))
    d.text((6, H - 24), t, font=font, fill=(255, 230, 90))
    sheet.paste(im, ((i % cols) * W, (i // cols) * H))
sheet.save(f'{O}/{name}.jpg', quality=88)
print(f'{O}/{name}.jpg', sheet.size)
