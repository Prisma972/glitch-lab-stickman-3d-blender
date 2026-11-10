# Kit reference (Blender, `kit/` of this skill)

All code lives in `pp/`, textures in `tex/`, shorts in `shorts/<slug>/`. Blender 5.2, EEVEE. Paths come from `pp/kitpath.py`: the kit root is the parent of `pp/` (env `STICKMAN_KIT` overrides), Blender is `BLENDER` or `blender` on PATH. Scripts run headless (`"$BLENDER" -b -P file.py`) or in a live Blender. Units are metres, characters face -Y, 30 fps. Run commands from the kit root; relative paths in `short.json` and `mix.json` are relative to it.

## Contents
1. Characters (`chars.py`)
2. Faces (`faces.py`)
3. Poses and actions (`acts.py`)
4. Walks, idles, camera (`anim.py`)
5. Shot helpers (`common.py`)
6. Look, materials, moods (`look.py`)
7. Sets (`street.py`, `room.py`, `village.py`)
8. Render and finish (`render_frames.py`, `finishing.py`, `short.py`, `mix.py`, `preview.py`, `words.py`)
9. Check tools
10. Python packages

## 1. Characters: `chars.build(name, spec, loc, rot_z, coll)`
Returns a dict `ch`: `root`, `torso`, `head`, `skull`, `cap` (cap hinge, flat cap only), `faces` (the family's names), `joints[tag]` for `L` and `R` with empties `sh` (shoulder), `el` (elbow), `hd` (wrist), `hand` (mitt rotation), `hp` (hip), `kn` (knee), `ft` (foot).
Spec keys: `profile` (`PROF_COAT` straight torso then a bell skirt, `PROF_DRESS`, `PROF_BEAN`), `coat`, `trim`, `btn` (linear RGB), `hat` (`flatcap`, `bowler`, None), `hat_col`, `belt` (height), `buttons` [(x, z)], `collar` (bool), `apron` (RGB), `hair`, `hair_style` (`cap`, `bun`), `shoe`, `family` (`hero` draws the moustache, `plain` does not), `face0` (resting face), `mitts` (`white` for the hero only, default black).
Ready cast: `LAMPLIGHTER` (hero: teal coat, rust flat cap, moustache, white mitts), `BAKER` (ochre dress, apron, bun), `CLERK` (green bean, bowler), `PASSER1` (plum coat, bowler), `PASSER2` (red dress, bun). A new character is a new spec dict: change colours, hat, profile, family.
Proportions measured on reference shorts (head = 1): bell coat 0.60 wide at 20 % below the collar, 0.67 at 50 %, belt 0.59 at 62 %, hem 0.73; collar to hem 1.15; visible legs 0.40 to 0.55. Head radius 0.30 m.
Posing by hand: `chars.set_arm(ch, 'L', wrist, elbow, hand_rot)` in root space; `chars.set_face(ch, 'worried', frame)` keys a face (constant).
Whites: `chars.HEAD_GLOW[0]` and `chars.GLOVE_GLOW[0]` set head and mitt emission before `build`. Street: 0.88 and 0.35. Room: 0.78 and 0.15.

## 2. Faces: `python pp/faces.py` (system Python)
Each face is built from parts: eyes (`lid`, `open`, `wide`, `closed`, `happy`, `sad`, `angry`, `squint`, with a look offset), brows (`flat`, `smug`, `raised`, `worried`, `sad`, `angry`, `skeptic`, `relaxed`), mouth (`smirk`, `smile`, `grin`, `flat`, `frown`, `side`, `wavy`, `o`, `talk_a`, `talk_o`, `laugh`, `teeth`). The moustache is drawn last on the `hero` family so it never disappears.
Names in both families: `neutral neutral_b smile smile_b happy surprised worried worried_b sad sad_b angry angry_b skeptical scared thinking sleepy determined embarrassed talk_a talk_o look_l look_r`. Older names: hero `sly sly_b sly_w laugh_m shock_m calm_m`, plain `flatface flatface_b calm calm_b laugh shock`.
Output: `tex/faces/atlas_hero.png`, `atlas_plain.png` (8 x 4 tiles of 1024), `atlas.json`, and the previews `preview_hero.jpg`, `preview_plain.jpg` (the kit ships these). One texture per head whatever the number of faces. A new expression is one line in `EXPR` plus a rerun; keep at most 32 per family.

## 3. Poses and actions: `acts.py`
`acts.pose(ch, frame, name, face=None, mix=1.0)` keys wrists, elbows, mitt rotation, torso and head. Poses: `rest hips behind carry shrug surprise cheer scared cross point wave think facepalm reach beckon`. `point` shows the hidden index finger.
Actions: `wave(ch, f0, f1)`, `nod(ch, f, n)`, `shake(ch, f, n)`, `hop(ch, f)` (dip, 4 frames up, squash), `run(ch, f0, f1, start, end)`, `sit(ch, f, seat)`, `talk(ch, f0, f1, base)` (mouth flaps every 3 frames).
Keep `anim.breathe(head=False)` when keying the head here, or the two curves fight.

## 4. Walks, idles, camera: `anim.py`
`walk(ch, f0, f1, start, end, period, lift, arm, bob, hold, release, curve)`: planted feet, 60/40 stance, head dips on contact, free arms swing out. Measured gait: hero 8 to 10 frames per cycle, `bob=0.018`, `lift=0.06` to `0.09`, 0.03 to 0.04 m per frame. `hold={'L': (wrist, elbow)}` pins a hand (carrying), `release=(fa, fb)` lets it go.
`stand(ch, f)` both feet down. `breathe(ch, f0, f1, amp, period, head, yaw)`. `blinks(ch, frames)`.
Camera grammar, measured on reference shorts:
- `hold(cam, f0, f1, pose, rate, dist, push)`: a locked shot is a straight constant dolly toward frame centre, 0.0013 to 0.0027 scale per frame, no pan, no roll. `push` is a list of scale steps on the last frames, for the acceleration into a hard cut (dive). Returns the last pose.
- `camera_move(cam, f0, f1, a, b, focus_a, focus_b, curve, aim)`: flights between shots in the same world. `anim.IN` ramps up late (fly-ins), `anim.OUT` snaps early and glides (fly-outs). `aim` keeps the target at the subject's distance so the move sweeps around it.
- Always start a move from the pose the previous hold returned.

## 5. Shot helpers: `common.py`
A shot file starts with the bootstrap of `shorts/allumeur/scene.py` (finds `pp/` two folders up, or in `STICKMAN_KIT`), then `from common import *`, which gives `bpy`, `Vector`, `L` (look), `chars`, `anim`, `R` (degrees to radians) and `P` (the kit root, with a trailing slash).
`run('build_street.py')` builds a set and returns its globals (`hero`, `baker`, `clerk`, `SET`, `M`). `place(ch, f0, f1, loc, rz)`, `away(ch, f0, f1)` parks a character under the floor, `show(o, f, on)` keys visibility with children, `to_local(ch, world)`, `key_hand(ch, tag, [(f, wrist, elbow)])`, `head_key(ch, [(f, rx, rz)])`, `key_ink(names, keys)`, props `wallet()`, `plane_uv()`, `postbox()`, `key_reveal()` with `note_mat()` (handwriting that writes itself), `cam_shot()` and `cam_hold()` (camera plus aperture keys).

## 6. Look: `look.py`
Moods (`L.setup(scene, mood)` or `L.apply_mood`): `day` (soft sun from behind left, 15 deg wide, fill and ambient), `dusk` (warm ground, violet sky only), `night`, `interior`, `room` (even warm ambient). Materials: `mat(name, rgb, rough, spec, paint, pscale, emis, form)` (painted, matte, `form` darkens only the silhouette), `tex_mat`, `brick_mat`, `wood_mat`, `glass_mat`, `glow_mat`, `halo_mat`. Ink: `L.ink(obj, w, soft, px)` inverted hull; `px` keeps the width constant on screen (characters: head 6, collar 5, hat and shoes 4, coat 3.6, mitts 3 at 1080 wide). `noink(m)` excludes a material from the post line. Primitives: `box cyl sph lathe empty collection wipe camera`. `matte_lights()` before saving.

## 7. Sets
`street.build()` (via `build_street.py`): a town street with shops, signs, lamps, stall, bins, bunting, poster column, tram, end terrace. `room.build()` (via `build_room.py`): a workshop with desk, lamp, shelves, wallpaper. `village.py` (via `build_village.py`): hip-roof houses on a grid for aerial views, at night. Camera starting points per set in `shots_street.json`, `shots_room.json`, `shots_village.json`. New places are new modules in the same pattern, built from `look` primitives and materials.
Textures: `python pp/make_signs.py` repaints `tex/signs/` (shop signs, displays, posters, chalk board, blade signs, OPEN card, post box plate), `python pp/make_room.py` repaints `tex/room/`. Fonts come from `pp/fonts.py` (Windows, macOS or Linux fonts, or your own in `STICKMAN_FONTS`).

## 8. Render and finish
- `render_frames.py`: `"$BLENDER" -b X.blend -P pp/render_frames.py -- OUTDIR start end [step] [samples] [percent]` or `-- OUTDIR 8,19,52 [samples] [percent]` (a frame list; one frame is `140,`). EXR multilayer (combined, depth, normal, vector, noink AOV) plus a camera json per frame; sets the character hulls in pixels each frame; skips frames on disk. Give OUTDIR as an absolute path.
- `finishing.frame(src, tag, f, ends, grade)`: ink lines from depth and normals, motion blur from the vector pass (shutter 0.4, never across a shot end), bloom gated off the ink, grade (`post.SCENES`: `st` day street, `dk` dusk, `wl` warm insert, `rm` room, `vl` night village), screen-fixed vignette.
- `python pp/short.py shorts/SLUG/short.json [--preview]`: the whole short from its plan (clips, dissolves, shot ends, grades, captions from the word timings, the mix); the format is in its docstring. Prints `Progress : x %`, resumes where it stopped. Output `out/SLUG/SLUG.mp4`. `--preview` renders half size at 6 samples into `out/SLUG_pv`. `ENCODER=nvenc` uses NVIDIA hardware encoding, default libx264.
- `python pp/mix.py shorts/SLUG/mix.json`: voice, music, sound effects to `mix.wav` at -9 LUFS, true peak -1 dBTP; the format is in its docstring.
- `python pp/words.py voice.wav words.json [model] [language]`: word timings with faster-whisper (`[{w, s, e}]`), the input of the auto captions. Whisper word starts run about 3 frames early: `short.py` already pops captions 3 frames after the start.
- `post.caption(im, text, sc)`: Arial Black 53 px at 1080 (a bold sans fallback elsewhere), black 6 px stroke, soft shadow, baseline fixed at y 1372, pop 0.85, 0.97, 1.03 over 3 frames.

## 9. Check tools
- `python pp/gpulock.py <command>`: runs a render command when no other kit render holds the graphics card (lock `out/.gpu.lock`, broken after 15 min if stale). Wrap every Blender render in it.
- `python pp/test_frames.py OUTDIR [tags]`: finishes every EXR of `OUTDIR/<tag>/` to `fNNNN_f.jpg` with the real finish (`NOBLUR=1` when frames are unrelated poses).
- `python pp/board.py OUTDIR TAG frames NAME`: a labelled grid of finished frames (labels from `out/kit_labels.json` when present).
- `python pp/preview.py BLEND NAME START END [samples] [percent] [tag]`: a frame range of any blend with the real finish, as `out/NAME/NAME.mp4`, no sound.
- `"$BLENDER" -b -P pp/kit_board.py` builds `kit.blend` (every face on the hero and on a plain character, every pose; labels in `out/kit_labels.json`); `pp/kit_motion.py` builds `kit_motion.blend` (walk, wave and talk, hop, think and nod, shrug, point, run). Render them with `render_frames.py`, finish with `NOBLUR=1 test_frames.py`, lay out with `board.py`.
- `python pp/measure.py a.jpg b.jpg ...`: median luma, percentiles and chroma, to compare a still with a target row by row.
- `python pp/ref_prep.py VIDEO SLUG [OUTDIR]`: evidence pack of a reference video the user supplies (frames, contact sheets, motion curve with hard cuts and flights, grade per second, word timings). Private study material: never republish it, never copy the story or the shots.

## 10. Python packages
System Python 3.10+: `numpy`, `Pillow`, `opencv-python`, `OpenEXR` (3.3+, for `OpenEXR.File`), and `faster-whisper` for `words.py` and `ref_prep.py`. Blender scripts use only Blender's own Python. ffmpeg on PATH for `short.py`, `mix.py`, `preview.py`, `ref_prep.py`.
