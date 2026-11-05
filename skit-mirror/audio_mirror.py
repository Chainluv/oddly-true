"""Audio for the mirror skit: dialogue (barber phone-filtered), quiet bathroom ambience, light-switch clicks,
one dramatic sting, phone ring. No music bed and no laugh track. All synthesized."""
import os
import sys
import numpy as np
import soundfile as sf
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__))
for sub in ("skit-detailer", "molasses-flood"):
    sys.path.insert(0, os.path.join(HERE, "..", sub))
import audio as A  # noqa: E402
import audio_skit as AS  # noqa: E402  (ring)
import mirror as M  # noqa: E402

A.N = N = int(M.DURATION * A.SR)
SR = A.SR


def click(level=0.4):
    n = int(0.05 * SR)
    return A.filt(A.noise(n), "bandpass", [1500, 6000]) * A.env_adsr(n, 0.0003, 0.006) * level


def build(out):
    voice = np.zeros((N, 2))
    for lid, spk, t0, _ in M.sk.LINES:
        v, sr = sf.read(os.path.join(M.sk.VOICE_DIR, f"{lid}.wav"))
        v = signal.resample_poly(v, SR, sr)
        v = A.filt(v, "highpass", 80, 2)
        if spk == "F":
            v = np.tanh(A.filt(v, "bandpass", [320, 3400], 4) * 3) * 0.6
        else:
            v = np.tanh((v + A.filt(v, "bandpass", [2500, 5000], 2) * 0.3) * 2) / np.tanh(2)
        A.place(voice, v, t0)
    voice = A.reverb(voice, 0.6, 0.12, 5000)  # small tiled room

    amb = np.zeros((N, 2))
    t = A.T(N)
    fan = A.filt(A.noise(N), "lowpass", 400) * 0.6 + np.sin(2 * np.pi * 120 * t) * 0.05
    A.place(amb, fan * 0.05, 0.0)                                                     # exhaust fan hum
    for k in range(5):                                                                # occasional faucet drip
        n = int(0.12 * SR)
        drip = A.sine_sweep(900, 1600, n) * A.env_adsr(n, 0.002, 0.03)
        A.place(amb, drip * 0.05, 2.5 + k * 4.3, pan=0.5)
    A.place(amb, A.filt(A.noise(int(1.4 * SR)), "bandpass", [800, 3000]) * 0.03, 0.1)  # hand rubbing hair
    A.place(amb, click(), M.LIGHT_OFF)
    A.place(amb, click(), M.LIGHT_ON)
    # the one dramatic sting
    A.place(amb, A.boom(1.6, 90, 30) * 0.55, M.LIGHT_ON + 0.05)
    for k, f in enumerate((146.83, 138.59, 130.81)):
        A.place(amb, A.piano(f, 1.2) * 0.3, M.LIGHT_ON + 0.05 + k * 0.28)
    for k in range(2):
        A.place(amb, AS.ring() * 0.35, M.RING_T + k * 0.55)
    A.place(amb, A.pop() * 0.12, M.ANSWER_T)
    A.place(amb, A.whoosh(0.25, 400, 3000) * 0.12, M.RAISE_T)
    A.place(amb, A.whoosh(0.25, 3000, 400) * 0.12, M.LOWER_T - 0.1)

    ve = A.filt(np.abs(voice).max(1), "lowpass", 5, 1)
    ve = np.clip(ve / (ve.max() + 1e-9) * 3, 0, 1)
    mixd = amb / np.abs(amb).max() * 0.35 * (1 - 0.4 * ve)[:, None] + voice / np.abs(voice).max() * 0.95
    cut = int(M.CUT_T * SR)
    mixd[cut:] *= 0.0  # hard cut to black: silence
    sf.write(out, (np.tanh(mixd * 1.1) * 0.9).astype(np.float32), SR, subtype="FLOAT")


if __name__ == "__main__":
    build(sys.argv[1])
