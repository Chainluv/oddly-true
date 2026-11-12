"""THE BEAT BUILDS ITSELF — renderer. Every motion is driven by events.json (written by music.py) or the tempo map
in config.py, so previews and finals match exactly. Usage:
    python3 beat.py out.mp4 [--preview]          (preview = 540x960)
    python3 beat.py frames_prefix --frames 120 300 ..."""
import bisect
import json
import os
import subprocess
import sys
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "molasses-flood"))
from common import font, smoothstep, ease_in_out, ease_out, lerp, GRAIN  # noqa: E402
from config import *  # noqa: E402,F401,F403

EV = json.load(open(os.path.join(HERE, "events.json")))
KICKS, SNARES, HATS = EV["kick"], EV["snare"], EV["hat"]
BASSN = [b[0] for b in EV["bass"]]
CHORDT = [c[0] for c in EV["chord"]]
MELT = [m[0] for m in EV["melody"]]
OW, OH = 1080, 1920  # set to 540x960 for previews


# ---------------------------------------------------------------- timing helpers
def since(t, times):
    i = bisect.bisect_right(times, t) - 1
    return (t - times[i], i) if i >= 0 else (1e9, -1)


def until(t, times):
    i = bisect.bisect_right(times, t)
    return (times[i] - t) if i < len(times) else 1e9


def env(t, times, decay):
    d, _ = since(t, times)
    return float(np.exp(-d / decay)) if d < 1e8 else 0.0


def camera(t):
    for (t0, z0, x0, y0), (t1, z1, x1, y1) in zip(CAMERA, CAMERA[1:]):
        if t < t1:
            k = ease_in_out((t - t0) / (t1 - t0))
            return lerp(z0, z1, k), lerp(x0, x1, k), lerp(y0, y1, k)
    return CAMERA[-1][1:]


def room_light(t):
    return float(np.interp(t, [0, 3.6, 6, 18, 41.5, 44.6, 45], [0.35, 0.4, 0.7, 1.0, 1.0, 0.35, 0.35]))


# ---------------------------------------------------------------- view (world -> screen)
class V:
    def __init__(self, img, z, cx, cy):
        self.d = ImageDraw.Draw(img, "RGBA")
        self.z, self.cx, self.cy = z, cx, cy
        self.r = OW / 1080

    def P(self, x, y):
        return ((x - self.cx) * self.z * self.r + OW / 2, (y - self.cy) * self.z * self.r + OH / 2)

    def S(self, l):
        return l * self.z * self.r

    def rect(self, x0, y0, x1, y1, fill=None, outline=None, width=1, radius=0):
        a, b = self.P(x0, y0), self.P(x1, y1)
        if radius:
            self.d.rounded_rectangle([a, b], self.S(radius), fill=fill, outline=outline, width=max(1, int(self.S(width))))
        else:
            self.d.rectangle([a, b], fill=fill, outline=outline, width=max(1, int(self.S(width))) if outline else 0)

    def ell(self, x, y, rx, ry, fill=None, outline=None, width=1):
        a, b = self.P(x - rx, y - ry), self.P(x + rx, y + ry)
        self.d.ellipse([a, b], fill=fill, outline=outline, width=max(1, int(self.S(width))) if outline else 0)

    def line(self, pts, fill, width):
        self.d.line([self.P(*p) for p in pts], fill=fill, width=max(1, int(self.S(width))), joint="curve")

    def poly(self, pts, fill):
        self.d.polygon([self.P(*p) for p in pts], fill=fill)


def shade(c, k):
    return tuple(int(min(255, v * k)) for v in c[:3])


# ---------------------------------------------------------------- scene pieces
def wall(v, L):
    v.rect(-400, -400, 1500, DESK_Y, fill=shade(NAVY2, 0.6 + 0.4 * L))
    for i in range(6):  # acoustic panels, right wall
        for j in range(3):
            x, y = 600 + i * 70, 820 + j * 70
            if x < 1060:
                v.rect(x, y, x + 62, y + 62, fill=shade(NAVY, 0.8 + 0.3 * L))


def window(v, t, L):
    x0, y0, x1, y1 = WINDOW
    v.rect(x0 - 18, y0 - 18, x1 + 18, y1 + 18, fill=shade(WOOD, 0.7 + 0.3 * L))
    v.rect(x0, y0, x1, y1, fill=(18, 16, 44))
    rng = np.random.default_rng(1)
    for _ in range(26):  # city lights behind the rain (static)
        bx, by, br = rng.uniform(x0 + 20, x1 - 20), rng.uniform(y0 + 200, y1 - 30), rng.uniform(6, 16)
        col = VIOLET if rng.random() < 0.5 else AMBER
        v.ell(bx, by, br, br, fill=col + (60,))
    rng = np.random.default_rng(2)
    for _ in range(70):  # rain streaks
        rx, sp, ph, ln = rng.uniform(x0, x1), rng.uniform(500, 800), rng.uniform(0, 1), rng.uniform(25, 60)
        ry = y0 + ((t * sp + ph * 1000) % (y1 - y0 + ln)) - ln
        v.line([(rx, max(y0, ry)), (rx - 4, min(y1, ry + ln))], fill=(170, 170, 220, 70), width=2)
    v.line([((x0 + x1) / 2, y0), ((x0 + x1) / 2, y1)], fill=shade(WOOD, 0.8), width=10)
    v.line([(x0, (y0 + y1) / 2), (x1, (y0 + y1) / 2)], fill=shade(WOOD, 0.8), width=10)
    v.rect(x0 - 40, SILL_Y - 10, x1 + 40, SILL_Y + 22, fill=shade(WOOD_HI, 0.6 + 0.4 * L))
    # hi-hat droplets: each falls down the glass and splashes on the sill exactly on its hit
    xs = [x0 + 60, x0 + 170, x0 + 280, x0 + 380, x0 + 120, x0 + 330]
    i0 = bisect.bisect_left(HATS, t - 0.25)
    for i in range(i0, min(len(HATS), i0 + 4)):
        h = HATS[i]
        x = xs[i % len(xs)]
        if h - 0.32 <= t < h:
            k = ((t - (h - 0.32)) / 0.32) ** 2
            y = lerp(SILL_Y - 170, SILL_Y - 12, k)
            v.ell(x, y, 6, 9, fill=(200, 210, 255, 220))
        elif h <= t < h + 0.25:
            a = (t - h) / 0.25
            for s in (-1, 1):
                v.line([(x, SILL_Y - 10), (x + s * 22 * a, SILL_Y - 10 - 26 * a * (1 - a) * 2)], fill=(210, 220, 255, int(230 * (1 - a))), width=3)
            v.ell(x, SILL_Y - 8, 26 * a, 6 * a, outline=(210, 220, 255, int(200 * (1 - a))), width=2)


def lamp(v, L):
    x, y = LAMP
    v.line([(x - 40, y - 220), (x, y - 40)], fill=(40, 36, 40), width=10)
    v.poly([(x - 70, y + 40), (x + 70, y + 40), (x + 40, y - 40), (x - 40, y - 40)], fill=shade((120, 80, 50), 0.6 + 0.5 * L))
    v.ell(x, y + 40, 70, 14, fill=shade(AMBER, 0.4 + 0.6 * L))


def monitors(v, t, L):
    v.rect(600, 700, 1060, 724, fill=shade(WOOD_HI, 0.6 + 0.4 * L))
    push = 6 * env(t, BASSN, 0.12) * (t >= BASS_IN) + 3 * env(t, KICKS, 0.1) * (t >= BASS_IN)
    for (x, y) in MONITORS:
        v.rect(x - 95, y - 140, x + 95, y + 140, fill=(28, 30, 40), radius=12)
        v.ell(x, y - 70, 34, 34, fill=(20, 20, 26), outline=(70, 70, 90), width=3)
        r = 64 + push
        v.ell(x, y + 50, r, r, fill=(24, 24, 30), outline=(90, 90, 110), width=4)
        v.ell(x, y + 50, 22 + push * 0.5, 22 + push * 0.5, fill=(60, 60, 75))


def desk(v, L):
    v.rect(-400, DESK_Y - 110, 1500, DESK_Y, fill=shade(WOOD_HI, 0.55 + 0.45 * L))
    v.rect(-400, DESK_Y, 1500, 1520, fill=shade(WOOD, 0.55 + 0.45 * L))
    v.rect(-400, 1520, 1500, 2400, fill=shade(NAVY, 0.7))


def record_state(t):
    """(height above platter, rotation angle)."""
    if t < 1.0:
        h = 320 + 6 * np.sin(t * 2.2)
    elif t < RECORD_LAND:
        h = lerp(320, 0, ease_in_out((t - 1.0) / (RECORD_LAND - 1.0)))
    elif t < RECORD_LIFT:
        h = 0
    else:
        h = lerp(0, 320, ease_in_out((t - RECORD_LIFT) / 2.2))
    # 33 rpm, spun up after landing, slowed before the lift
    def ang(tt):
        if tt < RECORD_LAND:
            return 0.0
        a = 0.0
        a += 3.46 * max(0, min(tt, RECORD_LIFT - 0.7) - RECORD_LAND - 0.2)
        a += 3.46 * 0.5 * min(0.2, max(0, tt - RECORD_LAND))
        a += 3.46 * 0.5 * max(0, min(tt, RECORD_LIFT) - (RECORD_LIFT - 0.7))
        return a
    return h, ang(t)


def turntable(v, t, L):
    x, y = TURNTABLE
    v.poly([(x - 220, y - 70), (x + 230, y - 70), (x + 250, y + 70), (x - 240, y + 70)], fill=(36, 32, 40))
    v.rect(x - 240, y + 70, x + 250, y + 110, fill=(26, 24, 30))
    glow = env(t, KICKS, 0.18)
    v.ell(x, y, PLATTER_R + 6, 58, fill=(60, 56, 66), outline=AMBER + (int(255 * glow),), width=4)
    # kick beater: felt mallet on an arm, struck from the platter's rotation
    k = env(t, KICKS, 0.09)
    pre = until(t, KICKS)
    lift = 0 if t < KICK_IN - 0.3 else (18 * smoothstep(0.25, 0.0, pre) if pre < 0.25 else 0)
    ang = np.deg2rad(-35 + 30 * (1 - k) - lift)
    bx, by = x + 205, y + 20
    hx, hy = bx + np.cos(ang) * 70, by + np.sin(ang) * 70
    v.rect(x + 180, y + 55, x + 250, y + 75, fill=(120, 40, 40), radius=6)  # mini pad
    v.line([(bx, by - 40), (hx, hy)], fill=(160, 150, 140), width=6)
    v.ell(hx, hy, 14, 14, fill=(230, 220, 200))
    # tonearm
    v.line([(x + 210, y - 60), (x + 170, y - 10), (x + 70, y + 10)], fill=(180, 180, 190), width=7)
    # record (hanging, then spinning)
    h, a = record_state(t)
    ry = y - 6 - h
    if h > 2:
        v.ell(x, y - 2, PLATTER_R * (1 - h / 900), 50 * (1 - h / 900), fill=(0, 0, 0, 90))
    v.ell(x, ry, PLATTER_R - 4, 54, fill=(16, 16, 20))
    for g in (110, 90, 70):
        v.ell(x, ry, g, g * 0.36, outline=(40, 40, 50), width=2)
    v.ell(x, ry, 46, 17, fill=AMBER)
    v.line([(x, ry), (x + np.cos(a) * 46, ry + np.sin(a) * 17)], fill=(80, 40, 20), width=4)
    v.line([(x + np.cos(a + 2.4) * 120, ry + np.sin(a + 2.4) * 43), (x + np.cos(a + 2.7) * 130, ry + np.sin(a + 2.7) * 47)],
           fill=(110, 110, 130), width=3)  # groove glint shows the rotation


def pencil(v, t, L):
    x, y = PENCIL
    if t < SNARE_IN - 0.7:
        ang = 0.0  # lying still
        base = (x + 150, y - 4)
        v.line([(x, y - 4), base], fill=(230, 180, 60), width=14)
        v.line([(x - 22, y - 4), (x, y - 4)], fill=(210, 190, 160), width=10)
        return
    d_since, _ = since(t, SNARES)
    d_until = until(t, SNARES)
    up = min(1.0, d_since / 0.18) * min(1.0, d_until / 0.08)
    stand = smoothstep(SNARE_IN - 0.7, SNARE_IN - 0.3, t)
    ang = np.deg2rad(lerp(0, 58, stand) + 22 * up * (t > SNARE_IN - 0.3))
    tail = (x + np.cos(ang) * 160, y - 4 - np.sin(ang) * 160)
    v.line([(x, y - 4), tail], fill=(230, 180, 60), width=14)
    v.line([(x, y - 4), (x + np.cos(ang) * 22, y - 4 - np.sin(ang) * 22)], fill=(210, 190, 160), width=10)
    v.ell(tail[0], tail[1], 8, 8, fill=(220, 120, 130))
    k = env(t, SNARES, 0.12)
    if k > 0.05:
        v.ell(x, y - 2, 30 * (1.3 - k), 8 * (1.3 - k), outline=CREAM + (int(220 * k),), width=2)


def mixer(v, t, L):
    x0, y0, x1, y1 = MIXER
    v.rect(x0, y0, x1, y1, fill=(34, 34, 44), radius=8)
    lv = [env(t, KICKS, 0.25), env(t, SNARES, 0.25), env(t, BASSN, 0.3) * (t >= BASS_IN),
          env(t, CHORDT, 0.6) * (t >= CHORDS_IN), env(t, MELT, 0.3) * (t >= MELODY_IN)]
    for i, l in enumerate(lv):
        x = x0 + 25 + i * 38
        v.rect(x, y0 + 12, x + 12, y1 - 12, fill=(18, 18, 24))
        hgt = (y1 - y0 - 24) * l
        v.rect(x, y1 - 12 - hgt, x + 12, y1 - 12, fill=(TEAL if i < 3 else VIOLET) + (230,))


def cable_pts(p0, p1, sag, wig=0.0, t=0.0, n=24):
    pts = []
    for i in range(n + 1):
        s = i / n
        x = lerp(p0[0], p1[0], s)
        y = lerp(p0[1], p1[1], s) + sag * 4 * s * (1 - s) + wig * np.sin(s * 9 + t * 7) * s * (1 - s) * 4
        pts.append((x, y))
    return pts


JACK = (AMP[0] - 130, AMP[1] + 50)


def amp(v, t, L):
    x, y = AMP
    # cable snakes across the desk and plugs itself in
    start = (MIXER[2] - 10, MIXER[3] - 20)
    if t < 10.6:
        end, wig = (start[0] + 80, DESK_Y - 30), 0.0
    elif t < BASS_IN - 0.15:
        k = ease_in_out((t - 10.6) / (BASS_IN - 0.15 - 10.6))
        end = (lerp(start[0] + 80, JACK[0], k), lerp(DESK_Y - 30, JACK[1], k) - 50 * np.sin(k * np.pi))
        wig = 14 * (1 - k)
    else:
        end, wig = JACK, 0.0
    v.line(cable_pts(start, end, 30, wig, t), fill=(30, 30, 36), width=10)
    v.rect(end[0] - 18, end[1] - 9, end[0] + 4, end[1] + 9, fill=(170, 170, 180), radius=3)
    # amp body
    v.rect(x - 140, y - 150, x + 140, y + 150, fill=(40, 30, 28), radius=16)
    v.rect(x - 120, y - 80, x + 120, y + 135, fill=(70, 60, 52), radius=10)
    push = 8 * env(t, BASSN, 0.12) * (t >= BASS_IN)
    v.ell(x, y + 28, 78 + push, 78 + push, fill=(30, 26, 26), outline=(110, 95, 80), width=4)
    v.ell(x, y + 28, 26 + push * 0.6, 26 + push * 0.6, fill=(80, 70, 64))
    v.ell(JACK[0], JACK[1], 10, 10, fill=(10, 10, 12))
    on = t >= BASS_IN
    v.ell(x + 95, y - 118, 12, 12, fill=(255, 70, 60) if on else (70, 30, 30))
    for k in range(3):
        v.ell(x - 90 + k * 50, y - 118, 12, 12, fill=(150, 140, 120))


def cup(v, t, L):
    x, y = CUP
    jig = 2.5 * env(t, BASSN, 0.08) * (t >= BASS_IN) * np.sin(t * 90)
    v.rect(x - 38 + jig, y - 70, x + 38 + jig, y, fill=(200, 190, 175), radius=10)
    v.ell(x + 46 + jig, y - 36, 16, 20, outline=(200, 190, 175), width=6)
    v.ell(x + jig, y - 70, 36, 10, fill=(70, 45, 30))
    r = env(t, BASSN, 0.25) * (t >= BASS_IN)
    if r > 0.05:
        v.ell(x + jig, y - 70, 28 * (1.2 - r), 7 * (1.2 - r), outline=(160, 120, 90, int(200 * r)), width=2)


NKEYS = 15
CHORD_KEYS = [(0, 2, 4, 6, 8), (5, 7, 9, 11, 13), (3, 5, 7, 9, 11), (4, 6, 8, 10, 12)]


def keyboard(v, t, L):
    x0, y0, x1, y1 = KEYBOARD
    v.rect(x0 - 16, y0 - 34, x1 + 16, y1 + 10, fill=(32, 30, 40), radius=10)
    d, i = since(t, CHORDT)
    pressed = set()
    downbeat = i >= 0 and abs(((CHORDT[i] - T0) / BAR) - round((CHORDT[i] - T0) / BAR)) < 0.01
    if i >= 0 and t >= CHORDS_IN and d < (0.55 if downbeat else 0.3):
        pressed = set(CHORD_KEYS[EV["chord"][i][1]])
    kw = (x1 - x0) / NKEYS
    for k in range(NKEYS):
        down = k in pressed
        x = x0 + k * kw
        v.rect(x + 2, y0 + (6 if down else 0), x + kw - 2, y1, fill=(200, 190, 175) if down else CREAM, radius=4)
        if down:
            v.rect(x + 2, y1 - 10, x + kw - 2, y1, fill=AMBER + (200,))
    for k in range(NKEYS - 1):
        if k % 7 in (0, 1, 3, 4, 5):
            x = x0 + (k + 1) * kw
            v.rect(x - kw * 0.3, y0, x + kw * 0.3, y0 + (y1 - y0) * 0.6, fill=(20, 20, 26), radius=3)


SYN_OUT = (SYNTH[0] + 20, SYNTH[1] + 10)
MIX_IN = (MIXER[0] + 150, MIXER[3])


def synth(v, t, L):
    x0, y0, x1, y1 = SYNTH
    pts = cable_pts(SYN_OUT, MIX_IN, 40)
    v.line(pts, fill=(60, 50, 90), width=8)
    v.rect(x0, y0, x1, y1, fill=(40, 34, 60), radius=10)
    for k in range(4):
        v.ell(x0 + 40 + k * 50, y0 + 35, 15, 15, fill=(20, 20, 26), outline=(140, 130, 170), width=2)
    # LED: flickers, then pulses with each melody note
    if MELODY_IN - 0.8 <= t < MELODY_IN:
        led = 1.0 if int(t * 23) % 3 else 0.2
    elif t >= MELODY_IN:
        led = 0.25 + 0.75 * env(t, MELT, 0.18)
    else:
        led = 0.08
    v.ell(x1 - 30, y0 + 70, 11, 11, fill=shade(VIOLET, 0.3 + 0.9 * led))
    # waveforms travel along the cable toward the mixer
    i0 = bisect.bisect_left(MELT, t - 0.7)
    for i in range(i0, bisect.bisect_right(MELT, t)):
        s = (t - MELT[i]) / 0.7
        idx = int(s * (len(pts) - 1))
        px, py = pts[min(idx, len(pts) - 1)]
        seg = [(px + dx, py - 14 + 10 * np.sin(dx * 0.4)) for dx in range(-24, 25, 4)]
        v.line(seg, fill=VIOLET + (230,), width=4)
    return led


def chair(v, t, L):
    x, y = CHAIR
    amp_ = np.interp(t, [27.2, 28.2, PAYOFF - 0.2, PAYOFF, RESET, 42.4], [0, 2.2, 2.2, 3.6, 3.6, 0])
    d = (t - T0) % BEAT
    ang = -amp_ * np.exp(-d / 0.16) if t > 27 else 0.0
    layer = Image.new("RGBA", (OW, OH), (0, 0, 0, 0))
    lv = V(layer, v.z, v.cx, v.cy)
    lv.line([(x, y + 40), (x, y + 200)], fill=(30, 30, 36), width=18)
    lv.rect(x - 150, y - 10, x + 150, y + 50, fill=(36, 34, 46), radius=24)
    lv.rect(x - 130, y - 320, x + 130, y - 30, fill=(44, 40, 56), radius=50)
    lv.rect(x - 105, y - 295, x + 105, y - 60, fill=(56, 50, 72), radius=40)
    piv = v.P(x, y + 40)
    layer = layer.rotate(ang, center=piv, resample=Image.BICUBIC)
    return layer


GLOW = None


def glow_sprite():
    yy, xx = np.mgrid[-64:64, -64:64].astype(np.float32) / 64
    return np.exp(-(xx ** 2 + yy ** 2) * 3.0)


def add_glow(arr, v, x, y, r, col, inten):
    if inten <= 0.01:
        return
    sx, sy = v.P(x, y)
    rr = int(max(4, v.S(r)))
    g = np.asarray(Image.fromarray((GLOW * 255).astype(np.uint8)).resize((2 * rr, 2 * rr), Image.BILINEAR), np.float32) / 255
    x0, y0 = int(sx - rr), int(sy - rr)
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(OW, x0 + 2 * rr), min(OH, y0 + 2 * rr)
    if xb <= xa or yb <= ya:
        return
    arr[ya:yb, xa:xb] += g[ya - y0:yb - y0, xa - x0:xb - x0, None] * np.array(col, np.float32) / 255 * inten


ZONES = [(WINDOW[0] + 220, 560, 420, VIOLET), (LAMP[0] + 60, 700, 420, AMBER), (810, 600, 380, TEAL), (505, 1330, 380, AMBER)]


def frame_arr(idx):
    t = idx / FPS
    z, cx, cy = camera(t)
    L = room_light(t)
    img = Image.new("RGB", (OW, OH), NAVY)
    v = V(img, z, cx, cy)
    wall(v, L)
    window(v, t, L)
    lamp(v, L)
    monitors(v, t, L)
    desk(v, L)
    turntable(v, t, L)
    mixer(v, t, L)
    pencil(v, t, L)
    amp(v, t, L)
    cup(v, t, L)
    keyboard(v, t, L)
    led = synth(v, t, L)
    ch = chair(v, t, L)
    img = img.convert("RGBA")
    img.alpha_composite(ch)
    arr = np.asarray(img.convert("RGB"), np.float32) / 255
    # lighting: dark room, warm lamp pool, glows that answer the music
    arr *= 0.55 + 0.45 * L
    add_glow(arr, v, LAMP[0] + 40, LAMP[1] + 260, 520, AMBER, 0.35 * L)
    add_glow(arr, v, TURNTABLE[0], TURNTABLE[1], 260, AMBER, 0.25 * env(t, KICKS, 0.2))
    add_glow(arr, v, AMP[0] + 95, AMP[1] - 118, 70, (255, 70, 60), 0.7 * (t >= BASS_IN) * L)
    add_glow(arr, v, SYNTH[2] - 30, SYNTH[1] + 70, 90, VIOLET, 0.6 * led)
    if t >= CHORDS_IN:
        d, i = since(t, CHORDT)
        if i >= 0:
            zx, zy, zr, zc = ZONES[EV["chord"][i][1]]
            add_glow(arr, v, zx, zy, zr, zc, 0.45 * np.exp(-d / 1.1))
    if PAYOFF <= t < RESET + 1.0:  # the whole room answers the full groove
        k = smoothstep(PAYOFF, PAYOFF + 0.4, t) * (1 - smoothstep(RESET, RESET + 1.0, t))
        for zx, zy, zr, zc in ZONES:
            add_glow(arr, v, zx, zy, zr, zc, 0.15 * k + 0.12 * k * env(t, KICKS, 0.2))
    # vignette + grain
    yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float32)
    r = np.sqrt(((xx - OW / 2) / (OW * 0.7)) ** 2 + ((yy - OH / 2) / (OH * 0.62)) ** 2)
    arr *= (1 - smoothstep(0.6, 1.3, r) * 0.7)[..., None]
    g = GRAIN[idx % len(GRAIN)]
    if OW != 1080:
        g = g[::1080 // OW, ::1080 // OW][:OH, :OW]
    arr = np.clip(arr + g[..., None] * 0.025, 0, 1)
    pil = Image.fromarray((arr * 255).astype(np.uint8)).convert("RGBA")
    # opening hook text
    a = smoothstep(0.4, 1.0, t) * (1 - smoothstep(4.6, 5.4, t))
    if a > 0:
        d = ImageDraw.Draw(pil)
        f = font("playi", int(54 * OW / 1080))
        txt = "What if the studio made its own beat?"
        tw = d.textlength(txt, font=f)
        d.text(((OW - tw) / 2, OH * 0.16), txt, font=f, fill=CREAM + (int(255 * a),))
    return np.asarray(pil.convert("RGB"))


def frame(idx):
    return frame_arr(idx).tobytes()


def _init():
    global GLOW
    GLOW = glow_sprite()


def init_worker(w, h):
    global OW, OH
    OW, OH = w, h
    _init()


if __name__ == "__main__":
    out = sys.argv[1]
    preview = "--preview" in sys.argv
    if preview:
        OW, OH = 540, 960
    _init()
    if "--frames" in sys.argv:
        for fi in map(int, sys.argv[sys.argv.index("--frames") + 1:]):
            Image.fromarray(frame_arr(fi)).save(f"{out}_{fi:04d}.png")
        sys.exit()
    nfr = int(DURATION * FPS)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium" if preview else "slow",
                           "-crf", "20" if preview else "17", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)

    with Pool(int(os.environ.get("JOBS", 4)), initializer=init_worker, initargs=(OW, OH)) as pool:
        for fb in pool.imap(frame, range(nfr), chunksize=6):
            ff.stdin.write(fb)
    ff.stdin.close()
    ff.wait()
