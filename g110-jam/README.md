# NO WAY. — Numbers That Shouldn't Be Real #1: The 12-Day Traffic Jam

`no-way-g110-jam.mp4`: 42.5s, 1080×1920, 30 fps, H.264/AAC, −14 LUFS. It follows the `CLAUDE.md` structure: the hook on frame 0, three escalating beats, a looping ending, the series tag and safe-zone captions.

**Idea score: 22/25.** Hook 5 · Escalation 4 · Payoff 4 · Animatability 5 · Freshness 4.

In August 2010, a jam on China National Highway 110 stretched more than 100 km and lasted about 12 days. Cars moved about 1 km a day, some drivers were stuck for five days, and locals sold water at up to 15 times the usual price. Road work had cut capacity in half on a road already carrying 60% more traffic than it was designed for, mostly coal trucks heading to Beijing. The claims, their sources and the script changes are in `sources.md`.

## Shot list
- **0–3s:** "THIS TRAFFIC JAM LASTED 12 DAYS" over a top-down jam, with a DAY 1 counter (on screen from frame 0).
- **3–7s:** trucks packing in while a distance ruler grows to 100+ km and 62+ miles.
- **7–11s:** a stylized Inner Mongolia / Hebei / Beijing map with the jam drawn as a red line along G110, and "AUGUST 14, 2010".
- **11–15s:** a car crawling along a 100 km bar: "1 KM / DAY".
- **15–18s:** "STUCK", the day counter running to DAY 5, and card games beside the trucks.
- **18–21s:** locals arriving with crates of water.
- **21–24s:** a price tag counting from ¥1 to ¥15, with a shake: "UP TO ¥15".
- **24–26s:** three noodle cups: "MORE THAN 3X".
- **26–32s:** a capacity bar dropping to 50% ("ROAD WORK") and a traffic bar overflowing to 160%.
- **32–36s:** coal trucks moving along the route "TO BEIJING".
- **36–39s:** the day counter running to DAY 12, the jam clearing, and "CLEARED: AUG 26".
- **39–42.5s:** back to the hook shot with "No way.", dissolving into frame 0.

## Files
- `jam.py`: the renderer (top-down road and trucks, ruler, stylized map with route animation, day counter, price tag, capacity bars, loop)
- `audio_jam.py`: an original pulsing score, engine idle, horns, counter ticks, a price hit, noodle pops, coal-truck rumble and whooshes
- `voices/`: narration (Kokoro TTS, `am_onyx`, speed 1.12)
- `sources.md`: each claim with its source, plus the changes from the original script

```bash
OT_FONTS=/path/to/fonts python3 jam.py video.mp4
python3 audio_jam.py mix.wav
ffmpeg -i video.mp4 -i mix.wav -map 0:v -map 1:a -af loudnorm=I=-14:TP=-1.5 -ar 48000 -c:v libx264 -crf 25 -c:a aac -b:a 192k out.mp4
```
