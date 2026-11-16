"""Audio for the Huang comeback news episode: brisk narration, an original synthesized electronic news pulse,
whooshes on every beat change, a glitch on the chip reversal, counter ticks and stamp hits. No samples."""
import os
import sys
import numpy as np
import soundfile as sf
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__))
for sub in ("rap-grammy", "molasses-flood"):
    sys.path.insert(0, os.path.join(HERE, "..", sub))
import audio as A  # noqa: E402
import audio_grammy as G  # noqa: E402  (kick / hat)

DUR = 45.0
A.N = N = int(DUR * A.SR)
SR = A.SR
NARR = {"n01": 0.1, "n02": 4.1, "n03": 9.8, "n04": 14.0, "n05": 19.5, "n06": 21.6, "n07": 24.4, "n08": 29.2,
        "n09": 36.0, "n10": 39.2, "n11": 41.1, "n12": 43.8}  # matches huang.py
CUTS = [4.0, 6.6, 8.4, 9.8, 12.4, 14.0, 19.3, 21.6, 24.2, 26.6, 29.1, 32.6, 35.8, 37.5, 39.1, 41.0, 43.6]


def blip(f=1200, v=0.2, d=0.05):
    n = int(0.12 * SR)
    return np.sin(2 * np.pi * f * A.T(n)) * A.env_adsr(n, 0.001, d) * v


def synth_bass(f, dur):
    n = int(dur * SR)
    t = A.T(n)
    ph = np.cumsum(np.full(n, f)) / SR
    x = 2 * (ph % 1) - 1
    return A.filt(x, "lowpass", 500, 2) * np.exp(-t / (dur * 0.6)) * np.minimum(1, t / 0.005)


def build(voice_dir, out):
    music = np.zeros((N, 2))
    step = 60 / 120 / 4
    roots = [55.0, 55.0, 65.41, 49.0]
    t, i = 0.0, 0
    while t < 43.5:
        s = i % 16
        bar = (i // 16) % 4
        if s in (0, 8) and t > 0.3:
            A.place(music, G.kick() * 0.6, t)
        if s in (4, 12):
            A.place(music, A.filt(G.snare(), "highpass", 800) * 0.25, t)
        if s % 2 == 1:
            A.place(music, G.hat() * 0.14, t, pan=0.3)
        if s in (0, 3, 6, 10, 13):
            A.place(music, synth_bass(roots[bar], step * 1.8) * 0.4, t)
        t += step
        i += 1
    A.place(music, A.drone(0.0, DUR, [110.0, 164.81, 220.0], 1600, 0.12, 0.5), 0.0)
    A.place(music, A.boom(1.4, 90, 30) * 0.5, 43.7)
    music = A.reverb(music, 1.0, 0.1)

    sfx = np.zeros((N, 2))
    for c in CUTS:
        A.place(sfx, A.whoosh(0.3, 500, 6000) * 0.18, c - 0.15)
    A.place(sfx, A.whoosh(1.2, 300, 3000) * 0.15, 0.3)                       # chip slides out
    A.place(sfx, A.glitch(0.3) * 0.35, 1.95)                                  # ...and snaps back
    for k in range(40):                                                      # accelerating counter ticks
        tk = 14.2 + 4.2 * (k / 40) ** 0.6
        A.place(sfx, blip(1500 + k * 20, 0.08, 0.02), tk)
    A.place(sfx, blip(2200, 0.25, 0.1), 18.4)
    stamp = A.filt(A.boom(0.5, 140, 60), "lowpass", 800)
    for s in (8.4, 19.35, 21.65, 37.5, 39.4):
        A.place(sfx, stamp * 0.45, s)
    A.place(sfx, A.glitch(0.12) * 0.2, 43.6)
    sfx = A.reverb(sfx, 0.6, 0.1)

    voice = np.zeros((N, 2))
    for k, t0 in NARR.items():
        v, sr = sf.read(f"{voice_dir}/{k}.wav")
        v = signal.resample_poly(v, SR, sr)
        v = A.filt(v, "highpass", 70, 2)
        v = v + A.filt(v, "bandpass", [2500, 5000], 2) * 0.3
        A.place(voice, np.tanh(v * 2.0) / np.tanh(2.0), t0)
    voice = A.reverb(voice, 0.5, 0.05, 6000)
    ve = A.filt(np.abs(voice).max(1), "lowpass", 5, 1)
    ve = np.clip(ve / (ve.max() + 1e-9) * 3, 0, 1)
    bed = music / np.abs(music).max() * 0.3 + sfx / np.abs(sfx).max() * 0.32
    mixd = bed * (1 - 0.5 * ve)[:, None] + voice / np.abs(voice).max() * 0.95
    tail = int(0.4 * SR)
    mixd[-tail:] *= np.linspace(1, 0, tail)[:, None]
    sf.write(out, (np.tanh(mixd * 1.1) * 0.9).astype(np.float32), SR, subtype="FLOAT")


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
