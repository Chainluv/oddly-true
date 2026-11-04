"""Audio for the detailer skit: two voices (friend phone-filtered), shop sound design and a quiet original lo-fi beat.
Everything is synthesized here or by the shared NO WAY. synths, so it is cleared for every platform."""
import os
import sys
import numpy as np
import soundfile as sf
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "rap-grammy"))
sys.path.insert(0, os.path.join(HERE, "..", "molasses-flood"))
import audio as A  # noqa: E402
import audio_grammy as G  # noqa: E402
import skit  # noqa: E402

A.N = N = int(30.0 * A.SR)
SR = A.SR


def vacuum(dur, spin_up=0.25, spin_down=0.4):
    n = int(dur * SR)
    t = A.T(n)
    ramp = np.minimum(1, t / spin_up) * np.minimum(1, (dur - t) / spin_down)
    f = 150 * (0.6 + 0.4 * ramp)
    motor = A.filt(np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)), "lowpass", 900, 2)
    whine = A.filt(A.noise(n), "bandpass", [2200, 3600], 2) * 0.8
    air = A.filt(A.noise(n), "bandpass", [400, 6000], 2) * 0.6
    x = (motor * 0.5 + whine + air) * ramp
    return x / np.abs(x).max()


def ring():
    n = int(0.5 * SR)
    t = A.T(n)
    x = (np.sin(2 * np.pi * 440 * t) + np.sin(2 * np.pi * 480 * t)) * (np.sin(2 * np.pi * 20 * t) > 0)
    return x * np.minimum(1, t / 0.01) * np.minimum(1, (0.5 - t) / 0.05) * 0.5


def scrub(dur, rate=4.5):
    n = int(dur * SR)
    t = A.T(n)
    x = A.filt(A.noise(n), "bandpass", [1500, 7000]) * (0.4 + 0.6 * np.abs(np.sin(np.pi * rate * t)))
    return x


def build(out):
    voice = np.zeros((N, 2))
    for lid, spk, t0, _ in skit.LINES:
        v, sr = sf.read(os.path.join(skit.VOICE_DIR, f"{lid}.wav"))
        v = signal.resample_poly(v, SR, sr)
        v = A.filt(v, "highpass", 80, 2)
        if spk == "F":  # phone line: band-limited, slightly crunchy
            v = np.tanh(A.filt(v, "bandpass", [320, 3400], 4) * 3) * 0.6
            A.place(voice, v, t0, pan=0.0)
        else:
            v = v + A.filt(v, "bandpass", [2500, 5000], 2) * 0.3
            A.place(voice, np.tanh(v * 2) / np.tanh(2), t0)
    voice = A.reverb(voice, 0.5, 0.06, 6000)  # small room

    sfx = np.zeros((N, 2))
    A.place(sfx, A.filt(A.noise(N), "lowpass", 300) * 0.04, 0.0)                     # shop room tone
    A.place(sfx, vacuum(3.1, 0.05, 0.05) * 0.9, 0.0)                                  # hook: already running hard
    A.place(sfx, A.filt(vacuum(2.9, 0.05, 0.6), "lowpass", 1500) * 0.35, 3.1)         # off-screen, winding down
    A.place(sfx, ring() * 0.5, 0.15)
    A.place(sfx, A.pop() * 0.15, 0.68)                                                # answer click
    A.place(sfx, A.whoosh(0.3, 300, 4000) * 0.3, 2.95)                                # punch-in
    A.place(sfx, A.boom(1.6, 90, 30) * 0.6, 9.9)                                      # dramatic carpet sting
    for k, f in enumerate((146.83, 138.59, 130.81)):
        A.place(sfx, A.piano(f, 1.2) * 0.35, 9.9 + k * 0.3)
    A.place(sfx, A.whoosh(0.3, 300, 4000) * 0.3, 12.5)                                # zoom on "Both, bro."
    A.place(sfx, vacuum(5.4, 0.3, 0.5) * 0.8, 14.4)                                   # same square foot
    A.place(sfx, scrub(1.7) * 0.4, 19.8)                                              # brush
    A.place(sfx, A.filt(A.noise(int(1.7 * SR)), "highpass", 6000) * 0.08, 19.8)       # sand trickle
    A.place(sfx, A.drone(24.0, 28.6, [73.42, 110.0], 500, 0.25, 1.2), 24.0)           # defeated swell
    A.place(sfx, A.boom(1.4, 90, 30) * 0.7, skit.OUTRO_T)
    A.place(sfx, A.glitch(0.15) * 0.25, skit.OUTRO_T)

    music = np.zeros((N, 2))
    G.beat(music, 0.0, 24.0, 0.6)
    music = A.filt(music, "lowpass", 2500, 2)  # lo-fi: dull, quiet

    ve = A.filt(np.abs(voice).max(1), "lowpass", 5, 1)
    ve = np.clip(ve / (ve.max() + 1e-9) * 3, 0, 1)
    duck = (1 - 0.6 * ve)[:, None]
    mixd = sfx / np.abs(sfx).max() * 0.45 * duck + music / np.abs(music).max() * 0.14 * duck + \
        voice / np.abs(voice).max() * 0.95
    end = int(skit.OUTRO_T * SR)
    mixd[end - int(0.02 * SR):end] *= np.linspace(1, 0.2, int(0.02 * SR))[:, None]  # hard cut feel
    tail = int(0.3 * SR)
    mixd[-tail:] *= np.linspace(1, 0, tail)[:, None]
    sf.write(out, (np.tanh(mixd * 1.1) * 0.9).astype(np.float32), SR, subtype="FLOAT")


if __name__ == "__main__":
    build(sys.argv[1])
