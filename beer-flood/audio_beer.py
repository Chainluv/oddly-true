"""Audio for the London Beer Flood episode: conversational opening that turns sober, a subtle original score,
wood cracking, metal (hoop) strain, rushing liquid. No party music, no cheering. All synthesized."""
import os
import sys
import numpy as np
import soundfile as sf
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "molasses-flood"))
import audio as A  # noqa: E402

DUR = 50.0
A.N = N = int(DUR * A.SR)
SR = A.SR
NARR = {"n01": 0.15, "n02": 2.25, "n03": 4.9, "n04": 10.3, "n05": 14.7, "n06": 20.6, "n07": 26.2, "n08": 29.0,
        "n09": 32.6, "n10": 35.6, "n11": 40.6, "n12": 45.1, "n13": 48.4}  # matches beer.py
T_BURST, T_DIED = 9.3, 32.6


def crack():
    n = int(0.5 * SR)
    x = np.zeros(n)
    for k in range(A.rng.integers(4, 8)):
        i = int(A.rng.uniform(0, 0.2) * SR)
        L = int(0.04 * SR)
        x[i:i + L] += A.filt(A.noise(L), "bandpass", [600, 4000]) * np.exp(-A.T(L) / 0.008) * A.rng.uniform(0.4, 1)
    x += A.filt(A.noise(n), "lowpass", 300) * A.env_adsr(n, 0.002, 0.12) * 0.6
    return x / np.abs(x).max()


def build(voice_dir, out):
    D2, A2, D3, F3, C3 = 73.42, 110.0, 146.83, 174.61, 130.81
    t = A.T(N)
    music = np.zeros((N, 2))
    A.place(music, A.drone(0.0, 20.6, [D2, A2, D3], 480, 0.35, 0.6), 0.0)
    A.place(music, A.tremolo_strings(14.5, 29.0, [293.7, 311.1, 440.0]) * 0.18, 14.5)
    A.place(music, A.drone(20.4, 50.0, [36.7, D2, F3 / 2, A2], 420, 0.45, 1.0), 20.4)
    for tn, f in [(35.8, 293.66), (37.4, 261.63), (39.0, 220.0), (44.9, 293.66), (46.5, 349.23), (48.0, 220.0)]:
        A.place(music, A.piano(f, 4.0) * 0.26, tn)
    A.place(music, A.boom(1.6, 80, 30) * 0.45, 48.4)
    music = A.reverb(music, 3.0, 0.3)
    # music lowers for "Eight people died" and lets it register
    music *= np.interp(t, [0, T_DIED - 0.4, T_DIED + 0.2, 35.4, 36.4, DUR], [1, 1, 0.45, 0.45, 1, 1])[:, None]

    sfx = np.zeros((N, 2))
    flow = A.roar(3.2, 120, 2200)
    A.place(sfx, flow * np.linspace(0.3, 1.0, len(flow)) * 0.6, 0.0)                    # hook surge
    A.place(sfx, A.whoosh(0.5, 3000, 300) * 0.2, 3.0)
    A.place(sfx, A.groan(1.8) * 0.4, T_BURST - 2.0)                                    # iron hoops straining
    A.place(sfx, crack() * 0.7, T_BURST)                                              # staves split
    A.place(sfx, A.clang(1.5) * 0.25, T_BURST + 0.05)                                 # hoop snaps
    gush = A.roar(5.0, 100, 2500)
    A.place(sfx, gush * np.minimum(1, A.T(len(gush)) / 0.2) * np.linspace(1, 0.5, len(gush)) * 0.6, T_BURST + 0.05)
    for s in (11.2, 12.4):
        A.place(sfx, crack() * 0.4, s)                                                # neighbouring containers
    A.place(sfx, A.filt(A.roar(5.0, 80, 900), "lowpass", 900) * 0.35, 14.5)          # volume spreading
    w = A.roar(4.2, 100, 2600)
    A.place(sfx, w * np.linspace(0.4, 1, len(w)) * 0.7, 20.4)                        # the wave
    A.place(sfx, A.boom(1.2, 90, 30) * 0.4, 24.4)
    A.place(sfx, A.wind(14.0) * 0.08, 29.0)                                           # aftermath: quiet
    for s in (36.2, 37.6, 39.0, 44.8):
        A.place(sfx, A.whoosh(0.35, 400, 3000) * 0.1, s - 0.1)
    sfx = A.reverb(sfx, 1.4, 0.15)

    voice = np.zeros((N, 2))
    for k, t0 in NARR.items():
        v, sr = sf.read(f"{voice_dir}/{k}.wav")
        v = signal.resample_poly(v, SR, sr)
        v = A.filt(v, "highpass", 70, 2)
        v = v + A.filt(v, "bandpass", [2500, 5000], 2) * 0.3
        A.place(voice, np.tanh(v * 2.0) / np.tanh(2.0), t0)
    voice = A.reverb(voice, 0.8, 0.07, 5000)
    ve = A.filt(np.abs(voice).max(1), "lowpass", 4, 1)
    ve = np.clip(ve / (ve.max() + 1e-9) * 3, 0, 1)
    bed = music / np.abs(music).max() * 0.32 + sfx / np.abs(sfx).max() * 0.38
    mixd = bed * (1 - 0.45 * ve)[:, None] + voice / np.abs(voice).max() * 0.95
    tail = int(0.5 * SR)
    mixd[-tail:] *= np.linspace(1, 0, tail)[:, None]
    sf.write(out, (np.tanh(mixd * 1.1) * 0.9).astype(np.float32), SR, subtype="FLOAT")


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
