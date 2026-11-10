# Lessons (binding, from building the kit and matching the style)

Read before the shot plan and before every fix round. Add a numbered line after each round: what went wrong, what fixed it.

## The look notes
1. The owner's eye outranks any critic score. These notes are binding: mitts never have a thumb, hand outline very fine, arms thick and near black with no outline and no cast shadow on the coat, head outline dark charcoal (it defines the style), heads very white, shoes very dark brown, collar flat on the coat, thin moustache always present with the mouth right under it, big pupils under a straight lid, everything matte, real cast shadows only (never painted blotches), roofs show a plane, set lines finer than character lines, zero film grain. The user's own notes join this list.
2. Stills before videos. A full render takes 30 to 45 minutes: iterate on key frames, check motion on a half-size preview, and render the full short only for a video that will be posted.
3. Do not ask the user at each step. Research, check, fix; stop only for real decisions (voice, story choice, look change, final render).
4. Never copy a reference's stories, characters or shots for a video that will be posted. Reference audio and frames are private study material.

## Look
5. A dark overlay must be darker than the lit surface in linear light, or it is invisible.
6. The post line pass (depth plus normals) inks every set edge; a break must hold over two pixel offsets or sub-pixel slivers draw dashes. Hulls carry `noink` so the post line never doubles them.
7. Bloom must never screen over ink: gate it by luminance and mask heads and mitts, or the head line turns grey.
8. Character hulls in pixels per frame, set hulls capped at 3.4 px: world-size hulls double on long lenses.
9. Simulated corrections lie about one time in three: a pavement colour simulated as right came out twice too dark on the still. Verify every number on one real frame, row by row against the target (`pp/measure.py`).
10. Head and mitt whites are emission, not light: dusk needs its own glove emission and a head lift, or whites go lilac.

## Camera and motion
11. Measure the camera grammar with the frame-difference curve (`pp/ref_prep.py` writes it): holds are a constant dolly, shots join by flights, hard cuts only at big jumps, often after a dive. Matching it took the motion from 3/10 to the same spikes on the same frames (correlation 0.95).
12. Motion blur from the Vector pass, after ink, before grade. Spread the fastest tile vector with a soft weight; never blur across a shot end.
13. A prop that must look small next to big hands: shrink the prop and move the lens closer, do not scale the hands.
14. `show()` must key children too, or a hidden prop leaves its parts floating.
15. `breathe(head=False)` whenever the head is keyed elsewhere; `stand()` after every walk, or a foot hangs in the air.
16. Whisper word starts run about 3 frames early: captions pop 3 frames after the word start.

## Example scene (the lamplighter)
17. An early-dusk street reads as daylight and the lamp does not show: go to late dusk (sun, fill and ambient down), keep the painted sky.
18. A lamp's own glass and cap shadow the light placed inside them: turn their shadows off or nothing reaches the street.
19. Thin props vanish in a wide shot (a 1.7 cm pole): thicken them and give small light sources their own light.
20. A prop held upright can cut a sign in the next shot: lean it during the flight between the two shots.

## Pipeline
21. Long multi-agent runs die on network cuts and lose their context; their files survive. Give each agent one file and a small scope, write a resume file early, retry with more attempts.
22. One render at a time on the graphics card: `pp/gpulock.py`.
23. Per-face textures hit shader limits: all expressions of a family live in one atlas.
24. Mix at -9 LUFS, true peak -1 dBTP (`pp/mix.py`).
