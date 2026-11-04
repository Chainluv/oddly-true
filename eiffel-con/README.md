# NO WAY. #7 — He Sold the Eiffel Tower. He Didn't Own It.

`no-way-07-eiffel-con.mp4`: 20s, 1080×1920, 30 fps, H.264/AAC, −14 LUFS.
In 1925, Victor Lustig posed as a government official and got scrap dealer André Poisson to pay for supposed rights to dismantle the Eiffel Tower. No ownership changed hands and the tower was never dismantled. By the usual account the buyer was too embarrassed to report it, and Lustig's second attempt was less successful.

- `eiffel.py`: the scenes (tower and "SOLD" stamp, desk with "FAKE" papers, payment and a tower schematic with a scrap tag, suitcase exit, return and bolt). All paperwork is a stylized reconstruction with generic text. There is no price, quotation or archival document, and the figures are generic silhouettes.
- `audio_eiffel.py`: an original synthesized caper groove (pizzicato bass, snaps) plus the shared mix chain from `../molasses-flood/audio.py`.

Narration: Kokoro TTS, voice `am_onyx`. Per `CLAUDE.md`, it ends on a spoken "No way." without "Yep."

```bash
OT_FONTS=/path/to/fonts python3 eiffel.py video.mp4
python3 audio_eiffel.py /path/to/voice_wavs mix.wav
ffmpeg -i video.mp4 -i mix.wav -map 0:v -map 1:a -af loudnorm=I=-14:TP=-1.5 -c:v libx264 -crf 22 -c:a aac -b:a 256k out.mp4
```
