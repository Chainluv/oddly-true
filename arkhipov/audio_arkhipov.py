"""Audio for the Arkhipov episode: narration, an original low tension score, sonar pings, muffled depth-charge
booms, a heartbeat under the vote, and a quiet resolve when the submarine surfaces."""
import os
import sys

import numpy as np
import soundfile as sf
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__))
for sub in ("zanzibar-war", "molasses-flood"):
    sys.path.insert(0, os.path.join(HERE, "..", sub))
import audio as A  # noqa: E402

DUR = 50.0
A.N = N = int(DUR * A.SR)
SR = A.SR
NARR = {"n1": 0.1, "n2": 6.0, "n3": 15.6, "n4": 25.6, "n5": 34.8, "n6": 43.0, "n7": 47.2}
CHARGES = [9.6 + i * 0.75 + 1.6 for i in range(10)]   # burst times, matching ark.py
BOOMS = [17.8, 19.2, 20.3, 21.6]                     # explosions felt inside the sub
VOTES = [29.4, 30.2]
NO_T = 31.8


def ping(f=1250, dur=2.2):
    n = int(dur * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * f * t) * np.exp(-t * 3.2) * np.minimum(1, t / 0.004)


def build(out):
    D2, A2, D3, F3, C3, Bb2 = 73.42, 110.0, 146.83, 174.61, 130.81, 116.54
    music = np.zeros((N, 2))
    A.place(music, A.drone(0.0, 25.4, [D2, A2, D3], 380, 0.4, 2.5), 0.0)
    A.place(music, A.tremolo_strings(15.4, 25.4, [293.7, 311.1]) * 0.18, 15.4)
    A.place(music, A.drone(25.4, 34.6, [D2, Bb2, F3 / 2], 320, 0.45, 1.0), 25.4)
    A.place(music, A.braam(3.0) * 0.6, NO_T)
    A.place(music, A.drone(34.6, DUR, [D2, A2, D3, F3], 520, 0.35, 2.0), 34.6)
    for i, f in enumerate([293.66, 349.23, 440.0, 392.0, 349.23, 293.66]):
        A.place(music, A.piano(f, 4.0) * 0.22, 36.0 + i * 2.2)
    A.place(music, A.boom(2.0) * 0.6, 0.15)
    A.place(music, A.boom(2.2) * 0.7, 47.2)
    music = A.reverb(music, 3.0, 0.3)

    sfx = np.zeros((N, 2))
    for tp in list(np.arange(1.0, 15.0, 3.2)) + [36.2, 39.4]:
        A.place(sfx, ping() * 0.25, tp, pan=0.2)
    for i, tc in enumerate(CHARGES):    # muffled underwater bursts
        A.place(sfx, A.filt(A.boom(1.6, 90, 30), "lowpass", 400) * (0.5 + 0.1 * (i % 3)), tc, pan=(i % 5 - 2) * 0.2)
    for tb in BOOMS:                    # inside the hull: heavier, with a metal clang
        A.place(sfx, A.filt(A.boom(2.0, 80, 26), "lowpass", 500) * 0.9, tb)
        A.place(sfx, A.clang(1.5) * 0.12, tb + 0.05)
    hb = A.heartbeat(25.6, NO_T)
    for th in hb:
        A.place(sfx, A.thump() * 0.45, th)
    for tv in VOTES + [NO_T]:
        A.place(sfx, A.paper_slap() * 0.25, tv)
    n = int(2.8 * SR)                   # surfacing: rushing water
    A.place(sfx, A.filt(A.noise(n), "bandpass", [300, 2500]) * A.env_adsr(n, 1.2, 1.2) * 0.25, 36.2)
    A.place(sfx, A.whoosh(0.6, 400, 3000) * 0.12, 43.0)
    sfx = A.reverb(sfx, 1.4, 0.18)

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
    bed = music / np.abs(music).max() * 0.32 + sfx / np.abs(sfx).max() * 0.34
    mixd = bed * (1 - 0.45 * ve)[:, None] + voice / np.abs(voice).max() * 0.95
    tail = int(0.8 * SR)
    mixd[-tail:] *= np.linspace(1, 0, tail)[:, None]
    sf.write(out, (np.tanh(mixd * 1.1) * 0.9).astype(np.float32), SR, subtype="FLOAT")


if __name__ == "__main__":
    build(sys.argv[1])
