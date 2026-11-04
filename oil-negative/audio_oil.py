"""NO WAY. #5 audio: reuses the molasses-flood synth/mix functions (original, synthesized = cleared everywhere)."""
import os
import sys
import numpy as np
import soundfile as sf
from scipy import signal

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "molasses-flood"))
import audio as A  # noqa: E402

NARR = {"l1": 0.1, "l2": 3.0, "l3": 7.0, "l4": 12.3, "l5": 15.6, "l6": 18.2, "l7": 19.15}


def coin(level=1.0):
    n = int(0.35 * A.SR)
    t = A.T(n)
    x = sum(np.sin(2 * np.pi * f * t) * np.exp(-t / d) for f, d in ((3150, 0.12), (4720, 0.08), (6310, 0.05), (2210, 0.15)))
    x += A.filt(A.noise(n), "highpass", 4000) * A.env_adsr(n, 0.0005, 0.006)
    return x / np.abs(x).max() * level


def build(voice_dir, out):
    N, SR = A.N, A.SR
    music = np.zeros((N, 2))
    sfx = np.zeros((N, 2))
    D2, A2, D3, F3 = 73.42, 110.0, 146.83, 174.61
    A.place(music, A.drone(0.0, 7.1, [D2, A2, D3], 520, 0.45, 0.2), 0.0)
    A.place(music, A.drone(7.0, 12.1, [36.7, D2, F3 / 2, A2], 450, 0.5, 0.3), 7.0)
    A.place(music, A.tremolo_strings(7.0, 10.3, [587.3, 622.3]) * 0.2, 7.0, pan=0.2)     # tension before the number
    A.place(music, A.boom(2.0) * 0.8, 10.3)                                              # -$37.63 lands
    A.place(music, A.drone(12.0, 18.3, [D2, A2, D3], 480, 0.4, 0.2), 12.0)
    for tn, f in [(15.5, 293.66), (16.3, 349.23), (17.1, 440.0)]:
        A.place(music, A.piano(f) * 0.3, tn)
    A.place(music, A.boom(1.8, 80, 30) * 0.7, 18.2)
    A.place(music, A.drone(18.2, 20.0, [36.7, D2, A2, F3], 380, 0.35, 0.05), 18.2)
    music = A.reverb(music, 2.8, 0.28)
    n = int(1.6 * SR)
    A.place(sfx, A.sine_sweep(600, 90, n) * A.env_adsr(n, 0.05, 1.2) * 0.22, 0.4)       # price sliding down
    A.place(sfx, A.pop() * 0.4, 2.05)                                                    # flips below zero
    A.place(sfx, A.whoosh(0.4, 300, 3000) * 0.2, 2.85)
    n = int(2.6 * SR)
    A.place(sfx, A.filt(A.roar(2.6, 80, 600), "lowpass", 500) * np.linspace(0.5, 0, n) * 0.4, 3.0)  # traffic winding down
    A.place(sfx, A.whoosh(0.4, 300, 3000) * 0.2, 6.85)
    A.place(sfx, A.paper_slap() * 0.35, 7.0)
    A.place(sfx, A.filt(A.boom(0.6, 140, 60), "lowpass", 800) * 0.6, 10.3)              # stamp
    A.place(sfx, A.whoosh(0.4, 300, 3000) * 0.2, 11.85)
    for k in range(3):                                                                    # cash moving
        A.place(sfx, A.whoosh(0.5, 800, 5000) * 0.18, 12.2 + k * 0.45)
        A.place(sfx, coin(0.3), 12.2 + k * 0.45 + 1.2, pan=0.4)
    A.place(sfx, A.whoosh(0.4, 300, 3000) * 0.2, 15.25)
    for k in range(10):                                                                   # barrels thudding into place
        A.place(sfx, A.filt(A.boom(0.25, 160, 80), "lowpass", 900) * 0.12, 15.4 + k * 0.1)
    A.place(sfx, A.filt(A.noise(int(0.6 * SR)), "bandpass", [300, 2500]) * A.env_adsr(int(0.6 * SR), 0.05, 0.3) * 0.25, 16.8)  # garage door
    A.place(sfx, A.glitch(0.12) * 0.2, 18.15)
    sfx = A.reverb(sfx, 1.2, 0.12)
    voice = np.zeros((N, 2))
    for k, t0 in NARR.items():
        v, sr = sf.read(f"{voice_dir}/{k}.wav")
        v = signal.resample_poly(v, SR, sr)
        v = A.filt(v, "highpass", 70, 2)
        v = v + A.filt(v, "bandpass", [2500, 5000], 2) * 0.35
        v = np.tanh(v * 2.2) / np.tanh(2.2)
        A.place(voice, v, t0)
    voice = A.reverb(voice, 0.9, 0.08, 5000)
    ve = A.filt(np.abs(voice).max(1), "lowpass", 4, 1)
    ve = np.clip(ve / (ve.max() + 1e-9) * 3, 0, 1)
    bed = music / np.abs(music).max() * 0.38 + sfx / np.abs(sfx).max() * 0.45
    mixd = bed * (1 - 0.5 * ve)[:, None] + voice / np.abs(voice).max() * 0.95
    tail = int(0.3 * SR)
    mixd[-tail:] *= np.linspace(1, 0, tail)[:, None]
    sf.write(out, (np.tanh(mixd * 1.1) * 0.9).astype(np.float32), SR, subtype="FLOAT")


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
