"""Audio for the GTA VI launch episode: narration, an original synthwave-style score (pads, arpeggios, a four-on-the-floor
pulse), a counter whir, cash clinks, stamps, crowd rumble for the stampede, and a quiet end."""
import os
import sys

import numpy as np
import soundfile as sf
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__))
for sub in ("eiffel-con", "zanzibar-war", "molasses-flood"):
    sys.path.insert(0, os.path.join(HERE, "..", sub))
import audio as A  # noqa: E402
import audio_eiffel as E  # noqa: E402  (pluck)
import audio_ep as Z  # noqa: E402  (tick)

DUR = 60.0
A.N = N = int(DUR * A.SR)
SR = A.SR
NARR = {"n1": 0.1, "n2": 6.2, "n3": 13.4, "n4": 18.4, "n5": 23.0, "n6": 32.1, "n7": 37.3, "n8": 46.3, "n9": 53.2,
        "n10": 56.9}
VDUR = {k: sf.info(os.path.join(HERE, "voices", f"{k}.wav")).duration for k in NARR}


def ease(x):
    return x * x * (3 - 2 * x)


def wt(pid, frac):
    return NARR[pid] + VDUR[pid] * frac


def clink(f=2600, dur=0.5):
    n = int(dur * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) + 0.6 * np.sin(2 * np.pi * f * 1.51 * t)) * np.exp(-t * 12)


def arp(buf, a, b, notes, step, level):
    t, i = a, 0
    while t < b - 0.3:
        A.place(buf, E.pluck(notes[i % len(notes)], 0.25) * level, t, pan=0.35 * np.sin(i * 1.3))
        t += step
        i += 1


def build(out):
    D2, A2, D3, F3, C3, Bb2, G2 = 73.42, 110.0, 146.83, 174.61, 130.81, 116.54, 98.0
    music = np.zeros((N, 2))
    A.place(music, A.drone(0.0, 18.2, [D2, A2, D3, F3], 900, 0.35, 1.5), 0.0)
    arp(music, 0.3, 13.2, [293.66, 440.0, 587.33, 440.0], 60 / 104 / 2, 0.1)
    A.place(music, A.drone(13.2, 18.2, [D2, Bb2, F3 / 2], 450, 0.4, 0.8), 13.2)       # the delays: tense
    A.place(music, A.tremolo_strings(13.4, 18.1, [293.7, 311.1]) * 0.16, 13.4)
    A.place(music, A.drone(18.2, 53.0, [G2, D3, 246.94, 293.66], 1500, 0.3, 0.8), 18.2)  # launch: driving
    arp(music, 18.3, 52.8, [392.0, 493.88, 587.33, 783.99], 60 / 120 / 2, 0.12)
    for tb in np.arange(18.3, 52.8, 0.5):
        A.place(music, A.thump() * 0.28, tb)
    A.place(music, A.drone(53.0, DUR, [D2, A2, D3], 450, 0.35, 1.5), 53.0)
    A.place(music, A.piano(293.66, 4.0) * 0.22, 53.3)
    A.place(music, A.piano(440.0, 4.0) * 0.2, wt("n9", 0.55))
    A.place(music, A.boom(2.0) * 0.6, 0.3)
    A.place(music, A.braam(3.0) * 0.55, wt("n5", 0.75))                              # entertainment record
    A.place(music, A.boom(1.6) * 0.45, wt("n7", 0.72))                               # GTA VI bar
    A.place(music, A.boom(2.2) * 0.7, 56.9)
    music = A.reverb(music, 2.6, 0.28)

    sfx = np.zeros((N, 2))
    rng = np.random.default_rng(5)
    for tc in np.sort(rng.uniform(0.3, 2.0, 10)):                                     # cash clinks on the hook
        A.place(sfx, clink(rng.uniform(2200, 3200)) * 0.12, tc, pan=rng.uniform(-0.7, 0.7))
    for k in range(13):                                                                 # calendar flips
        A.place(sfx, A.paper_slap() * 0.08, 6.6 + 4.5 * ease(k / 12))
    A.place(sfx, A.paper_slap() * 0.4, wt("n3", 0.5) + 1.0)                           # DELAYED stamp
    n = int(4.4 * SR)                                                                   # crowd rumble
    A.place(sfx, A.filt(A.noise(n), "bandpass", [80, 900]) * A.env_adsr(n, 0.5, 1.0) * 0.5, 18.3)
    for k in range(40):
        A.place(sfx, A.thump() * 0.08, 18.4 + k * 0.1 + rng.uniform(0, 0.05), pan=rng.uniform(-0.6, 0.6))
    t0 = wt("n5", 0.3)                                                                  # counter whir
    n = int(2.0 * SR)
    ph = np.cumsum(np.linspace(200, 1600, n)) / SR
    A.place(sfx, A.filt(np.sign(np.sin(2 * np.pi * ph)), "lowpass", 3000) * A.env_adsr(n, 0.05, 0.2) * 0.05, t0)
    A.place(sfx, clink(2600, 1.0) * 0.2, t0 + 2.0)
    A.place(sfx, A.paper_slap() * 0.45, wt("n5", 0.75))                               # record stamp
    for k in range(35):                                                                 # boxes stacking
        A.place(sfx, A.pop() * 0.05, 32.6 + 3.0 * k / 35)
    for tw in (37.0, 46.0, 52.8):
        A.place(sfx, A.whoosh(0.5, 400, 3000) * 0.13, tw)
    sfx = A.reverb(sfx, 1.0, 0.12)

    voice = np.zeros((N, 2))
    for k, t0 in NARR.items():
        v, sr = sf.read(os.path.join(HERE, "voices", f"{k}.wav"))
        v = signal.resample_poly(v, SR, sr)
        v = A.filt(v, "highpass", 70, 2)
        v = v + A.filt(v, "bandpass", [2500, 5000], 2) * 0.3
        A.place(voice, np.tanh(v * 2.0) / np.tanh(2.0), t0)
    voice = A.reverb(voice, 0.8, 0.06, 5000)
    ve = A.filt(np.abs(voice).max(1), "lowpass", 4, 1)
    ve = np.clip(ve / (ve.max() + 1e-9) * 3, 0, 1)
    bed = music / np.abs(music).max() * 0.32 + sfx / np.abs(sfx).max() * 0.3
    mixd = bed * (1 - 0.45 * ve)[:, None] + voice / np.abs(voice).max() * 0.95
    tail = int(0.8 * SR)
    mixd[-tail:] *= np.linspace(1, 0, tail)[:, None]
    sf.write(out, (np.tanh(mixd * 1.1) * 0.9).astype(np.float32), SR, subtype="FLOAT")


if __name__ == "__main__":
    build(sys.argv[1])
