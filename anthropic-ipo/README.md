# NO WAY. — The $1.5 Trillion Breakup

`no-way-anthropic-ipo.mp4`: 73s, 1080×1920, 30 fps, H.264/AAC, −14 LUFS. Ends on "No way." with the NO WAY. wordmark.

Dario and Daniela Amodei left OpenAI in late 2020 and co-founded Anthropic in 2021. Anthropic priced its IPO at $83 a share on November 18, 2026, and began trading on Nasdaq as ANT on November 19.

## Fact-check notes (checked November 20, 2026)
- **The departure:** reported as announced in late December 2020. Anthropic was founded in 2021. The script said "In 2021 they left", so the video says "late 2020".
- **SBF:** FTX/Alameda put about $500M into Anthropic in 2022, as non-voting shares. That stake was later sold off after FTX collapsed.
- **Amazon** invested $8B in total by November 2024. **Google** has invested billions, but reported totals vary, so the video just says "billions".
- **The IPO:** priced at $83, above the $70–78 range. The roughly $1.5 trillion figure is the fully diluted valuation at the IPO price. The stock closed its first day at about $97, about $1.76T per CNN. The video says "around $1.5 trillion" and labels it "valuation at the IPO price".
- **"Biggest IPO":** CNBC called it the largest offering on record, ahead of SpaceX.
- **Voting control:** a Founder LLC owned by all **seven** co-founders holds a Class F share carrying 50.1% of the general vote. A Long-Term Benefit Trust elects most of the board. The script said "the founders", and the video says "its seven co-founders".
- **Visuals:** people are generic shapes with name labels. There are no company logos, and names are set in the show's own type.

## Files
- `ipo.py`: the scenes. "$1.5 TRILLION" cracked by "A BREAKUP"; two figures leaving an "OPENAI" building ("LATE 2020"); a safety core with a "FOUNDED 2021" stamp; the early investor with ~$500M and an "FTX COLLAPSED" stamp; investment bars and "CLAUDE VS CHATGPT"; a Nasdaq board ("ANT $83.00") and "~$1.5 TRILLION"; a 50.1% voting pie for the seven co-founders; 2021 → 2026 and the wordmark.
- `audio_ipo.py`: an original score that builds into a driving pulse for the listing, plus a crack, stamps, a price ding and a braam on the valuation.
- `voices/`: narration (Kokoro TTS, `am_onyx`, speed 1.12).

```bash
OT_FONTS=/path/to/fonts python3 ipo.py video.mp4
python3 audio_ipo.py mix.wav
ffmpeg -i video.mp4 -i mix.wav -map 0:v -map 1:a -af loudnorm=I=-14:TP=-1.5 -ar 48000 -c:v libx264 -crf 24 -c:a aac -b:a 192k out.mp4
```
