# NO WAY. #6 — They Won the First Rap Grammy—and Boycotted the Show

`no-way-06-rap-grammy.mp4`: 20s, 1080×1920, 30 fps, H.264/AAC, −14 LUFS.
DJ Jazzy Jeff & The Fresh Prince won the first Best Rap Performance Grammy (1989) for "Parents Just Don't Understand". Because that award was left out of the TV broadcast, they joined a boycott and didn't attend. They still received the award. The Fresh Prince is Will Smith.

- `grammy.py`: the scenes (gold gramophone and stamped invitation, record sleeve and turntable, CRT TV with the category marked "NOT TELEVISED", performers turning away, the name flip and boombox). The silhouettes are generic, there is no archival footage and no invented dialogue.
- `audio_grammy.py`: an original synthesized 90 BPM boom-bap beat (no samples, nothing taken from the actual song) plus the shared mix chain from `../molasses-flood/audio.py`.

Narration: Kokoro TTS, voice `am_onyx`. Per `CLAUDE.md`, the video ends on "No way." without "Yep."

```bash
OT_FONTS=/path/to/fonts python3 grammy.py video.mp4
python3 audio_grammy.py /path/to/voice_wavs mix.wav
ffmpeg -i video.mp4 -i mix.wav -map 0:v -map 1:a -af loudnorm=I=-14:TP=-1.5 -c:v libx264 -crf 22 -c:a aac -b:a 256k out.mp4
```
