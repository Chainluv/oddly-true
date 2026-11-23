---
name: no-way-episode
description: Make a NO WAY. episode (strange-but-true Short, skit, news Short or long-form video) fully in code, with procedural animation, Kokoro narration and synthesized audio. Use whenever the user sends a script, topic or idea for a new video, asks for video ideas, or asks to remake, lengthen or re-cut an existing episode.
---

# Making a NO WAY. episode

Read these first; the rules always win over the episode prompt:
- `CLAUDE.md`: the standing rules, idea process, video structure and series format
- `HOW-I-MAKE-VIDEOS.md`: the style guide
- `IDEAS.md`: the queue and series numbers

## 0. Set up the environment (the container may be fresh)
- **Fonts aren't in the repo.** Fetch them from npm into a scratch dir, then `export OT_FONTS=<dir>`:
  ```bash
  for p in anton unifrakturmaguntia old-standard-tt special-elite playfair-display oswald; do npm pack @fontsource/$p; done
  # untar each, then copy package/files/*.woff into the dir
  ```
- **Kokoro:** `pip install kokoro-onnx soundfile`, plus the `kokoro-v1.0.onnx` and `voices-v1.0.bin` model files. The call is `Kokoro(...).create(text, voice="am_onyx", speed=..., lang="en-us")`.

## 1. Pick and score the idea (new ideas only)
- **Research, don't brainstorm from memory.** Use:
  - Wikipedia's "Unusual articles" and the "List of unusual deaths" sublists
  - Atlas Obscura, Damn Interesting and Smithsonian
  - Chronicling America and Papers Past
  - The `no-way-ideas` skill, if it's available
- Skip overdone topics (the Emu War, the Dancing Plague, the Mary Celeste, basic Tesla, Phineas Gage) unless there's a new angle.
- Score 1–5 each for hook (under 10 words), escalation (stranger twice), payoff (twist or loop), animatability and freshness. **Make only 20/25+.**
- Assign the series and the next number from `IDEAS.md`. A topic the user hands over (news, their own script) still gets a series if one fits. If none fits, say so and ask.

## 2. Fact-check and write `sources.md`
- Every claim needs at least one solid source. Write `<episode>/sources.md` as a list of claim → source link.
- Disputed claims get "allegedly", "per X" or "disputed" on screen, and a note in `sources.md`.
- Correct the user's script where the facts disagree, and tell them what changed.

## 3. Script (Shorts, 30–50s)
- **Line 1 is the hook,** the weird part in under 10 words, spoken from about 0.1s. Don't open with "No way…" as filler.
- **Then three beats,** each stranger than the last.
- **The last story line leads back into the hook,** so the loop works. Then a short "No way." (never "Yep." or "It happened.").
- Long-form cut-down Shorts add the on-screen line "FULL STORY ON THE CHANNEL" before the wordmark.

## 4. Narration (`<episode>/voices/`)
- One wav per line (n1, n2, ...). Spell out numbers for TTS, e.g. "nineteen sixty-two".
- Speed is about 1.05–1.12 for Shorts and about 0.88 for long form.
- Measure the clip lengths and set the `NARR` start times with gaps of about 0.4–0.6s. Total length is 30–50s.

## 5. Renderer (`<episode>/<name>.py`)
Copy the structure of a recent vertical episode, e.g. `bitcoin-overflow/btc.py`, `gta6-launch/gta.py` or `arkhipov/ark.py`.
- Put `molasses-flood` and the helper folders on `sys.path`.
- `zw.LINES`, `zw.NARR`, `zw.DUR` and `zw.SPOKEN` feed `zw.build_chunks()`, which sets `mf.CHUNKS`. Set `mf.KEYWORDS` for the amber words.
- `SCENES = [(t0, t1, fn), ...]` with 0.3s crossfades. `frame()` does `grade(...)` and then `mf.caption_layer(t)`.
- **Frame 0 shows the hook text at full opacity.** No fade-in on the first scene.
- **New visual every 2–3s:**
  - Inside a scene: add elements, counters or camera moves.
  - No shot holds longer than 3s.
- **Brand visuals:** counters ticking up, maps with spreading pulses, timelines, price charts, before/after splits.
- **Loop:** the last scene before the wordmark echoes the first frame's composition. After the wordmark, dissolve into the first scene's frame-0 image.
- **Series tag:** a small, persistent label in the top safe area (y ≈ 90–130, centered), e.g. "FORGOTTEN ATTACKS #1".
- **Safe zones:**
  - Captions are handled by `mf.caption_layer`: `CAP_Y` = 1300, `CAP_MAX_W` = W − 300, and the text auto-shrinks to fit.
  - Keep key art and labels out of the bottom 20% (y > 1536) and the right 150px.
  - Keep them out of the caption band, y ≈ 1230–1470.
- **Known gotchas:**
  - Cast PIL boxes to int, and sort rectangle coordinates.
  - Skip drawing text or lines whose alpha is about 0.
  - Glyphs such as ▲ ● × may be missing from the fonts.
  - Keep dark art light enough to see.
- **Reusable helpers:**
  - `zanzibar-war/episode.py`: headline, dark_bg, build_chunks, draw_clock
  - `rap-grammy/grammy.py`: stamp
  - `eiffel-con/eiffel.py`: man, papers, money
  - `bonus-army/bonus.py`: groups, soldier, smoke_layer
  - `tesla-name/tesla.py`: roadster, figure, motor
  - `skit-detailer/skit.py`: face rig
  - `gta6-launch/gta.py`: sunset skyline, runners, bar charts
  - `bitcoin-overflow/btc.py`: coins, chain blocks, code panel

## 6. Preview
- Run `python <name>.py <prefix> <frame> <frame> ...` to write PNGs, then make a contact sheet and look at it.
- Check:
  - Frame 0 has the hook.
  - No collisions, and the safe zones are respected.
  - The series tag is present.
  - The last and first frames loop.
- Fix problems before the full render.

## 7. Audio (`<episode>/audio_<name>.py`)
- Use the `molasses-flood/audio.py` synths (drone, tremolo_strings, piano, boom, braam, thump, heartbeat, whoosh, clang, paper_slap, glitch, pop, wind, reverb), plus `audio_eiffel.pluck` and `audio_ep.tick`.
- Hit sound on the first frame: the voice and the music start together.
- Process the voice with a high-pass and a little presence, then tanh. Duck the bed under the voice.

## 8. Render and deliver
```bash
JOBS=4 python <name>.py video.mp4      # run in the background (~6 min per 50s)
python audio_<name>.py mix.wav
ffmpeg -i video.mp4 -i mix.wav -map 0:v -map 1:a -af loudnorm=I=-14:TP=-1.5 -ar 48000 \
  -c:v libx264 -preset slow -crf 25 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart <episode>/no-way-<slug>.mp4
```
- Check: the duration (30–50s for Shorts), ebur128 integrated loudness of about −14, size under 100 MB (raise the crf if needed), and a few frames from the final file.
- Write an episode README (idea score, series and number, file list, commands) and `sources.md`.
- Add a row to the root `README.md` table and update the series numbers in `IDEAS.md`.
- Delete `__pycache__`, commit, push to the session branch, send the MP4 and give the GitHub link.

## Long form
- Follow `molasses-long/` and `tesla-long/`: story.py, then narrate.py → timeline.json, chunked renders with --from/--to, an SRT and chapters.
- Plan one when a Short performs well. Afterwards, cut 2–3 extra Shorts from it, each ending with "FULL STORY ON THE CHANNEL".
