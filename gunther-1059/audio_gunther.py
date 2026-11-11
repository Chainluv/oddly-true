"""Audio for the Henry Gunther episode: measured narration, an original restrained score, a ticking clock,
distant battlefield ambience that falls to silence at 11:00. No triumphant ending, no gunshot sting."""
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

DUR = 65.0
A.N = N = int(DUR * A.SR)
SR = A.SR
NARR = {"n01": 0.3, "n02": 3.0, "n03": 7.2, "n04": 10.2, "n05": 14.0, "n06": 18.2, "n07": 22.8, "n08": 28.2,
        "n09": 33.0, "n10": 36.3, "n11": 42.4, "n12": 47.3, "n13": 49.1, "n14": 53.2, "n15": 58.4, "n16": 62.2}
T_1059, T_1100 = 33.5, 43.3


def gain_curve(points):
    t = A.T(N)
    xs, ys = zip(*points)
    return np.interp(t, xs, ys)


def build(voice_dir, out):
    D2, A2, D3, F3, C3 = 73.42, 110.0, 146.83, 174.61, 130.81
    music = np.zeros((N, 2))
    A.place(music, A.drone(0.0, 43.6, [D2, A2, D3], 430, 0.4, 2.0), 0.0)
    A.place(music, A.tremolo_strings(18.0, 33.6, [293.7, 311.1]) * 0.15, 18.0)
    for tn, f in [(47.4, 293.66), (49.2, 261.63), (51.0, 220.0), (53.4, 293.66), (55.4, 349.23), (58.6, 220.0),
                  (60.4, 196.0), (62.4, 146.83)]:
        A.place(music, A.piano(f, 4.5) * 0.26, tn)
    A.place(music, A.drone(47.2, 65.0, [D2, F3 / 2, C3], 380, 0.3, 3.0), 47.2)
    music = A.reverb(music, 3.2, 0.32)
    # music briefly lowers at 10:59, and falls away entirely into the silence at 11:00
    music *= gain_curve([(0, 1), (T_1059, 1), (T_1059 + 0.4, 0.35), (T_1059 + 2.5, 0.35), (T_1059 + 4.0, 0.8),
                         (T_1100, 0.8), (T_1100 + 0.8, 0.0), (47.0, 0.0), (47.4, 1.0), (DUR, 1.0)])[:, None]

    amb = np.zeros((N, 2))
    A.place(amb, A.wind(T_1100 + 1.0) * 0.1, 0.0)
    rng = np.random.default_rng(3)
    for ts in np.sort(rng.uniform(0.5, T_1100 - 0.5, 22)):   # distant artillery, low and soft
        A.place(amb, A.filt(A.boom(1.6, 70, 28), "lowpass", 300) * rng.uniform(0.15, 0.35), ts, pan=rng.uniform(-0.6, 0.6))
    amb *= gain_curve([(0, 1), (T_1100, 1), (T_1100 + 1.0, 0.0), (DUR, 0.0)])[:, None]
    A.place(amb, A.wind(DUR - 47.3) * 0.04, 47.3)            # after the silence, only a faint wind

    ticks = np.zeros((N, 2))
    for s in np.arange(0.0, 7.0, 1.0):
        A.place(ticks, Z.tick(0.45), s + 0.05)
    for s in np.arange(15.6, T_1059, 1.0):
        A.place(ticks, Z.tick(0.35), s)
    for s in np.arange(40.3, T_1100 + 0.01, 1.0):
        A.place(ticks, Z.tick(0.5), s)
    A.place(ticks, A.whoosh(0.5, 400, 3000) * 0.08, 15.3)
    A.place(ticks, A.paper_slap() * 0.2, 9.3)

    voice = np.zeros((N, 2))
    for k, t0 in NARR.items():
        v, sr = sf.read(f"{voice_dir}/{k}.wav")
        v = signal.resample_poly(v, SR, sr)
        v = A.filt(v, "highpass", 70, 2)
        v = v + A.filt(v, "bandpass", [2500, 5000], 2) * 0.3
        A.place(voice, np.tanh(v * 2.0) / np.tanh(2.0), t0)
    voice = A.reverb(voice, 0.9, 0.08, 5000)
    ve = A.filt(np.abs(voice).max(1), "lowpass", 4, 1)
    ve = np.clip(ve / (ve.max() + 1e-9) * 3, 0, 1)
    bed = music / np.abs(music).max() * 0.34 + amb / np.abs(amb).max() * 0.28 + ticks / np.abs(ticks).max() * 0.22
    mixd = bed * (1 - 0.4 * ve)[:, None] + voice / np.abs(voice).max() * 0.95
    tail = int(0.6 * SR)
    mixd[-tail:] *= np.linspace(1, 0, tail)[:, None]
    sf.write(out, (np.tanh(mixd * 1.1) * 0.9).astype(np.float32), SR, subtype="FLOAT")


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
