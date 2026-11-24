"""Audio for the Highway 110 jam episode: narration from frame 0, an original pulsing score, engine idle and horns,
counter ticks, a cash-register hit on the water price, a stamp, coal-truck rumble and a soft loop back to the opening."""
import os
import sys

import numpy as np
import soundfile as sf
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__))
for sub in ("eiffel-con", "zanzibar-war", "molasses-flood"):
    sys.path.insert(0, os.path.join(HERE, "..", sub))
import audio as A  # noqa: E402
import audio_ep as Z  # noqa: E402  (tick)

DUR = 42.5
A.N = N = int(DUR * A.SR)
SR = A.SR
NARR = {"n1": 0.1, "n2": 3.25, "n3": 11.7, "n4": 18.6, "n5": 26.1, "n6": 36.0, "n7": 40.9}
VDUR = {k: sf.info(os.path.join(HERE, "voices", f"{k}.wav")).duration for k in NARR}


def wt(pid, frac):
    return NARR[pid] + VDUR[pid] * frac


def ping(f=3000, dur=0.25):
    n = int(dur * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * f * t) * np.exp(-t * 30)


def horn(f=420, dur=0.5):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.sign(np.sin(2 * np.pi * f * t)) * 0.5 + np.sign(np.sin(2 * np.pi * f * 1.26 * t)) * 0.5
    return A.filt(x, "lowpass", 2200) * A.env_adsr(n, 0.02, 0.1)


def build(out):
    D2, A2, D3, F3, Bb2, C3, G2 = 73.42, 110.0, 146.83, 174.61, 116.54, 130.81, 98.0
    music = np.zeros((N, 2))
    A.place(music, A.drone(0.0, 18.35, [D2, A2, D3], 600, 0.35, 0.2), 0.0)       # starts on frame 0
    for tb in np.arange(0.1, 18.3, 0.5):
        A.place(music, A.thump() * 0.18, tb)
    A.place(music, A.drone(18.35, 35.8, [G2, D3, 246.94], 900, 0.3, 1.0), 18.35)   # the hustle + the cause
    for tb in np.arange(18.4, 35.6, 0.25):
        A.place(music, A.thump() * (0.2 if int(tb * 4) % 2 == 0 else 0.08), tb)
    A.place(music, A.tremolo_strings(26.1, 35.6, [293.7, 311.1]) * 0.14, 26.1)
    A.place(music, A.drone(35.8, DUR, [D2, A2, D3, F3], 500, 0.35, 1.0), 35.8)
    A.place(music, A.piano(293.66, 4.0) * 0.2, 36.1)
    A.place(music, A.piano(440.0, 4.0) * 0.2, 38.4)
    A.place(music, A.boom(1.6) * 0.5, 0.1)
    A.place(music, A.boom(2.0) * 0.6, 40.9)
    music = A.reverb(music, 2.6, 0.28)

    sfx = np.zeros((N, 2))
    rng = np.random.default_rng(3)
    n = int(18.0 * SR)                                                          # idling engines
    idle = A.filt(A.noise(n), "lowpass", 160) * (0.7 + 0.3 * np.sin(2 * np.pi * 9 * np.arange(n) / SR))
    A.place(sfx, idle * 0.25, 0.0)
    for th in (1.2, 4.6, 9.8, 15.6, 37.0):                                      # horns
        A.place(sfx, horn(rng.uniform(380, 460)) * 0.16, th, pan=rng.uniform(-0.6, 0.6))
    for k in range(12):                                                         # distance + day counters
        A.place(sfx, Z.tick(0.25), 3.6 + k * 0.27)
    for k in range(5):
        A.place(sfx, Z.tick(0.4), 14.8 + k * 0.4)
    tw = wt("n4", 0.42)
    A.place(sfx, A.glitch(0.25) * 0.3, tw + 1.5)                                 # ¥15 hit
    A.place(sfx, ping(2600, 0.6) * 0.3, tw + 1.5)
    for k in range(3):
        A.place(sfx, A.pop() * 0.2, wt("n4", 0.72) + 0.2 + k * 0.25)            # noodle cups
    A.place(sfx, A.whoosh(0.8, 2000, 200) * 0.14, 27.0)                         # capacity halves
    n = int(4.0 * SR)                                                           # coal trucks rumbling
    A.place(sfx, A.filt(A.noise(n), "lowpass", 220) * A.env_adsr(n, 0.5, 1.0) * 0.5, wt("n5", 0.62))
    for k in range(8):
        A.place(sfx, Z.tick(0.35), 36.1 + k * 0.28)                            # day counter to 12
    A.place(sfx, A.whoosh(0.8, 300, 3000) * 0.18, 38.3)                         # cleared
    for tw_ in (3.1, 11.4, 18.35, 25.85, 35.8):
        A.place(sfx, A.whoosh(0.4, 500, 3500) * 0.08, tw_ - 0.15)
    sfx = A.reverb(sfx, 1.0, 0.14)

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
    bed = music / np.abs(music).max() * 0.3 + sfx / np.abs(sfx).max() * 0.36
    mixd = bed * (1 - 0.45 * ve)[:, None] + voice / np.abs(voice).max() * 0.95
    tail = int(0.6 * SR)   # short tail: the loop restarts on the opening drone
    mixd[-tail:] *= np.linspace(1, 0.3, tail)[:, None]
    sf.write(out, (np.tanh(mixd * 1.1) * 0.9).astype(np.float32), SR, subtype="FLOAT")


if __name__ == "__main__":
    build(sys.argv[1])
