"""Soundtrack for the long-form Nikola Tesla episode: narration from timeline.json, an original synthesized score
that changes with each chapter, and restrained effects (hum, sparks, fire, tower fall, typing, stamps)."""
import json
import os
import sys

import numpy as np
import soundfile as sf
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__))
for sub in ("eiffel-con", "rap-grammy", "zanzibar-war", "molasses-flood"):
    sys.path.insert(0, os.path.join(HERE, "..", sub))
import audio as A  # noqa: E402
import audio_eiffel as E  # noqa: E402  (pluck)
import audio_ep as Z  # noqa: E402  (tick)

TL = json.load(open(os.path.join(HERE, "timeline.json")))
DUR = TL["duration"]
A.N = N = int(DUR * A.SR)
SR = A.SR
P = {p["id"]: p for p in TL["paragraphs"]}
SEC = TL["sections"]


def st(pid, i=0):
    return P[pid]["sentences"][min(i, len(P[pid]["sentences"]) - 1)][0]


def end(pid):
    return P[pid]["start"] + P[pid]["dur"]


def arp(buf, a, b, notes, step, level, pan=0.3):
    t, i = a, 0
    while t < b - 0.5:
        A.place(buf, E.pluck(notes[i % len(notes)], 0.35) * level, t, pan=pan * np.sin(i))
        t += step
        i += 1


def build(out):
    music = np.zeros((N, 2))
    sfx = np.zeros((N, 2))
    place = A.place
    D2, A2, D3, F3, E3, C3, G2 = 73.42, 110.0, 146.83, 174.61, 164.81, 130.81, 98.0
    t_ = A.T(N)

    a, b = SEC["cold"]  # quiet, mysterious
    place(music, A.drone(a, b, [D2, A2, D3], 500, 0.3, 2.0), a)
    for i, f in enumerate([293.66, 349.23, 440.0, 392.0]):
        place(music, A.piano(f, 4.0) * 0.2, a + 2 + i * 6)
    place(music, A.boom(2.0) * 0.7, SEC["title"][0])
    for c0, _, _ in TL["chapters"]:
        place(sfx, A.whoosh(0.5, 300, 4000) * 0.14, c0 - 0.2)
        place(music, A.boom(1.4, 80, 30) * 0.3, c0)

    a, b = SEC["man"]  # the immigrant: light, curious
    place(music, A.drone(a, b, [D2, A2, F3], 700, 0.3, 1.5), a)
    arp(music, a + 1, b, [587.33, 698.46, 880.0, 698.46], 60 / 96 / 2, 0.12)
    place(sfx, A.paper_slap() * 0.2, P["m4"]["start"] + st("m4", 1) - P["m4"]["start"])
    place(sfx, A.filt(A.boom(0.5, 140, 60), "lowpass", 800) * 0.5, P["m5"]["start"] + 1.0)

    a, b = SEC["motor"]  # the motor: electric hum rising with the rotor
    place(music, A.drone(a, b, [D2, A2, D3, E3], 900, 0.3, 1.0), a)
    hum = (np.sin(2 * np.pi * 60 * t_) + 0.4 * np.sin(2 * np.pi * 120 * t_)) * np.interp(t_, [a, a + 1, b - 1, b], [0, 1, 1, 0])
    place(sfx, hum * 0.03, 0)
    spin = np.interp(t_, [P["o2"]["start"], end("o2"), b, b + 0.5], [0, 1, 1, 0])
    ph = np.cumsum(150 + 700 * spin) / SR
    place(sfx, A.filt(np.sin(2 * np.pi * ph) * spin, "lowpass", 2500) * 0.08, 0)

    a, b = SEC["war"]  # war of the currents: pulse + tension
    place(music, A.drone(a, b, [D2, A2, C3], 500, 0.4, 1.0), a)
    for tb in np.arange(a + 0.5, b - 1, 0.7):
        place(music, A.thump() * 0.3, tb)
    place(music, A.tremolo_strings(P["x2"]["start"], end("x8"), [293.7, 311.1]) * 0.2, P["x2"]["start"])
    for k in range(10):  # sparks in the stage demonstration
        n = int(0.08 * SR)
        place(sfx, A.filt(A.noise(n), "highpass", 3000) * A.env_adsr(n, 0.001, 0.02) * 0.2, P["x9"]["start"] + 0.5 + k * 0.45)
    place(music, A.boom(1.6, 80, 30) * 0.4, P["x6"]["start"])
    place(music, A.braam(3.0) * 0.6, st("x7") + 1.2)  # "should have been rich, right?"

    a, b = SEC["fall"]  # the fall: somber
    place(music, A.drone(a, b, [D2, F3 / 2, A2], 420, 0.4, 1.5), a)
    for i, f in enumerate([440.0, 349.23, 293.66, 261.63, 233.08, 220.0] * 3):
        tt = a + 1.5 + i * 3.8
        if tt < b - 1:
            place(music, A.piano(f, 4.0) * 0.16, tt)
    n = int((end("f7") - P["f7"]["start"]) * SR)  # lab fire crackle
    cr = np.zeros(n)
    cr[A.rng.integers(0, n, 500)] = A.rng.uniform(-1, 1, 500)
    place(sfx, (A.filt(cr, "bandpass", [800, 5000]) + A.filt(A.noise(n), "lowpass", 300) * 0.4) * 0.25, P["f7"]["start"])
    place(sfx, A.creak(1.6, 380) * 0.3, P["f5"]["start"] + st("f5", 1) - P["f5"]["start"] + 0.8)
    place(sfx, A.boom(2.0, 100, 30) * 0.6, P["f5"]["start"] + st("f5", 1) - P["f5"]["start"] + 2.6)
    place(sfx, A.clang(2.0) * 0.25, P["f5"]["start"] + st("f5", 1) - P["f5"]["start"] + 2.6)

    a, b = SEC["myths"]  # myth vs fact: playful-investigative
    place(music, A.drone(a, b, [D2, A2, D3], 800, 0.3, 1.0), a)
    arp(music, a + 0.5, b, [293.66, 349.23, 440.0, 523.25], 60 / 110 / 2, 0.1, 0.4)
    for pid in ("y2", "y3", "y4"):
        place(sfx, A.whoosh(0.4, 600, 5000) * 0.15, P[pid]["start"] + 0.2)
    place(sfx, A.filt(A.boom(0.5, 140, 60), "lowpass", 800) * 0.5, st("y5", 1))

    a, b = SEC["name"]  # the name returns: modern, driving
    place(music, A.drone(a, b, [G2, D3, 246.94], 1400, 0.25, 1.0), a)
    arp(music, a + 0.5, b, [392.0, 493.88, 587.33, 739.99], 60 / 118 / 2, 0.13, 0.5)
    place(sfx, A.filt(A.boom(0.5, 140, 60), "lowpass", 800) * 0.5, st("n4", 1))
    for k in range(9):  # typing the address
        place(sfx, Z.tick(0.3), st("n5", 1) + k * 0.13)

    a, b = SEC["outro"]
    place(music, A.drone(a, b, [D2, A2, D3], 450, 0.35, 2.0), a)
    for i, f in enumerate([293.66, 349.23, 440.0, 392.0, 349.23]):
        place(music, A.piano(f, 4.0) * 0.2, a + 1 + i * 2.8)
    place(music, A.boom(2.0) * 0.7, P["q3"]["start"])
    music = A.reverb(music, 2.8, 0.3)
    sfx = A.reverb(sfx, 1.0, 0.12)

    voice = np.zeros((N, 2))
    for pid, p in P.items():
        v, sr = sf.read(os.path.join(HERE, "voices", f"{pid}.wav"))
        v = signal.resample_poly(v, SR, sr)
        v = A.filt(v, "highpass", 70, 2)
        v = v + A.filt(v, "bandpass", [2500, 5000], 2) * 0.3
        place(voice, np.tanh(v * 2.0) / np.tanh(2.0), p["start"])
    voice = A.reverb(voice, 0.8, 0.06, 5000)
    ve = A.filt(np.abs(voice).max(1), "lowpass", 4, 1)
    ve = np.clip(ve / (ve.max() + 1e-9) * 3, 0, 1)
    bed = music / np.abs(music).max() * 0.3 + sfx / np.abs(sfx).max() * 0.3
    mixd = bed * (1 - 0.5 * ve)[:, None] + voice / np.abs(voice).max() * 0.95
    fade = int(1.2 * SR)
    mixd[-fade:] *= np.linspace(1, 0, fade)[:, None]
    mixd[:int(0.3 * SR)] *= np.linspace(0, 1, int(0.3 * SR))[:, None]
    sf.write(out, (np.tanh(mixd * 1.1) * 0.9).astype(np.float32), SR, subtype="FLOAT")


if __name__ == "__main__":
    build(sys.argv[1])
