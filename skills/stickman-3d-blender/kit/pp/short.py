"""Render any short of this style from its plan: python pp/short.py shorts/SLUG/short.json [--preview]
Blender frames per clip -> parallel finishing (ink, motion blur, grade) -> dissolves, captions -> one encode with the mix.
Prints 'Progress : x %'; finished frames are skipped, so a stopped run resumes. Output: out/SLUG/SLUG.mp4.
--preview: half size, 6 samples, into out/SLUG_pv, for checking motion before the full render.
Relative paths (the argument and every path inside short.json) are relative to the kit root.
Env: BLENDER (Blender executable, default `blender` on PATH), ENCODER=nvenc for NVIDIA hardware encoding (default libx264),
WORKERS (finishing processes, default up to 8).

short.json:
{
  "slug": "the-honest-thief", "fps": 30, "last": 1799,
  "clips": [["shorts/x/street.blend", "st", 0, 400], ["shorts/x/dusk.blend", "dk", 392, 900], ...],
  "dissolves": [[392, 400]],                 // overlap of two clips, linear mix
  "shot_ends": [36, 163],                    // last frame before a jump inside a clip: no motion vector crosses it
  "grades": [[0, "st"], [392, "dk"], [901, "rm"]],     // grade per frame range (post.SCENES), optional lerps below
  "grade_lerps": [["wl", "rm", 232, 244]],
  "audio": "shorts/x/mix.wav",               // final mix: voice, music, sound effects
  "words": "shorts/x/words.json",            // [{w, s, e}] from pp/words.py
  "captions": "auto"                         // or [[frame, "text"], ...]
}
"""
import json
import os
import re
import subprocess
import sys
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kitpath

R = kitpath.KIT
BL = kitpath.BLENDER
# words that never stand alone on screen: they ride with the next word ("a key", "he said", "and every")
JOIN = {'a', 'an', 'the', 'and', 'but', 'or', 'he', 'she', 'it', 'i', 'we', 'they', 'you', 'to', 'of', 'in', 'on', 'at', 'his', 'her',
        'my', 'your', 'our', 'their', 'is', 'was', 'so', 'for', 'no', 'not', 'just', 'its', 'this', 'that'}


def captions(words, fps, max_len=14):
    """Groups of one or two words. Whisper word starts run about 3 frames early against the ear, so a caption pops
    3 frames after the word start, which lands it on the sound (measured: mean error 0.3 frame)."""
    out, i = [], 0
    while i < len(words):
        w = words[i]['w'].strip()
        bare = re.sub(r'[^\w\']', '', w).lower()
        start = words[i]['s']
        if bare in JOIN and i + 1 < len(words) and not re.search(r'[,.!?:;]$', w) and len(w) + 1 + len(words[i + 1]['w']) <= max_len:
            w = w + ' ' + words[i + 1]['w'].strip()
            i += 1
        out.append((max(0, round(start * fps) + 3), w))
        i += 1
    return out


def load(path):
    S = json.load(open(path))
    S.setdefault('fps', 30)
    S.setdefault('dissolves', [])
    S.setdefault('shot_ends', [])
    S.setdefault('grade_lerps', [])
    return S


def grade_fn(S):
    sys.path.insert(0, R + '/pp')
    import post
    keys = sorted(S.get('grades', []))

    def g(tag, f):
        for a, b, f0, f1 in S['grade_lerps']:
            if f0 < f < f1:
                A, B = post.SCENES[a], post.SCENES[b]
                t = (f - f0) / (f1 - f0)
                return {k: (tuple(p + (q - p) * t for p, q in zip(A.get(k, B.get(k)), B.get(k, A.get(k))))
                            if isinstance(A.get(k, B.get(k)), tuple) else A.get(k, B.get(k)) + (B.get(k, A.get(k)) - A.get(k, B.get(k))) * t)
                        for k in set(A) | set(B)}
        name = tag
        for f0, n in keys:
            if f >= f0:
                name = n
        return post.SCENES[name]
    return g


def fin(job):
    path, O, tag, f = job
    dst = f'{O}/fin/{tag}_{f:04d}.png'
    if os.path.exists(dst):
        return f
    sys.path.insert(0, R + '/pp')
    import cv2
    cv2.setNumThreads(1)
    import numpy as np
    import finishing
    from PIL import Image
    S = load(path)
    a = finishing.frame(f'{O}/{tag}/f{f:04d}', tag, f, ends=tuple(S['shot_ends']), grade=grade_fn(S))
    Image.fromarray((a * 255 + .5).astype(np.uint8)).save(dst, compress_level=1)
    return f


def main():
    path = sys.argv[1] if os.path.isabs(sys.argv[1]) else f'{R}/{sys.argv[1]}'
    preview = '--preview' in sys.argv
    S = load(path)
    fps, last = S['fps'], S['last']
    O = f"{R}/out/{S['slug']}" + ('_pv' if preview else '')
    samples, pct = ('6', '50') if preview else ('32', '100')
    os.makedirs(f'{O}/fin', exist_ok=True)
    clips = S['clips']
    total = sum(b - a + 1 for _, _, a, b in clips)
    done = 0
    for blend, tag, a, b in clips:
        p = subprocess.Popen([BL, '-b', f'{R}/{blend}', '-P', f'{R}/pp/render_frames.py', '--', f'{O}/{tag}', str(a), str(b), '1', samples, pct],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors='replace')
        for line in p.stdout:
            m = re.match(r'FRAME \d+ (\d+)/(\d+)', line)
            if m:
                print(f'Progress : {100 * 0.8 * (done + int(m.group(1))) / total:.1f} %', flush=True)
        p.wait()
        done += b - a + 1
    jobs = [(path, O, t, f) for _, t, a, b in clips for f in range(a, b + 1)]
    with Pool(int(os.environ.get('WORKERS', min(8, os.cpu_count() or 4)))) as pool:
        for i, _ in enumerate(pool.imap_unordered(fin, jobs)):
            if i % 10 == 0:
                print(f'Progress : {80 + 16 * i / len(jobs):.1f} %', flush=True)

    sys.path.insert(0, R + '/pp')
    import numpy as np
    import post
    from PIL import Image

    def frame(tag, f):
        return np.asarray(Image.open(f'{O}/fin/{tag}_{f:04d}.png').convert('RGB'), np.float32)

    def sources(g):
        """The clip(s) covering frame g: two inside a dissolve."""
        for (b1, t1, a1, e1), (b2, t2, a2, e2) in zip(clips, clips[1:]):
            for x0, x1 in S['dissolves']:
                if x0 == a2 and x1 == e1 and x0 <= g <= x1:
                    return [(t1, 1 - (g - x0 + 1) / (x1 - x0 + 2)), (t2, (g - x0 + 1) / (x1 - x0 + 2))]
        for blend, t, a, b in clips:
            if a <= g <= b:
                return [(t, 1.0)]
        return [(clips[-1][1], 1.0)]

    caps = S['captions']
    if caps == 'auto':
        caps = captions(json.load(open(f"{R}/{S['words']}")), fps)
    out = f"{O}/{S['slug']}.mp4"
    size = 'x'.join(map(str, frame(clips[0][1], clips[0][2]).shape[1::-1]))
    dur = (last + 1) / fps
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', size, '-r', str(fps), '-i', '-']
    if S.get('audio'):
        cmd += ['-t', f'{dur}', '-i', f"{R}/{S['audio']}", '-map', '0:v:0', '-map', '1:a:0', '-af', f'afade=t=out:st={dur - 0.06}:d=0.06', '-c:a', 'aac', '-b:a', '192k']
    if os.environ.get('ENCODER') == 'nvenc':
        cmd += ['-c:v', 'h264_nvenc', '-preset', 'p7', '-tune', 'hq', '-rc', 'vbr', '-cq', '18', '-b:v', '0', '-maxrate', '25M', '-bufsize', '50M']
    else:
        cmd += ['-c:v', 'libx264', '-preset', 'slow', '-crf', '16']
    cmd += ['-profile:v', 'high', '-pix_fmt', 'yuv420p', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', '-movflags', '+faststart', out]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for g in range(last + 1):
        a = sum(frame(t, g) * k for t, k in sources(g))
        im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
        ws = [x for x in caps if x[0] <= g]
        if ws:
            s0, word = ws[-1]
            n = g - s0
            im = post.caption(im, word, 1.0 if n >= 3 else (0.85, 0.97, 1.03)[n])
        ff.stdin.write(np.asarray(im, np.uint8).tobytes())
        if g % 15 == 0:
            print(f'Progress : {96 + 4 * g / last:.1f} %', flush=True)
    ff.stdin.close()
    ff.wait()
    print('OK', out, flush=True)


if __name__ == '__main__':
    main()
