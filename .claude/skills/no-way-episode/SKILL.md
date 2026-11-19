---
name: no-way-episode
description: Make a NO WAY. episode (strange-but-true history short, skit, news short or long-form video) fully in code, with procedural animation, Kokoro narration and synthesized audio. Use whenever the user sends a script or topic for a new video, or asks to remake, lengthen or re-cut an existing episode.
---

# Making a NO WAY. episode

Read `CLAUDE.md` (standing rules) and `HOW-I-MAKE-VIDEOS.md` (style guide) first. The rules always win over the episode prompt.
- Never use "Yep." or "It happened." End on "No way." with the wordmark.
- Shorts are vertical 1080×1920, 30 fps, −14 LUFS.

## 0. Set up the environment (the container may be fresh)
- **Fonts aren't in the repo.** Fetch them from npm into a scratch dir, then `export OT_FONTS=<dir>`:
  ```bash
  for p in anton unifrakturmaguntia old-standard-tt special-elite playfair-display oswald; do npm pack @fontsource/$p; done
  # untar each, then copy package/files/*.woff into the dir
  ```
- **Kokoro:** `pip install kokoro-onnx soundfile`, plus the `kokoro-v1.0.onnx` and `voices-v1.0.bin` model files. The call is `Kokoro(...).create(text, voice="am_onyx", speed=..., lang="en-us")`.

## 1. Fact-check
- Web-search every claim before building anything.
- Drop unsupported claims, or hedge them on screen: "per crew accounts", "by his own account", "MYTH".
- Write the notes into the episode README.

## 2. Narration (`<episode>/voices/`)
- One wav per line (n1, n2, ...). Spell out numbers for TTS, e.g. "nineteen sixty-two".
- Speed is about 1.05–1.12 for shorts and about 0.88 for long form.
- Measure each clip's length, then set the `NARR` start times with gaps of about 0.5–0.8s.

## 3. Renderer (`<episode>/<name>.py`)
Copy the structure of the most recent vertical episode, e.g. `arkhipov/ark.py`, `beer-flood/beer.py` or `gunther-1059/gunther.py`.
- Put `molasses-flood` and the helper folders on `sys.path`.
- `zw.LINES`, `zw.NARR`, `zw.DUR` and `zw.SPOKEN` feed `zw.build_chunks()`, which sets `mf.CHUNKS`. Set `mf.KEYWORDS` for the amber words.
- `SCENES = [(t0, t1, fn), ...]` with 0.3s crossfades. `frame()` does `grade(...)` and then `mf.caption_layer(t)`.
- **Layout:** captions sit around y 1300–1470 in portrait, so keep key art and labels above about 1250 or below about 1560. The subtitle box in 16:9 is at y 958–1036.
- **Known gotchas:** cast PIL boxes to int, sort rectangle coordinates, skip drawing text whose alpha is about 0, and keep dark art light enough to see.
- Reusable helpers:
  - `zanzibar-war/episode.py`: headline, dark_bg, build_chunks, draw_clock
  - `rap-grammy/grammy.py`: stamp
  - `eiffel-con/eiffel.py`: man, papers
  - `bonus-army/bonus.py`: groups, soldier, smoke_layer
  - `tesla-name/tesla.py`: roadster, figure, motor
  - `skit-detailer/skit.py`: face rig

## 4. Preview
- Run `python <name>.py <prefix> <frame> <frame> ...` to write PNGs.
- Make a contact sheet and look at it. Fix collisions before the full render.

## 5. Audio (`<episode>/audio_<name>.py`)
- Use the `molasses-flood/audio.py` synths: drone, tremolo_strings, piano, boom, braam, thump, heartbeat, whoosh, clang, paper_slap, wind and reverb, plus effects specific to the episode.
- Process the voice with a high-pass and a little presence, then tanh. Duck the bed under the voice.

## 6. Render and deliver
```bash
JOBS=4 python <name>.py video.mp4      # run in the background (~6 min for 50s)
python audio_<name>.py mix.wav
ffmpeg -i video.mp4 -i mix.wav -map 0:v -map 1:a -af loudnorm=I=-14:TP=-1.5 -ar 48000 \
  -c:v libx264 -preset slow -crf 24 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart <episode>/no-way-<slug>.mp4
```
- Check: duration, ebur128 integrated loudness of about −14, size under 100 MB (raise the crf if needed), and a few frames from the final file.
- Add an episode README (fact-check notes, file list, commands) and a row in the root `README.md` table.
- Delete `__pycache__`, commit, push to the session branch, send the MP4 and give the GitHub link.
- Long form: follow `molasses-long/` and `tesla-long/` (story.py, narrate.py → timeline.json, chunked renders with --from/--to, an SRT, chapters).
