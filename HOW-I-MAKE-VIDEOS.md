# How I make my videos

**NO WAY.** tells strange-but-true stories. Every frame and every sound is generated in code. There's no stock footage, no real photos, no logos and no licensed music. The binding rules are in `CLAUDE.md`, and the idea queue and series numbers are in `IDEAS.md`.

## Ideas
- Every idea starts from research, never from memory. Good places to look:
  - Wikipedia's "Unusual articles" and "List of unusual deaths"
  - Atlas Obscura, Damn Interesting and Smithsonian
  - Chronicling America and Papers Past
- Skip overdone stories (the Emu War, the Dancing Plague, the Mary Celeste, basic Tesla, Phineas Gage) unless there's a new angle.
- Score each idea 1–5 on hook, escalation, payoff, animatability and freshness, and only make the 20/25+ ones.
- Every fact has a source, listed in the video's `sources.md`.

## Series
Every Short belongs to a numbered series with a small on-screen tag, e.g. "FORGOTTEN ATTACKS #1":
- America's Forgotten Attacks
- Petty Crimes, Massive Damage
- Numbers That Shouldn't Be Real
- Black Markets for Normal Things
- Countries That Didn't Last
- Deaths That Shouldn't Happen

## Structure (Shorts, 30–50 seconds)
1. **0–1s:** the hook is on screen and spoken at the same time. No intro, no logo, no "did you know."
2. **Three beats,** each stranger than the last, with a new visual every 2–3 seconds.
3. **A looping ending:** the last line leads back into the hook, then a short "No way." plays over the wordmark. The final frame flows into the first one.

## Style
- **Look:** vintage film (sepia with a little color kept, film grain, a vignette, a subtle camera shake) and bold condensed type in cream, amber and red.
- **Brand visuals:** counters ticking up, maps with spreading pulses, timelines, price charts, before/after splits.
- **People:** generic silhouettes, never real likenesses. Documents and maps are labeled as reconstructions.
- **Captions:** big, centered and burned in, word by word, with keywords in amber. They stay out of the bottom 20% and the right edge (the Shorts buttons).
- **Never "Yep." or "It happened."**

## Voice, music and format
- **Voice:** Kokoro TTS `am_onyx`, at speed 1.05–1.12 for Shorts and about 0.88 for long form.
- **Music:** an original synthesized score (drones, strings, sparse piano, booms on the big beats) plus effects that fit the story, ducked under the voice.
- **Format:** Shorts are 1080×1920 at 30–50s. Long form is 1920×1080 at about 8 minutes, with chapters and an SRT. Everything is 30 fps, −14 LUFS and under 100 MB.

## Long-form tie-in
- When a Short does well, plan a long-form version.
- Cut extra Shorts from the long-form, each ending with "FULL STORY ON THE CHANNEL."

## The steps
1. **Research and score** the idea, then confirm its series and number.
2. **Fact-check and write `sources.md`.** Hedge anything disputed.
3. **Script** a hook in under 10 words, three escalating beats and a looping ending, for 30–50s.
4. **Narration:** one Kokoro clip per line, measured to build the timeline.
5. **Scenes** in Python with a new visual every 2–3s, reusing the shared grade, captions and figures.
6. **Preview** key frames on a contact sheet. Check frame 0 (the hook is visible), the safe zones, the loop and the series tag.
7. **Sound:** score and effects built to the same timeline, with the voice mixed in.
8. **Render and mux:** loudnorm to −14 LUFS, then check the length, loudness and size.
9. **Publish:** each video gets a folder (MP4, source, README, `sources.md`), a row in the main README, and an `IDEAS.md` update. Then commit, push and share the link.
