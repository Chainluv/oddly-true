"""NO WAY. #7 audio: an original synthesized caper groove (pizzicato bass + snaps) plus the shared
molasses-flood synths and mix chain. No samples, so it is cleared for every platform."""
import os
import sys
import numpy as np
import soundfile as sf
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "rap-grammy"))
sys.path.insert(0, os.path.join(HERE, "..", "molasses-flood"))
import audio as A  # noqa: E402
import audio_grammy as G  # noqa: E402  (kick / snare / hat)

NARR = {"l1": 0.1, "l2": 3.0, "l3": 8.2, "l4": 11.3, "l5": 15.0, "l6": 17.0, "l7": 19.1}
STEP = 60 / 116 / 2  # eighth notes at 116 BPM


def pluck(f, dur=0.22):
    n = int(dur * A.SR)
    t = A.T(n)
    x = sum(a * np.sin(2 * np.pi * f * (k + 1) * t) for k, a in enumerate((1, 0.45, 0.2, 0.1)))
    return x * np.exp(-t / 0.07) * np.minimum(1, t / 0.002)


def caper(buf, t0, t1, level=1.0):
    walk = [73.42, 87.31, 110.0, 130.81, 146.83, 130.81, 110.0, 87.31]  # D F A C D C A F (original line)
    snap = A.filt(G.snare(), "highpass", 1500)
    i, t = 0, t0
    while t < t1:
        A.place(buf, pluck(walk[i % 8]) * 0.7 * level, t)
        if i % 4 == 2:
            A.place(buf, snap * 0.35 * level, t, pan=0.2)
        if i % 2 == 0:
            A.place(buf, G.hat() * 0.12 * level, t, pan=-0.3)
        if i % 8 == 0:
            A.place(buf, G.kick() * 0.5 * level, t)
        i += 1
        t += STEP


def build(voice_dir, out):
    N, SR = A.N, A.SR
    music = np.zeros((N, 2))
    sfx = np.zeros((N, 2))
    caper(music, 0.0, 16.9)
    caper(music, 17.6, 19.0, 0.6)
    A.place(music, A.drone(0.0, 20.0, [73.42, 110.0], 600, 0.1, 1.0), 0.0)
    A.place(music, A.boom(1.8, 80, 30) * 0.6, 19.0)
    A.place(music, A.drone(19.0, 20.0, [36.7, 73.42, 110.0], 380, 0.3, 0.05), 19.0)
    music = A.reverb(music, 1.2, 0.14)
    stampfx = A.filt(A.boom(0.5, 140, 60), "lowpass", 800)
    A.place(sfx, stampfx * 0.6, 1.2)                                                 # SOLD
    A.place(sfx, A.whoosh(0.35, 400, 4000) * 0.2, 2.85)
    A.place(sfx, A.whoosh(0.9, 3000, 1200) * 0.15, 4.6)                              # paper slide
    A.place(sfx, A.paper_slap() * 0.3, 5.55)
    A.place(sfx, stampfx * 0.6, 6.5)                                                 # FAKE
    A.place(sfx, A.whoosh(0.35, 400, 4000) * 0.2, 7.85)
    for k in range(3):
        A.place(sfx, A.paper_slap() * 0.18, 8.4 + k * 0.25)                         # bills
    A.place(sfx, A.whoosh(0.5, 300, 3000) * 0.15, 9.0)
    A.place(sfx, A.whoosh(0.35, 400, 4000) * 0.2, 11.05)
    A.place(sfx, A.pop() * 0.3, 11.7)                                                # suitcase latch
    for k in range(6):                                                               # footsteps
        A.place(sfx, A.filt(A.boom(0.15, 180, 90), "lowpass", 900) * 0.12, 12.0 + k * 0.38, pan=0.4)
    A.place(sfx, A.paper_slap() * 0.25, 15.6)
    A.place(sfx, stampfx * 0.4, 15.9)                                                # HE TRIED AGAIN
    A.place(sfx, A.whoosh(0.35, 400, 4000) * 0.2, 16.85)
    n = int(0.6 * SR)                                                                # bolt clink
    tt = A.T(n)
    clink = sum(np.sin(2 * np.pi * f * tt) * np.exp(-tt / d) for f, d in ((2800, 0.2), (4100, 0.12), (5900, 0.07)))
    A.place(sfx, clink / np.abs(clink).max() * 0.3, 17.05)
    A.place(sfx, A.glitch(0.12) * 0.2, 18.95)
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
    bed = music / np.abs(music).max() * 0.38 + sfx / np.abs(sfx).max() * 0.4
    mixd = bed * (1 - 0.5 * ve)[:, None] + voice / np.abs(voice).max() * 0.95
    tail = int(0.3 * SR)
    mixd[-tail:] *= np.linspace(1, 0, tail)[:, None]
    sf.write(out, (np.tanh(mixd * 1.1) * 0.9).astype(np.float32), SR, subtype="FLOAT")


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
