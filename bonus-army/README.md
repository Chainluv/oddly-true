# NO WAY. — America Sent Troops Against Its Own Veterans

`no-way-bonus-army.mp4`: 65s, 1080×1920, 30 fps, H.264/AAC, −14 LUFS. Serious tone, with no punchline.

In 1932, thousands of World War I veterans (the "Bonus Army") came to Washington asking for early payment of a service bonus. Their certificates were not payable until 1945. The House passed early payment and the Senate rejected it. On July 28, after a deadly clash with police, federal troops cleared the camps with tear gas, and shelters burned. In 1936, Congress authorized early payment over President Roosevelt's veto.

- `bonus.py`: the scenes (veterans facing troops with the Capitol behind; the road to Washington; a closed store and shrinking savings; a "PAYABLE: 1945" certificate with a 1932–1945 timeline; the camp with "HOUSE: PASSED" and "SENATE: REJECTED"; July 28, shown first as a tense police line and then as a separate troop clearance with tear gas and fire; the ruins; the 1936 bill with "VETO OVERRIDDEN" and "EARLY PAYMENT AUTHORIZED"; and the closing "A CRISIS OF TRUST" over the certificate and Capitol). Every document is labeled as an illustrative reconstruction. There are no casualty counts, quotations or invented headlines.
- `audio_bonus.py`: an original low drone and strings score, tension strings for July 28, sparse piano, and restrained effects (boots, gas hiss, fire). All of it is synthesized with `../molasses-flood/audio.py`.
- `voices/`: narration lines (Kokoro TTS, `am_onyx`). Per `CLAUDE.md`, it ends on "No way."

```bash
OT_FONTS=/path/to/fonts python3 bonus.py video.mp4
python3 audio_bonus.py voices mix.wav
ffmpeg -i video.mp4 -i mix.wav -map 0:v -map 1:a -af loudnorm=I=-14:TP=-1.5 -c:v libx264 -crf 25 -c:a aac -b:a 192k out.mp4
```
