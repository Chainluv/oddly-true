"""Audio for the NASA selfie episode: conversational narration, a subtle original space-ambient score
(pad + soft arpeggio), light camera/interface effects. All synthesized with the shared NO WAY. synths."""
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

DUR = 61.0
A.N = N = int(DUR * A.SR)
SR = A.SR
NARR = {"n01": 0.2, "n02": 3.3, "n03": 6.8, "n04": 15.2, "n05": 20.8, "n06": 23.4, "n07": 25.7, "n08": 29.6,
        "n09": 32.6, "n10": 38.0, "n11": 45.4, "n12": 51.8, "n13": 54.4, "n14": 58.0}  # matches nasa.py


def shutter(v=0.4):
    n = int(0.12 * SR)
    x = A.filt(A.noise(n), "bandpass", [1500, 7000]) * (A.env_adsr(n, 0.0005, 0.006) + 0.6 * np.roll(A.env_adsr(n, 0.0005, 0.008), int(0.05 * SR)))
    return x * v


def blip(f=1200, v=0.2):
    n = int(0.12 * SR)
    return np.sin(2 * np.pi * f * A.T(n)) * A.env_adsr(n, 0.002, 0.04) * v


def build(voice_dir, out):
    music = np.zeros((N, 2))
    # lydian-flavoured pad (D, F#, A, C#, G#) + slow arpeggio, quiet and airy
    A.place(music, A.drone(0.0, DUR, [146.83, 220.0, 277.18], 1400, 0.35, 2.0), 0.0)
    arp = [587.33, 739.99, 880.0, 1108.73, 830.61, 880.0, 739.99, 659.25]
    step = 60 / 100 / 2
    t, i = 0.6, 0
    while t < DUR - 1.5:
        lvl = 0.5 if (t < 37.6 or t > 51.2) else 0.65
        A.place(music, E.pluck(arp[i % 8], 0.4) * 0.22 * lvl, t, pan=0.4 * np.sin(i * 0.7))
        t += step
        i += 1
    A.place(music, A.boom(1.8, 80, 30) * 0.45, 58.0)
    music = A.reverb(music, 3.0, 0.4, 6000)

    sfx = np.zeros((N, 2))
    A.place(sfx, shutter(0.45), 1.2)                                           # the selfie
    A.place(sfx, A.whoosh(1.5, 200, 6000) * 0.3, 1.9)                          # push into the lens
    A.place(sfx, A.whoosh(0.8, 5000, 300) * 0.2, 4.3)                          # out to space
    A.place(sfx, A.sine_sweep(900, 300, int(4.5 * SR)) * A.env_adsr(int(4.5 * SR), 0.2, 3) * 0.06, 8.4)  # shrinking
    for k in range(10):
        A.place(sfx, blip(900 + k * 60, 0.07), 16.2 + k * 0.32)               # pixels assembling
    A.place(sfx, blip(1760, 0.25), 20.7)
    A.place(sfx, blip(2200, 0.18), 20.78)                                       # CAMERA ON A CHIP chime
    for t0 in (26.3, 27.6, 28.4):
        A.place(sfx, blip(1300, 0.18), t0)
    A.place(sfx, A.whoosh(0.6, 400, 3000) * 0.15, 33.0)
    A.place(sfx, A.whoosh(0.6, 3000, 400) * 0.15, 37.5)
    A.place(sfx, blip(700, 0.15), 39.6)                                          # call connects
    A.place(sfx, blip(1050, 0.15), 39.75)
    A.place(sfx, shutter(0.35), 41.6)
    A.place(sfx, shutter(0.35), 43.3)
    for k in range(16):                                                         # 17 attempts
        A.place(sfx, shutter(0.22), 54.4 + k * (2.6 / 16))
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
    bed = music / np.abs(music).max() * 0.32 + sfx / np.abs(sfx).max() * 0.38
    mixd = bed * (1 - 0.4 * ve)[:, None] + voice / np.abs(voice).max() * 0.95
    tail = int(0.6 * SR)
    mixd[-tail:] *= np.linspace(1, 0, tail)[:, None]
    sf.write(out, (np.tanh(mixd * 1.1) * 0.9).astype(np.float32), SR, subtype="FLOAT")


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
