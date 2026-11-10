"""One EXR -> one finished frame: ink, motion blur, grade. Used by the final render and by the stills, so both match."""
import json
import cv2
import numpy as np
import inkpost
import post

SHUTTER = 0.4
SHOT_END = ()      # last frames of shots: the frame after each one jumps, so no vector may cross it


def scene(tag, f):
    """Default grade: the one named by the clip tag (post.SCENES), as short.py does when no grade range is given."""
    return post.SCENES[tag]


def frame(src, tag, f, shutter=SHUTTER, ends=None, grade=None):
    """src without extension. Returns float rgb 0..1, no caption.
    ends: last frames of shots (no motion vector may cross them), grade: f(tag, frame) -> post.finish arguments.
    Defaults: no shot end, the grade of the tag."""
    rgb, z, nrm = inkpost.load(src + '.exr')
    cam = json.load(open(src + '.json'))
    a = inkpost.apply(inkpost.to_srgb(rgb), inkpost.lines(z, nrm, focus=cam['focus'], fstop=cam['fstop'], lens=cam['lens']))
    mk = inkpost.LAST['noink']
    nb = None
    if mk is not None:
        nb = np.clip(cv2.dilate(mk, np.ones((9, 9), np.uint8)), 0, 1)
        if tag == 'dk':     # without their own glow, dusk heads fall under the reference: bright noink pixels only, not the arms
            w = mk * np.clip((a @ np.array([.2126, .7152, .0722], np.float32) - 0.4) / 0.2, 0, 1)
            a = 1 - (1 - a) * (1 - 0.3 * w[..., None])
    ends = SHOT_END if ends is None else ends
    side = -1 if f in ends else 1 if f - 1 in ends else 0
    a = inkpost.motion_blur(a, shutter, side)
    return post.finish(a, nobloom=nb, **(grade or scene)(tag, f))
