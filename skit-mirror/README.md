# NO WAY. skit — Mirror Check

`no-way-mirror-check.mp4`: 30s, 1080×1920, 30 fps, H.264/AAC, −14 LUFS.

A guy at the bathroom mirror slowly suspects his hair is thinning. It's an illustrated animation drawn in code, using the detailer skit's character style (clean-shaven). The beats are: the head rub and squint, a check from another angle, a long stare into his own eyes, a light-off "test", one dramatic sting when the light comes back on, the barber's call, a POV of his phone showing the top of his head, then a cut to black and a small NO WAY. logo.

- `mirror.py`: the shots, pose and lighting timing, phone UI and logo. It reuses `../skit-detailer/skit.py` (face rig, lip-sync, captions).
- `audio_mirror.py`: dialogue, with the barber filtered to sound like a phone line. The bed is quiet bathroom ambience (fan hum, faucet drips), with light-switch clicks, a phone ring and one sting. There's no music bed and no laugh track.
- `voices/`: dialogue clips (Kokoro TTS). The guy is `am_michael`, the barber is `am_fenrir`.

```bash
OT_FONTS=/path/to/fonts python3 mirror.py video.mp4
python3 audio_mirror.py mix.wav
ffmpeg -i video.mp4 -i mix.wav -map 0:v -map 1:a -af loudnorm=I=-14:TP=-1.5 -c:v libx264 -crf 22 -c:a aac -b:a 256k out.mp4
```
