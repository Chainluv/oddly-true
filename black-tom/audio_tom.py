"""Audio for Black Tom: narration that starts with the first frame, an original low tension score, a ticking clock,
a huge explosion with a rolling rumble, shockwave whooshes, a seismograph scratch, shrapnel pings, a stamp, and a
soft return to the opening drone so the loop sits cleanly."""
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

DUR = 48.0
A.N = N = int(DUR * A.SR)
SR = A.SR
NARR = {"n1": 0.1, "n2": 3.8, "n3": 12.35, "n4": 16.15, "n5": 21.5, "n6": 26.8, "n7": 33.5, "n8": 40.4, "n9": 45.4}
VDUR = {k: sf.info(os.path.join(HERE, "voices", f"{k}.wav")).duration for k in NARR}
BLAST = 12.35


def wt(pid, frac):
    return NARR[pid] + VDUR[pid] * frac


def ping(f=3000, dur=0.25):
    n = int(dur * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * f * t) * np.exp(-t * 30)


def build(out):
    D2, A2, D3, F3, Bb2, C3 = 73.42, 110.0, 146.83, 174.61, 116.54, 130.81
    music = np.zeros((N, 2))
    A.place(music, A.drone(0.0, BLAST, [D2, A2, D3], 450, 0.4, 0.2), 0.0)     # starts on frame 0
    A.place(music, A.tremolo_strings(7.2, BLAST, [293.7, 311.1]) * 0.16, 7.2)
    A.place(music, A.drone(BLAST + 1.0, 33.3, [D2, Bb2, F3 / 2], 380, 0.45, 1.0), BLAST + 1.0)
    for tb in np.arange(16.0, 33.0, 0.6):
        A.place(music, A.thump() * 0.22, tb)
    A.place(music, A.drone(33.3, DUR, [D2, A2, D3, F3], 480, 0.35, 1.0), 33.3)
    for i, f in enumerate([293.66, 349.23, 440.0, 392.0, 349.23]):
        A.place(music, A.piano(f, 4.0) * 0.2, 33.6 + i * 1.4)
    A.place(music, A.boom(1.6) * 0.5, 0.1)
    A.place(music, A.braam(3.0) * 0.5, wt("n6", 0.6))                           # torch closed
    A.place(music, A.boom(2.0) * 0.6, 45.4)
    music = A.reverb(music, 2.8, 0.3)

    sfx = np.zeros((N, 2))
    for k in range(7):                                                          # the 2:08 clock
        A.place(sfx, Z.tick(0.45), 4.0 + k * 0.5)
    A.place(sfx, A.boom(4.0, 70, 20) * 1.0, BLAST)                              # the blast
    A.place(sfx, A.roar(4.0, 60, 1200, 0.4) * 0.6, BLAST + 0.05)
    A.place(sfx, A.filt(A.boom(3.0, 60, 22), "lowpass", 300) * 0.6, BLAST + 1.2)
    rng = np.random.default_rng(2)
    for tc in np.sort(rng.uniform(BLAST + 0.3, BLAST + 3.0, 30)):               # debris crackle
        A.place(sfx, A.pop() * rng.uniform(0.05, 0.15), tc, pan=rng.uniform(-0.8, 0.8))
    for i in range(4):                                                          # shockwave rings
        A.place(sfx, A.whoosh(0.8, 2000, 200) * 0.14, 16.0 + i * 0.7)
    A.place(sfx, A.glitch(0.3) * 0.25, wt("n4", 0.55))                         # windows
    n = int(2.0 * SR)                                                           # seismograph scratch
    A.place(sfx, A.filt(A.noise(n), "bandpass", [1500, 4000]) * A.env_adsr(n, 0.3, 0.5) * 0.08, 21.5)
    A.place(sfx, A.filt(A.boom(1.5, 50, 25), "lowpass", 200) * 0.5, 22.3)
    hit = wt("n6", 0.1)
    for i in range(12):                                                         # shrapnel
        A.place(sfx, ping(rng.uniform(2400, 3800)) * 0.18, hit + i * 0.08 + 0.4, pan=rng.uniform(-0.5, 0.5))
    A.place(sfx, A.clang(2.0) * 0.18, hit + 0.6)
    A.place(sfx, A.paper_slap() * 0.4, wt("n7", 0.45))                          # GERMANY RESPONSIBLE
    for k in range(10):                                                         # 63-year counter
        A.place(sfx, Z.tick(0.25), 40.4 + k * 0.14)
    A.place(sfx, A.whoosh(0.6, 300, 3000) * 0.14, 44.6)                         # back to the torch
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
