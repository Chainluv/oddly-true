"""Soundtrack for the long-form Great Molasses Flood: narration from timeline.json, an original synthesized score
that follows the chapters, and sound effects keyed to the same timeline. Uses the shared molasses-flood synths."""
import json
import os
import sys

import numpy as np
import soundfile as sf
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__))
for sub in ("zanzibar-war", "molasses-flood"):
    sys.path.insert(0, os.path.join(HERE, "..", sub))
import audio as A  # noqa: E402
import audio_ep as Z  # noqa: E402  (tick)

TL = json.load(open(os.path.join(HERE, "timeline.json")))
DUR = TL["duration"]
A.N = N = int(DUR * A.SR)
SR = A.SR
P = {p["id"]: p for p in TL["paragraphs"]}
SEC = TL["sections"]


def st(pid, i=0):
    return P[pid]["sentences"][i][0]


def end(pid):
    return P[pid]["start"] + P[pid]["dur"]


def sec(name):
    return SEC[name]


def build(out):
    D1, D2, A2, D3, F3, C3, Bb2 = 36.71, 73.42, 110.0, 146.83, 174.61, 130.81, 116.54
    music = np.zeros((N, 2))
    sfx = np.zeros((N, 2))
    place = A.place

    # ---- cold open: quiet street, then the rumble and the wave
    c0, c1 = sec("cold")
    place(music, A.drone(c0, c1, [D2, A2], 400, 0.25, 2.0), c0)
    place(sfx, A.wind(c1 - c0) * 0.08, c0)
    mg = st("c2", 0)
    for k in range(14):  # "a sound like a machine gun": rivets
        place(sfx, A.pop() * 0.35, mg + 0.6 + k * 0.09 + 0.02 * np.sin(k))
    place(sfx, A.groan(2.5) * 0.5, mg + 1.2)
    w = A.roar(end("c2") - st("c2", 2) + 0.5, 120, 2200)
    place(sfx, w * np.linspace(0.3, 1.0, len(w)) * 0.6, st("c2", 2))
    place(music, A.braam(3.0) * 0.7, st("c3", 1))
    # ---- title + chapter hits
    t0, t1 = sec("title")
    place(music, A.boom(2.0) * 0.8, t0)
    for c0_, c1_, _ in TL["chapters"]:
        place(sfx, A.whoosh(0.6, 300, 4000) * 0.15, c0_ - 0.2)
        place(music, A.boom(1.6, 80, 30) * 0.35, c0_)

    # ---- the tank: calm, slightly uneasy
    a, b = sec("tank")
    place(music, A.drone(a, b, [D2, A2, D3], 450, 0.35, 2.0), a)
    for i, (tn, f) in enumerate([(0, 293.66), (4, 261.63), (8, 220.0), (12, 233.08)] * 6):
        tt = a + 3 + i * 3.6
        if tt < b - 2:
            place(music, A.piano(f, 3.5) * 0.18, tt, pan=0.2 * np.sin(i))
    place(sfx, A.paper_slap() * 0.2, P["t4"]["start"] + 0.3)
    place(sfx, A.filt(A.boom(0.5, 140, 60), "lowpass", 800) * 0.5, st("t4", 3) + 0.3)       # stamp
    for k in range(6):
        place(sfx, A.gurgles(0.8, 6) * 0.08, P["t5"]["start"] + k * 0.5)                  # drips
    place(sfx, A.groan(2.5) * 0.45, st("t6", 1))
    place(sfx, A.creak(1.6, 380) * 0.3, st("t6", 1) + 0.8, pan=-0.3)
    sw = A.filt(A.noise(int(3 * SR)), "bandpass", [600, 3000]) * 0.12                      # paint roller
    place(sfx, sw * np.abs(np.sin(np.pi * 2.2 * A.T(len(sw))))[:], st("t6", 3))

    # ---- the perfect storm: pressure builds
    a, b = sec("storm")
    place(music, A.drone(a, b, [D2, A2, F3], 480, 0.4, 1.5), a)
    place(music, A.tremolo_strings(P["s3"]["start"], b, [293.7, 311.1, 440.0]) * 0.22, P["s3"]["start"])
    for tb in A.heartbeat(P["s4"]["start"], b - 0.4):
        place(music, A.thump() * 0.6, tb)
    for k in range(4):
        place(sfx, A.paper_slap() * 0.12, a + 0.3 + k * 0.5)                               # calendar pages
    place(sfx, A.creak(2.0, 420, 30, 70) * 0.25, P["s4"]["start"] + 1.0)

    # ---- the wave
    a, b = sec("wave")
    for s in np.arange(P["w1"]["start"], P["w1"]["start"] + 3.0, 0.5):
        place(sfx, Z.tick(0.5), s)
    burst = st("w2", 1) + 0.6
    for k in range(18):
        place(sfx, A.pop() * 0.4, st("w2", 0) + 1.0 + k * (burst - st("w2", 0) - 1.2) / 18, pan=np.sin(k) * 0.6)
    place(sfx, A.groan(2.0) * 0.5, st("w2", 0))
    place(sfx, A.boom(3.0, 110, 25), burst)
    place(sfx, A.clang(3.0) * 0.4, burst)
    r = A.roar(b - burst - 3, 150, 3000)
    place(sfx, r * np.minimum(1, A.T(len(r)) / 0.2) * np.linspace(0.9, 0.5, len(r)) * 0.55, burst)
    place(music, A.drone(burst, b, [D1, D2, A2], 380, 0.5, 0.3), burst)
    for k in range(6):
        place(sfx, A.snap() * 0.35, P["w4"]["start"] + 1.2 + k * 1.7, pan=np.sin(k))
    place(sfx, A.gurgles(4.0, 12) * 0.25, st("w4", 3))
    place(music, A.braam(4.0) * 0.8, st("w6", 0) + 1.6)                                       # cliffhanger

    # ---- the trap: cold and slow
    a, b = sec("trap")
    place(music, A.drone(a, b, [D2, F3 / 2, A2, 293.7], 900, 0.3, 2.0), a)
    for i in range(10):
        place(music, A.piano([440.0, 349.23, 293.66, 261.63][i % 4], 4.0) * 0.14, a + 2 + i * 4.4, pan=-0.2)
    place(sfx, A.gurgles(6.0, 4) * 0.12, P["r2"]["start"])
    place(sfx, A.wind(b - a) * 0.07, a)
    # quieter around the death toll
    # ---- the cleanup
    a, b = sec("cleanup")
    place(music, A.drone(a, b, [D2, A2, D3], 600, 0.3, 1.5), a)
    hose = A.filt(A.noise(int((end("k1") - P["k1"]["start"]) * SR)), "bandpass", [1500, 8000]) * 0.08
    place(sfx, hose, P["k1"]["start"])
    place(sfx, A.wind(b - a) * 0.08, a)
    # ---- the blame game: courtroom pulse
    a, b = sec("blame")
    place(music, A.drone(a, b, [D2, A2, C3], 420, 0.35, 1.0), a)
    for tb in np.arange(a + 1.0, b - 1, 1.4):
        place(music, A.thump() * 0.25, tb)
    for pid in ("b3", "b4"):
        for k in range(5):
            place(sfx, A.paper_slap() * 0.12, P[pid]["start"] + 0.4 + k * 0.7)
    place(sfx, A.filt(A.boom(0.6, 140, 60), "lowpass", 800) * 0.6, P["b5"]["start"] + 1.4)    # NO BOMB stamp
    for k in range(20):
        place(sfx, A.blip(1400 + k * 30, 0.06, 0.02) if hasattr(A, "blip") else Z.tick(0.2), P["b6"]["start"] + 0.4 + k * 0.14)
    # ---- the legacy: warmer
    a, b = sec("legacy")
    place(music, A.drone(a, b, [D2, A2, D3, 185.0], 700, 0.3, 2.0), a)
    for i, f in enumerate([293.66, 369.99, 440.0, 587.33, 440.0, 369.99, 293.66, 440.0] * 2):
        tt = a + 1 + i * 2.6
        if tt < b - 1:
            place(music, A.piano(f, 3.5) * 0.16, tt, pan=0.25 * np.sin(i))
    for k in range(3):
        place(sfx, A.filt(A.boom(0.5, 140, 60), "lowpass", 800) * 0.35, P["l2"]["start"] + 1.5 + k * 2.6)
    # ---- outro
    a, b = sec("outro")
    place(music, A.drone(a, b, [D2, A2, D3], 450, 0.35, 2.0), a)
    for i, f in enumerate([293.66, 349.23, 440.0, 392.0, 349.23, 293.66]):
        place(music, A.piano(f, 4.0) * 0.2, a + 1 + i * 3.0)
    place(music, A.boom(2.0) * 0.7, P["o3"]["start"])
    music = A.reverb(music, 3.0, 0.3)
    sfx = A.reverb(sfx, 1.2, 0.12)

    # music level automation: dip for the death toll, settle under the mid-roll beat
    t = A.T(N)
    auto = np.interp(t, [0, P["r4"]["start"] - 0.5, P["r4"]["start"], end("r4") + 1.5, end("r4") + 3.0, DUR],
                     [1, 1, 0.5, 0.5, 1, 1])
    music *= auto[:, None]

    voice = np.zeros((N, 2))
    for pid, p in P.items():
        v, sr = sf.read(os.path.join(HERE, "voices", f"{pid}.wav"))
        v = signal.resample_poly(v, SR, sr)
        v = A.filt(v, "highpass", 70, 2)
        v = v + A.filt(v, "bandpass", [2500, 5000], 2) * 0.3
        place(voice, np.tanh(v * 2.0) / np.tanh(2.0), p["start"])
    voice = A.reverb(voice, 0.8, 0.06, 5000)
    ve = A.filt(np.abs(voice).max(1), "lowpass", 4, 1)
    ve = np.clip(ve / (ve.max() + 1e-9) * 3, 0, 1)
    bed = music / np.abs(music).max() * 0.3 + sfx / np.abs(sfx).max() * 0.36
    mixd = bed * (1 - 0.5 * ve)[:, None] + voice / np.abs(voice).max() * 0.95
    fade = int(1.2 * SR)
    mixd[-fade:] *= np.linspace(1, 0, fade)[:, None]
    mixd[:int(0.3 * SR)] *= np.linspace(0, 1, int(0.3 * SR))[:, None]
    sf.write(out, (np.tanh(mixd * 1.1) * 0.9).astype(np.float32), SR, subtype="FLOAT")


if __name__ == "__main__":
    build(sys.argv[1])
