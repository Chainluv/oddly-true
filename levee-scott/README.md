# NO WAY. — Petty Crimes, Massive Damage #1: He Flooded a Town to Keep His Wife Away?

`no-way-levee-scott.mp4`: 50s, 1080×1920, 30 fps, H.264/AAC, −14 LUFS. It follows the `CLAUDE.md` structure: the hook on frame 0, three escalating beats, a looping ending, the series tag and safe-zone captions.

**Idea score: 23/25.** Hook 5 · Escalation 4 · Payoff 5 · Animatability 5 · Freshness 4.

James Scott was convicted of breaking the West Quincy, Missouri, levee during the 1993 flood. The break flooded about 14,000 acres and closed the bridge to Quincy for 71 days. Witnesses say he wanted to strand his wife across the river so he could party. He got a life sentence, which was overturned; he was then convicted again at a retrial. His defense says the levee could have failed on its own, and he still denies it. Missouri prisons say he's scheduled for release in July 2028. **His guilt is disputed**, so the motive is always attributed to witnesses, and the video ends on "GUILTY?". The claims, their sources and the changes from the original script are in `sources.md`.

Pinned comment idea: "Guilty or scapegoat? 👇"

## Shot list
- **0–5s:** "HE FLOODED A TOWN / TO KEEP HIS WIFE AWAY? / ALLEGEDLY" over a dark river map (on screen from frame 0).
- **5–9s:** a "1993" stamp and a rising river gauge as the river widens.
- **9–15s:** a sandbag wall stacking; one bag is highlighted as "JAMES SCOTT, 23 · VOLUNTEER".
- **15–21s:** "JULY 16, 1993", the levee cracks, water spreads over the Missouri side with an acre counter to 14,000, the bridge goes dark, and "BRIDGE CLOSED · 71 DAYS".
- **21–26s:** a retro TV with a LIVE bug: "SAYS HE MOVED SANDBAGS" and "A POLICE SGT. GETS SUSPICIOUS".
- **26–32s:** a split map with "WITNESSES SAY", his wife on the Missouri side ("STRANDED?") and Scott on the Illinois side ("PARTY").
- **32–35s:** a gavel, "LIFE SENTENCE", 1994 struck through as OVERTURNED, then 1998 "CONVICTED AGAIN".
- **35–42s:** levee failures across the Midwest counting to 1,083, with dots popping along the rivers; "DEFENSE: IT COULD FAIL ON ITS OWN", then a "SCOTT DENIES IT" stamp.
- **42–45s:** a timeline: 1993 → 2026 first parole hearing → 2028 scheduled release.
- **45–50s:** "GUILTY?" with YES/NO buttons, then back to the opening map with "No way.", dissolving into frame 0.

## Files
- `levee.py`: the renderer (stylized river map, flood spread, sandbag wall, TV, split map, gavel, failure map, timeline, loop)
- `audio_levee.py`: an original score; rising water; sandbag thuds; the crack and rush; TV static; a gavel; popping dots; stamps
- `voices/`: narration (Kokoro TTS, `am_onyx`, speed 1.18)
- `sources.md`: each claim with its source, plus the changes from the original script

```bash
OT_FONTS=/path/to/fonts python3 levee.py video.mp4
python3 audio_levee.py mix.wav
ffmpeg -i video.mp4 -i mix.wav -map 0:v -map 1:a -af loudnorm=I=-14:TP=-1.5 -ar 48000 -c:v libx264 -crf 25 -c:a aac -b:a 192k out.mp4
```
