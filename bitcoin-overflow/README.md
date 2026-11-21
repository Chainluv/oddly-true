# NO WAY. — Someone Created 184 Billion Bitcoin

`no-way-bitcoin-overflow.mp4`: 53s, 1080×1920, 30 fps, H.264/AAC, −14 LUFS. Ends on "No way." with the NO WAY. wordmark.

On August 15, 2010, someone exploited a bug in Bitcoin's code. A transaction in block 74638 created 184,467,440,737.09551616 BTC, nearly 9,000 times the 21 million coins that can ever exist. A patched client (version 0.3.10) came out in about five hours. The patched chain overtook the bad one at block 74691, which erased the fake coins. Who did it is still unknown.

## Fact-check notes
- **The amount and how it happened:** from the Bitcoin Wiki's "Value overflow incident" (CVE-2010-5139). Two outputs of about 92.2 billion BTC each overflowed when summed, so the "inputs ≥ outputs" check passed. The on-screen code is a simplified reconstruction, not the original source.
- **The fix:** version 0.3.10, released within about five hours, is credited to Satoshi Nakamoto (announced on BitcoinTalk) working with other developers. The narration says "Satoshi Nakamoto, and others".
- **"Nearly nine thousand times":** 184.47 billion ÷ 21 million ≈ 8,784.
- **The creator:** still unknown, per Decrypt.

## Files
- `btc.py`: the scenes. A counter rolls up to 184,467,440,737 under raining coins; a 21,000,000 max-supply coin; "AUG 15, 2010" with a highlighted bug line; two outputs adding up until OVERFLOW and a "CHECK PASSED" stamp; block #74638 and the supply comparison; a five-hour clock, a hooded "?" for Satoshi Nakamoto and "PATCH: VERSION 0.3.10"; the chain split, where the honest chain wins and the fake coins are erased; "WHO DID IT: STILL UNKNOWN"; and the wordmark.
- `audio_btc.py`: an original synthesized score, coin clinks, a counter whir with a glitch on the overflow, a stamp, clock ticks, and whooshes.
- `voices/`: narration (Kokoro TTS, `am_onyx`, speed 1.12).

```bash
OT_FONTS=/path/to/fonts python3 btc.py video.mp4
python3 audio_btc.py mix.wav
ffmpeg -i video.mp4 -i mix.wav -map 0:v -map 1:a -af loudnorm=I=-14:TP=-1.5 -ar 48000 -c:v libx264 -crf 25 -c:a aac -b:a 192k out.mp4
```
