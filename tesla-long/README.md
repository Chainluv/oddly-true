# NO WAY. — Nikola Tesla: The Man vs. the Brand (long form, 8:06)

`no-way-tesla-long.mp4`: 1920×1080 (16:9), 30 fps, H.264/AAC, −14 LUFS, 8:06 (with a 15-second end-screen hold).
`no-way-tesla-long.srt`: captions to upload to YouTube.

The long version of the Tesla short. It covers the man who died broke in room 3327, his AC induction motor, the War of the Currents, Wardenclyffe and the slide into poverty, a myth-vs-fact chapter, and how his name returned on a car company in 2003, plus the tesla.com twist.

Chapters for the YouTube description:
0:00 Cold open · 0:38 Title · 0:40 The Immigrant · 1:44 The Motor · 2:29 The War of the Currents · 3:43 The Fall · 4:58 Myth vs. Fact · 6:02 The Name Returns · 7:28 Outro

## Fact-check notes
- **The Edison $50,000 bonus** comes from Tesla's own account. The video says so, and that some historians doubt it.
- **"Tore up a billion-dollar contract"** is treated as a myth. What's documented is the 1897 lump-sum buyout, about $216,000.
- **The 1943 Supreme Court ruling** struck down parts of Marconi's patent. It did not name Tesla the inventor of radio, so that's treated as a myth.
- **The death ray** is presented as a claimed design, with no evidence it was built.
- **Company history:** incorporated July 1, 2003 by Eberhard and Tarpenning, with the name credited to Eberhard. Musk led the 2004 Series A ($6.5M) and became chairman. The 2009 settlement recognizes five co-founders. tesla.com was held by Stu Grossman from 1992 and acquired in 2016; the $11M price is Musk's own figure. The company was renamed Tesla, Inc. in 2017.
- **Visuals:** the people are generic silhouettes and the documents are labeled as reconstructions. There are no company logos or real photos.

## Files
- `story.py`: the script (spoken and display text), pacing and chapters
- `narrate.py`: generates the narration (Kokoro TTS, `am_onyx`) and `timeline.json`
- `tesla_long.py`: the renderer, which reuses `../molasses-long/long.py` helpers and the motor and Roadster from `../tesla-name/tesla.py`. Supports `--from/--to`, `--frames` and `--srt`.
- `audio_tesla_long.py`: original synthesized score and effects, plus the narration mix
