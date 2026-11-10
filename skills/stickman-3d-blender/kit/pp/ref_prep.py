"""python pp/ref_prep.py VIDEO SLUG [OUTDIR] : evidence pack for one reference video of your own choosing, in refs/SLUG/ (or OUTDIR).
frames/fNNNN.jpg (540x960, 1-based: fNNNN = frame NNNN-1), sheet_NN.jpg (one frame per second, 20 per sheet),
motion.json + motion.png (frame difference: hard cuts are one-frame spikes, flights are runs), words.json + transcript.txt
(word timings of the voice, needs faster-whisper), grade.json (luma and chroma per second), cover.jpg (the attached thumbnail, if any).
Study material only: keep it private, never republish someone else's video, frames or audio, never copy their story or shots.
Needs ffmpeg on PATH."""
import glob
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kitpath
from fonts import font as _font

V, slug = sys.argv[1], sys.argv[2]
O = sys.argv[3] if len(sys.argv) > 3 else f'{kitpath.KIT}/refs/{slug}'
os.makedirs(f'{O}/frames', exist_ok=True)
run = lambda *a: subprocess.run(list(a), check=True)
if not glob.glob(f'{O}/frames/*.jpg'):
    run('ffmpeg', '-v', 'error', '-y', '-i', V, '-map', '0:v:0', '-vf', 'scale=540:960:flags=lanczos', '-q:v', '3', f'{O}/frames/f%04d.jpg')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', V, '-map', '0:v:1', '-frames:v', '1', f'{O}/cover.jpg'])
if not os.path.exists(f'{O}/voice.wav'):
    run('ffmpeg', '-v', 'error', '-y', '-i', V, '-map', '0:a:0', '-ac', '1', '-ar', '16000', f'{O}/voice.wav')
fr = sorted(glob.glob(f'{O}/frames/*.jpg'))
n = len(fr)

# contact sheets, one frame per second
font = _font('arialbd', 20)
secs = list(range(0, n, 30))
for s in range(0, len(secs), 20):
    grp = secs[s:s + 20]
    W, H = 270, 480
    sh = Image.new('RGB', (W * 10, H * ((len(grp) + 9) // 10)), (0, 0, 0))
    for i, f in enumerate(grp):
        im = Image.open(fr[f]).resize((W, H))
        d = ImageDraw.Draw(im)
        d.rectangle((0, 0, 120, 26), fill=(0, 0, 0))
        d.text((4, 2), f'{f / 30:.0f}s f{f}', font=font, fill=(255, 230, 90))
        sh.paste(im, ((i % 10) * W, (i // 10) * H))
    sh.save(f'{O}/sheet_{s // 20 + 1:02d}.jpg', quality=85)

# motion curve and grade per second
prev, diff, grade = None, [], []
for i, p in enumerate(fr):
    a = Image.open(p).convert('RGB')
    g = np.asarray(a.convert('L').resize((135, 240)), np.float32)
    if prev is not None:
        diff.append(float(np.abs(g - prev).mean()))
    prev = g
    if i % 30 == 0:
        c = np.asarray(a.resize((135, 240)), np.float32) / 255
        y = c @ np.array([.2126, .7152, .0722], np.float32)
        grade.append(dict(t=i // 30, med=round(float(np.median(y)), 3), p5=round(float(np.percentile(y, 5)), 3),
                          p95=round(float(np.percentile(y, 95)), 3), chroma=round(float((c.max(2) - c.min(2)).mean()), 3)))
d = np.array(diff)
m = float(d.mean())
cuts = [int(i + 1) for i in range(1, len(d) - 1) if d[i] > 3 * m and d[i] > 2 * d[i - 1] and d[i] > 2 * d[i + 1]]
runs, cur = [], None
for i, v in enumerate(d):
    if v > 1.8 * m:
        cur = [i + 1, i + 1] if cur is None else [cur[0], i + 1]
    elif cur:
        if cur[1] - cur[0] >= 3:
            runs.append(cur)
        cur = None
json.dump(dict(frames=n, mean=round(m, 2), diff=[round(x, 2) for x in diff], hard_cuts=cuts, fast_runs=runs), open(f'{O}/motion.json', 'w'))
json.dump(grade, open(f'{O}/grade.json', 'w'), indent=0)
# motion plot, 2 px per frame
Wp, Hp = 2 * len(d), 220
pl = Image.new('RGB', (Wp, Hp + 20), (16, 16, 18))
dr = ImageDraw.Draw(pl)
top = max(60.0, float(d.max()))
for i, v in enumerate(d):
    dr.line((2 * i, Hp, 2 * i, Hp - v / top * Hp), fill=(255, 90, 90) if i + 1 in cuts else (110, 200, 255))
for s in range(0, len(d), 30):
    dr.line((2 * s, Hp, 2 * s, Hp + 6), fill=(255, 255, 255))
    dr.text((2 * s + 2, Hp + 4), f'{s // 30}s', fill=(255, 255, 255))
pl.save(f'{O}/motion.png')

if not os.path.exists(f'{O}/words.json'):
    subprocess.run([sys.executable, f'{kitpath.PP}/words.py', f'{O}/voice.wav', f'{O}/words.json'], check=True)
w = json.load(open(f'{O}/words.json'))
words = w['words'] if isinstance(w, dict) and 'words' in w else w
txt = ' '.join(str(x.get('w', x.get('word', x.get('text', '')))).strip() for x in words)
open(f'{O}/transcript.txt', 'w', encoding='utf-8').write(txt)
print(slug, 'frames', n, 'hard cuts', cuts, 'fast runs', runs[:12], '...', 'words', len(words))
