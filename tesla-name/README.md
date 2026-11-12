# NO WAY. — Why Tesla Is Called Tesla—And Who Actually Named It

`no-way-tesla-name.mp4`: 45s, 1080×1920, 30 fps, H.264/AAC, −14 LUFS. Curious and conversational.

Martin Eberhard and Marc Tarpenning founded Tesla Motors in 2003, and Eberhard is credited with proposing the name. Elon Musk joined in 2004 as a major investor and is also recognized as a co-founder. The name honors Nikola Tesla, a pioneer of polyphase AC systems and induction motors. The original Roadster used an AC induction motor. That says nothing about later models, and the Roadster's motor reflects much later engineering.

- `tesla.py`: the scenes ("WHY TESLA?" with "ELON NAMED IT?" crossed out and "THE NAME CAME BEFORE HE JOINED."; a 2003/2004 timeline with stylized figures and the notes "name proposed by Eberhard" and "later also recognized as a co-founder"; an illustrated 19th-century workshop where a motor sketch becomes a simplified induction motor; a rotating magnetic field shown as an amber arc, with no lightning, turning a slightly lagging rotor, labeled "SIMPLIFIED"; the motor driving the original Roadster's rear wheels; and an old-style motor illustration dissolving into the car, with "OLD PRINCIPLE. NEW APPLICATION."). The car is a generic stylized sports car.
- `audio_tesla.py`: a subtle original pad and pluck pattern, a soft electrical hum, and a motor whine whose pitch follows the rotor speed. All synthesized.
- `voices/`: narration (Kokoro TTS, `am_onyx`). Per `CLAUDE.md`, it ends on "No way." without "Yep."

```bash
OT_FONTS=/path/to/fonts python3 tesla.py video.mp4
python3 audio_tesla.py voices mix.wav
ffmpeg -i video.mp4 -i mix.wav -map 0:v -map 1:a -af loudnorm=I=-14:TP=-1.5 -c:v libx264 -crf 24 -c:a aac -b:a 192k out.mp4
```
