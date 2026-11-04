"""NO WAY. #3 — The War That Lasted Less Than an Hour (Anglo-Zanzibar War, 27 Aug 1896).
Reuses the molasses-flood film grade, fonts, captions and typewriter labels."""
import os
import subprocess
import sys
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "molasses-flood"))
from common import (W, H, FPS, NFRAMES, NOISE, NOISE2, NOISE_FINE, tex, font, to_img, from_img, cam2d, shake,
                    grade, lerp, smoothstep, ease_in_out, ease_out, ease_out_back)
import render as mf  # molasses-flood: caption + typewriter helpers

AMBER = mf.AMBER
NARR = {"l1": 0.15, "l2": 4.2, "l3": 8.4, "l4": 12.9, "l5": 15.6, "l6": 18.25, "l7": 19.2}
DUR = {"l1": 3.14, "l2": 3.06, "l3": 2.65, "l4": 2.12, "l5": 2.46, "l6": 0.75, "l7": 0.52}

# (line, groups of words) — word times spread over each clip by spoken length
LINES = [
    ("l1", [["THE", "SHORTEST", "WAR"], ["ON", "RECORD"], ["WAS", "OVER", "IN"], ["LESS", "THAN", "AN", "HOUR."]]),
    ("l2", [["IN", "1896,"], ["BRITAIN", "AND"], ["ZANZIBAR"], ["WENT", "TO", "WAR."]]),
    ("l3", [["BRITISH", "WARSHIPS"], ["BOMBARDED", "THE"], ["SULTAN'S", "PALACE."]]),
    ("l4", [["THE", "FIGHTING", "ENDED"], ["THAT", "SAME", "MORNING."]]),
    ("l5", [["YOU", "COULD", "START"], ["A", "MOVIE", "AND", "MISS"], ["THE", "ENTIRE", "WAR."]]),
    ("l6", [["NO", "WAY."]]),
    ("l7", [["YEP."]]),
]
SPOKEN = {"1896,": "eighteen ninety six"}
mf.KEYWORDS = {"SHORTEST", "HOUR.", "1896,", "ZANZIBAR", "BRITAIN", "BOMBARDED", "MORNING.", "ENTIRE", "WAY.", "YEP."}


def build_chunks():
    chunks = []
    for line, groups in LINES:
        words = [w for g in groups for w in g]
        wts = [len(SPOKEN.get(w, w)) + 2 for w in words]
        t0, d = NARR[line] + 0.05, DUR[line] - 0.15
        times, t = [], t0
        for wt in wts:
            dt = d * wt / sum(wts)
            times.append((t, t + dt))
            t += dt
        i = 0
        for g in groups:
            chunks.append([(w, *times[i + k]) for k, w in enumerate(g)])
            i += len(g)
    out = []
    for k, ws in enumerate(chunks):
        end = ws[-1][2] + 0.35
        if k + 1 < len(chunks):
            end = min(end, chunks[k + 1][0][1] - 0.04)
        out.append((ws[0][1] - 0.04, end, ws))
    return out


mf.CHUNKS = build_chunks()


# ---------------------------------------------------------------- helpers
def paper_bg(seed=0, tone=(0.78, 0.7, 0.55)):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    n = tex(NOISE, xx * 0.3 + seed * 40, yy * 0.3)
    f = tex(NOISE_FINE, xx * 2, yy * 2)
    v = (0.8 + 0.25 * n + 0.08 * f)[..., None]
    return np.clip(np.array(tone, np.float32) * v, 0, 1)


DARK = None
PAPER = None


def dark_bg():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    v = 0.1 + 0.07 * tex(NOISE2, xx * 0.15, yy * 0.15)
    return (v[..., None] * np.array([1.0, 0.88, 0.72], np.float32)).astype(np.float32)


def draw_clock(img, cx, cy, r, minute_angle, hour_angle):
    """Pocket-watch face drawn with PIL on an RGB image (angles in degrees, 0 = 12 o'clock)."""
    d = ImageDraw.Draw(img)
    d.ellipse([cx - r - 34, cy - r - 34, cx + r + 34, cy + r + 34], fill=(60, 50, 38))
    d.ellipse([cx - r - 22, cy - r - 22, cx + r + 22, cy + r + 22], fill=(150, 125, 85))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(232, 222, 198), outline=(40, 32, 25), width=5)
    d.rectangle([cx - 26, cy - r - 80, cx + 26, cy - r - 30], fill=(130, 105, 70))
    d.ellipse([cx - 40, cy - r - 125, cx + 40, cy - r - 60], outline=(130, 105, 70), width=10)
    fr = font("old", int(r * 0.2))
    for k, num in enumerate(["XII", "I", "II", "III", "IIII", "V", "VI", "VII", "VIII", "IX", "X", "XI"]):
        a = np.deg2rad(k * 30)
        x, y = cx + np.sin(a) * r * 0.78, cy - np.cos(a) * r * 0.78
        w = d.textlength(num, font=fr)
        d.text((x - w / 2, y - r * 0.13), num, font=fr, fill=(35, 28, 22))
    for k in range(60):
        a = np.deg2rad(k * 6)
        r0 = r * (0.9 if k % 5 else 0.86)
        d.line([(cx + np.sin(a) * r0, cy - np.cos(a) * r0), (cx + np.sin(a) * r * 0.95, cy - np.cos(a) * r * 0.95)],
               fill=(35, 28, 22), width=3 if k % 5 == 0 else 1)
    for ang, L, wd in ((hour_angle, 0.5, 14), (minute_angle, 0.78, 8)):
        a = np.deg2rad(ang)
        d.line([(cx - np.sin(a) * r * 0.1, cy + np.cos(a) * r * 0.1), (cx + np.sin(a) * r * L, cy - np.cos(a) * r * L)],
               fill=(25, 20, 16), width=wd)
    d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=(25, 20, 16))


def ticking(t, start_deg, deg_per_s):
    """Minute hand that jumps once per second (watch tick) with a tiny overshoot."""
    whole = np.floor(t)
    frac = t - whole
    k = ease_out_back(frac / 0.12, 3) if frac < 0.12 else 1
    return start_deg + (whole - 1 + k) * deg_per_s


def headline(d, lines, y, t, t0, size=150, gap=150):
    for i, (txt, col) in enumerate(lines):
        ti = t0 + i * 0.25
        if t < ti:
            continue
        k = ease_out((t - ti) / 0.18, 3)
        s = int(size * (1.4 - 0.4 * k))
        f = font("anton", s)
        w = d.textlength(txt, font=f)
        a = int(255 * min(1, k * 1.5))
        d.text(((W - w) / 2, y + i * gap - (s - size) * 0.5), txt, font=f, fill=col + (a,), stroke_width=10,
               stroke_fill=(0, 0, 0, a))


# ---------------------------------------------------------------- scenes
def scene_clock_intro(t):
    img = to_img(DARK)
    draw_clock(img, W // 2, 860, 300, ticking(t, 0, 6.0), 270 + t * 0.5)
    sx, sy, sr = shake(t, 2, 3, seed=1)
    return from_img(cam2d(img, 1.0 + 0.03 * t / 4, W / 2, 860, sr, sx, sy))


# map coordinates: designed on the 1080x1920 canvas, then zoomed
AFRICA = [(-200, 120), (260, 60), (430, 150), (520, 330), (640, 380), (760, 360), (860, 470), (960, 560),
          (900, 700), (790, 860), (700, 1000), (640, 1120), (600, 1240), (580, 1360), (560, 1500), (500, 1640),
          (420, 1800), (380, 2100), (-200, 2100)]
ZNZ = (708, 1205)
MADAGASCAR = [(1000, 1550), (1060, 1600), (1080, 1750), (1040, 1900), (980, 1950), (950, 1800), (960, 1640)]


def build_map():
    base = to_img(paper_bg(3, (0.82, 0.74, 0.58)))
    d = ImageDraw.Draw(base)
    # sea tint + engraved wave lines
    land = Image.new("L", (W, H), 0)
    ImageDraw.Draw(land).polygon(AFRICA, fill=255)
    ImageDraw.Draw(land).polygon(MADAGASCAR, fill=255)
    sea = np.asarray(base, np.float32) / 255.0
    m = np.asarray(land, np.float32)[..., None] / 255.0
    sea_col = sea * np.array([0.78, 0.86, 0.9]) * 0.9
    arr = sea_col * (1 - m) + sea * np.array([1.0, 0.95, 0.85]) * m
    base = to_img(arr)
    d = ImageDraw.Draw(base)
    for k in range(1, 6):  # coastline echo lines (old map style)
        off = k * 14
        pts = [(x + off, y) for x, y in AFRICA[1:-1]]
        d.line(pts, fill=(95, 110, 115), width=1)
    d.line(AFRICA[1:-1], fill=(50, 40, 30), width=4)
    d.polygon(MADAGASCAR, outline=(50, 40, 30))
    # Zanzibar island (+ Pemba to the north)
    zx, zy = ZNZ
    d.polygon([(zx - 10, zy - 45), (zx + 12, zy - 30), (zx + 16, zy + 10), (zx + 6, zy + 48), (zx - 10, zy + 30),
               (zx - 14, zy - 5)], fill=(225, 205, 160), outline=(50, 40, 30))
    d.polygon([(zx - 8, zy - 140), (zx + 8, zy - 130), (zx + 6, zy - 95), (zx - 8, zy - 100)], fill=(225, 205, 160),
              outline=(50, 40, 30))
    # graticule
    for gx in range(0, W, 180):
        d.line([(gx, 0), (gx, H)], fill=(120, 105, 85), width=1)
    for gy in range(0, H, 180):
        d.line([(0, gy), (W, gy)], fill=(120, 105, 85), width=1)
    fo = font("oldi", 46)
    d.text((300, 900), "AFRICA", font=font("oldb", 70), fill=(60, 48, 36))
    d.text((800, 1330), "Indian", font=fo, fill=(60, 75, 85))
    d.text((800, 1385), "Ocean", font=fo, fill=(60, 75, 85))
    return base.filter(ImageFilter.GaussianBlur(0.6))


MAP = None


def scene_map(t):
    a = t - 4.0
    p = ease_in_out(a / 4.0)
    img = MAP.copy()
    d = ImageDraw.Draw(img, "RGBA")
    zx, zy = ZNZ
    # dashed route from Britain (off-map, top left) to Zanzibar
    rp = np.clip((a - 0.9) / 1.4, 0, 1)
    pts = [(lerp(-40, zx, s) + np.sin(s * 3.1) * -220, lerp(-40, zy, s)) for s in np.linspace(0, rp, 60)]
    for i in range(0, len(pts) - 1, 2):
        d.line([pts[i], pts[i + 1]], fill=(150, 30, 25, 230), width=6)
    # pulsing marker
    if a > 0.5:
        for k in range(2):
            ph = ((a - 0.5) * 1.1 + k * 0.5) % 1.0
            r = 30 + ph * 120
            d.ellipse([zx - r, zy - r, zx + r, zy + r], outline=(170, 35, 25, int(220 * (1 - ph))), width=6)
        d.ellipse([zx - 12, zy - 12, zx + 12, zy + 12], fill=(170, 35, 25, 255))
    zoom = lerp(1.0, 1.55, p)
    cx, cy = lerp(W / 2, zx - 60, p), lerp(H / 2, zy - 40, p)
    out = cam2d(img, zoom, cx, cy, lerp(-2, 0, p), 0, 0)
    od = ImageDraw.Draw(out, "RGBA")

    def S(x, y):
        return ((x - cx) * zoom + W / 2, (y - cy) * zoom + H / 2)

    def label(txt, x, y, t0, size=64):
        if a < t0:
            return
        k = ease_out((a - t0) / 0.25)
        f = font("anton", size)
        w = od.textlength(txt, font=f)
        al = int(255 * k)
        od.rectangle([x - 16, y - 8, x + w + 16, y + size + 18], fill=(20, 16, 12, int(200 * k)))
        od.text((x, y), txt, font=f, fill=(245, 236, 215, al))
    sx, sy = S(zx, zy)
    label("ZANZIBAR", min(sx + 50, W - 360), sy - 40, 0.6)
    label("FROM BRITAIN", 90, 560, 1.2, 56)
    # big year
    if a > 0.15:
        k = ease_out_back((a - 0.15) / 0.3, 2)
        f = font("anton", int(230 * k) + 1)
        w = od.textlength("1896", font=f)
        od.text(((W - w) / 2, 250), "1896", font=f, fill=AMBER + (255,), stroke_width=10, stroke_fill=(0, 0, 0, 255))
    return from_img(out)


def build_harbour():
    """Static background: dawn sky, sea, coastline with the palace and palms (RGBA layers)."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    hz = 1080.0
    g = np.clip(yy / hz, 0, 1)
    sky = 0.55 + 0.35 * g ** 2 + 0.1 * tex(NOISE2, xx * 0.3, yy * 0.8)
    sun = np.exp(-(((xx - 820) / 180) ** 2 + ((yy - 900) / 120) ** 2)) * 0.3
    sea = 0.35 + 0.12 * tex(NOISE2, xx * 0.8, (yy - hz) * 4) + 0.15 * np.exp(-((xx - 820) / 120) ** 2) * (yy > hz)
    v = np.where(yy < hz, sky + sun, sea)
    bg = to_img(np.repeat(v[..., None], 3, 2) * np.array([1.0, 0.93, 0.82], np.float32))
    d = ImageDraw.Draw(bg)
    # coastline + palace complex (right side of frame)
    shore = 1070
    d.polygon([(380, shore + 12), (520, shore - 20), (W, shore - 30), (W, shore + 14)], fill=(70, 62, 52))
    px = 600
    d.rectangle([px, shore - 260, px + 330, shore - 15], fill=(150, 140, 125))           # main block
    for fl in range(3):
        y0 = shore - 245 + fl * 76
        d.rectangle([px - 10, y0 + 54, px + 340, y0 + 62], fill=(110, 100, 90))           # balconies
        for wx in range(px + 18, px + 320, 36):
            d.rectangle([wx, y0 + 14, wx + 16, y0 + 48], fill=(55, 50, 45))
            d.ellipse([wx, y0 + 6, wx + 16, y0 + 22], fill=(55, 50, 45))
    d.rectangle([px + 130, shore - 360, px + 200, shore - 260], fill=(140, 130, 116))     # tower
    d.polygon([(px + 120, shore - 360), (px + 210, shore - 360), (px + 165, shore - 410)], fill=(110, 100, 90))
    d.line([(px + 165, shore - 410), (px + 165, shore - 480)], fill=(40, 35, 30), width=4)
    d.polygon([(px + 167, shore - 478), (px + 225, shore - 465), (px + 167, shore - 452)], fill=(150, 40, 30))
    d.rectangle([px + 360, shore - 120, px + 480, shore - 15], fill=(120, 112, 100))      # side buildings
    d.rectangle([px - 160, shore - 95, px - 20, shore - 15], fill=(125, 116, 104))
    for tx, th in ((520, 170), (990, 200), (1050, 150)):                                   # palms
        d.line([(tx, shore - 10), (tx + 12, shore - th)], fill=(45, 40, 35), width=8)
        for ang in (-150, -110, -60, -20, 20):
            a = np.deg2rad(ang)
            d.line([(tx + 12, shore - th), (tx + 12 + np.cos(a) * 70, shore - th + np.sin(a) * -25 + 30)],
                   fill=(45, 40, 35), width=6)
    bg = bg.filter(ImageFilter.GaussianBlur(1.0))
    # warships (foreground layer, left), 1890s cruisers in silhouette
    ships = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(ships)
    for sx, sy, s in ((-60, 1290, 1.25), (250, 1180, 0.8), (40, 1130, 0.55)):
        def P(x, y):
            return (sx + x * s, sy + y * s)
        c = (28, 26, 24, 255)
        sd.polygon([P(0, 0), P(560, 0), P(520, 70), P(40, 70)], fill=c)                    # hull
        sd.rectangle([P(110, -60), P(430, 0)], fill=c)                                     # superstructure
        for fx in (200, 290):
            sd.rectangle([P(fx, -150), P(fx + 38, -60)], fill=c)                           # funnels
        for mx in (80, 470):
            sd.line([P(mx, 0), P(mx, -260)], fill=c, width=max(2, int(7 * s)))
            sd.line([P(mx - 40, -200), P(mx + 40, -200)], fill=c, width=max(2, int(5 * s)))
        sd.line([P(80, -260), P(470, -260)], fill=(28, 26, 24, 160), width=max(1, int(2 * s)))
        sd.rectangle([P(520, -30), P(600, -16)], fill=c)                                   # forward gun
    return bg, ships


HARB = None
SHOTS = [(8.55, 0), (8.95, 1), (9.5, 0), (9.9, 2), (10.5, 1), (11.0, 0), (11.6, 2), (12.1, 1)]
MUZZLES = [(-60 + 600 * 1.25, 1290 - 23 * 1.25), (250 + 600 * 0.8, 1180 - 23 * 0.8), (40 + 600 * 0.55, 1130 - 23 * 0.55)]


def scene_bombard(t):
    a = t - 8.0
    bg, ships = HARB
    zb = 1.0 + 0.05 * a / 5
    img = cam2d(bg, zb, W / 2 + a * 6, H / 2, 0, 0, 0)
    # rising smoke over the palace (grows as the bombardment continues)
    sm = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sm)
    hits = [s for s in SHOTS if s[0] < t]
    for i, (ts, _) in enumerate(hits):
        age = t - ts
        hx = 640 + (i * 97) % 300
        for k in range(14):
            r = 20 + k * 6 + age * 25
            y = 820 - k * 22 - age * 40
            x = hx + k * 8 + age * 30
            al = int(max(0, 120 - k * 6) * min(1, age * 3))
            sd.ellipse([x - r, y - r, x + r, y + r], fill=(60, 56, 52, al))
        if age < 0.35:  # restrained impact flash at the palace
            fl = int(200 * (1 - age / 0.35))
            sd.ellipse([hx - 40, 860 - 40, hx + 40, 860 + 40], fill=(255, 225, 170, fl))
    sm = sm.filter(ImageFilter.GaussianBlur(10))
    img = Image.alpha_composite(img.convert("RGBA"), sm)
    # ships (foreground parallax) + muzzle flashes and gun smoke
    sh = cam2d(ships, 1.0 + 0.08 * a / 5, W / 2 - a * 10, H / 2, 0, 0, 0, fill=(0, 0, 0, 0))
    img = Image.alpha_composite(img, sh)
    fx = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fx)
    sc = 1.0 + 0.08 * a / 5
    for ts, k in SHOTS:
        age = t - ts
        if age < 0:
            continue
        mx, my = MUZZLES[k]
        mx, my = (mx - (W / 2 - a * 10)) * sc + W / 2, (my - H / 2) * sc + H / 2
        if age < 0.12:
            r = 40 * (1 - age / 0.12) + 15
            fd.ellipse([mx - r, my - r * 0.6, mx + r * 1.6, my + r * 0.6], fill=(255, 220, 150, 230))
        for k2 in range(6):
            r = 18 + k2 * 8 + age * 40
            x = mx + 30 + k2 * 18 + age * 60
            y = my - age * 30 - k2 * 4
            al = int(max(0, 150 - k2 * 18) * np.exp(-age * 0.8))
            fd.ellipse([x - r, y - r, x + r, y + r], fill=(200, 196, 188, al))
    fx = fx.filter(ImageFilter.GaussianBlur(6))
    img = Image.alpha_composite(img, fx)
    amp = 2 + sum(14 * np.exp(-(t - ts) * 10) for ts, _ in SHOTS if t >= ts)
    sx, sy, sr = shake(t, amp, 12, seed=4)
    return from_img(cam2d(img.convert("RGB"), 1.02, W / 2, H / 2, sr, sx, sy))


STOP_T = 15.0


def scene_clock_end(t):
    img = to_img(DARK)
    # minute hand sweeps through part of one hour, then stops (no numeric counter)
    p = np.clip((t - 13.0) / (STOP_T - 13.0), 0, 1)
    ang = 0 + 240 * ease_in_out(p)
    hour = 270 + 20 * ease_in_out(p)
    draw_clock(img, W // 2, 900, 300, ang, hour)
    amp = 2 + (16 * np.exp(-(t - STOP_T) * 8) if t >= STOP_T else 0)
    sx, sy, sr = shake(t, amp, 10, seed=5)
    return from_img(cam2d(img, 1.0 + 0.03 * p, W / 2, 900, sr, sx, sy))


def scene_movie(t):
    a = t - 15.5
    img = Image.new("RGB", (W, H), (10, 9, 8))
    d = ImageDraw.Draw(img, "RGBA")
    # vintage screen with projector beam glow
    sx0, sy0, sx1, sy1 = 90, 420, W - 90, 980
    glow = np.asarray(img, np.float32) / 255.0
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    beam = np.exp(-(((xx - W / 2) / 420) ** 2 + ((yy - 700) / 360) ** 2)) * 0.12
    img = to_img(glow + beam[..., None] * np.array([1.0, 0.9, 0.75]))
    d = ImageDraw.Draw(img, "RGBA")
    flick = 0.9 + 0.1 * np.sin(t * 47)
    v = int(205 * flick)
    d.rectangle([sx0, sy0, sx1, sy1], fill=(v, int(v * 0.95), int(v * 0.86)))
    d.rectangle([sx0 - 12, sy0 - 12, sx1 + 12, sy1 + 12], outline=(60, 50, 40), width=12)
    # countdown leader style circle, then the wordmark appears as the "feature title"
    cx, cy = W / 2, (sy0 + sy1) / 2
    if t < 18.2:
        d.ellipse([cx - 190, cy - 190, cx + 190, cy + 190], outline=(40, 35, 30), width=8)
        d.ellipse([cx - 160, cy - 160, cx + 160, cy + 160], outline=(40, 35, 30), width=4)
        d.line([(cx, sy0), (cx, sy1)], fill=(40, 35, 30), width=4)
        d.line([(sx0, cy), (sx1, cy)], fill=(40, 35, 30), width=4)
        ang = (a * 360) % 360
        d.pieslice([cx - 160, cy - 160, cx + 160, cy + 160], -90, -90 + ang, fill=(40, 35, 30, 90))
        d.polygon([(cx - 50, cy - 70), (cx - 50, cy + 70), (cx + 70, cy)], fill=(40, 35, 30))
    else:
        k = ease_out((t - 18.2) / 0.35)
        f = font("anton", 200)
        w = d.textlength("NO WAY.", font=f)
        al = int(255 * k)
        d.text((cx - w / 2, cy - 150), "NO WAY.", font=f, fill=(25, 20, 16, al))
        bw = 480 * k
        d.rectangle([cx - bw / 2, cy + 110, cx + bw / 2, cy + 124], fill=AMBER + (al,))
    # progress bar under the screen: barely moves
    by = sy1 + 80
    d.rounded_rectangle([sx0, by, sx1, by + 22], 11, fill=(70, 62, 55))
    prog = 0.004 + 0.012 * np.clip(a / 4.0, 0, 1)
    px = sx0 + (sx1 - sx0) * prog
    d.rounded_rectangle([sx0, by, max(sx0 + 22, px), by + 22], 11, fill=AMBER)
    d.ellipse([px - 20, by - 9, px + 20, by + 31], fill=(245, 236, 215))
    d.text((sx0, by + 44), "WAR: ALREADY OVER", font=font("oswaldm", 40), fill=(200, 190, 175))
    sx, sy, sr = shake(t, 1.5, 3, seed=6)
    return from_img(cam2d(img, 1.0 + 0.02 * a, W / 2, 900, sr, sx, sy))


# ---------------------------------------------------------------- overlays
def overlay(t):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    used = False
    if t < 3.95:
        used = True
        mf.typewriter(d, "THE SHORTEST WAR ON RECORD", 110, 230, t, 0.1, cps=40, size=44)
        headline(d, [("A WAR.", (255, 255, 255)), ("UNDER ONE HOUR.", AMBER)], 310, t, 0.15, size=140, gap=150)
    if 8.2 < t < 12.95:
        used = True
        mf.typewriter(d, "ZANZIBAR TOWN  ·  27 AUGUST 1896", 90, 250, t, 8.25, cps=36, size=44)
    if 13.0 < t < 15.45:
        used = True
        headline(d, [("OVER THAT", (255, 255, 255)), ("SAME MORNING.", AMBER)], 260, t, 13.05, size=130, gap=140)
    return layer if used else None


def mix(a, b, k):
    return a * (1 - k) + b * k


def frame(idx):
    t = idx / FPS
    if t < 4.0:
        img = scene_clock_intro(t)
        if t > 3.75:
            img = mix(img, scene_map(4.0), smoothstep(3.75, 4.0, t))
    elif t < 8.0:
        img = scene_map(t)
        if t > 7.75:
            img = img * (1 - smoothstep(7.75, 8.0, t))
    elif t < 13.0:
        img = scene_bombard(t)
        img = img * smoothstep(8.0, 8.2, t)
        if t > 12.75:
            img = mix(img, scene_clock_end(13.0), smoothstep(12.75, 13.0, t))
    elif t < 15.5:
        img = scene_clock_end(t)
        if t > 15.3:
            img = mix(img, scene_movie(15.5), smoothstep(15.3, 15.5, t))
    else:
        img = scene_movie(t)
    out = grade(img, idx, t)
    if t > 19.75:
        out = out * (1 - smoothstep(19.75, 20.0, t) * 0.85)
    pil = to_img(out).convert("RGBA")
    ov = overlay(t)
    if ov is not None:
        pil = Image.alpha_composite(pil, ov)
    cap = mf.caption_layer(t)
    if cap is not None:
        pil = Image.alpha_composite(pil, cap)
    return np.asarray(pil.convert("RGB")).tobytes()


def _init():
    global DARK, MAP, HARB
    DARK = dark_bg()
    MAP = build_map()
    HARB = build_harbour()


if __name__ == "__main__":
    out = sys.argv[1]
    if len(sys.argv) > 2:
        _init()
        for fi in map(int, sys.argv[2:]):
            Image.frombytes("RGB", (W, H), frame(fi)).save(f"{out}_{fi:03d}.png")
        sys.exit()
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "16",
                           "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    with Pool(int(os.environ.get("JOBS", 4)), initializer=_init) as pool:
        for i, fb in enumerate(pool.imap(frame, range(NFRAMES), chunksize=4)):
            ff.stdin.write(fb)
    ff.stdin.close()
    ff.wait()
