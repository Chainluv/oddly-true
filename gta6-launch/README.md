# NO WAY. — GTA 6's $3.79 Billion Day

`no-way-gta6-launch.mp4`: 60s, 1080×1920, 30 fps, H.264/AAC, −14 LUFS. Ends on "No way." with the NO WAY. wordmark.

Grand Theft Auto VI launched on November 19, 2026, 13 years after GTA V. Take-Two reports $3.79 billion in day-one retail sales, which it calls a record for any entertainment launch, and 32.5 million copies sold before release.

## Fact-check notes (checked November 23, 2026)
- **$3.79B and "entertainment record":** Take-Two's own press release. The total includes pre-orders, and the video labels it "per Take-Two (retail, incl. pre-orders)".
- **32.5M copies before release:** Take-Two.
- **The lower estimate:** Sensor Tower estimated about $2.36B (about 24.5M units, pre-orders plus first day), as reported by the BBC. The narration rounds it to "around $2.4 billion". It's about 3× GTA V's day one.
- **GTA V:** about $800M on its first day in 2013, per NBC News and CNBC. $3.79B is about 4.7×, which the video calls "nearly five times".
- **Delays:** first planned for 2025, then moved to May 26, 2026, then to November 19, 2026.
- **The trailer:** Trailer 1 (December 2023) set the record for most-viewed non-music YouTube video in 24 hours.
- **Visuals:** no game art, screenshots, logos or characters. It uses a generic sunset skyline, generic figures and the show's own type.

## Files
- `gta.py`: the scenes. "$3.79B IN ONE DAY" over a sunset skyline; a year calendar flipping 2013 → 2026; the trailer record and the struck-through release dates with a "DELAYED TWICE" stamp; a crowd stampede; a day-one counter with an "ENTERTAINMENT RECORD" stamp; a stack of 32.5M pre-release copies; GTA V vs GTA VI day-one bars (~5×) and the Sensor Tower estimate; "13 YEARS OF WAITING. 1 DAY OF BUYING."; and the wordmark.
- `audio_gta.py`: an original synthwave-style score, cash clinks, calendar flips, crowd rumble, a counter whir and stamps.
- `voices/`: narration (Kokoro TTS, `am_onyx`, speed 1.12).

```bash
OT_FONTS=/path/to/fonts python3 gta.py video.mp4
python3 audio_gta.py mix.wav
ffmpeg -i video.mp4 -i mix.wav -map 0:v -map 1:a -af loudnorm=I=-14:TP=-1.5 -ar 48000 -c:v libx264 -crf 25 -c:a aac -b:a 192k out.mp4
```
