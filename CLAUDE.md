# NO WAY. — standing rules for every video

These rules apply to every episode and override an episode prompt when they conflict. Full workflow: `.claude/skills/no-way-episode/SKILL.md`. Style guide: `HOW-I-MAKE-VIDEOS.md`. Idea queue and series numbers: `IDEAS.md`.

## What stays the same
- Every video is built entirely in code: Python/PIL/numpy animation, the `molasses-flood/` grade, captions and audio synths, and the `zanzibar-war/` helpers. The render pipeline (frames piped to ffmpeg, `JOBS=4`) is unchanged.
- Narration is Kokoro TTS, voice `am_onyx`. Use speed 1.05–1.12 for Shorts and about 0.88 for long form.
- **Never include "Yep." or "It happened."** in the voiceover, captions or on-screen text, even if a prompt asks. The last spoken words are "No way." over the NO WAY. wordmark, unless a prompt explicitly asks for no spoken catchphrase.
- Shorts are 1080×1920 and long form is 1920×1080. Both are 30 fps, H.264/AAC, −14 LUFS, and under 100 MB.
- One video per folder, holding the MP4, its source, a README and `sources.md`. Add each new video to the table in `README.md`.
- No real likenesses, logos, game art or photos. Use generic figures and the show's own type, and label any reconstruction as one.

## Idea process
- **Never brainstorm ideas from memory. Research first.** Sources to research from:
  - Wikipedia's "Unusual articles" and the "List of unusual deaths" sublists
  - Atlas Obscura, Damn Interesting and Smithsonian
  - Old newspaper archives: Chronicling America and Papers Past
  - The `no-way-ideas` skill, when it's available, applying these rules
- **Skip overdone topics** unless there's a genuinely new angle: the Emu War, the Dancing Plague, the Mary Celeste, basic Tesla, Phineas Gage.
- **Score each idea 1–5** on five criteria, and only make ideas that score **20/25 or more**. Record the score in the video's README.
  - **Hook:** the weird part fits in under 10 words.
  - **Escalation:** it gets stranger at least twice.
  - **Payoff:** it ends on a twist or a loop.
  - **Animatability:** how well it works in code.
  - **Freshness.**
- **Every fact needs at least one solid source.** Put the sources in `sources.md` next to each video, as claim → source link. Disputed claims get hedged on screen ("allegedly", "per X", "disputed") and noted in `sources.md`.

## Video structure (Shorts, 30–50s)
1. **0–1s: the hook is on screen and spoken at the same moment.**
   - The hook text is visible from frame 0, with no fade-in, and narration starts by about 0.1s.
   - No intro, no logo, no "did you know".
   - Don't open with "No way…" as filler. Open on the weird claim itself.
2. **Three beats, each stranger than the last.** A new visual every 2–3 seconds: a cut, a new element, a counter or a camera move. No shot holds longer than 3s.
3. **The ending loops.**
   - The final story line leads back into the hook, so a rewatch feels natural.
   - Then a short "No way." (under 1s) plays over the wordmark.
   - The last frame matches or dissolves into the first frame's composition.
4. **Burned-in captions: big, centered and in the safe zone.**
   - Keep clear of the bottom 20% (y > 1536) and the right edge, where the Shorts buttons sit (keep the right 150px clear).
   - `mf.caption_layer` enforces this with `CAP_Y` and `CAP_MAX_W`.
   - Key art and labels also stay out of those zones.
5. **Lean into what code does best. These are the brand look:**
   - counters ticking up
   - maps with spreading pulses
   - timelines
   - price charts
   - before/after splits

## Series format
- Every Short belongs to a numbered series, shown on screen as a small tag (e.g. "FORGOTTEN ATTACKS #1"). The tag sits in the top safe area for the whole video and stays out of the hook's way.
- Track series numbers in `IDEAS.md`. Starting series:
  - America's Forgotten Attacks
  - Petty Crimes, Massive Damage
  - Numbers That Shouldn't Be Real
  - Black Markets for Normal Things
  - Countries That Didn't Last
  - Deaths That Shouldn't Happen

## Long-form tie-in
- When a Short performs well, plan a long-form version (follow `molasses-long/` and `tesla-long/`).
- Cut extra Shorts from each long-form video. Those Shorts end with the on-screen line "FULL STORY ON THE CHANNEL" before the wordmark.
