"""Audio for the Anthropic IPO episode: narration, an original pulsing score that builds toward the listing, a crack
for the "breakup", stamps, a cash-register-style ding for the price, and a big hit on the valuation."""
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

DUR = 73.0
A.N = N = int(DUR * A.SR)
SR = A.SR
NARR = {"n1": 0.1, "n2": 5.9, "n3": 13.6, "n4": 23.3, "n5": 32.7, "n6": 42.3, "n7": 54.8, "n8": 62.5, "n9": 70.1}
VDUR = {k: sf.info(os.path.join(HERE, "voices", f"{k}.wav")).duration for k in NARR}


def wt(pid, frac):
    return NARR[pid] + VDUR[pid] * frac


def arp(buf, a, b, notes, step, level):
    t, i = a, 0
    while t < b - 0.3:
        A.place(buf, E.pluck(notes[i % len(notes)], 0.3) * level, t, pan=0.3 * np.sin(i))
        t += step
        i += 1


def ding(f=1318.5, dur=1.5):
    n = int(dur * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.01 * t)) * np.exp(-t * 4)


def build(out):
    D2, A2, D3, F3, C3, G2, Bb2 = 73.42, 110.0, 146.83, 174.61, 130.81, 98.0, 116.54
    music = np.zeros((N, 2))
    A.place(music, A.drone(0.0, 23.1, [D2, A2, D3], 500, 0.35, 2.0), 0.0)
    for i, f in enumerate([293.66, 349.23, 440.0, 392.0]):
        A.place(music, A.piano(f, 4.0) * 0.2, 6.0 + i * 3.5)
    A.place(music, A.drone(23.1, 32.5, [D2, Bb2, F3 / 2], 380, 0.4, 1.0), 23.1)        # SBF: darker
    A.place(music, A.tremolo_strings(23.4, 32.4, [293.7, 311.1]) * 0.15, 23.4)
    A.place(music, A.drone(32.5, 54.6, [G2, D3, 246.94], 1200, 0.3, 1.0), 32.5)       # growth + IPO: driving
    arp(music, 32.7, 42.1, [392.0, 493.88, 587.33, 739.99], 60 / 112 / 2, 0.12)
    arp(music, 42.1, 54.6, [392.0, 493.88, 587.33, 783.99], 60 / 124 / 2, 0.14)
    for tb in np.arange(42.3, 54.4, 60 / 124):
        A.place(music, A.thump() * 0.25, tb)
    A.place(music, A.drone(54.6, DUR, [D2, A2, D3, F3], 520, 0.35, 1.5), 54.6)
    for i, f in enumerate([293.66, 349.23, 440.0, 523.25, 440.0]):
        A.place(music, A.piano(f, 4.0) * 0.2, 62.6 + i * 1.6)
    A.place(music, A.boom(2.0) * 0.6, 0.2)
    A.place(music, A.braam(3.0) * 0.55, wt("n6", 0.75))                                 # ~$1.5 trillion
    A.place(music, A.boom(2.2) * 0.7, 70.1)
    music = A.reverb(music, 2.8, 0.3)

    sfx = np.zeros((N, 2))
    A.place(sfx, A.snap() * 0.5, wt("n1", 0.75))                                       # the breakup crack
    A.place(sfx, A.creak(1.0, 500) * 0.15, 6.6)                                        # door
    A.place(sfx, A.paper_slap() * 0.4, wt("n3", 0.78))                                 # FOUNDED stamp
    A.place(sfx, A.paper_slap() * 0.4, wt("n4", 0.78) + 0.5)                           # FTX stamp
    A.place(sfx, A.filt(A.boom(1.2, 120, 40), "lowpass", 600) * 0.4, wt("n4", 0.78) + 0.5)
    A.place(sfx, A.whoosh(0.5, 400, 4000) * 0.15, wt("n5", 0.68) - 0.2)                 # CLAUDE vs CHATGPT
    A.place(sfx, ding() * 0.25, wt("n6", 0.52) + 0.8)                                  # $83.00 lands
    A.place(sfx, A.whoosh(0.5, 300, 3000) * 0.14, 54.4)
    for tr in (wt("n7", 0.4), 62.4):
        A.place(sfx, A.whoosh(0.4, 600, 5000) * 0.12, tr)
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
