"""Generate narration clips with Kokoro (am_onyx) and write timeline.json (same as molasses-long) (paragraph + sentence timings)."""
import json
import os
import re
import sys

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import story as S  # noqa: E402

SPLIT = re.compile(r"(?<=[.?!])\s+")


def main(model_dir, regen=True):
    vdir = os.path.join(HERE, "voices")
    if regen:
        from kokoro_onnx import Kokoro
        k = Kokoro(os.path.join(model_dir, "kokoro-v1.0.onnx"), os.path.join(model_dir, "voices-v1.0.bin"))
        for pid, sec, spoken, disp in S.P:
            a, sr = k.create(spoken, voice="am_onyx", speed=S.SPEED, lang="en-us")
            i = np.where(np.abs(a) > 0.01)[0]
            a = a[max(0, i[0] - 200):i[-1] + 2000]
            sf.write(os.path.join(vdir, f"{pid}.wav"), a, sr)
    t = S.START_PAD
    out = {"paragraphs": [], "sections": {}}
    prev_sec = None
    for pid, sec, spoken, disp in S.P:
        if prev_sec == "cold" and sec != "cold":
            out["sections"]["title"] = [t, t + S.TITLE_CARD]
            t += S.TITLE_CARD
        if sec not in out["sections"]:
            out["sections"][sec] = [t, None]
            if sec in S.CHAPTERS:
                out.setdefault("chapters", []).append([t, t + S.CHAPTER_CARD, S.CHAPTERS[sec]])
                t += S.CHAPTER_CARD
        d = sf.info(os.path.join(vdir, f"{pid}.wav")).duration
        ss, sd = SPLIT.split(spoken), SPLIT.split(disp)
        assert len(ss) == len(sd), (pid, len(ss), len(sd))
        w = np.array([len(x) + 6 for x in ss], float)
        bounds = np.concatenate([[0], np.cumsum(w) / w.sum()]) * (d - 0.15)
        sents = [[t + bounds[i], t + bounds[i + 1], sd[i]] for i in range(len(sd))]
        out["paragraphs"].append({"id": pid, "section": sec, "start": t, "dur": d, "sentences": sents})
        nxt = S.P[S.P.index((pid, sec, spoken, disp)) + 1][1] if (pid, sec, spoken, disp) != S.P[-1] else None
        gap = S.PAUSE_AFTER.get(pid, S.PAUSE_SECTION if nxt != sec else S.PAUSE_DEFAULT)
        t += d + gap
        prev_sec = sec
    secs = [k for k in out["sections"]]
    for a, b in zip(secs, secs[1:]):
        out["sections"][a][1] = out["sections"][b][0]
    total = t - S.PAUSE_AFTER.get(S.P[-1][0], S.PAUSE_DEFAULT) + S.END_PAD
    out["sections"][secs[-1]][1] = total
    out["duration"] = round(total, 2)
    json.dump(out, open(os.path.join(HERE, "timeline.json"), "w"), indent=1)
    print("duration", round(total, 1), "s =", f"{int(total // 60)}:{int(total % 60):02d}")
    for k, (a, b) in out["sections"].items():
        print(f"  {k:8s} {a:7.1f} -> {b:7.1f}")


if __name__ == "__main__":
    main(sys.argv[1], regen="--no-regen" not in sys.argv)
