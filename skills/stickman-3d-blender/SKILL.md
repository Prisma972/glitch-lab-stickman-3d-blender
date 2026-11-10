---
name: stickman-3d-blender
description: Makes original narrated vertical story shorts (60-75 s, 9:16) with 3D bean characters built in Blender - white ball heads with painted faces, bell coats, black stick limbs, mitts, a painted 3D town, a true or plausible story with a twist, 1-2 word captions - using the Blender kit shipped inside this skill (characters, faces, poses, camera grammar, sets, ink and grade finishing, captions, sound mix). Covers first-use setup, story, script, voice, shot plan, build, stills check, motion preview, mix, final render and delivery. Use it whenever the user asks for a "stickman 3D" or "Stickman 3D Blender" short, "make me a stickman 3D short about ...", a story short with bean characters in Blender, or wants to use, extend or change this kit, its look, expressions or poses, even if the skill is not named.
---

# Stickman 3D Blender

Original story shorts in a style measured on reference shorts (the measured rules are in `references/da-bible.md`). Everything is built in Blender 5.2 with the kit in `kit/`, next to this file. Never republish anyone else's video, never reuse their stories, characters or shots.

Read these when the step needs them:
- `references/da-bible.md`: the style rules, measured (story formula, shots, characters, acting, look, captions, sound, cover, variants, kit gaps).
- `references/sop.md`: the production procedure, step by step, with checks.
- `references/kit.md`: the code API (characters, faces, poses, camera grammar, sets, render tools).
- `references/lessons.md`: what went wrong before and how it was fixed. Read before the shot plan and before every fix round.

## The kit and the work folder
- `kit/pp/` code, `kit/tex/` textures (faces atlas, signs, room), `kit/shorts/<slug>/` one folder per short. Example: `kit/shorts/allumeur/` (8 s, a lamplighter lights a street lamp at dusk while a neighbour waves from the tea room).
- Every path is derived from the file location, so the kit works from any folder. On first use, copy `kit/` to a work folder (Step 0) and work there: updating the skill then never touches the user's shorts. Below, `KIT` means that work folder; run every command from it.
- Environment variables, all optional: `BLENDER` (the Blender executable, default `blender` on PATH, then the usual install folders), `STICKMAN_KIT` (forces the kit root), `ENCODER=nvenc` (NVIDIA hardware encoding in `short.py`, default libx264), `WORKERS` (finishing processes), `STICKMAN_FONTS` (a folder of .ttf fonts searched first, see `pp/fonts.py`).

## Step 0: first use (once per computer)
1. **Blender 5.2 or newer.** Try `blender --version`. If it is not on PATH, look in the usual places (Windows `C:/Program Files/Blender Foundation/Blender 5.*/blender.exe`, macOS `/Applications/Blender.app/Contents/MacOS/Blender`, Linux `/usr/bin/blender`, `/snap/bin/blender`). Not found: ask the user for the path (or to install it from blender.org), then set `BLENDER` to it for every command (making it permanent is the user's call: ask). Older than 5.2: say so, the kit is built for 5.2 (EEVEE, Geometry Nodes).
2. **Python 3.10+** with numpy, Pillow, opencv-python and OpenEXR (3.3 or newer): `python -c "import numpy, PIL, cv2, OpenEXR"`. If something is missing, ask before running `pip install numpy pillow opencv-python OpenEXR`. For word timings the kit also uses `faster-whisper` (ask before installing it too, it downloads a speech model on first run).
3. **ffmpeg** on PATH: `ffmpeg -version`. Missing: tell the user how to get it (`winget install ffmpeg`, `brew install ffmpeg`, `sudo apt install ffmpeg`) and ask before installing anything.
4. **Work folder.** Ask where the shorts should live (suggest `~/stickman-3d`), copy the whole `kit/` folder there.
5. **Proof that it works.** From the work folder:
   - `"$BLENDER" -b -P shorts/allumeur/scene.py` must print `allumeur ok` and write `shorts/allumeur/scene.blend` (about 20 s).
   - One still at quarter size: `python pp/gpulock.py "$BLENDER" -b shorts/allumeur/scene.blend -P pp/render_frames.py -- <absolute KIT>/out/check/dk 140, 8 25` (the trailing comma makes `140,` a frame list), then `python pp/test_frames.py <absolute KIT>/out/check dk`.
   - Look at `out/check/dk/f0140_f.jpg`: a dusk street, the lamplighter with his pole, very white head with a dark outline, ink lines, no grain. Show it to the user.
6. Optional, to review what the kit can do: `"$BLENDER" -b -P pp/kit_board.py` (every face and pose, labelled) and `pp/kit_motion.py` (the actions in a row), see kit.md section 9.

## How to work with the user
- Answer in the user's language, short and structured.
- Do not ask at every step: research, check on stills, fix, move on. Stop only for the decisions below.
- The user's eye outranks any critic. Their notes on the look are binding: add them to `references/lessons.md`.
- A full render takes long (about 30 to 45 minutes for 60 s on a recent graphics card, more without one): iterate on stills, check motion on a half-size preview, and render the full short only for a video the user will post.

## Decisions that are the user's (ask, one question each)
1. The story, among 3 checked proposals.
2. The language of the voice if not stated (English by default).
3. The voice: their own recording, or which text-to-speech tool and voice. If the tool is paid per character, give the character count before generating.
4. Any change to the look itself (skin-tone heads, ball hands, coloured arms; see da-bible.md section 11).
5. The final render: say how long it will take before starting it.

## The procedure in one screen (details in sop.md)
1. **Story:** 3 true or plausible stories with a one-line paradox, escalation, twist at 45 to 70 %, a planted line that comes back, a last line that loops. The user picks.
2. **Script:** 180 to 220 words, about 3 words per second, hook paradox in the first 3 to 5 s, "You see," as the hinge into the explanation. Beat list: one line = one visual idea.
3. **Voice and timings:** any TTS or the user's own recording, saved as `shorts/<slug>/voice.wav`; then `python pp/words.py shorts/<slug>/voice.wav shorts/<slug>/words.json` (faster-whisper word timings); fix misheard words by hand.
4. **Shot plan** in `shorts/<slug>/plan.md`: about 40 shots of 1.3 s, holds that creep, flights inside one world, hard cuts between places on the key word, dissolves for time jumps, a quarter of inserts carrying every number and key word on props.
5. **Build:** one shot file per world and time of day, written like `shorts/allumeur/scene.py` (same bootstrap, `from common import *`, `run('build_street.py')`, cast, keys, cameras, save); `short.json` for the render.
6. **Stills gate:** one frame per shot, finished, in a sheet; look at every one; fix; then a fresh critic subagent against da-bible.md.
7. **Motion preview:** `python pp/short.py shorts/<slug>/short.json --preview` (half size, 6 samples).
8. **Sound:** voice, music bed, sparse effects; `python pp/mix.py shorts/<slug>/mix.json` must print about -9 LUFS, true peak -1 dBTP.
9. **Final render** (after the user's yes): `python pp/short.py shorts/<slug>/short.json`, run in the background; it resumes where it stopped. Output `out/<slug>/<slug>.mp4`.
10. **QA and delivery:** checks on the final file, a fresh critic's raw score (never a self-score), title, description with sources, cover frame. Nothing is posted by Claude.
11. **After:** lessons in `references/lessons.md`, state of the short in its `plan.md`.

## Non-negotiables of the look (details in da-bible.md and lessons.md)
- Heads very white, painted grey face marks, head outline dark charcoal and the darkest line on the figure.
- White mitts for the hero only, black mitts for everyone else, never a thumb, hand outline very fine.
- Thick near-black stick arms with no outline and no cast shadow on the coat; very dark brown shoes; collar flat on the coat; the hero's thin moustache always drawn, mouth right under it.
- Everything matte; real cast shadows only; set lines finer than character lines; zero film grain.
- Captions: 1 or 2 words, white heavy sans with a black outline at 0.70 H, scale pop, on the word.
- Every hold creeps inward; joins land on the words.

## Where things are (inside KIT)
- `pp/` the code (kit.md), `tex/` textures, `shorts/<slug>/` shot files, `short.json`, `mix.json`, voice, words, plan.
- `out/` every render (stills, previews, finals), `refs/` analyses of the user's own reference videos made with `python pp/ref_prep.py VIDEO SLUG`. Both stay private: never publish someone else's frames or audio.
- Kit boards: `kit.blend` and `kit_motion.blend` once built (kit.md section 9).
