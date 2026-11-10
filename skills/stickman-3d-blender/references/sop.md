# SOP: one original short, A to Z

Each step ends with a check. Stop for the user only where marked **ASK**. Everything else: do it, check it, move on.
Work folder: `KIT/shorts/<slug>/`, where `KIT` is the user's copy of the kit (SKILL.md, Step 0). Code: `pp/` (see kit.md). Style rules: da-bible.md. Run every command from `KIT`.

## 0. Before anything
- Step 0 of SKILL.md done once on this computer (Blender, Python packages, ffmpeg, the example scene builds and renders).
- Read da-bible.md and lessons.md.
- Make the folder `shorts/<slug>/` with `plan.md` (the living document of this short: story, sources, script, shot table, state).

## 1. Story (**ASK** the user to choose)
- Find 3 true stories (or plausible fables, said as such) that fit the formula in da-bible.md section 1: one paradox you can say in one line, a human hero, escalation in 3 or 4 visible steps, a twist, a last line that lands. Check the facts against two sources and keep them in `plan.md`. Never reuse a story another channel has already told as a short.
- Propose the 3 loglines with the hook line of each. The user picks one.

## 2. Script
- 180 to 220 words for 60 to 75 s (3.0 to 3.1 words per second). One idea per sentence. Hook paradox in the first 3 seconds, hero and want in the first shot.
- Write it in English unless the user asks for another language (**ASK** once per short if not stated).
- Write the beat list under it: one line of narration = one beat = one visual idea (a noun or a verb you can show).
- Check: read it aloud at 3 words per second; every beat has something to show; no beat describes what the picture already shows.

## 3. Voice (**ASK** which voice, every short)
- The user's own recording, or any text-to-speech tool they choose. If it is paid per character, give the character count before generating. Never print an API key.
- Save the take as `shorts/<slug>/voice.wav` (convert with `ffmpeg -i take.mp3 shorts/<slug>/voice.wav` if needed).
- Word timings: `python pp/words.py shorts/<slug>/voice.wav shorts/<slug>/words.json` (faster-whisper; add `medium` or `large-v3` as third argument for accuracy, and the language code as fourth if it is not English). Fix any misheard word by hand, keep the timings.
- Check: listen to the take once for pace and stumbles; the duration sets `last` in `short.json` (`round(seconds * 30) - 1`).

## 4. Shot plan
- In `plan.md`, a table: shot, frames, words over it, place and time of day, framing, camera (hold rate and push, or flight in or out), transition, characters on screen, action, face per beat. Frames come from `words.json` (`round(seconds * 30)`).
- Grammar (da-bible.md section 3): holds creep, shots in one world join by flights, hard cuts only on a change of place or time (often after a dive), a dissolve for a time jump, inserts for objects, a hold lasts 1 to 4 s. Every action lands 0 to 3 frames before its word.
- Cast and sets: list what exists in the kit and what must be built (new costume spec, new set module, new prop).
- Check: every narration line has a picture, the people count per shot is set, nothing is copied from someone else's shot.

## 5. Build
- One shot file per world and time of day: `shorts/<slug>/<clip>.py`, written like `shorts/allumeur/scene.py` (same bootstrap at the top, `from common import *`, build a set with `run()`, cast, keys, cameras, save `shorts/<slug>/<clip>.blend` with `P + 'shorts/<slug>/<clip>.blend'`, print an ok line). Start every move from the pose the previous hold returned.
- New characters are spec dicts (kit.md section 1); new faces are lines in `faces.py`; new places are set modules in `pp/`.
- Build headless: `"$BLENDER" -b -P shorts/<slug>/<clip>.py`.
- `short.json` next to it: clips, dissolves, shot ends, grades, `audio`, `words`, `captions: "auto"` (format in the docstring of `pp/short.py`; example `shorts/allumeur/short.json`).
- Check: the build prints its ok line, every blend saves.

## 6. Stills gate (no video)
- Render one key frame per shot plus the peak of each flight, finish them with the real finish, put them in a sheet: `python pp/gpulock.py "$BLENDER" -b shorts/<slug>/<clip>.blend -P pp/render_frames.py -- <absolute KIT>/out/<slug>_st/<tag> 12,40,77 16 50`, then `python pp/test_frames.py <absolute KIT>/out/<slug>_st <tag>`, then `python pp/board.py <absolute KIT>/out/<slug>_st <tag> 12,40,77 sheet` (kit.md sections 8 and 9).
- LOOK at every still: faces readable, whites white, outlines (head charcoal, mitts fine), nothing floating or crossing a body, people count, mood colours, captions band clear of the action.
- Fix and re-render until the sheet is clean. Then a fresh critic subagent (it did not build the short) checks the sheet against da-bible.md and the look notes in lessons.md; verify each of its claims on the frames before acting.

## 7. Motion preview
- `python pp/short.py shorts/<slug>/short.json --preview` (half size, 6 samples; about a third of the full render time). Run it in the background.
- Check motion: flights read as one move, holds creep, no pop, feet planted, hands land on their words. Strips of consecutive frames show what one frame cannot.
- Fix, re-preview only if the change touched motion.

## 8. Sound
- Music and effects per da-bible.md section 9: the user's own, generated, or licensed for reuse. `shorts/<slug>/mix.json` then `python pp/mix.py shorts/<slug>/mix.json`: the mix must print about -9 LUFS, true peak -1 dBTP.
- Check: voice always on top, music ducked under it, effects on their frames.

## 9. Final render (**ASK** the user first, with the expected duration)
- `python pp/short.py shorts/<slug>/short.json` in the background (32 samples, full size). It skips finished frames, so a stopped render resumes where it was. Output `out/<slug>/<slug>.mp4`. `ENCODER=nvenc` for NVIDIA hardware encoding.
- Only one Blender render at a time on the graphics card: wait for previews or stills to finish first.

## 10. QA and delivery
- On the final file: 1080x1920, 30 fps, duration, no black, white or frozen frame, captions on every word, loudness about -9 LUFS.
- A fresh critic scores the final against da-bible.md; report its raw score, never a self-score.
- Give the user the mp4 path with a title (da-bible.md section 10, under 60 characters), a description with the facts and their sources, and a cover frame. Nothing is posted by Claude.

## 11. After
- Append what went wrong and what fixed it to lessons.md. Write the final state in `plan.md`.
