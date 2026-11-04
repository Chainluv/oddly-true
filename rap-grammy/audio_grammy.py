"""NO WAY. #6 audio: an original 90 BPM boom-bap beat (synthesized drums and bass, no samples, nothing taken from
the real song) plus the molasses-flood synths/mix chain. Cleared for every platform."""
import os
import sys
import numpy as np
import soundfile as sf
from scipy import signal

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "molasses-flood"))
import audio as A  # noqa: E402

NARR = {"l1": 0.1, "l2": 3.1, "l3": 8.3, "l4": 12.1, "l5": 16.0, "l6": 17.45, "l7": 18.6}
BPM = 90
STEP = 60 / BPM / 4


def kick():
    n = int(0.4 * A.SR)
    return np.tanh(A.sine_sweep(140, 45, n) * A.env_adsr(n, 0.002, 0.12) * 2.5)


def snare():
    n = int(0.3 * A.SR)
    x = A.filt(A.noise(n), "bandpass", [1200, 7000]) * A.env_adsr(n, 0.001, 0.07)
    x += np.sin(2 * np.pi * 190 * A.T(n)) * A.env_adsr(n, 0.001, 0.05) * 0.6
    return x


def hat(open_=False):
    n = int((0.25 if open_ else 0.06) * A.SR)
    return A.filt(A.noise(n), "highpass", 7000) * A.env_adsr(n, 0.0005, 0.08 if open_ else 0.015)


def bass(f, dur):
    n = int(dur * A.SR)
    t = A.T(n)
    x = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t)
    return np.tanh(x * 1.5) * A.env_adsr(n, 0.01, dur * 0.6)


def beat(buf, t0, t1, level=1.0):
    K, S, Hc, Ho = kick(), snare(), hat(), hat(True)
    bassline = {0: 73.42, 6: 73.42, 10: 87.31, 14: 65.41}  # D, D, F, C (original pattern)
    step = 0
    t = t0
    while t < t1:
        s = step % 16
        swing = 0.018 if s % 2 else 0.0
        if s in (0, 7, 10):
            A.place(buf, K * 0.9 * level, t + swing)
        if s in (4, 12):
            A.place(buf, S * 0.55 * level, t + swing)
        if s % 2 == 0:
            A.place(buf, (Ho if s == 14 else Hc) * 0.25 * level, t + swing, pan=0.3)
        if s in bassline:
            A.place(buf, bass(bassline[s], STEP * 3.5) * 0.45 * level, t)
        step += 1
        t += STEP


def build(voice_dir, out):
    N, SR = A.N, A.SR
    music = np.zeros((N, 2))
    sfx = np.zeros((N, 2))
    beat(music, 0.0, 16.0)
    beat(music, FLIP_T := 17.45, 18.6, 0.8)
    A.place(music, A.drone(0.0, 20.0, [73.42, 110.0], 600, 0.12, 1.0), 0.0)          # soft pad
    A.place(music, A.boom(1.8, 80, 30) * 0.7, 18.6)
    A.place(music, A.drone(18.6, 20.0, [36.7, 73.42, 110.0], 380, 0.3, 0.05), 18.6)
    crackle = np.zeros(N)
    idx = A.rng.integers(0, N, 900)
    crackle[idx] = A.rng.uniform(-1, 1, 900)
    A.place(music, A.filt(crackle, "highpass", 2000) * 0.15, 0.0)                     # vinyl crackle
    music = A.reverb(music, 1.2, 0.12)
    A.place(sfx, A.filt(A.boom(0.5, 140, 60), "lowpass", 800) * 0.6, 1.6)              # stamp
    A.place(sfx, A.whoosh(0.35, 400, 4000) * 0.2, 2.85)
    A.place(sfx, A.whoosh(0.5, 2500, 300) * 0.25, 3.0)                                 # sleeve slides in
    A.place(sfx, A.whoosh(0.35, 400, 4000) * 0.2, 7.85)
    n = int(0.6 * SR)
    A.place(sfx, A.filt(A.noise(n), "bandpass", [2000, 9000]) * A.env_adsr(n, 0.005, 0.12) * 0.15, 8.0)  # TV static
    A.place(sfx, A.filt(A.boom(0.5, 140, 60), "lowpass", 800) * 0.6, 9.6)              # NOT TELEVISED stamp
    A.place(sfx, A.whoosh(0.35, 400, 4000) * 0.2, 11.85)
    A.place(sfx, A.whoosh(0.6, 3000, 400) * 0.18, 12.9)                                # they turn away
    A.place(sfx, A.whoosh(0.3, 300, 5000) * 0.3, FLIP_T - 0.1)                         # name flip
    A.place(sfx, A.glitch(0.12) * 0.2, 18.55)
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
    bed = music / np.abs(music).max() * 0.4 + sfx / np.abs(sfx).max() * 0.4
    mixd = bed * (1 - 0.5 * ve)[:, None] + voice / np.abs(voice).max() * 0.95
    tail = int(0.3 * SR)
    mixd[-tail:] *= np.linspace(1, 0, tail)[:, None]
    sf.write(out, (np.tanh(mixd * 1.1) * 0.9).astype(np.float32), SR, subtype="FLOAT")


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
