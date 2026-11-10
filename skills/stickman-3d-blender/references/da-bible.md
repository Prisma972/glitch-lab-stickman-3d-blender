# DA bible: 3D bean-character story shorts

The style rules of this kit, measured frame by frame on three reference story shorts of 58, 70 and 75 s (studied privately, never republished, their stories never reused). Where the three agree, it is a rule. Where they differ, the variants are listed in section 11 with the kit's default.
Frames are at 30 fps. "%W" and "%H" are shares of frame width and height; px values are given at 1080x1920.

## Contents
1. Story formula
2. Script and narration
3. Shots and camera
4. Characters
5. Acting
6. Sets, props and text
7. Look
8. Captions
9. Sound
10. Cover and title
11. Variants and the kit's default
12. Kit gaps, by priority

## 1. Story formula
- **Length:** 58 to 75 s. 181 to 218 words.
- **Hook (first 3 to 5 s):** the paradox in one flat declarative sentence, no question, no "imagine". The hero, the act and the contradiction are all said by 5 s (for example: "A lamplighter lit every lamp in town for forty years, and he was afraid of the dark."). A second-person variant works too: a two-word place tag, then the threat, with the viewer cast as the one who must act.
- **Build:** escalation in 2 to 4 visible steps, each one sentence, often a list of three actions. A count-up or countdown on a prop (100, 200, 300 / three minutes, two, one).
- **Plant and callback:** a line planted early comes back changed at about 70 % (a note's advice comes back as "Told you so.").
- **Twist:** lands at 45 to 70 % of the runtime and flips the meaning of the hook: the kind act was a cover, the model citizen was the culprit, the hero is the one on trial.
- **Hinge:** "You see," opens the explanation in all three references. The explanation runs fastest (3.5 to 3.8 words per second).
- **Ending:** a short restatement in fragments (a number, then what it means, two short sentences), a moral in one line, or a direct question cut off mid-sentence. The last line or the last frame runs back into the first one: every short is built to loop (the final frame equals the first frame, or the last words run into the first sentence).
- **Truth:** a real event framed as "you", or a fable told as an anecdote. Props invent names, places and dates. For these shorts: true or plausible, facts checked when claimed as real, and never a story another channel already told.
- **Devices:** numbers as refrains, lists of three, one-word punch lines ("Nothing."), antithesis in two short mirrored sentences, a single quoted line from an authority.

## 2. Script and narration
- **Pace:** 2.94 to 3.13 words per second overall, 3.35 to 3.40 while speaking. Lists, count-ups and the last line slow down to 2.2 to 2.7; escalations and explanations speed up to 3.6 to 3.9.
- **Sentences:** short, 6.7 to 10.4 words on average, many fragments. Linking words drive the pace: So, But, Then, Meanwhile, You see, Because.
- **Pauses:** only at sentence ends, 0.12 to 0.54 s. The longest pause sits before the hinge into the explanation. First word at 0.00 s.
- **Person:** third person past tense (fables) or second person present (the viewer is cast as the hero; every "you" acts on screen as the hero).
- **Voice:** one adult narrator, dry close-mic, no room, an energetic storyteller with a wide pitch range (13 to 20 semitones), the pitch dropping as the story turns grave. Deadpan and wry.
- **Quotes:** at most one or two quoted lines, given to a character on screen (police, judge, controller) who lip-flaps them.

## 3. Shots and camera
- **Shot count:** 39 to 48 shots for 58 to 75 s. Median shot 1.28 to 1.30 s, mean 1.49 to 1.59 s, shortest about 0.45 s, longest 3 to 6 s (a reveal). One clause or one beat per shot.
- **Holds:** every hold creeps inward: a straight dolly toward frame centre, no pan, no roll, full speed from the first frame. Median rate 0.08 to 0.34 % of scale per frame (0.08, 0.19 and 0.34 on the three references); deliberate punch shots push 1 to 1.6 % per frame.
- **Joins:** a hard cut changes place or subject; a camera move stays inside one world; a dissolve (5 to 8 frames) marks a jump in time, a new section or a step into the hypothetical. Every join lands on a caption pop: a hard cut falls on the key word of a new sentence (median 0.15 s after the sentence starts, the article is said over the old shot), a move starts about 0.2 s before the sentence it introduces.
- **Moves:** flights of 11 to 16 frames (fly-in pushes, fly-outs, dives from a wide down onto an insert, orbits, crane-ups, whip pans and tilts with heavy directional blur). Fly-ins ramp up late (`anim.IN`), fly-outs snap early and glide (`anim.OUT`).
- **Accelerate into the cut:** most hard cuts end a 6 to 19 frame acceleration of the outgoing camera (median +20 % of scale, ramping to +4 to 5 % per frame on the last frame), cut at peak speed.
- **Time budget:** about 71 to 73 % of the runtime in creeping holds, 13 to 21 % in transitions.
- **Camera height:** eye or chest level on characters; high, looking down, on desks, tables and rooms; low on crowds and towers; top-down on documents and objects; aerial with a long lens for towns and countryside.
- **Lens:** medium-long on characters (about 40 to 46 mm equivalent, heads never distorted), wider only to establish a room, long and flat for aerials and cutaways.
- **Inserts:** 10 to 12 of every 40 shots are inserts with no face: hands, documents, screens, keys, coins. Every spoken number and every story-critical word appears on an in-world prop when it is said (screens, scoreboards, ledgers, chalk boards, calendars, newspapers). Text and counts live on props, never as on-screen graphics.
- **Devices worth reusing:** dive with roll into a top-down insert; foreground pass-overs and over-the-shoulder blurred heads; background life (a tram crossing); a look straight into the lens for the last line; screen geography kept (one place always on the left, the other always on the right); a cutaway cross-section that travels (down, across, up).

## 4. Characters
- **Body:** one shared bean or pill body with the costume modelled on it (coat with a bell skirt, dress, uniform, suit); no neck; small black ball feet or dark shoes; thin solid black stick limbs, no outline of their own.
- **Head:** a ball at one scale for everyone. Age and size come from body height, hair and costume, never from wrinkles. Children: shorter body, same head.
- **Face:** painted marks in mid grey (luma about 95 to 125), never ink black: lidded eyes with a half pupil under a straight lid (the default), round ring eyes with dot pupils for surprise and fear, heavy brows, a mouth line. No nose, no ears, no lashes. Facial hair marks authority or age (moustache, goatee, walrus moustache).
- **Hands:** ball mitts with no thumb. White mitts are the hero's signature; everyone else wears black mitts. `chars.py`: `mitts='white'` on the hero spec only.
- **Hair:** a dark hair band hugging the skull under any hat (all hatted men), buns, topknots, side buns for girls, white wavy hair for the elderly.
- **Costume colours:** one saturated identity colour per character (teal, red, ochre, lime, sky blue), muted world around them.
- **Extras and crowds:** the same body with swapped coat colour, hat and hair; backs to the camera when no face is needed; one shared expression per beat for a crowd; up to 6 to 15 hand-placed people, instanced grids of hundreds for stadiums.
- **People per shot:** median 1. About a quarter of the shots have nobody (inserts, places).

## 5. Acting
- **Expressions used:** smug (the hero's default), smile, happy, laugh, surprised, shocked, worried, sad, angry, skeptical (one brow up), scared, thinking (eyes aside), sleepy, determined, embarrassed, talking. Also: wink (a good signature beat for a hero), star eyes, crying with tear streams, gritted teeth, toothy grin, bored half lids, one-eye peek, evil grin, deadpan stare into the lens. Add-ons: sweat drop, blush.
- **Expression swaps:** a change of expression hides behind a one-frame closed-eye frame. Blinks take 2 to 3 frames (half, closed, half); frequency varies from rare to one every 0.7 to 0.8 s on face holds, more for nerves.
- **Talking:** only a character who speaks a quoted line lip-flaps it: 3 to 6 mouth shapes switching every 1 to 4 frames, not phoneme-accurate. Everyone else keeps a fixed mouth.
- **Bodies:** characters stay planted; acting is in the face, a head turn and one arm. Short walks of 2 to 3 steps; full walk cycles only when travel is the point (8 to 10 frames per cycle). Reactions are fast and in steps: squint 5 frames, look down 4, shocked hold 16.
- **Gestures:** hat tip, point with an index finger, hold up an object to camera (paper, key, clipboard), toss, write, press, file, drop into a slot or sack, turn around, head turn to camera, hand to cheek, hands on head (panic), hand over mouth (giggle), hands behind the head (relaxed), rub hands (scheming), count on fingers, wave, cheer with arms up, shrug with palms up, sit at a desk, sip, mop, crawl, sleep on one side.

## 6. Sets, props and text
- **Sets:** heavily dressed, 8 to 20 props per set, each with at least one readable joke sign that comments on the scene (a sign that says the opposite of what is happening, an arrow pointing the wrong way). Old-European small-town streets, offices, kitchens, courtrooms, cells, banks, cockpits, studios; interiors in mint, teal, cream and wood; exteriors in brick, painted shopfronts, striped awnings, cobbles.
- **Text:** English, bold capitals sans for signs and labels, engraved serif for institutions (banks, courts), old-style serif mastheads for newspapers, blue cursive for handwritten notes, chalk caps on boards. Every story-critical word is legible at phone size.
- **Effects:** 4-point white sparkle glints on metal, gold and keys; light sweeps; steam; sweat drops; Zzz and music-note symbols; tear streams; star eyes; flying pages; chalk numbers that pop with the caption curve; candle and lamp glows with light shafts; smoke and flame for disasters; flashing police lights; screen glow and scanlines; number tickers and bar fills synced to words. No weather in any of the three references.
- **Vehicles:** simple, low to medium detail, thin ink (tram, taxi, police car, airliner, fighter jet).

## 7. Look
- **Grade:** one grade per place and time, not one global grade. Day streets neutral-green and soft (median luma 0.43); warm interiors amber (0.45 to 0.52); offices teal and high key (0.51); dusk with a warm ground and a violet sky only (0.34); night violet-blue with warm practical lights and faces still white (0.20 to 0.40); courts the most saturated (chroma up to 0.30). Highlights blow only on lamps and the sun.
- **Ink:** a thin near-black line on characters, sets and props, about constant on screen: 4 to 5 px at 1080 on characters in mid shots, 6 to 8 px in close-ups, 2 to 4 px on sets; far geometry and aerial fields carry almost none. Head outline the darkest line on the figure. Face marks are grey fills, not ink.
- **Depth of field:** shallow on close-ups and inserts (background 3 to 5 times softer than the subject), deep on wides and aerials. Foreground objects go strongly out of focus.
- **Vignette:** strong top and bottom fall-off in two of three references (edges at 0.5 to 0.7 of the centre, corners 0.36 to 0.52); none in the third. The kit's `post.finish` vignette matches the first two.
- **Bloom:** soft halos on lamps, moons, windows, gold and white heads on dark backgrounds. Never over the ink.
- **Grain:** none. Matte materials; glints only on brass, gold and steel.
- **Motion blur:** strong and directional on every flight and whip; fast hands smear too.

## 8. Captions
- **Type:** heavy sans (Arial Black or a rounded geometric equivalent), white fill, hard black outline about 5 to 6 px at 1080, a tight soft shadow. One line, centred, text centre at 0.70 to 0.705 H (baseline 0.713 to 0.717 H).
- **Size:** cap height about 2 % H (two of three references); 3 % in the third. The kit's `post.caption`: Arial Black 53 px at 1080.
- **Grouping:** 1.4 to 1.65 words per caption: half single words, a function word always rides with the next word ("a key", "he said"), at most 3 to 5 words on a long fragment. Case and punctuation follow speech; digits for numbers; curly quotes for quoted lines.
- **Timing:** each caption pops with its first word (0 to +2.4 frames), stays until the next, about 0.47 s each; no gaps. After a hard cut the next caption comes 1 frame later.
- **Animation:** a scale pop with overshoot in two of three references: 0.82 to 0.88, then 0.95 to 1.0, then 1.03 to 1.04, settled at 1.0 by frame 4. No fade, no colour emphasis, no keyword highlight, no emoji.

## 9. Sound
- **Voice on top, music under everything:** a continuous music bed from 0 s to the end, 10 to 20 dB under the voice: a quiet mystery or storybook underscore (sustained pad, bell-like partials, low bass notes, sometimes a slow pulse around 78 BPM). No intro, no outro, no change at the twist; a sustained chord on the last line.
- **Sound effects:** sparse, about one every 2 to 4 s, each tied to a visual beat: whooshes on flights and whips, coin tings, twinkles on sparkles and star eyes, bell tolls, lock clicks, gavel hits, crowd laughter and cheers, alarm beeps, sirens, UI blips on screens. Mixed from 5 to 15 dB under the voice. Use effects you made or that are licensed for reuse.
- **Punch lines:** a hard mute of the whole mix (0.15 to 0.2 s) just before a punch line works.
- **Loudness:** the references run from -16.8 to -8.4 LUFS. The kit: mix at -9 LUFS, true peak -1 dBTP (`pp/mix.py`).

## 10. Cover and title
- **Title:** "The [Role] Who [Act]", or "He [paradoxical wish] [number]!". The title sells the hook's paradox and hides the twist. 5 to 9 words, Title Case, no emoji.
- **Cover:** a frame of the video itself, not a designed thumbnail: the most characterful expression of the hero (a wink, tears, anger), one character, centred, on a readable set, no added text. YouTube places it in a 16:9 frame with blurred sides.

## 11. Variants and the kit's default
| | Reference A | Reference B | Reference C | Kit default |
|---|---|---|---|---|
| Heads | white | white | skin tones (5 or more) | white, very white |
| Hands | hero white mitts, others black | black mitts | skin-coloured balls | hero white, others black |
| Arms | thick black sticks | black sticks | thin, sleeve-coloured | thick near-black sticks |
| Joins | flights | hard cuts and whips | 5-frame dissolves and whip-slides | flights in one world, hard cuts between places, dissolves for time |
| Caption pop | yes | yes | no | yes |
| Vignette | strong | strong | none | strong |
| Loudness | -16.8 LUFS | -11.9 | -8.4 | -9 |
Any switch to variant C (skin tones, ball hands, coloured arms) is the user's decision: ask before building it.

## 12. Kit gaps, by priority
1. **Costumes and hair:** uniforms (police tunic and peaked cap, guard, pilot flight suit and helmet), robes (judge), suits with shirt and tie, sweaters and cardigans, nightcap and pyjamas, fedora and pork-pie hats, helmet hair, buns, topknots, white elderly hair, glasses, moustache and goatee variants, child proportions.
2. **Faces:** ring eyes set (surprised, hopeful, scared, goggle grin), wink, star eyes, crying with tears, gritted teeth, toothy grin, deadpan to lens; sweat drop and blush overlays; a lip-flap set of about 6 mouths.
3. **Actions:** hold up to camera, toss, write, press, drop into a slot, turn around, head turn to lens, hands on head, hand over mouth, hands behind head, rub hands, count on fingers, sip, sleep on one side, crawl, seated at a desk, crowd cheer and laugh.
4. **Camera:** whip pan and tilt (10 to 16 frames, heavy blur), dive with roll into top-down, orbit, crane-up, lateral truck, a final shot that lands on frame 0 for the loop.
5. **Sets:** office (police or manager), kitchen at night, newsstand, clock tower and night sky (moon, stars), aerial town grid, courtroom, cell and cell block, bank vault, cockpit, TV studio, living room. Each built from `look` primitives with readable joke signs.
6. **Props and effects:** newspaper with headline, tear-off calendar, chalk board with popping numbers, screens with tickers and bars, sparkle glints, steam, light shafts, flashing lights, smoke and flame.
7. **Sound:** a small effects library (whooshes, tings, twinkles, bells, clicks, hits, crowd, beeps, siren) and a quiet mystery bed.
