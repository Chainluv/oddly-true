# NO WAY. — No Way One Man Stopped a Nuclear War

`no-way-arkhipov.mp4`: 50s, 1080×1920, 30 fps, H.264/AAC, −14 LUFS. Ends on "No way." with the NO WAY. wordmark.

October 27, 1962, during the Cuban Missile Crisis: US Navy destroyers dropped practice depth charges on the Soviet submarine B-59 to signal it to surface. The crew had lost contact with Moscow, and the captain, Valentin Savitsky, reportedly wanted to launch its nuclear torpedo. On that boat, launch needed the agreement of three senior officers. Flotilla chief of staff Vasili Arkhipov refused, and the sub surfaced. The Americans didn't know it was carrying a nuclear weapon.

## Fact-check notes
- **The officers' vote** comes from later crew and participant accounts. The video labels it "per later crew accounts".
- **The depth charges** were practice charges, meant as signals to surface. They were not attacks.
- **The figures** are generic silhouettes with no likeness of anyone, and the submarine and ships are stylized.

## Files
- `ark.py`: the scenes. "OCTOBER 1962"; a cross-section of destroyers dropping practice charges on a sub; a red-lit interior with "NO CONTACT: MOSCOW" and the nuclear torpedo; three officers voting YES, YES, NO; the sub surfacing; "ONE DECISION."; and the wordmark. It reuses the grade and captions from `molasses-flood`, plus helpers from `zanzibar-war`, `bonus-army` and `eiffel-con`.
- `audio_arkhipov.py`: an original drone and strings score, sonar pings, muffled depth-charge booms, a heartbeat under the vote, and a quiet piano resolve.
- `voices/`: narration (Kokoro TTS, `am_onyx`).

```bash
OT_FONTS=/path/to/fonts python3 ark.py video.mp4
python3 audio_arkhipov.py mix.wav
ffmpeg -i video.mp4 -i mix.wav -map 0:v -map 1:a -af loudnorm=I=-14:TP=-1.5 -c:v libx264 -crf 24 -c:a aac -b:a 192k out.mp4
```
