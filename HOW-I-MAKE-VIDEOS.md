# How I make my videos

**NO WAY.** tells strange-but-true history stories. Every frame and every sound is generated in code. There's no stock footage, no real photos, no logos and no licensed music.

## Style
- A vintage film look: sepia with a little color kept, film grain, a vignette and a subtle camera shake.
- Bold condensed type (Anton/Oswald), cream text, with amber and red accents.
- The people are generic silhouettes, never real likenesses. Documents and maps are labeled as reconstructions.
- Word-by-word captions in the lower third, timed to the voice, with keywords in amber.
- The open is a hook with a big date or number. The ending is "No way." on the NO WAY. wordmark. There's never a "Yep." or "It happened."

## Length
- **Shorts:** vertical 1080×1920, usually 45–65 seconds (the default is 20s when no length is given).
- **Skits:** about 30 seconds.
- **Long form:** 16:9 1920×1080, about 8 minutes, with chapters, an SRT caption file and a 15-second end-screen hold.
- All formats: 30 fps, H.264/AAC, loudness −14 LUFS, and files under 100 MB.

## Voice
- Kokoro TTS, voice `am_onyx`: a deep, measured narrator.
- Speed is about 1.05–1.12 for shorts and about 0.88 for long form. A long video that drags gets more content, not a slower voice.
- Each line is its own clip, placed on a timeline with short pauses between lines.

## Music and sound
- An original synthesized score: low drones, tremolo strings, sparse piano, and booms and braams on the big beats.
- Sound effects match the story, such as sonar pings, depth charges, ticking clocks, crowds, fire and sparks.
- The music ducks under the voice, and the final mix is normalized to −14 LUFS.

## The steps
1. **Script:** get the topic or script, then fact-check every claim with sources. Drop anything that can't be supported, or hedge it ("per crew accounts", "by his own account", "myth").
2. **Narration:** generate one Kokoro clip per line and measure the lengths to set the timeline.
3. **Scenes:** write a Python renderer (PIL and numpy) that reuses the shared grade, captions and figures from earlier episodes. One scene per beat of the script.
4. **Preview:** render key frames into a contact sheet. Check that text doesn't collide with captions, everything is readable, and the ending is right.
5. **Sound:** write a script that builds the score and effects to the same timeline and mixes in the voice.
6. **Render and mux:** render frames in parallel into ffmpeg, add the audio, run loudnorm to −14 LUFS, and check the length, loudness and file size.
7. **Publish:** each episode gets its own folder (MP4, source and README with fact-check notes) and a row in the main README. Then commit, push and share the link.
