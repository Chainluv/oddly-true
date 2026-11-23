# NO WAY. — America's Forgotten Attacks #1: The Day Germany Bombed New Jersey

`no-way-black-tom.mp4`: 48s, 1080×1920, 30 fps, H.264/AAC, −14 LUFS. This is the first video made under the new structure: the hook on frame 0, three escalating beats, a looping ending and a series tag.

**Idea score: 23/25.** Hook 5 · Escalation 4 · Payoff 5 · Animatability 5 · Freshness 4.

At 2:08 a.m. on July 30, 1916, German saboteurs blew up the munitions depot on Black Tom Island in Jersey City. The blast was felt in Philadelphia and broke windows up to 25 miles away. Shrapnel hit the Statue of Liberty, and the torch has been closed to the public ever since. Germany was found responsible in 1939, and the last payment came in 1979. All claims and sources are in `sources.md`.

## Structure
1. **0–3.7s, the hook (on screen from frame 0):** "WHY YOU CAN'T GO UP THE TORCH", the statue and a padlock.
2. **Beat 1, the attack:** the 2:08 clock, then a harbor schematic (Black Tom next to the statue), with the munitions and "GERMAN SABOTEURS".
3. **Beat 2, the scale:** the flash and fireball with a 2,000,000 lbs counter, a shockwave map pulsing out to Philadelphia with a 25-mile ring, a seismograph (~M5), and a 1914–1917 timeline showing the U.S. wasn't at war yet.
4. **Beat 3, the twist:** shrapnel hits the statue and "TORCH CLOSED SINCE 1916". A payment timeline runs 1916 → 1939 ("GERMANY RESPONSIBLE") → 1979.
5. **Loop:** "63 YEARS TO PAY FOR ONE NIGHT", back to the torch with "No way." on the wordmark, then a dissolve into frame 0.

## Files
- `tom.py`: the renderer (stylized regional map, statue silhouette, padlock, series tag, loop dissolve)
- `audio_tom.py`: an original drone, strings and piano score; a clock; the blast and rumble; shockwave whooshes; a seismograph scratch; shrapnel pings; a stamp
- `voices/`: narration (Kokoro TTS, `am_onyx`, speed 1.12)
- `sources.md`: each claim with its source, plus notes on disputed details

```bash
OT_FONTS=/path/to/fonts python3 tom.py video.mp4
python3 audio_tom.py mix.wav
ffmpeg -i video.mp4 -i mix.wav -map 0:v -map 1:a -af loudnorm=I=-14:TP=-1.5 -ar 48000 -c:v libx264 -crf 25 -c:a aac -b:a 192k out.mp4
```
