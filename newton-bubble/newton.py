"""NO WAY. #4 — Even Newton Got Burned (South Sea Bubble, 1720).
Reuses the molasses-flood grade/captions and the zanzibar-war helpers (headline, backgrounds)."""
import os
import subprocess
import sys
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "zanzibar-war"))
sys.path.insert(0, os.path.join(HERE, "..", "molasses-flood"))
from common import (W, H, FPS, NFRAMES, font, to_img, from_img, cam2d, shake, grade, lerp, smoothstep,
                    ease_in_out, ease_out, ease_out_back)
import render as mf   # molasses-flood captions + typewriter
import episode as zw  # zanzibar-war: headline(), dark_bg(), paper_bg()

AMBER = mf.AMBER
RED = (220, 70, 50)
NARR = {"l1": 0.1, "l2": 2.5, "l3": 4.45, "l4": 7.55, "l5": 10.75, "l6": 14.1, "l7": 15.75, "l8": 18.2, "l9": 19.15}
DUR = {"l1": 2.31, "l2": 1.8, "l3": 2.95, "l4": 2.3, "l5": 2.18, "l6": 1.48, "l7": 2.19, "l8": 0.75, "l9": 0.52}
LINES = [
    ("l1", [["THINK", "MARKET", "HYPE"], ["ONLY", "FOOLS", "BEGINNERS?"]]),
    ("l2", [["ISAAC", "NEWTON"], ["GOT", "CAUGHT", "TOO."]]),
    ("l3", [["IN", "1720,"], ["HE", "MADE", "MONEY"], ["ON", "SOUTH", "SEA", "STOCK,"]]),
    ("l4", [["THEN", "BOUGHT", "BACK", "IN"], ["AS", "PRICES", "CLIMBED."]]),
    ("l5", [["THE", "BUBBLE", "BURST."], ["HE", "LOST", "A", "FORTUNE."]]),
    ("l6", [["HE", "UNDERSTOOD"], ["GRAVITY."]]),
    ("l7", [["HIS", "PORTFOLIO"], ["GOT", "A"], ["DEMONSTRATION."]]),
    ("l8", [["NO", "WAY."]]),
    ("l9", [["YEP."]]),
]
zw.LINES, zw.NARR, zw.DUR = LINES, NARR, DUR
zw.SPOKEN = {"1720,": "seventeen twenty"}
mf.CHUNKS = zw.build_chunks()
mf.KEYWORDS = {"HYPE", "NEWTON", "1720,", "SOUTH", "SEA", "BACK", "BURST.", "FORTUNE.", "GRAVITY.", "DEMONSTRATION.",
               "WAY.", "YEP."}

# ---------------------------------------------------------------- layout
PX0, PY0, PX1, PY1 = 70, 520, 1010, 1180   # chart panel
NEWTON = (800, 860)                           # bust centre (face)
STACK = (250, 1150)                           # coin stack base


def price(s):
    """Illustrative bubble curve, s in [0,1] -> [0,1] (no real prices)."""
    rise = 0.12 + 0.1 * s + 0.75 * smoothstep(0.25, 0.7, s) ** 2.2
    crash = smoothstep(0.72, 0.86, s)
    return rise * (1 - crash) + (0.1 + 0.03 * np.sin(s * 40)) * crash


def chart_head(t):
    if t < 4.3:
        return lerp(0.02, 0.38, ease_in_out(t / 4.0))
    if t < 10.6:
        return lerp(0.38, 0.72, ease_in_out((t - 7.4) / 3.0))
    if t < 14.0:
        return lerp(0.72, 0.9, ease_in_out((t - 10.75) / 1.4))
    return 0.9


def chart_xy(s):
    return PX0 + 60 + s * (PX1 - PX0 - 120), PY1 - 50 - price(s) * (PY1 - PY0 - 120)


def draw_panel(d, t):
    d.rectangle([PX0, PY0, PX1, PY1], fill=(214, 198, 165), outline=(70, 55, 40), width=6)
    for k in range(1, 6):
        y = PY0 + k * (PY1 - PY0) / 6
        d.line([(PX0 + 10, y), (PX1 - 10, y)], fill=(170, 152, 120), width=2)
    for k in range(1, 8):
        x = PX0 + k * (PX1 - PX0) / 8
        d.line([(x, PY0 + 10), (x, PY1 - 10)], fill=(185, 168, 136), width=1)
    d.text((PX0 + 24, PY0 + 18), "SOUTH SEA STOCK  (ILLUSTRATIVE)", font=font("oldb", 34), fill=(70, 55, 40))
    head = chart_head(t)
    ss = np.linspace(0, head, 160)
    pts = [chart_xy(s) for s in ss]
    up = [p for s, p in zip(ss, pts) if s <= 0.72]
    dn = [p for s, p in zip(ss, pts) if s >= 0.72]
    if len(up) > 1:
        d.line(up, fill=(150, 95, 20), width=12, joint="curve")
    if len(dn) > 1:
        d.line(dn, fill=RED, width=12, joint="curve")
    x, y = pts[-1]
    d.ellipse([x - 14, y - 14, x + 14, y + 14], fill=(40, 30, 22))


def draw_newton(d, cx, cy, s=1.0):
    """Code-drawn bust in early-18th-century dress: full-bottomed wig, coat, cravat. Neutral expression."""
    def E(x0, y0, x1, y1, **kw):
        d.ellipse([cx + x0 * s, cy + y0 * s, cx + x1 * s, cy + y1 * s], **kw)

    def Pg(pts, **kw):
        d.polygon([(cx + x * s, cy + y * s) for x, y in pts], **kw)
    Pg([(-230, 420), (-190, 230), (-80, 170), (80, 170), (190, 230), (230, 420)], fill=(48, 38, 32))      # coat
    Pg([(-30, 150), (30, 150), (40, 260), (0, 300), (-40, 260)], fill=(236, 230, 214))                    # cravat
    wig = (205, 198, 186)
    for x0, y0 in [(-150, -40), (60, -40), (-160, 60), (70, 60), (-150, 150), (60, 150)]:                  # wig lobes
        E(x0, y0, x0 + 95, y0 + 130, fill=wig, outline=(150, 142, 130), width=3)
    E(-120, -150, 120, 30, fill=wig, outline=(150, 142, 130), width=3)                                     # crown
    E(-72, -85, 72, 110, fill=(226, 196, 165), outline=(120, 90, 70), width=3)                             # face
    E(-128, -150, 20, -60, fill=wig, outline=(150, 142, 130), width=3)                                     # forelock
    for ex in (-34, 18):
        E(ex, -8, ex + 18, 6, fill=(40, 30, 25))                                                           # eyes
        d.line([(cx + (ex - 6) * s, cy - 24 * s), (cx + (ex + 24) * s, cy - 22 * s)], fill=(90, 80, 72), width=max(2, int(5 * s)))
    d.line([(cx + 4 * s, cy), (cx + 12 * s, cy + 40 * s), (cx, cy + 46 * s)], fill=(140, 100, 80), width=max(2, int(4 * s)))
    d.line([(cx - 22 * s, cy + 70 * s), (cx + 22 * s, cy + 70 * s)], fill=(120, 70, 60), width=max(2, int(4 * s)))


def draw_coin(d, x, y, r=46, a=255):
    d.ellipse([x - r, y - r * 0.38 + 8, x + r, y + r * 0.38 + 8], fill=(120, 85, 30, a))
    d.ellipse([x - r, y - r * 0.38, x + r, y + r * 0.38], fill=(222, 178, 80, a), outline=(140, 100, 40, a), width=3)
    d.ellipse([x - r * 0.6, y - r * 0.22, x + r * 0.6, y + r * 0.22], outline=(170, 130, 55, a), width=2)


def stack_count(t):
    if t < 4.3:
        return 0
    if t < 7.4:
        return int(np.clip((t - 4.8) / 0.32, 0, 8))
    if t < 10.6:
        return 8 + int(np.clip((t - 7.7) / 0.4, 0, 6))
    if t < 14.0:
        return 14 - int(np.clip((t - 11.0) / 0.2, 0, 11))
    return 3


def draw_stack(d, t, base=STACK):
    n = stack_count(t)
    bx, by = base
    for i in range(n):
        draw_coin(d, bx + ((i * 7) % 5 - 2) * 2, by - i * 17)
    return n


def stage(t, newton_in=1.0):
    img = to_img(zw.DARK).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    draw_panel(d, t)
    if newton_in > 0:
        nx = lerp(W + 250, NEWTON[0], ease_out(newton_in))
        draw_newton(d, nx, NEWTON[1] + 120, 0.95)
    return img, d


def scene_hook(t):
    img, d = stage(t, np.clip((t - 1.9) / 0.6, 0, 1))
    sx, sy, sr = shake(t, 2, 3, seed=1)
    return from_img(cam2d(img.convert("RGB"), 1.0 + 0.02 * t / 4, W / 2, 860, sr, sx, sy))


def certificate():
    img = to_img(zw.paper_bg(5, (0.86, 0.8, 0.64)))
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 90, 420, W - 90, 1000
    d.rectangle([x0, y0, x1, y1], outline=(70, 50, 35), width=10)
    d.rectangle([x0 + 22, y0 + 22, x1 - 22, y1 - 22], outline=(110, 80, 50), width=3)
    for k in range(0, int(x1 - x0 - 60), 30):                                   # guilloche-ish border
        d.arc([x0 + 30 + k, y0 + 30, x0 + 60 + k, y0 + 60], 0, 180, fill=(120, 90, 60), width=2)
        d.arc([x0 + 30 + k, y1 - 60, x0 + 60 + k, y1 - 30], 180, 360, fill=(120, 90, 60), width=2)

    def C(txt, y, f, col=(45, 32, 24)):
        w = d.textlength(txt, font=f)
        d.text(((W - w) / 2, y), txt, font=f, fill=col)
    C("The", 470, font("black", 60))
    C("South Sea Company", 545, font("black", 88))
    C("SOUTH SEA COMPANY — 1720", 690, font("oldb", 58))
    C("Certificate of Stock", 780, font("oldi", 54))
    d.ellipse([W / 2 - 70, 860, W / 2 + 70, 990], fill=(150, 40, 30), outline=(100, 25, 20), width=4)
    d.ellipse([W / 2 - 48, 882, W / 2 + 48, 968], outline=(200, 90, 70), width=3)
    return mf.paper.age_paper(img, 3) if hasattr(mf, "paper") else img


CERT = None


def scene_cert(t):
    a = t - 4.3
    img = cam2d(CERT, 1.0 + 0.04 * a / 3, W / 2, 800, lerp(-2, 0, ease_out(a / 0.6)), 0, 0).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    n = draw_stack(d, t, (W / 2, 1220))
    # newest coin drops in
    if 0 < n < 8:
        ph = ((t - 4.8) / 0.32) % 1.0
        draw_coin(d, W / 2, lerp(1220 - n * 17 - 260, 1220 - n * 17, ph ** 2))
    return from_img(img.convert("RGB"))


def scene_buyback(t):
    img, d = stage(t)
    n = draw_stack(d, t, STACK)
    # coins arc from Newton into the investment stack
    ph = ((t - 7.7) / 0.4) % 1.0
    if 7.7 < t < 10.1:
        sx, sy = NEWTON[0] - 160, NEWTON[1] + 250
        ex, ey = STACK[0], STACK[1] - n * 17
        x = lerp(sx, ex, ph)
        y = lerp(sy, ey, ph) - np.sin(ph * np.pi) * 220
        draw_coin(d, x, y)
    sx_, sy_, sr = shake(t, 2, 3, seed=2)
    return from_img(cam2d(img.convert("RGB"), 1.02, W / 2, 860, sr, sx_, sy_))


def scene_burst(t):
    img, d = stage(t)
    n = draw_stack(d, t, STACK)
    # coins popping off the top and falling away
    for k in range(4):
        tk = 11.0 + k * 0.6
        a = t - tk
        if 0 < a < 0.9:
            draw_coin(d, STACK[0] + 60 + k * 30 + a * 160, STACK[1] - 14 * 17 + a * a * 1600, a=int(255 * (1 - a / 0.9)))
    burst = 10.75
    amp = 2 + (18 * np.exp(-(t - burst) * 6) if t >= burst else 0)
    sx, sy, sr = shake(t, amp, 12, seed=3)
    return from_img(cam2d(img.convert("RGB"), 1.02, W / 2, 860, sr, sx, sy))


APPLE_T0, APPLE_T1 = 14.4, 15.2


def scene_gravity(t):
    img, d = stage(t)
    draw_stack(d, t, STACK)
    # portfolio line: a dashed red drop off the end of the chart, timed to "demonstration"
    p = ease_in_out((t - 15.9) / 1.6)
    if p > 0:
        x0, y0 = chart_xy(0.9)
        x1, y1 = PX1 + 40, PY1 + 160
        xe, ye = lerp(x0, x1, p), lerp(y0, y1, p ** 1.6)
        d.line([(x0, y0), (xe, ye)], fill=RED + (255,), width=12)
        d.polygon([(xe - 22, ye - 30), (xe + 22, ye - 22), (xe + 6, ye + 22)], fill=RED + (255,))
    # apple falls beside Newton, bounces once
    ax = NEWTON[0] - 230
    floor = PY1 - 70
    if t >= APPLE_T0 - 0.3:
        if t < APPLE_T0:
            ay = 380
        elif t < APPLE_T1:
            ay = lerp(380, floor, ((t - APPLE_T0) / (APPLE_T1 - APPLE_T0)) ** 2)
        else:
            b = t - APPLE_T1
            ay = floor - max(0, np.sin(min(b / 0.35, 1) * np.pi)) * 60
        d.ellipse([ax - 38, ay - 36, ax + 38, ay + 36], fill=(170, 40, 30), outline=(90, 20, 15), width=3)
        d.line([(ax, ay - 34), (ax + 6, ay - 58)], fill=(60, 40, 25), width=5)
        d.ellipse([ax + 6, ay - 62, ax + 40, ay - 46], fill=(70, 110, 50))
        d.ellipse([ax - 20, ay - 18, ax - 4, ay - 2], fill=(220, 120, 100))
    # wordmark stamped onto the chart panel
    if t > 18.2:
        k = ease_out_back((t - 18.2) / 0.3, 2.5)
        f = font("anton", int(190 * k) + 1)
        w = d.textlength("NO WAY.", font=f)
        cy = (PY0 + PY1) / 2 - 130
        d.rectangle([W / 2 - 360, cy - 10, W / 2 + 360, cy + 250], fill=(20, 16, 12, int(215 * min(1, k))))
        d.text((W / 2 - w / 2, cy + 125 - 125 * k), "NO WAY.", font=f, fill=(245, 236, 215, 255))
        d.rectangle([W / 2 - 240 * k, cy + 225, W / 2 + 240 * k, cy + 238], fill=AMBER + (255,))
    amp = 2 + (12 * np.exp(-(t - APPLE_T1) * 10) if t >= APPLE_T1 else 0)
    sx, sy, sr = shake(t, amp, 10, seed=4)
    return from_img(cam2d(img.convert("RGB"), 1.02, W / 2, 860, sr, sx, sy))


def overlay(t):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for t0, t1, lines in [(0.0, 4.15, [("TOO SMART", (255, 255, 255)), ("TO GET BURNED?", AMBER)]),
                          (7.5, 10.55, [("BOUGHT", (255, 255, 255)), ("BACK IN.", AMBER)]),
                          (10.7, 13.95, [("THE BUBBLE", (255, 255, 255)), ("BURST.", RED)])]:
        if t0 <= t < t1:
            zw.headline(d, lines, 200, t, t0 + 0.05, size=130, gap=140)
            return layer
    if 4.4 < t < 7.3:
        mf.typewriter(d, "LONDON  ·  1720", 110, 250, t, 4.5, cps=24, size=48)
        return layer
    return None


def mix(a, b, k):
    return a * (1 - k) + b * k


def frame(idx):
    t = idx / FPS
    if t < 4.3:
        img = scene_hook(t)
        if t > 4.1:
            img = mix(img, scene_cert(4.3), smoothstep(4.1, 4.3, t))
    elif t < 7.4:
        img = scene_cert(t)
        if t > 7.2:
            img = mix(img, scene_buyback(7.4), smoothstep(7.2, 7.4, t))
    elif t < 10.6:
        img = scene_buyback(t)
    elif t < 14.0:
        img = scene_burst(t)
    else:
        img = scene_gravity(t)
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
    global CERT
    zw.DARK = zw.dark_bg()
    CERT = certificate()


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
        for fb in pool.imap(frame, range(NFRAMES), chunksize=4):
            ff.stdin.write(fb)
    ff.stdin.close()
    ff.wait()
