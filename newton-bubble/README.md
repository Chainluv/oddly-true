# NO WAY. #4 — Even Newton Got Burned

`no-way-04-newton-burned.mp4`: 20s, 1080×1920, 30 fps, H.264/AAC, −14 LUFS.
South Sea Bubble, 1720: Newton made early gains, bought back in, and took heavy losses. The chart is labelled illustrative and shows no prices, percentages or loss amounts.

- `newton.py`: the scenes (chart and Newton bust, stock certificate, coin stack, burst, apple and wordmark). It reuses `../molasses-flood` (grade, captions) and `../zanzibar-war` (headline, backgrounds, caption timing).
- `audio_newton.py`: music, sound effects and voice mix, built with the synths in `../molasses-flood/audio.py`. All audio is original and synthesized.

Narration: Kokoro TTS, voice `am_onyx`. Lines `l1`–`l9` are listed in `newton.py`.

```bash
OT_FONTS=/path/to/fonts python3 newton.py video.mp4
python3 audio_newton.py /path/to/voice_wavs mix.wav
ffmpeg -i video.mp4 -i mix.wav -map 0:v -map 1:a -af loudnorm=I=-14:TP=-1.5 -c:v libx264 -crf 22 -c:a aac -b:a 256k out.mp4
```
