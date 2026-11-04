# NO WAY. #5 — Oil Got So Cheap, Sellers Paid Buyers

`no-way-05-negative-oil.mp4`: 20s, 1080×1920, 30 fps, H.264/AAC, −14 LUFS.
On 20 April 2020 the expiring May 2020 WTI crude oil futures contract settled at −$37.63 per barrel. The voiceover rounds this to "negative thirty-seven dollars". Only that contract is meant, not all oil or pump prices, and the storage scene shows space running low, not every tank full.

- `oil.py`: the scenes (barrel and price board, traffic and storage tanks, contract, seller and buyer, barrel pile and garage). It reuses `../molasses-flood` (grade, captions) and `../zanzibar-war` (headline, backgrounds, caption timing).
- `audio_oil.py`: music, sound effects and voice mix, built with the synths in `../molasses-flood/audio.py`. All audio is original and synthesized.

Narration: Kokoro TTS, voice `am_onyx`. Lines `l1`–`l7` are listed in `oil.py`.

```bash
OT_FONTS=/path/to/fonts python3 oil.py video.mp4
python3 audio_oil.py /path/to/voice_wavs mix.wav
ffmpeg -i video.mp4 -i mix.wav -map 0:v -map 1:a -af loudnorm=I=-14:TP=-1.5 -c:v libx264 -crf 22 -c:a aac -b:a 256k out.mp4
```
