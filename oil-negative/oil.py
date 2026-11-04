"""NO WAY. #5 — Oil Got So Cheap, Sellers Paid Buyers (May 2020 WTI futures settled at -$37.63 on 20 April 2020).
Reuses the molasses-flood grade/captions and the zanzibar-war helpers (headline, backgrounds, caption timing)."""
import os
import subprocess
import sys
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "zanzibar-war"))
sys.path.insert(0, os.path.join(HERE, "..", "molasses-flood"))
from common import (W, H, FPS, NFRAMES, font, to_img, from_img, cam2d, shake, grade, lerp, smoothstep,
                    ease_in_out, ease_out, ease_out_back)
import render as mf   # molasses-flood captions + typewriter + paper aging
import episode as zw  # zanzibar-war: headline(), dark_bg(), paper_bg(), build_chunks()

AMBER = mf.AMBER
RED = (225, 70, 50)
MINUS = "-"  # ASCII hyphen: renders in every bundled font
NARR = {"l1": 0.1, "l2": 3.0, "l3": 7.0, "l4": 12.3, "l5": 15.6, "l6": 18.2, "l7": 19.15}
DUR = {"l1": 2.66, "l2": 3.73, "l3": 5.05, "l4": 2.38, "l5": 2.09, "l6": 0.75, "l7": 0.52}
LINES = [
    ("l1", [["OIL", "ONCE", "GOT", "SO", "CHEAP,"], ["SELLERS", "PAID", "BUYERS."]]),
    ("l2", [["IN", "APRIL", "2020,"], ["DEMAND", "CRASHED,"], ["AND", "AVAILABLE", "STORAGE"], ["WAS", "SCARCE."]]),
    ("l3", [["AN", "EXPIRING", "U.S."], ["OIL", "FUTURES", "CONTRACT"], ["SETTLED", "AT"], ["NEGATIVE", "$37"], ["A", "BARREL."]]),
    ("l4", [["BUYERS", "WERE", "BEING", "PAID"], ["TO", "TAKE", "ON", "DELIVERY."]]),
    ("l5", [["YOUR", "GARAGE"], ["WAS", "NOT", "THE", "SOLUTION."]]),
    ("l6", [["NO", "WAY."]]),
    ("l7", [["YEP."]]),
]
zw.LINES, zw.NARR, zw.DUR = LINES, NARR, DUR
zw.SPOKEN = {"2020,": "twenty twenty", "$37": "thirty seven dollars", "U.S.": "you ess"}
mf.CHUNKS = zw.build_chunks()
mf.KEYWORDS = {"CHEAP,", "PAID", "CRASHED,", "SCARCE.", "FUTURES", "NEGATIVE", "$37", "DELIVERY.", "GARAGE", "WAY.", "YEP."}


# ---------------------------------------------------------------- drawing helpers
def barrel(d, x, y, w=150, h=210, a=255):
    """Steel oil drum, (x, y) = bottom centre."""
    body, rib, top = (48, 52, 58, a), (90, 96, 104, a), (110, 115, 122, a)
    e = w * 0.16
    d.rectangle([x - w / 2, y - h, x + w / 2, y - e], fill=body)
    d.ellipse([x - w / 2, y - 2 * e, x + w / 2, y], fill=body)
    for k in (0.33, 0.66):
        yy = y - e - (h - e) * k
        d.arc([x - w / 2, yy - e, x + w / 2, yy + e], 0, 180, fill=rib, width=max(2, int(w * 0.04)))
    d.rectangle([x - w * 0.42, y - h * 0.8, x - w * 0.3, y - h * 0.25], fill=(80, 86, 94, a))  # highlight
    d.ellipse([x - w / 2, y - h - e, x + w / 2, y - h + e], fill=top, outline=rib, width=2)
    d.ellipse([x + w * 0.12, y - h - e * 0.4, x + w * 0.26, y - h + e * 0.2], fill=(40, 42, 46, a))


def price_board(d, x0, y0, x1, y1, txt, col):
    d.rectangle([x0, y0, x1, y1], fill=(18, 15, 12), outline=(110, 90, 60), width=6)
    d.text((x0 + 28, y0 + 18), "OIL PRICE", font=font("oswaldm", 44), fill=(190, 175, 150))
    f = font("anton", 150)
    w = d.textlength(txt, font=f)
    d.text(((x0 + x1 - w) / 2, y0 + 90), txt, font=f, fill=col)


def tank(d, x, y, w, h, space):
    """Storage tank (bottom centre x,y) with an 'available space' band at the top."""
    e = w * 0.14
    d.rectangle([x - w / 2, y - h, x + w / 2, y], fill=(150, 142, 128))
    fill_top = y - h * (1 - space)
    d.rectangle([x - w / 2 + 10, fill_top, x + w / 2 - 10, y - 8], fill=(40, 34, 28))
    d.line([(x - w / 2 + 10, fill_top), (x + w / 2 - 10, fill_top)], fill=AMBER, width=5)
    d.ellipse([x - w / 2, y - h - e, x + w / 2, y - h + e], fill=(170, 162, 146), outline=(90, 82, 70), width=3)
    d.rectangle([x - w / 2, y - h, x + w / 2, y], outline=(90, 82, 70), width=4)


def car(d, x, y, s=1.0):
    c = (170, 160, 142)
    d.rounded_rectangle([x - 90 * s, y - 50 * s, x + 90 * s, y], 14, fill=c)
    d.polygon([(x - 55 * s, y - 50 * s), (x - 35 * s, y - 88 * s), (x + 40 * s, y - 88 * s), (x + 60 * s, y - 50 * s)], fill=c)
    for wx in (-55, 55):
        d.ellipse([x + (wx - 22) * s, y - 22 * s, x + (wx + 22) * s, y + 22 * s], fill=(15, 13, 12), outline=(120, 110, 95), width=3)


def plane(d, x, y, s=1.0):
    c = (185, 175, 158)
    d.rounded_rectangle([x - 150 * s, y - 18 * s, x + 150 * s, y + 18 * s], 18, fill=c)
    d.polygon([(x - 20 * s, y), (x + 40 * s, y), (x - 50 * s, y + 90 * s), (x - 90 * s, y + 90 * s)], fill=c)
    d.polygon([(x - 120 * s, y - 10 * s), (x - 150 * s, y - 70 * s), (x - 125 * s, y - 70 * s), (x - 95 * s, y - 10 * s)], fill=c)


def garage(d, x, y, door_open):
    d.polygon([(x - 120, y - 150), (x, y - 230), (x + 120, y - 150)], fill=(110, 70, 50))
    d.rectangle([x - 110, y - 150, x + 110, y], fill=(190, 178, 155), outline=(90, 80, 65), width=4)
    dh = 120 * (1 - door_open)
    d.rectangle([x - 75, y - 120, x + 75, y], fill=(25, 22, 20))
    d.rectangle([x - 75, y - 120, x + 75, y - 120 + dh], fill=(160, 150, 130), outline=(90, 80, 65), width=3)
    for k in range(1, 4):
        yy = y - 120 + dh * k / 4
        d.line([(x - 75, yy), (x + 75, yy)], fill=(110, 100, 85), width=2)
    d.text((x - 62, y + 18), "GARAGE", font=font("oswaldm", 36), fill=(200, 190, 170))


# ---------------------------------------------------------------- scenes
def base():
    return to_img(zw.DARK).convert("RGBA")


def scene_hook(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    k = ease_out_back(t / 0.4, 2)
    barrel(d, 270, 1120, 300 * k + 1, 420 * k + 1)
    # price rolls down to zero, then flips below it
    p = ease_in_out((t - 0.4) / 1.6)
    if t < 2.05:
        price_board(d, 470, 640, 1010, 900, f"${18 * (1 - p):.2f}", AMBER)
    else:
        price_board(d, 470, 640, 1010, 900, "< $0", RED)
    amp = 2 + (16 * np.exp(-(t - 2.05) * 9) if t >= 2.05 else 0)
    sx, sy, sr = shake(t, amp, 10, seed=1)
    return from_img(cam2d(img.convert("RGB"), 1.0 + 0.02 * t / 3, W / 2, 900, sr, sx, sy))


def scene_storage(t):
    a = t - 3.0
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    # traffic and flights slow to a stop
    v = max(0.0, 1 - a / 2.6)
    dist = 520 * (a - a * a / 5.2) if a < 2.6 else 520 * 1.3
    d.line([(0, 760), (W, 760)], fill=(120, 108, 90), width=6)
    for k, x0 in enumerate((-200, 260, 720)):
        car(d, (x0 + dist) % (W + 300) - 150, 750, 0.9)
    plane(d, lerp(-200, 640, min(1, a / 2.6)) if a < 2.6 else 640, 520 - 30 * v, 1.1)
    # available storage space shrinks (never shown as completely gone)
    space = lerp(0.5, 0.08, ease_in_out(a / 3.5))
    for x in (220, 540, 860):
        tank(d, x, 1200, 280, 250, space)
    d.text((70, 820), "AVAILABLE STORAGE", font=font("oswaldm", 46), fill=AMBER)
    return from_img(img.convert("RGB"))


CONTRACT = None


def contract_img():
    img = to_img(zw.paper_bg(7, (0.88, 0.84, 0.72)))
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 80, 300, W - 80, 1170
    d.rectangle([x0, y0, x1, y1], outline=(60, 45, 35), width=8)

    def C(txt, y, f, col=(40, 30, 24)):
        w = d.textlength(txt, font=f)
        d.text(((W - w) / 2, y), txt, font=f, fill=col)
    C("FUTURES CONTRACT", 340, font("oldb", 66))
    C("WTI — MAY 2020", 430, font("anton", 120))
    C("CRUDE OIL  ·  1,000 BARRELS  ·  U.S.", 590, font("oldb", 40))
    d.line([(x0 + 60, 660), (x1 - 60, 660)], fill=(60, 45, 35), width=3)
    C("SETTLEMENT PRICE", 675, font("oldb", 48))
    return mf.paper.age_paper(img, 9)


STAMP_T = 10.3


def scene_contract(t):
    a = t - 7.0
    img = cam2d(CONTRACT, 1.0 + 0.03 * a / 5, W / 2, H / 2, 0, 0, 0).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    if t >= STAMP_T:
        k = ease_out_back((t - STAMP_T) / 0.25, 2.5)
        f = font("anton", int(200 * (1.6 - 0.6 * k)))
        txt = MINUS + "$37.63"
        w = d.textlength(txt, font=f)
        d.text(((W - w) / 2, 800 - (200 * (0.6 - 0.6 * k))), txt, font=f, fill=RED + (255,), stroke_width=6, stroke_fill=(60, 15, 10, 255))
        f2 = font("anton", 90)
        w2 = d.textlength("/ BARREL", font=f2)
        d.text(((W - w2) / 2, 1050), "/ BARREL", font=f2, fill=(60, 20, 15, int(255 * min(1, k))))
    else:
        f = font("anton", 200)
        w = d.textlength("$ ? ? ?", font=f)
        d.text(((W - w) / 2, 800), "$ ? ? ?", font=f, fill=(120, 105, 85))
    amp = 2 + (18 * np.exp(-(t - STAMP_T) * 9) if t >= STAMP_T else 0)
    sx, sy, sr = shake(t, amp, 10, seed=3)
    return from_img(cam2d(img.convert("RGB"), 1.02, W / 2, 900, sr, sx, sy))


def scene_pay(t):
    a = t - 12.0
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    # seller (left) and buyer (right)
    for x, lab in ((220, "SELLER"), (860, "BUYER")):
        d.rounded_rectangle([x - 140, 660, x + 140, 1000], 20, fill=(60, 52, 44), outline=(140, 120, 90), width=5)
        d.ellipse([x - 50, 700, x + 50, 800], fill=(200, 190, 170))
        d.polygon([(x - 90, 960), (x - 70, 830), (x + 70, 830), (x + 90, 960)], fill=(200, 190, 170))
        f = font("anton", 64)
        w = d.textlength(lab, font=f)
        d.text((x - w / 2, 1020), lab, font=f, fill=(240, 230, 210))
    # money and the delivery obligation travel together, seller -> buyer, repeating
    for k in range(3):
        ph = ((a - 0.2 - k * 0.45) / 1.3)
        if 0 <= ph <= 1:
            x = lerp(330, 750, ease_in_out(ph))
            y = 820 - np.sin(ph * np.pi) * 160
            d.rounded_rectangle([x - 70, y - 38, x + 70, y + 38], 8, fill=(120, 150, 90), outline=(50, 70, 40), width=4)
            d.text((x - 16, y - 34), "$", font=font("anton", 56), fill=(40, 60, 30))
            barrel(d, x, y + 190, 80, 110)
    d.text((440, 1110), "+ DELIVERY", font=font("oswaldm", 44), fill=AMBER)
    sx, sy, sr = shake(t, 2, 3, seed=4)
    return from_img(cam2d(img.convert("RGB"), 1.0 + 0.02 * a / 3.4, W / 2, 900, sr, sx, sy))


GARAGE_T = 16.3


def scene_garage(t):
    a = t - 15.4
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    # enormous pile of barrels (stacked pyramid, rows reveal from the back)
    rows = 7
    for r in range(rows):
        n = rows - r + 3
        y = 1200 - r * 115
        for i in range(n):
            x = 90 + r * 45 + i * 92
            if x > 740:
                continue
            ti = 15.4 + (r * 0.12 + i * 0.015)
            if t >= ti:
                barrel(d, x, y, 90, 125)
    gk = ease_out_back((t - GARAGE_T) / 0.35, 2) if t > GARAGE_T else 0
    if gk > 0:
        garage(d, 880, 1200, np.clip((t - GARAGE_T - 0.5) / 0.6, 0, 1) * 0.6)
    if t > 18.2:  # wordmark plate above the pile
        k = ease_out_back((t - 18.2) / 0.3, 2.5)
        f = font("anton", int(190 * k) + 1)
        w = d.textlength("NO WAY.", font=f)
        cy = 330
        d.rectangle([W / 2 - 360, cy - 10, W / 2 + 360, cy + 250], fill=(20, 16, 12, int(225 * min(1, k))))
        d.text((W / 2 - w / 2, cy + 125 - 125 * k), "NO WAY.", font=f, fill=(245, 236, 215, 255))
        d.rectangle([W / 2 - 240 * k, cy + 225, W / 2 + 240 * k, cy + 238], fill=AMBER + (255,))
    sx, sy, sr = shake(t, 2, 3, seed=5)
    return from_img(cam2d(img.convert("RGB"), 1.0 + 0.02 * a / 4.6, W / 2, 900, sr, sx, sy))


def overlay(t):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for t0, t1, lines in [(0.0, 2.95, [("OIL WENT", (255, 255, 255)), ("BELOW ZERO.", RED)]),
                          (3.05, 6.95, [("APRIL 20,", (255, 255, 255)), ("2020.", AMBER)]),
                          (12.05, 15.35, [("PAID TO ACCEPT", (255, 255, 255)), ("DELIVERY.", AMBER)])]:
        if t0 <= t < t1:
            zw.headline(d, lines, 200, t, t0 + 0.05, size=130, gap=140)
            return layer
    return None


def mix(a, b, k):
    return a * (1 - k) + b * k


SCENES = [(0.0, 3.0, scene_hook), (3.0, 7.0, scene_storage), (7.0, 12.0, scene_contract),
          (12.0, 15.4, scene_pay), (15.4, 20.01, scene_garage)]


def frame(idx):
    t = idx / FPS
    for i, (t0, t1, fn) in enumerate(SCENES):
        if t0 <= t < t1:
            img = fn(t)
            if i + 1 < len(SCENES) and t > t1 - 0.2:  # short cross-dissolve, as in the earlier episodes
                img = mix(img, SCENES[i + 1][2](t1), smoothstep(t1 - 0.2, t1, t))
            break
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
    global CONTRACT
    zw.DARK = zw.dark_bg()
    CONTRACT = contract_img()


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
