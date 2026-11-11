# NO WAY. — He Died One Minute Before the Ceasefire

`no-way-gunther-1059.mp4`: 65s, 1080×1920, 30 fps, H.264/AAC, −14 LUFS. Serious, restrained, with no spoken catchphrase at the end.

On November 11, 1918, the armistice signed that morning stopped the fighting on the Western Front at 11 a.m. Henry Gunther, an American soldier from Baltimore, was killed in France at 10:59. He is generally recognized as the last American soldier killed in action in WWI.

- `gunther.py`: the scenes (10:59 above a lone silhouette with "CEASEFIRE: 11:00"; a stylized armistice document that dissolves into a clock; a stylized Western Front map and battlefield silhouettes with an inset clock; "HENRY GUNTHER — BALTIMORE, MARYLAND", where his silhouette stops at 10:59 and fades into mist with no close-up; the big clock reaching 11:00, then a hold in silence; "AGREEMENT: SIGNED / DEADLINE: 11:00"; "ARMISTICE DAY" flipping to "VETERANS DAY"; and a final card with his name, "10:59 A.M. — NOVEMBER 11, 1918" and a small NO WAY. beneath). The document and map are labeled as reconstructions. There are no signing times, casualty totals or quotations.
- `audio_gunther.py`: a restrained original drone and piano score, a ticking clock, and distant soft artillery. The music dips at 10:59, and everything falls to silence at 11:00 for about 3 seconds. There's no gunshot and no triumphant ending.
- `voices/`: narration lines (Kokoro TTS, `am_onyx`).

```bash
OT_FONTS=/path/to/fonts python3 gunther.py video.mp4
python3 audio_gunther.py voices mix.wav
ffmpeg -i video.mp4 -i mix.wav -map 0:v -map 1:a -af loudnorm=I=-14:TP=-1.5 -c:v libx264 -crf 25 -c:a aac -b:a 192k out.mp4
```
