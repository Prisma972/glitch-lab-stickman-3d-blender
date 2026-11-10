"""python test_frames.py OUTDIR [tags]: finish every EXR of OUTDIR/<tag>/ to fNNNN_f.jpg with the real finish, motion blur included.
NOBLUR=1 for boards, where each frame is a different pose and the vectors mean nothing."""
import sys, glob, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import finishing
from PIL import Image
O = sys.argv[1]
for tag in (sys.argv[2].split(',') if len(sys.argv) > 2 else ('st', 'dk', 'rm')):
    for p in sorted(glob.glob(f'{O}/{tag}/*.exr')):
        f = int(re.search(r'f(\d+)\.exr$', p).group(1))
        o = finishing.frame(p[:-4], tag, f, shutter=0 if os.environ.get('NOBLUR') else finishing.SHUTTER)
        Image.fromarray((o * 255 + .5).astype(np.uint8)).save(p[:-4] + '_f.jpg', quality=93)
        print(os.path.basename(p), flush=True)
