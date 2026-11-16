# NO WAY. — The Great Molasses Flood (long form, ~8:20)

`no-way-molasses-flood-long.mp4`: 1920×1080 (16:9), 30 fps, H.264/AAC, −14 LUFS, 8:21.
`no-way-molasses-flood-long.srt`: subtitle file to upload to YouTube as captions (the video also has burned-in subtitles).

Built from Derrick's 8-minute script, with these edits:
- **Fact fixes.** The unsourced ladder anecdote is replaced with the documented firehouse rescue (rescuers spent hours cutting through floorboards). "Some victims weren't found for months" now says one victim wasn't found for nearly four months (Cesare Nicolo).
- **Ending.** The video ends on "No way." per `CLAUDE.md`, and the outro call to action is generic ("watch another one next").
- **Chapters.** Each section opens with a chapter card (PART 1–7). Together with a storytelling-paced voice (0.78×), this brings the runtime to about 8:20.

Chapter start times for the YouTube description (from `timeline.json`):
0:00 Cold open · 0:31 Title · 0:34 The Tank · 2:02 The Perfect Storm · 3:05 The Wave · 4:14 The Trap · 5:11 The Cleanup · 5:45 The Blame Game · 7:02 The Legacy · 7:46 Outro

## Files

| File | What it does |
|---|---|
| `story.py` | The script: spoken text for the voice and display text for subtitles, plus pauses, chapter titles and pacing |
| `narrate.py` | Generates the narration (Kokoro TTS, `am_onyx`) and writes `timeline.json` (paragraph and sentence timings) |
| `long.py` | Renderer: one scene per paragraph (with sub-shots), chapter cards, subtitles, `--srt` export, and `--from/--to` for rendering in chunks |
| `audio_long.py` | Original synthesized score that follows the chapters, plus sound effects keyed to the timeline and the narration mix |

It reuses the molasses-flood engines (3D street and wave, tank, aerial map, film grade), the zanzibar-war clock, the rap-grammy stamp and the eiffel-con figures. The shared `common.py` frame size is now configurable through `OT_W`/`OT_H` (the default is still 1080×1920 for the shorts).

```bash
python3 narrate.py /path/to/kokoro_model_dir          # voices + timeline.json
OT_FONTS=/path/to/fonts python3 long.py video.mp4      # or --from 0 --to 126 in chunks
python3 long.py captions.srt --srt
python3 audio_long.py mix.wav
ffmpeg -i video.mp4 -i mix.wav -map 0:v -map 1:a -af loudnorm=I=-14:TP=-1.5 -c:v libx264 -crf 26 -c:a aac -b:a 192k out.mp4
```

All scenes are stylized reconstructions: no archival photos, documents or real headlines.
