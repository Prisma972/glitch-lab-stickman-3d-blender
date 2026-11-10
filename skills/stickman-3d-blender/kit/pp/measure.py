"""Compare luma/chroma stats of images. python measure.py a.jpg b.jpg ..."""
import sys
import numpy as np
from PIL import Image
for f in sys.argv[1:]:
    a = np.asarray(Image.open(f).convert('RGB').resize((270, 480)), float) / 255
    y = a @ [.2126, .7152, .0722]
    c = a.max(2) - a.min(2)
    print(f.split('/')[-1][:18].ljust(19), 'med %.3f p5 %.3f p95 %.3f chroma %.3f p90 %.3f' % (np.median(y), np.percentile(y, 5), np.percentile(y, 95), c.mean(), np.percentile(c, 90)))
