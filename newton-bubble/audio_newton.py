"""NO WAY. #4 audio: reuses the molasses-flood synth/mix functions (original, synthesized = cleared everywhere)."""
import os
import sys
import numpy as np
import soundfile as sf
from scipy import signal

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "molasses-flood"))
import audio as A  # noqa: E402

NARR = {"l1": 0.1, "l2": 2.5, "l3": 4.45, "l4": 7.55, "l5": 10.75, "l6": 14.1, "l7": 15.75, "l8": 18.2, "l9": 19.15}


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
    A.place(music, A.drone(0.0, 10.7, [D2, A2, D3], 520, 0.45, 0.2), 0.0)
    A.place(music, A.tremolo_strings(7.4, 10.7, [587.3, 880.0]) * 0.2, 7.4, pan=0.2)     # rising hype
    A.place(music, A.boom(2.0) * 0.8, 10.75)                                             # the burst
    A.place(music, A.drone(10.75, 14.2, [36.7, D2, F3 / 2], 420, 0.45, 0.1), 10.75)
    for tn, f in [(14.1, 293.66), (15.0, 349.23), (15.9, 440.0), (16.8, 329.63)]:
        A.place(music, A.piano(f) * 0.3, tn)
    A.place(music, A.boom(1.8, 80, 30) * 0.7, 18.2)
    A.place(music, A.drone(18.2, 20.0, [36.7, D2, A2, F3], 380, 0.35, 0.05), 18.2)
    music = A.reverb(music, 2.8, 0.28)
    A.place(sfx, A.whoosh(0.5, 300, 4000) * 0.25, 4.0)
    A.place(sfx, A.paper_slap() * 0.35, 4.3)
    for i in range(8):                                                                    # early gains
        A.place(sfx, coin(0.35), 4.8 + (i + 1) * 0.32, pan=0.1)
    A.place(sfx, A.whoosh(0.4, 300, 3000) * 0.2, 7.2)
    for i in range(6):                                                                    # bought back in
        A.place(sfx, coin(0.35), 7.7 + (i + 1) * 0.4, pan=-0.2)
    A.place(sfx, A.pop() * 0.4, 10.75)
    for k in range(4):                                                                    # coins falling away
        A.place(sfx, coin(0.25), 11.5 + k * 0.6, pan=0.3)
    A.place(sfx, A.whoosh(0.8, 2500, 200) * 0.25, 10.8)
    A.place(sfx, A.whoosh(0.6, 2000, 300) * 0.2, 14.6)                                   # apple falls
    A.place(sfx, A.filt(A.boom(0.5, 120, 60), "lowpass", 600) * 0.6, 15.2)               # apple lands
    n = int(1.6 * SR)
    A.place(sfx, A.sine_sweep(700, 90, n) * A.env_adsr(n, 0.05, 1.2) * 0.25, 15.9)      # portfolio drop
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
