# NO WAY. skit — The Detailer's Worst Nightmare

`no-way-detailers-worst-nightmare.mp4`: 30s, 1080×1920, 30 fps, H.264/AAC, −14 LUFS.

An illustrated animation drawn entirely in code: no live-action footage, no AI video. It has a detailing shop, an SUV with hair and sand in the carpet, the detailer with his mouth synced to his voice, carpet close-ups with crash zooms, a phone-call bar, word-synced captions (the friend's lines in light blue) and a hard cut to the NO WAY. outro.

- `skit.py`: shots, characters, captions, phone UI and outro. Line timings are listed in `LINES`.
- `audio_skit.py`: the mix. The friend's voice is filtered to sound like a phone line; sound effects are a shop vac, phone ring, carpet sting, brush scrub and sand. Under it sits a quiet original lo-fi beat built from the rap-grammy drum synths.
- `voices/`: the dialogue clips (Kokoro TTS). Detailer is `am_michael`, friend is `am_puck`.

```bash
OT_FONTS=/path/to/fonts python3 skit.py video.mp4
python3 audio_skit.py mix.wav
ffmpeg -i video.mp4 -i mix.wav -map 0:v -map 1:a -af loudnorm=I=-14:TP=-1.5 -c:v libx264 -crf 22 -c:a aac -b:a 256k out.mp4
```
