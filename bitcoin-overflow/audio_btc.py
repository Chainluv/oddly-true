"""Audio for the Bitcoin overflow episode: narration, an original pulsing electronic score, coin clinks, a
counter that whirs up and glitches on the overflow, a stamp, a clock tick for the five-hour fix, and a quiet end."""
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

DUR = 53.0
A.N = N = int(DUR * A.SR)
SR = A.SR
NARR = {"n1": 0.1, "n2": 5.8, "n3": 11.0, "n4": 16.0, "n5": 23.5, "n6": 32.4, "n7": 40.0, "n8": 46.6, "n9": 50.0}
VDUR = {k: sf.info(os.path.join(HERE, "voices", f"{k}.wav")).duration for k in NARR}


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
    D2, A2, D3, F3, C3, Bb2 = 73.42, 110.0, 146.83, 174.61, 130.81, 116.54
    music = np.zeros((N, 2))
    A.place(music, A.drone(0.0, 15.8, [D2, A2, D3], 600, 0.35, 1.5), 0.0)
    arp(music, 0.3, 15.6, [587.33, 698.46, 880.0, 698.46], 60 / 110 / 2, 0.1)
    A.place(music, A.drone(15.8, 32.2, [D2, Bb2, F3 / 2], 420, 0.4, 1.0), 15.8)     # overflow + block: tense
    A.place(music, A.tremolo_strings(16.0, 32.0, [293.7, 311.1]) * 0.16, 16.0)
    for tb in np.arange(16.0, 32.0, 60 / 120):
        A.place(music, A.thump() * 0.22, tb)
    A.place(music, A.drone(32.2, 46.4, [D2, A2, D3, F3], 800, 0.3, 1.0), 32.2)       # the fix: resolve
    arp(music, 32.4, 46.2, [293.66, 349.23, 440.0, 523.25], 60 / 100 / 2, 0.1)
    A.place(music, A.drone(46.4, DUR, [D2, A2, D3], 400, 0.35, 1.5), 46.4)
    A.place(music, A.piano(293.66, 4.0) * 0.22, 46.7)
    A.place(music, A.piano(349.23, 4.0) * 0.2, 48.2)
    A.place(music, A.boom(2.0) * 0.6, 0.2)
    A.place(music, A.braam(3.0) * 0.55, wt("n5", 0.38))                              # +184 billion
    A.place(music, A.boom(2.2) * 0.7, 50.0)
    music = A.reverb(music, 2.6, 0.28)

    sfx = np.zeros((N, 2))
    rng = np.random.default_rng(5)
    for tc in np.sort(rng.uniform(0.3, 5.4, 18)):                                     # raining coins
        A.place(sfx, clink(rng.uniform(2200, 3200)) * 0.12, tc, pan=rng.uniform(-0.7, 0.7))
    n = int(3.2 * SR)                                                                   # counter whir
    ph = np.cumsum(np.linspace(200, 1400, n)) / SR
    A.place(sfx, A.filt(np.sign(np.sin(2 * np.pi * ph)), "lowpass", 3000) * A.env_adsr(n, 0.05, 0.3) * 0.05, 0.4)
    tov = wt("n4", 0.42)
    n = int((tov - 17.8) * SR)
    ph = np.cumsum(np.linspace(150, 1800, n)) / SR
    A.place(sfx, A.filt(np.sign(np.sin(2 * np.pi * ph)), "lowpass", 3000) * 0.05, 17.8)
    A.place(sfx, A.glitch(0.4) * 0.5, tov)
    A.place(sfx, A.paper_slap() * 0.45, wt("n4", 0.78))                               # CHECK PASSED
    A.place(sfx, A.paper_slap() * 0.25, wt("n3", 0.75))                               # BUG
    for k in range(10):                                                                 # five-hour clock
        A.place(sfx, Z.tick(0.35), 33.0 + k * 0.5)
    A.place(sfx, A.whoosh(0.5, 400, 3000) * 0.14, 39.6)
    A.place(sfx, A.whoosh(0.6, 3000, 300) * 0.14, wt("n7", 0.72))                     # fake coins erased
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
