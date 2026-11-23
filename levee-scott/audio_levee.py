"""Audio for the West Quincy levee episode: narration from frame 0, an original low, uneasy score, rising water,
a levee crack and rush, TV static, a gavel, popping failure dots, and a soft return to the opening drone for the loop."""
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

DUR = 50.0
A.N = N = int(DUR * A.SR)
SR = A.SR
NARR = {"n1": 0.1, "n2": 5.3, "n3": 9.5, "n4": 14.8, "n5": 21.45, "n6": 26.5, "n7": 31.85, "n8": 35.6, "n9": 42.2,
        "n10": 45.4, "n11": 49.0}
VDUR = {k: sf.info(os.path.join(HERE, "voices", f"{k}.wav")).duration for k in NARR}


def wt(pid, frac):
    return NARR[pid] + VDUR[pid] * frac


def ping(f=3000, dur=0.25):
    n = int(dur * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * f * t) * np.exp(-t * 30)


def build(out):
    D2, A2, D3, F3, Bb2, C3, E3 = 73.42, 110.0, 146.83, 174.61, 116.54, 130.81, 164.81
    music = np.zeros((N, 2))
    A.place(music, A.drone(0.0, 21.35, [D2, A2, D3], 450, 0.4, 0.2), 0.0)       # starts on frame 0
    A.place(music, A.tremolo_strings(14.8, 21.3, [293.7, 311.1]) * 0.16, 14.8)
    A.place(music, A.drone(21.35, 35.5, [D2, Bb2, F3 / 2], 380, 0.4, 1.0), 21.35)  # suspicion + trial
    for tb in np.arange(21.5, 35.3, 0.7):
        A.place(music, A.thump() * 0.2, tb)
    A.place(music, A.drone(35.5, DUR, [D2, A2, D3, F3], 480, 0.35, 1.0), 35.5)  # doubt
    for i, f in enumerate([293.66, 349.23, 329.63, 293.66, 261.63]):
        A.place(music, A.piano(f, 4.0) * 0.2, 35.8 + i * 1.9)
    A.place(music, A.boom(1.6) * 0.5, 0.1)
    A.place(music, A.braam(3.0) * 0.45, 45.5)                                   # GUILTY?
    A.place(music, A.boom(2.0) * 0.6, 49.0)
    music = A.reverb(music, 2.8, 0.3)

    sfx = np.zeros((N, 2))
    A.place(sfx, A.paper_slap() * 0.4, 5.4)                                     # 1993 stamp
    n = int(4.0 * SR)                                                           # rising water
    A.place(sfx, A.filt(A.noise(n), "lowpass", 500) * np.linspace(0.05, 0.25, n), 5.3)
    rng = np.random.default_rng(4)
    for k in range(36):                                                         # sandbags thudding
        A.place(sfx, A.thump() * 0.06, 9.6 + k * 3.2 / 36 + rng.uniform(0, 0.02), pan=rng.uniform(-0.5, 0.5))
    tb = wt("n4", 0.2)
    A.place(sfx, A.snap() * 0.6, tb)                                            # the crack
    A.place(sfx, A.creak(1.0, 300) * 0.25, tb + 0.05)
    n = int(5.5 * SR)                                                           # the rush of water
    A.place(sfx, A.filt(A.noise(n), "bandpass", [150, 2500]) * A.env_adsr(n, 0.3, 2.0) * 0.6, tb + 0.2)
    A.place(sfx, A.boom(2.0, 80, 30) * 0.5, tb + 0.2)
    for k in range(12):
        A.place(sfx, Z.tick(0.25), wt("n4", 0.7) + k * 0.11)                   # day counter
    n = int(5.0 * SR)                                                           # TV static
    A.place(sfx, A.filt(A.noise(n), "highpass", 2500) * A.env_adsr(n, 0.05, 0.3) * 0.05, 21.45)
    A.place(sfx, A.clang(1.2) * 0.35, 32.25)                                    # gavel
    A.place(sfx, A.boom(0.8, 140, 60) * 0.6, 32.25)
    A.place(sfx, A.paper_slap() * 0.3, wt("n7", 0.45))
    for k in range(40):                                                         # failure dots popping
        A.place(sfx, A.pop() * 0.07, 35.9 + 3.2 * k / 40, pan=rng.uniform(-0.6, 0.6))
    A.place(sfx, A.paper_slap() * 0.4, wt("n8", 0.78))                          # SCOTT DENIES IT
    for tw in (5.2, 9.4, 14.7, 21.35, 26.4, 31.75, 35.5, 42.1, 45.3):
        A.place(sfx, A.whoosh(0.4, 500, 3500) * 0.08, tw - 0.15)
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
