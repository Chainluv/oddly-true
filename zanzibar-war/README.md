# NO WAY. #3 — The War That Lasted Less Than an Hour

`no-way-03-shortest-war.mp4`: 20s, 1080×1920, 30 fps, H.264/AAC, −14 LUFS.
Anglo-Zanzibar War, 27 August 1896. The script says "less than an hour", and the video shows no minute counter.

- `episode.py`: the scenes (clock, map, bombardment, clock stop, movie bar with the NO WAY. wordmark). It reuses the film grade, fonts, captions and typewriter labels from `../molasses-flood`.
- `audio_ep.py`: music, sound effects and voice mix, built with the synths in `../molasses-flood/audio.py`. All audio is original and synthesized, so it is cleared for every platform.

Narration: Kokoro TTS, voice `am_onyx`. Lines `l1`–`l7` are listed in `episode.py` (`LINES`, `NARR`).

```bash
OT_FONTS=/path/to/fonts python3 episode.py video.mp4
python3 audio_ep.py /path/to/voice_wavs mix.wav
ffmpeg -i video.mp4 -i mix.wav -map 0:v -map 1:a -af loudnorm=I=-14:TP=-1.5 -c:v libx264 -crf 22 -c:a aac -b:a 256k out.mp4
```
