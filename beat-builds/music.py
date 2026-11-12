"""Original instrumental for THE BEAT BUILDS ITSELF (86 BPM, D minor), built as separate layers that enter one
by one. Writes the mixed WAV plus events.json (every hit/note time) that drives the animation.
Synthesized with numpy/scipy and the shared NO WAY. synth helpers; no samples, no vocals."""
import json
import os
import sys

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "molasses-flood"))
import audio as A  # noqa: E402  filt, reverb, place, noise, env_adsr, sine_sweep, whoosh
from config import *  # noqa: E402,F401,F403

A.SR = SR
A.N = N = int(DURATION * SR)
T = A.T


# ---------------------------------------------------------------- instruments
def kick(v=1.0):
    n = int(0.45 * SR)
    x = A.sine_sweep(105, 44, n) * A.env_adsr(n, 0.003, 0.2)
    x += A.filt(A.noise(n), "bandpass", [1500, 4000]) * A.env_adsr(n, 0.0005, 0.004) * 0.25
    return np.tanh(x * 1.8) * v


def snare(v=1.0):
    n = int(0.35 * SR)
    x = A.filt(A.noise(n), "bandpass", [1200, 6000]) * A.env_adsr(n, 0.001, 0.09)
    x += np.sin(2 * np.pi * 185 * T(n)) * A.env_adsr(n, 0.001, 0.05) * 0.5
    return A.filt(x, "lowpass", 5000) * v


def hat(v=1.0, open_=False):
    n = int((0.22 if open_ else 0.05) * SR)
    return A.filt(A.noise(n), "highpass", 7500) * A.env_adsr(n, 0.0005, 0.07 if open_ else 0.014) * v


def shaker(v=1.0):
    n = int(0.08 * SR)
    return A.filt(A.noise(n), "bandpass", [5000, 11000]) * A.env_adsr(n, 0.01, 0.02) * v


def crash():
    n = int(2.5 * SR)
    return A.filt(A.noise(n), "highpass", 5000) * A.env_adsr(n, 0.002, 0.8)


def bass(f, dur, v=1.0):
    n = int(dur * SR)
    t = T(n)
    x = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t)
    env = np.minimum(1, t / 0.01) * np.exp(-t / (dur * 1.2)) * np.minimum(1, (dur - t) / 0.03)
    return A.filt(np.tanh(x * 1.4) * env, "lowpass", 600) * v


def epiano(freqs, dur, v=1.0):
    """Rhodes-like FM tone with bell attack and gentle tremolo."""
    n = int((dur + 1.2) * SR)
    t = T(n)
    x = np.zeros(n)
    for k, f in enumerate(freqs):
        idx = 1.8 * np.exp(-t / 0.25)
        x += np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * t)) / (1 + 0.15 * k)
    env = np.minimum(1, t / 0.006) * np.exp(-t / 2.2)
    env *= np.where(t < dur, 1, np.exp(-(t - dur) / 0.3))
    x *= env * (0.85 + 0.15 * np.sin(2 * np.pi * 4.5 * t))
    return A.filt(x, "lowpass", 3200) * v / len(freqs)


def lead(f, dur, v=1.0):
    n = int((dur + 0.4) * SR)
    t = T(n)
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.5 * t) * np.minimum(1, t / 0.3)
    ph = np.cumsum(f * vib) / SR
    x = np.sin(2 * np.pi * ph) + np.sin(2 * np.pi * 3 * ph) / 9 + np.sin(2 * np.pi * 5 * ph) / 25
    env = np.minimum(1, t / 0.03) * np.where(t < dur, 1, np.exp(-(t - dur) / 0.12))
    return A.filt(x * env, "lowpass", 2400) * v


def pad(freqs, dur):
    n = int(dur * SR)
    x = sum(A.filt(np.sign(np.sin(2 * np.pi * f * (1 + d) * T(n))), "lowpass", 900, 2) for f in freqs for d in (-0.003, 0.003))
    t = T(n)
    return x * np.minimum(1, t / 0.6) * np.minimum(1, (dur - t) / 0.6) / (2 * len(freqs))


def click(v=0.4):
    n = int(0.05 * SR)
    return A.filt(A.noise(n), "bandpass", [1500, 6000]) * A.env_adsr(n, 0.0003, 0.006) * v


# ---------------------------------------------------------------- arrangement
def build(wav_out, events_out):
    L = {k: np.zeros((N, 2)) for k in ("drums", "bass", "keys", "lead", "fx", "room")}
    ev = {k: [] for k in ("kick", "snare", "hat", "bass", "chord", "melody", "crash", "shaker")}
    swing = STEP * 0.12

    def st(b, s):  # time of 16th step s in bar b
        return bar(b) + s * STEP + (swing if s % 2 else 0)

    for b in range(15):
        t_bar = bar(b)
        if t_bar >= DURATION:
            break
        drums_on = t_bar < bar(13) + BAR / 2
        for s in range(16):
            t = st(b, s)
            if t >= DURATION:
                continue
            anticip = bar(10) + BAR * 0.5 <= t < PAYOFF  # half-bar drop before the payoff
            if t >= KICK_IN and s in (0, 7, 10) and not anticip and t < bar(13) + BAR / 2:
                A.place(L["drums"], kick(1.0 if s == 0 else 0.8), t)
                ev["kick"].append(t)
            if t >= SNARE_IN and s in (4, 12) and not anticip and t < bar(13) + BAR / 2:
                A.place(L["drums"], snare(0.75), t, pan=-0.05)
                ev["snare"].append(t)
            if t >= HAT_IN and s % 2 == 0 and t < bar(14):
                v = 0.32 if s % 4 == 0 else 0.2
                A.place(L["drums"], hat(v, open_=(s == 14 and t >= PAYOFF)), t, pan=0.25)
                ev["hat"].append(t)
            if PAYOFF <= t < RESET and s % 2 == 1:
                A.place(L["drums"], shaker(0.12), t, pan=-0.3)
                ev["shaker"].append(t)
        _, voicing, root = CHORDS[b % 4]
        # bass: root on 1, octave pickup, fifth; ends at bar 13.5
        if BASS_IN <= t_bar < bar(13) + 0.01:
            for s, mult, ln in ((0, 1, 5), (6, 2, 2), (10, 1, 3), (14, 1.5, 2)):
                t = st(b, s)
                if b == 13 and s > 6:
                    break
                A.place(L["bass"], bass(root * mult, ln * STEP * 0.95, 0.9), t)
                ev["bass"].append([t, ln * STEP, root * mult])
        # chords: downbeat + lighter re-hit; last chord rings out
        if CHORDS_IN <= t_bar < RESET + 0.01:
            A.place(L["keys"], epiano(voicing, BAR * 0.6, 1.0), t_bar)
            ev["chord"].append([t_bar, b % 4])
            if t_bar < RESET:
                A.place(L["keys"], epiano(voicing[1:], BAR * 0.3, 0.55), st(b, 10))
                ev["chord"].append([st(b, 10), b % 4])
        # melody (2-bar motif), with an echo
        if MELODY_IN <= t_bar < RESET and (b - 8) % 2 == 0:
            for off, ln, f in MOTIF:
                t = t_bar + off * STEP + (swing if off % 2 else 0)
                if t >= RESET:  # melody is the first layer to drop out
                    continue
                note = lead(f, ln * STEP, 0.5)
                A.place(L["lead"], note, t, pan=0.15)
                A.place(L["lead"], note * 0.28, t + 3 * STEP, pan=-0.35)
                if t_bar >= PAYOFF:  # harmony a third below in the payoff
                    A.place(L["lead"], lead(f * 0.8409, ln * STEP, 0.25), t, pan=-0.15)
                ev["melody"].append([t, ln * STEP, f])
    # payoff extras
    A.place(L["fx"], A.whoosh(1.4, 300, 7000) * 0.25, PAYOFF - 1.4)
    A.place(L["fx"], crash() * 0.35, PAYOFF)
    ev["crash"].append(PAYOFF)
    for b in (11, 12):
        A.place(L["keys"], pad(CHORDS[b % 4][1], BAR), bar(b))
    # final chord rings out into the rain
    A.place(L["keys"], epiano(CHORDS[0][1], 2.2, 0.9), FINAL_CHORD)
    ev["chord"].append([FINAL_CHORD, 0])
    # room: rain, record clicks, vinyl crackle
    rain = A.filt(A.noise(N), "bandpass", [600, 6000], 2) * 0.12
    drops = np.zeros(N)
    r = np.random.default_rng(2)
    drops[r.integers(0, N, 2500)] = r.uniform(-1, 1, 2500)
    rain += A.filt(drops, "bandpass", [2000, 8000]) * 0.5
    A.place(L["room"], rain * 0.35, 0.0)
    A.place(L["fx"], click(0.5), 1.0)                       # soft mechanical click: the record starts to lower
    A.place(L["fx"], A.filt(kick(0.3), "lowpass", 300), RECORD_LAND)  # record settles on the platter
    A.place(L["fx"], click(0.4), RECORD_LAND + 0.05)
    A.place(L["fx"], click(0.4), RECORD_LIFT)
    cr = np.zeros(N)
    cr[r.integers(int(RECORD_LAND * SR), int(RECORD_LIFT * SR), 1400)] = r.uniform(-1, 1, 1400)
    A.place(L["room"], A.filt(cr, "highpass", 1500) * 0.25, 0.0)

    gains = {"drums": 0.85, "bass": 0.75, "keys": 0.6, "lead": 0.42, "fx": 0.4, "room": 0.5}
    mix = np.zeros((N, 2))
    for k, buf in L.items():
        wet = A.reverb(buf, 1.8, {"drums": 0.12, "keys": 0.3, "lead": 0.35, "fx": 0.2}.get(k, 0.05))
        mix += wet * gains[k]
    lift = np.interp(T(N), [PAYOFF - 0.05, PAYOFF, RESET, RESET + 1.5], [1.0, 1.25, 1.25, 1.0])
    mix *= lift[:, None]  # the full groove sits a little louder
    tail = int(1.2 * SR)  # gentle fade, no abrupt cut
    mix[-tail:] *= np.linspace(1, 0, tail)[:, None] ** 1.5
    mix = np.tanh(mix * 1.2) * 0.85
    sf.write(wav_out, mix.astype(np.float32), SR, subtype="FLOAT")
    with open(events_out, "w") as f:
        json.dump(ev, f)


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "events.json"))
