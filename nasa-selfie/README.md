# NO WAY. — Your Selfie Camera Has a NASA Origin Story

`no-way-nasa-selfie.mp4`: 61s, 1080×1920, 30 fps, H.264/AAC, −14 LUFS. Curious and lightly funny.

In the early 1990s, Eric Fossum's team at NASA's Jet Propulsion Laboratory developed the CMOS active-pixel image sensor ("a camera on a chip") to make spacecraft cameras smaller and more power-efficient. The technology moved into commercial products and helped make modern phone cameras practical. NASA didn't invent CMOS chips, the digital camera or the smartphone. The video names the phone's other parts as coming from "many other inventions".

- `nasa.py`: the scenes (a selfie, a push through the front camera into a pixel sensor, a reveal of a generic spacecraft; "EARLY 1990s — NASA / JPL" with a bulky camera shrinking beside a power-use meter labeled "CONCEPTUAL ANIMATION — NOT MEASURED DATA"; "ERIC FOSSUM + TEAM" with a pixel grid assembling on a chip, "CMOS ACTIVE-PIXEL SENSOR" then "CAMERA ON A CHIP"; a spacecraft-and-phone split screen sharing "SMALL / LOW POWER / GOOD IMAGES"; the chip becoming a phone camera, then a video call, a selfie and a food photo; the phone's parts with only the camera sensor marked "ROOTS IN SPACE RESEARCH"; and a probe imaging a distant world beside a phone counting up to "ATTEMPT 17"). The hook icons are drawn in code instead of emoji, and there's no real NASA footage or documents.
- `audio_nasa.py`: a subtle original space-ambient pad and arpeggio, plus shutter, interface-blip and whoosh effects. All of it is synthesized.
- `voices/`: narration (Kokoro TTS, `am_onyx`). Per `CLAUDE.md`, it ends on "No way." without "Yep."

```bash
OT_FONTS=/path/to/fonts python3 nasa.py video.mp4
python3 audio_nasa.py voices mix.wav
ffmpeg -i video.mp4 -i mix.wav -map 0:v -map 1:a -af loudnorm=I=-14:TP=-1.5 -c:v libx264 -crf 25 -c:a aac -b:a 192k out.mp4
```
