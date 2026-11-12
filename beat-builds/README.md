# THE BEAT BUILDS ITSELF

`the-beat-builds-itself.mp4`: 45s, 1080×1920, 30 fps, H.264/AAC (about −13 LUFS). No narration; the only text is the opening hook.

**Soundtrack: generated.** No music file was supplied, so `music.py` builds an original 86 BPM D-minor instrumental in separate layers that really do enter one at a time: kick, snare, hi-hats, bass, electric-piano chords, the synth melody, then the full groove (crash, shaker, pad, harmony). Then they drop out in order and a final chord rings into the rain. There are no samples and no vocals.

| File | What it does |
|---|---|
| `config.py` | Tempo map (86 BPM, bar grid from 4.00s), section entrances, harmony, palette, layout and camera keyframes |
| `music.py` | Synthesizes each layer, mixes them, and writes `events.json` with every kick, snare, hat, bass note, chord and melody note |
| `events.json` | The event list that drives the animation, so motion is synced to the actual audio |
| `beat.py` | Deterministic renderer. `--preview` renders at 540×960 and `--frames N ...` renders stills |

Sync, verified on exact frames: the turntable's beater and rim glow fire on every kick, the pencil hits the desk on every snare, a droplet lands on the sill on every hi-hat, the amp light turns on at the frame the bass enters, chord hits press the keys and light a zone of the room, and each melody note pulses the synth LED and sends a waveform along the cable.

```bash
python3 music.py beat.wav events.json
OT_FONTS=/path/to/fonts python3 beat.py video.mp4 [--preview]
ffmpeg -i video.mp4 -i beat.wav -map 0:v -map 1:a -af loudnorm=I=-14:TP=-1 -c:v libx264 -crf 21 -c:a aac -b:a 256k out.mp4
```
