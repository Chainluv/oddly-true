"""Audio for the Tesla-name episode: conversational narration, a subtle original pad + pulse, restrained electrical
hum and an induction-motor whine that spins up with the rotor. All synthesized with the shared NO WAY. synths."""
import os
import sys
import numpy as np
import soundfile as sf
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__))
for sub in ("eiffel-con", "rap-grammy", "molasses-flood"):
    sys.path.insert(0, os.path.join(HERE, "..", sub))
import audio as A  # noqa: E402
import audio_eiffel as E  # noqa: E402  (pluck)

DUR = 45.0
A.N = N = int(DUR * A.SR)
SR = A.SR
NARR = {"n01": 0.2, "n02": 3.0, "n03": 7.0, "n04": 11.5, "n05": 15.1, "n06": 20.8, "n07": 25.4, "n08": 30.9,
        "n09": 37.5, "n10": 43.6}  # matches tesla.py


def build(voice_dir, out):
    t = A.T(N)
    music = np.zeros((N, 2))
    A.place(music, A.drone(0.0, DUR, [146.83, 220.0, 293.66], 1100, 0.3, 1.5), 0.0)
    step = 60 / 104 / 2
    notes = [293.66, 440.0, 349.23, 440.0, 293.66, 392.0, 349.23, 329.63]
    tt, i = 0.4, 0
    while tt < DUR - 1.2:
        A.place(music, E.pluck(notes[i % 8] * 2, 0.35) * 0.18, tt, pan=0.3 * np.sin(i))
        tt += step
        i += 1
    A.place(music, A.boom(1.6, 80, 30) * 0.45, 43.6)
    music = A.reverb(music, 2.5, 0.35, 6000)

    sfx = np.zeros((N, 2))
    hum = (np.sin(2 * np.pi * 60 * t) + 0.5 * np.sin(2 * np.pi * 120 * t) + 0.25 * np.sin(2 * np.pi * 180 * t))
    hum_env = np.interp(t, [0, 15, 16, 25, 26, 35, 36, 45], [0, 0, 0.5, 0.5, 1.0, 1.0, 0.3, 0.2])
    A.place(sfx, hum * hum_env * 0.05, 0.0)
    # motor whine: pitch follows the rotor speed (spins up 26-28s, steady, drives the wheels 31-35s)
    speed = np.interp(t, [0, 25.8, 28.0, 35.0, 36.5, 45], [0, 0, 1.0, 1.0, 0.0, 0.0])
    ph = np.cumsum(180 + 900 * speed) / SR
    whine = (np.sin(2 * np.pi * ph) + 0.3 * np.sin(2 * np.pi * 2 * ph)) * speed
    A.place(sfx, A.filt(whine, "lowpass", 3000) * 0.12, 0.0)
    for s in (0.0, 6.85, 14.85, 24.85, 34.85):
        A.place(sfx, A.whoosh(0.4, 400, 4000) * 0.15, s)
    A.place(sfx, A.pop() * 0.25, 3.0)                       # the cross-out
    for s in (7.3, 11.8):
        A.place(sfx, A.paper_slap() * 0.2, s)               # timeline entries
    A.place(sfx, A.whoosh(1.2, 300, 2000) * 0.12, 19.6)     # sketch becomes diagram
    sfx = A.reverb(sfx, 0.8, 0.1)

    voice = np.zeros((N, 2))
    for k, t0 in NARR.items():
        v, sr = sf.read(f"{voice_dir}/{k}.wav")
        v = signal.resample_poly(v, SR, sr)
        v = A.filt(v, "highpass", 70, 2)
        v = v + A.filt(v, "bandpass", [2500, 5000], 2) * 0.3
        A.place(voice, np.tanh(v * 2.0) / np.tanh(2.0), t0)
    voice = A.reverb(voice, 0.8, 0.06, 5000)
    ve = A.filt(np.abs(voice).max(1), "lowpass", 4, 1)
    ve = np.clip(ve / (ve.max() + 1e-9) * 3, 0, 1)
    bed = music / np.abs(music).max() * 0.3 + sfx / np.abs(sfx).max() * 0.32
    mixd = bed * (1 - 0.4 * ve)[:, None] + voice / np.abs(voice).max() * 0.95
    tail = int(0.5 * SR)
    mixd[-tail:] *= np.linspace(1, 0, tail)[:, None]
    sf.write(out, (np.tanh(mixd * 1.1) * 0.9).astype(np.float32), SR, subtype="FLOAT")


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
