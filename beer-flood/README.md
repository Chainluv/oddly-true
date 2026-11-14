# NO WAY. — London Was Flooded With Beer. Eight People Died.

`no-way-beer-flood.mp4`: 50s, 1080×1920, 30 fps, H.264/AAC, −14 LUFS. It opens in disbelief, then turns sober.

On October 17, 1814, a 22-foot wooden vat burst at Meux & Co.'s Horse Shoe Brewery in London. The escaping porter damaged other containers. Estimates of the total run up to 323,000 imperial gallons, which is an upper estimate. A wave reported at about 15 feet hit the crowded St Giles neighbourhood. Buildings were damaged, homes flooded, and eight people died.

- `beer.py`: the scenes. Porter surges between houses, reusing the molasses-flood 3D street-and-wave engine with its 1919 details (rails, signs, elevated railway) removed. A pull-back to a stylized London map marks only St Giles. Then come the brewery and a hooped vat with a "22 FEET" marker that ruptures and hits neighbouring containers, and "UP TO / 323,000 GALLONS / IMPERIAL • UPPER ESTIMATE". The wave heads into St Giles, followed by a building comparison ("15-FOOT WAVE", "REPORTED HEIGHT", labeled "ILLUSTRATION"). Damaged buildings and flooding basements are shown with no people, under "8 PEOPLE DIED." The video ends on "VAT FAILURE → CHAIN REACTION → FLOODED HOMES" and the brewery silhouette with "THE LONDON BEER FLOOD". Everything is a stylized reconstruction, and the liquid is dark brown porter with no foam.
- `audio_beer.py`: a subtle original score that lowers at "Eight people died", with hoop strain, splitting wood, rushing liquid and quiet aftermath wind. There's no party music or cheering, and all of it is synthesized.
- `voices/`: narration (Kokoro TTS, `am_onyx`). Per `CLAUDE.md`, it ends on "No way."

```bash
OT_FONTS=/path/to/fonts python3 beer.py video.mp4
python3 audio_beer.py voices mix.wav
ffmpeg -i video.mp4 -i mix.wav -map 0:v -map 1:a -af loudnorm=I=-14:TP=-1.5 -c:v libx264 -crf 25 -c:a aac -b:a 192k out.mp4
```
