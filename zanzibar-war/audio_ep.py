"""NO WAY. #3 audio: reuses the molasses-flood synth/mix functions (all original, synthesized = safe on every platform)."""
import os
import sys
import numpy as np
import soundfile as sf
from scipy import signal

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "molasses-flood"))
import audio as A  # noqa: E402

NARR = {"l1": 0.15, "l2": 4.2, "l3": 8.4, "l4": 12.9, "l5": 15.6, "l6": 18.25, "l7": 19.2}  # match episode.py
SHOTS = [8.55, 8.95, 9.5, 9.9, 10.5, 11.0, 11.6, 12.1]


def tick(level=1.0):
    n = int(0.05 * A.SR)
    x = A.filt(A.noise(n), "bandpass", [2500, 7000]) * A.env_adsr(n, 0.0003, 0.004)
    return x * level


def build(voice_dir, out):
    N, SR = A.N, A.SR
    music = np.zeros((N, 2))
    sfx = np.zeros((N, 2))
    D2, A2, D3, F3 = 73.42, 110.0, 146.83, 174.61
    # score: same palette as episode 1
    A.place(music, A.drone(0.0, 8.1, [D2, A2, D3], 520, 0.45, 0.3), 0.0)
    A.place(music, A.tremolo_strings(4.0, 8.0, [587.3, 880.0]) * 0.18, 4.0, pan=0.2)
    A.place(music, A.drone(8.0, 13.1, [36.7, D2, F3 / 2, A2], 450, 0.5, 0.2), 8.0)
    A.place(music, A.drone(13.0, 15.6, [D2, A2, D3], 500, 0.4, 0.2), 13.0)
    for tn, f in [(15.6, 293.66), (16.4, 349.23), (17.2, 440.0)]:
        A.place(music, A.piano(f) * 0.3, tn)
    A.place(music, A.boom(1.8, 80, 30) * 0.7, 0.12)
    A.place(music, A.boom(2.0) * 0.8, 18.2)
    A.place(music, A.drone(18.2, 20.0, [36.7, D2, A2, F3], 380, 0.35, 0.05), 18.2)
    music = A.reverb(music, 2.8, 0.28)
    # sound design: subtle
    for s in np.arange(1.0, 4.0, 1.0):           # watch ticks, intro
        A.place(sfx, tick(0.5), s)
    A.place(sfx, A.whoosh(0.5, 300, 4000) * 0.25, 3.7)
    A.place(sfx, A.paper_slap() * 0.3, 4.05)
    A.place(sfx, A.wind(5.0) * 0.12, 8.0)        # sea air
    for ts in SHOTS:                              # distant naval guns
        A.place(sfx, A.filt(A.boom(1.6, 70, 28), "lowpass", 900) * 0.55, ts, pan=-0.4)
        A.place(sfx, A.filt(A.boom(1.2, 60, 25), "lowpass", 400) * 0.3, ts + 0.45, pan=0.4)
    A.place(sfx, A.whoosh(0.5, 300, 3000) * 0.25, 12.7)
    for s in np.arange(13.1, 15.0, 0.25):         # fast ticks while the hand sweeps, then silence
        A.place(sfx, tick(0.4), s)
    A.place(sfx, A.pop() * 0.3, 15.0)            # the clock stops
    A.place(sfx, A.projector(4.5) * 0.12, 15.5)
    A.place(sfx, A.glitch(0.12) * 0.2, 18.15)
    sfx = A.reverb(sfx, 1.2, 0.12)
    # narration
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
