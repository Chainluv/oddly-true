"""Audio for the Bonus Army episode: serious narration with pauses, an original low string/drone score,
restrained effects (march, gas hiss, fire). All synthesized with the shared molasses-flood synths."""
import os
import sys
import numpy as np
import soundfile as sf
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "molasses-flood"))
import audio as A  # noqa: E402

DUR = 65.0
A.N = N = int(DUR * A.SR)
SR = A.SR
NARR = {"n01": 0.3, "n02": 6.0, "n03": 11.0, "n04": 14.2, "n05": 18.2, "n06": 22.4, "n07": 25.2, "n08": 28.0,
        "n09": 31.4, "n10": 33.9, "n11": 36.2, "n12": 41.8, "n13": 44.3, "n14": 46.3, "n15": 48.5, "n16": 52.4,
        "n17": 60.0, "n18": 63.8}  # matches bonus.py


def build(voice_dir, out):
    D2, A2, D3, F3, C3 = 73.42, 110.0, 146.83, 174.61, 130.81
    music = np.zeros((N, 2))
    A.place(music, A.drone(0.0, 16.4, [D2, A2, D3], 450, 0.4, 1.5), 0.0)
    A.place(music, A.drone(16.2, 35.9, [D2, A2, F3], 480, 0.4, 0.8), 16.2)
    A.place(music, A.tremolo_strings(35.8, 46.2, [293.7, 311.1, 440.0]) * 0.22, 35.8)   # tension, July 28
    A.place(music, A.drone(35.8, 46.3, [36.7, D2, A2], 380, 0.5, 0.6), 35.8)
    A.place(music, A.drone(46.0, 59.6, [D2, F3 / 2, C3], 420, 0.35, 1.0), 46.0)
    for tn, f in [(46.2, 293.66), (47.6, 261.63), (49.0, 220.0), (60.2, 293.66), (61.6, 349.23), (63.0, 220.0)]:
        A.place(music, A.piano(f, 4.0) * 0.28, tn)
    A.place(music, A.drone(59.4, 65.0, [D2, A2, D3], 400, 0.35, 0.5), 59.4)
    A.place(music, A.boom(1.8, 80, 30) * 0.5, 63.8)
    music = A.reverb(music, 3.0, 0.3)

    sfx = np.zeros((N, 2))
    A.place(sfx, A.wind(DUR) * 0.08, 0.0)
    for k in range(10):                                                          # boots marching (open + troops)
        A.place(sfx, A.filt(A.boom(0.2, 160, 80), "lowpass", 700) * 0.12, 0.5 + k * 0.55)
    A.place(sfx, A.whoosh(0.5, 300, 3000) * 0.15, 15.9)
    A.place(sfx, A.paper_slap() * 0.25, 16.4)
    stampfx = A.filt(A.boom(0.5, 140, 60), "lowpass", 800)
    for s in (32.2, 34.6, 55.6, 57.4):
        A.place(sfx, stampfx * 0.5, s)
    for k in range(14):
        A.place(sfx, A.filt(A.boom(0.2, 160, 80), "lowpass", 700) * 0.14, 40.2 + k * 0.42, pan=0.3)
    n = int(4.0 * SR)
    A.place(sfx, A.filt(A.noise(n), "bandpass", [2500, 9000]) * A.env_adsr(n, 0.6, 2.0) * 0.15, 41.6)  # gas hiss
    n = int(6.0 * SR)
    crackle = np.zeros(n)
    idx = A.rng.integers(0, n, 600)
    crackle[idx] = A.rng.uniform(-1, 1, 600)
    fire = A.filt(crackle, "bandpass", [800, 5000]) + A.filt(A.noise(n), "lowpass", 300) * 0.4
    A.place(sfx, fire * np.minimum(1, A.T(n) / 1.0) * np.minimum(1, (6.0 - A.T(n)) / 2.0) * 0.25, 44.0)
    A.place(sfx, A.whoosh(0.6, 300, 3000) * 0.12, 51.2)
    A.place(sfx, A.paper_slap() * 0.25, 51.6)
    sfx = A.reverb(sfx, 1.5, 0.15)

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
    bed = music / np.abs(music).max() * 0.36 + sfx / np.abs(sfx).max() * 0.35
    mixd = bed * (1 - 0.45 * ve)[:, None] + voice / np.abs(voice).max() * 0.95
    tail = int(0.5 * SR)
    mixd[-tail:] *= np.linspace(1, 0, tail)[:, None]
    sf.write(out, (np.tanh(mixd * 1.1) * 0.9).astype(np.float32), SR, subtype="FLOAT")


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
