"""NO WAY. — Your Selfie Camera Has a NASA Origin Story (CMOS active-pixel sensor, Eric Fossum's JPL team,
early 1990s). ~61s. Reuses molasses-flood (grade, captions), zanzibar-war (headline, backgrounds, caption timing)
and bonus-army (caption grouping). All imagery is a stylized reconstruction."""
import os
import subprocess
import sys
from multiprocessing import Pool

import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
for sub in ("bonus-army", "eiffel-con", "rap-grammy", "zanzibar-war", "molasses-flood"):
    sys.path.insert(0, os.path.join(HERE, "..", sub))
from common import (W, H, FPS, font, to_img, from_img, cam2d, shake, grade, lerp, smoothstep, ease_in_out, ease_out,
                    ease_out_back)
import render as mf   # captions
import episode as zw  # headline(), dark_bg(), build_chunks()
import bonus as ba    # groups()

DURATION = 61.0
NFR = int(DURATION * FPS)
AMBER, RED, CREAM = mf.AMBER, (215, 60, 45), (236, 226, 205)
INK = (30, 26, 22)
VOICES = os.path.join(HERE, "voices")

NARR = {"n01": 0.2, "n02": 3.3, "n03": 6.8, "n04": 15.2, "n05": 20.8, "n06": 23.4, "n07": 25.7, "n08": 29.6,
        "n09": 32.6, "n10": 38.0, "n11": 45.4, "n12": 51.8, "n13": 54.4, "n14": 58.0}
TEXT = {"n01": "YOUR SELFIE CAMERA HAS A NASA ORIGIN STORY.",
        "n02": "NOT THE FILTER. THE ACTUAL TECHNOLOGY BEHIND THE PICTURE.",
        "n03": "IN THE EARLY 1990S, ENGINEERS AT NASA'S JET PROPULSION LABORATORY WERE TRYING TO MAKE CAMERAS "
               "SMALLER AND MORE ENERGY-EFFICIENT FOR SPACECRAFT.",
        "n04": "A TEAM LED BY ERIC FOSSUM DEVELOPED A BREAKTHROUGH: A CMOS ACTIVE-PIXEL SENSOR.",
        "n05": "BASICALLY, A CAMERA ON A CHIP.",
        "n06": "NOW THINK ABOUT WHAT A PHONE NEEDS.",
        "n07": "A TINY CAMERA THAT TAKES GOOD PICTURES WITHOUT EATING THE BATTERY.",
        "n08": "SAME PROBLEM. VERY DIFFERENT DESTINATION.",
        "n09": "THE TECHNOLOGY MOVED INTO COMMERCIAL PRODUCTS AND HELPED MAKE MODERN PHONE CAMERAS PRACTICAL.",
        "n10": "SO THE ENGINEERING BEHIND EXPLORING SPACE ALSO HELPED ENABLE SELFIES, VIDEO CALLS, AND THE CAMERA "
               "YOU USE TO FILM YOUR LUNCH.",
        "n11": "NASA DIDN'T INVENT YOUR ENTIRE SMARTPHONE. BUT A KEY PIECE OF ITS CAMERA HAS ROOTS IN SPACE RESEARCH.",
        "n12": "THEY WANTED BETTER PICTURES FROM SPACE.",
        "n13": "WE NEEDED 17 ATTEMPTS AT A PROFILE PICTURE.",
        "n14": "NO WAY."}
zw.LINES = [(k, ba.groups(TEXT[k])) for k in NARR]
zw.NARR = NARR
zw.DUR = {k: sf.info(os.path.join(VOICES, f"{k}.wav")).duration for k in NARR}
zw.SPOKEN = {"1990S,": "nineteen nineties", "1990S": "nineteen nineties", "17": "seventeen", "CMOS": "see moss"}
mf.CHUNKS = zw.build_chunks()
mf.KEYWORDS = {"NASA", "ORIGIN", "STORY.", "TECHNOLOGY", "1990S", "JET", "PROPULSION", "LABORATORY", "SMALLER",
               "ENERGY-EFFICIENT", "FOSSUM", "CMOS", "ACTIVE-PIXEL", "SENSOR.", "CHIP.", "TINY", "BATTERY.",
               "DIFFERENT", "DESTINATION.", "COMMERCIAL", "PRACTICAL.", "SELFIES,", "LUNCH.", "DIDN'T", "ENTIRE",
               "ROOTS", "SPACE.", "17", "WAY."}


# ---------------------------------------------------------------- icons & props
def phone(d, cx, cy, s=1.0, screen=(40, 38, 44)):
    w, h = 300 * s, 600 * s
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], 44 * s, fill=(26, 24, 28), outline=(140, 130, 115), width=max(2, int(5 * s)))
    d.rounded_rectangle([cx - w / 2 + 14 * s, cy - h / 2 + 14 * s, cx + w / 2 - 14 * s, cy + h / 2 - 14 * s], 34 * s, fill=screen)
    d.ellipse([cx - 11 * s, cy - h / 2 + 26 * s, cx + 11 * s, cy - h / 2 + 48 * s], fill=(12, 12, 16), outline=(90, 90, 110), width=max(1, int(2 * s)))
    return (cx, cy - h / 2 + 37 * s)  # front-camera position


def face(d, cx, cy, s=1.0, col=(214, 170, 130), tilt=0.0):
    d.ellipse([cx - 70 * s, cy - 90 * s, cx + 70 * s, cy + 90 * s], fill=col)
    d.chord([cx - 75 * s, cy - 100 * s, cx + 75 * s, cy + 10 * s], 180, 360, fill=(50, 38, 30))
    for ex in (-26, 26):
        d.ellipse([cx + (ex - 8 + tilt) * s, cy - 6 * s, cx + (ex + 8 + tilt) * s, cy + 10 * s], fill=(30, 24, 20))
    d.arc([cx - 30 * s, cy + 20 * s, cx + 30 * s, cy + 55 * s], 20, 160, fill=(120, 60, 50), width=max(2, int(5 * s)))
    d.polygon([(cx - 120 * s, cy + 200 * s), (cx - 80 * s, cy + 90 * s), (cx + 80 * s, cy + 90 * s), (cx + 120 * s, cy + 200 * s)], fill=(150, 60, 50))


def spacecraft(d, cx, cy, s=1.0, col=CREAM):
    """Generic deep-space probe (not a specific mission): dish, bus, boom, camera."""
    d.rectangle([cx - 60 * s, cy - 40 * s, cx + 60 * s, cy + 40 * s], fill=(150, 140, 120), outline=col, width=max(2, int(3 * s)))
    d.chord([cx - 130 * s, cy - 210 * s, cx + 130 * s, cy - 30 * s], 0, 180, fill=(210, 200, 180))
    d.line([(cx, cy - 120 * s), (cx, cy - 170 * s)], fill=col, width=max(2, int(4 * s)))
    d.line([(cx + 60 * s, cy), (cx + 230 * s, cy + 60 * s)], fill=col, width=max(2, int(5 * s)))
    d.rectangle([cx + 210 * s, cy + 40 * s, cx + 270 * s, cy + 80 * s], fill=(60, 56, 52), outline=col, width=max(2, int(3 * s)))
    d.ellipse([cx + 248 * s, cy + 50 * s, cx + 268 * s, cy + 70 * s], fill=RED)        # camera lens
    d.line([(cx - 60 * s, cy + 20 * s), (cx - 250 * s, cy + 90 * s)], fill=col, width=max(2, int(4 * s)))
    d.rectangle([cx - 300 * s, cy + 70 * s, cx - 230 * s, cy + 120 * s], fill=(90, 80, 120))  # RTG / panel
    return (cx + 268 * s, cy + 60 * s)


def stars(d, seed=3, n=120):
    rng = np.random.default_rng(seed)
    for _ in range(n):
        x, y, r = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(1, 3.2)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(230, 222, 205, int(rng.uniform(80, 230))))


def chip(d, cx, cy, s=1.0, cells=1.0, t=0.0):
    w = 420 * s
    for k in range(9):  # pins
        o = -w / 2 + 30 * s + k * (w - 60 * s) / 8
        for side in (-1, 1):
            p, q = sorted((side * (w / 2 + 2 * s), side * (w / 2 + 34 * s)))
            d.rectangle([cx + o - 8 * s, cy + p, cx + o + 8 * s, cy + q], fill=(190, 180, 160))
            d.rectangle([cx + p, cy + o - 8 * s, cx + q, cy + o + 8 * s], fill=(190, 180, 160))
    d.rounded_rectangle([cx - w / 2, cy - w / 2, cx + w / 2, cy + w / 2], 18 * s, fill=(40, 40, 46), outline=(120, 115, 105), width=max(2, int(4 * s)))
    g = 10
    cw = (w - 80 * s) / g
    x0, y0 = cx - w / 2 + 40 * s, cy - w / 2 + 40 * s
    for i in range(g):
        for j in range(g):
            k = (i * g + j) / (g * g)
            if k > cells or cw < 6:
                continue
            col = [(200, 70, 60), (90, 170, 90), (80, 110, 200)][(i + j) % 3]
            d.rectangle([x0 + j * cw + 2, y0 + i * cw + 2, x0 + (j + 1) * cw - 2, y0 + (i + 1) * cw - 2], fill=col)
            d.rectangle([x0 + j * cw + 2, y0 + i * cw + 2, x0 + j * cw + cw * 0.35, y0 + i * cw + cw * 0.35], fill=(230, 220, 200))  # per-pixel amplifier


def link_icon(d, cx, cy, s=1.0, col=RED):
    """Two interlocked rings: the 'connection' between the phone icon and the spacecraft icon."""
    for dx in (-22, 22):
        d.ellipse([cx + (dx - 34) * s, cy - 24 * s, cx + (dx + 34) * s, cy + 24 * s], outline=col, width=max(3, int(9 * s)))


def mini_phone(d, cx, cy, s, col=CREAM):
    d.rounded_rectangle([cx - 34 * s, cy - 62 * s, cx + 34 * s, cy + 62 * s], 12 * s, outline=col, width=max(2, int(7 * s)))
    d.ellipse([cx - 5 * s, cy - 50 * s, cx + 5 * s, cy - 40 * s], fill=col)


def mini_probe(d, cx, cy, s, col=CREAM):
    d.chord([cx - 60 * s, cy - 70 * s, cx + 60 * s, cy + 10 * s], 0, 180, outline=col, width=max(2, int(7 * s)))
    d.rectangle([cx - 24 * s, cy + 10 * s, cx + 24 * s, cy + 50 * s], outline=col, width=max(2, int(7 * s)))
    d.line([(cx + 24 * s, cy + 30 * s), (cx + 80 * s, cy + 50 * s)], fill=col, width=max(2, int(7 * s)))


def base():
    return to_img(zw.DARK).convert("RGBA")


def cam(img, t, seed, amp=0.8, zoom=1.0, cx=W / 2, cy=900):
    sx, sy, sr = shake(t, amp, 1.5, seed=seed)
    return from_img(cam2d(img.convert("RGB"), zoom, cx, cy, sr, sx, sy))


# ---------------------------------------------------------------- scenes
def scene_hook(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    if t < 3.4:  # phone takes a selfie, then we push into the front camera
        lens = phone(d, W / 2, 940, 1.25)
        face(d, W / 2, 900, 1.2)
        if 1.2 < t < 1.45:
            d.rectangle([0, 0, W, H], fill=(255, 255, 255, int(220 * (1 - (t - 1.2) / 0.25))))  # shutter flash
        z = 1.0 if t < 1.9 else 1.0 + 30 * ease_in_out((t - 1.9) / 1.5) ** 2
        return cam(img, t, 1, 0.6, z, lens[0], lens[1])
    if t < 4.4:  # inside the lens: a tiny pixel sensor
        stars(d, 5, 40)
        chip(d, W / 2, 900, 1.4, 1.0)
        return cam(img, t, 1, 0.4, lerp(1.6, 1.0, ease_out((t - 3.4) / 1.0)))
    stars(d, 7)
    spacecraft(d, W / 2 - 60, 980, 1.25)
    d.ellipse([700, 1180, 1300, 1780], fill=(120, 70, 60))  # a distant world
    return cam(img, t, 1, 0.4, 1.0 + 0.03 * (t - 4.4))


def scene_shrink(t):
    a = t - 6.0
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    k = ease_in_out((t - 8.4) / 4.6)
    s = lerp(1.0, 0.32, k)
    cx, cy = 430, 820
    d.rounded_rectangle([cx - 280 * s, cy - 180 * s, cx + 280 * s, cy + 180 * s], 20 * s, fill=(150, 140, 120), outline=CREAM, width=max(2, int(6 * s)))
    d.rectangle([cx - 200 * s, cy - 240 * s, cx - 60 * s, cy - 180 * s], fill=(120, 110, 95))
    d.ellipse([cx - 120 * s, cy - 120 * s, cx + 120 * s, cy + 120 * s], fill=(30, 28, 32), outline=CREAM, width=max(2, int(8 * s)))
    d.ellipse([cx - 50 * s, cy - 50 * s, cx + 50 * s, cy + 50 * s], fill=(70, 80, 110))
    for k2 in range(3):  # cables that disappear as it shrinks
        d.line([(cx + 280 * s, cy + (k2 - 1) * 60 * s), (cx + 280 * s + 120 * (1 - k), cy + (k2 - 1) * 90)],
               fill=(110, 100, 90, int(255 * (1 - k))), width=8)
    # power-use indicator (conceptual)
    lvl = lerp(1.0, 0.25, k)
    x0, y0, x1, y1 = 820, 560, 940, 1080
    d.rounded_rectangle([x0, y0, x1, y1], 14, outline=CREAM, width=6)
    d.rectangle([x0 + 40, y0 - 24, x1 - 40, y0], fill=CREAM)
    hh = (y1 - y0 - 24) * lvl
    d.rectangle([x0 + 12, y1 - 12 - hh, x1 - 12, y1 - 12], fill=RED if lvl > 0.6 else AMBER)
    d.text((770, 1100), "POWER USE", font=font("oswaldm", 44), fill=CREAM)
    d.text((80, 1160), "CONCEPTUAL ANIMATION — NOT MEASURED DATA", font=font("oswaldm", 34), fill=(160, 150, 135))
    return cam(img, t, 2, 0.6, 1.0 + 0.02 * a / 9)


def scene_chip(t):
    a = t - 15.0
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    cells = smoothstep(16.2, 19.4, t)
    chip(d, W / 2, 820, 1.25, cells)
    if 18.6 < t < 20.7:
        k = ease_out((t - 18.6) / 0.3)
        f = font("anton", 66)
        tw = d.textlength("CMOS ACTIVE-PIXEL SENSOR", font=f)
        d.text(((W - tw) / 2, 1130), "CMOS ACTIVE-PIXEL SENSOR", font=f, fill=CREAM + (int(255 * k),))
    if t >= 20.7:
        k = ease_out_back((t - 20.7) / 0.3, 2)
        f = font("anton", int(120 * k) + 1)
        tw = d.textlength("CAMERA ON A CHIP", font=f)
        d.text(((W - tw) / 2, 1110 + (1 - k) * 40), "CAMERA ON A CHIP", font=f, fill=RED + (255,), stroke_width=6, stroke_fill=(20, 16, 12, 255))
    return cam(img, t, 3, 0.6, 1.0 + 0.03 * a / 10)


NEEDS = [("SMALL", 26.3), ("LOW POWER", 27.6), ("GOOD IMAGES", 28.4)]


def scene_split(t):
    a = t - 25.3
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, 0, W / 2, H], fill=(18, 18, 30))
    stars(d, 9, 50)
    d.rectangle([W / 2 - 3, 200, W / 2 + 3, 1240], fill=(120, 110, 95))
    spacecraft(d, 250, 470, 0.55)
    phone(d, 810, 470, 0.55)
    face(d, 810, 470, 0.5)
    for i, (txt, t0) in enumerate(NEEDS):
        if t < t0:
            continue
        k = ease_out((t - t0) / 0.3)
        y = 820 + i * 120
        f = font("anton", 72)
        tw = d.textlength(txt, font=f)
        d.rounded_rectangle([W / 2 - tw / 2 - 24, y - 6, W / 2 + tw / 2 + 24, y + 92], 16, fill=(20, 16, 12, int(230 * k)), outline=RED + (int(255 * k),), width=4)
        d.text((W / 2 - tw / 2, y), txt, font=f, fill=CREAM + (int(255 * k),))
        d.line([(W / 2 - tw / 2 - 24, y + 43), (250, 650)], fill=(170, 160, 140, int(150 * k)), width=3)
        d.line([(W / 2 + tw / 2 + 24, y + 43), (810, 650)], fill=(170, 160, 140, int(150 * k)), width=3)
    if t > 33.0:  # into commercial products: a chip slides toward the phone side
        k = ease_in_out((t - 33.0) / 1.6)
        chip(d, lerp(W / 2, 810, k), lerp(700, 470, k), 0.18, 1.0)
        al = int(255 * smoothstep(33.4, 34.0, t))
        f = font("oswaldm", 44)
        tw = d.textlength("INTO COMMERCIAL PRODUCTS", font=f)
        d.text(((W - tw) / 2, 1180), "INTO COMMERCIAL PRODUCTS", font=f, fill=AMBER + (al,))
    return cam(img, t, 4, 0.5, 1.0 + 0.02 * a / 12)


def screen_content(d, cx, cy, s, which, t):
    """Phone screen states: video call, selfie, food photo."""
    w, h = 272 * s, 572 * s
    x0, y0 = cx - w / 2, cy - h / 2
    if which == 0:
        d.rectangle([x0, y0, cx + w / 2, cy], fill=(70, 80, 100))
        face(d, cx, cy - h / 4 + 10 * s, 0.6 * s, (200, 150, 110))
        d.rectangle([x0, cy, cx + w / 2, cy + h / 2], fill=(90, 70, 80))
        face(d, cx, cy + h / 4, 0.6 * s, (150, 100, 75))
        d.ellipse([cx - 30 * s, cy + h / 2 - 90 * s, cx + 30 * s, cy + h / 2 - 30 * s], fill=RED)
    elif which == 1:
        d.rectangle([x0, y0, cx + w / 2, cy + h / 2], fill=(110, 140, 170))
        face(d, cx, cy, 0.9 * s)
        d.line([(cx + 60 * s, cy + 140 * s), (cx + 136 * s, cy + 40 * s)], fill=(214, 170, 130), width=int(30 * s))
    else:
        d.rectangle([x0, y0, cx + w / 2, cy + h / 2], fill=(150, 120, 90))
        d.ellipse([cx - 120 * s, cy - 80 * s, cx + 120 * s, cy + 80 * s], fill=(236, 230, 220))
        d.polygon([(cx - 80 * s, cy + 20 * s), (cx + 80 * s, cy - 40 * s), (cx + 60 * s, cy + 30 * s)], fill=(200, 150, 80))
        d.polygon([(cx - 76 * s, cy + 12 * s), (cx + 76 * s, cy - 46 * s), (cx + 74 * s, cy - 30 * s), (cx - 74 * s, cy + 28 * s)], fill=(110, 160, 80))
        d.ellipse([cx - 130 * s, cy - 230 * s, cx - 70 * s, cy - 170 * s], outline=(255, 255, 255), width=int(4 * s))  # focus ring


def scene_uses(t):
    a = t - 37.6
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    if t < 39.6:  # chip shrinks into a phone's camera module
        k = ease_in_out((t - 37.6) / 2.0)
        phone(d, W / 2, 820, lerp(2.4, 1.2, k))
        chip(d, W / 2, lerp(820 - 263 * 2.4 / 1.0 * 0, 820 - 263 * 1.2 * 0, k), lerp(1.2, 0.05, k), 1.0)
        return cam(img, t, 5, 0.4)
    if t < 45.4:  # video call -> selfie -> food photo
        phone(d, W / 2, 820, 1.2)
        which = 0 if t < 41.6 else (1 if t < 43.3 else 2)
        screen_content(d, W / 2, 820, 1.2, which, t)
        for tf in (41.6, 43.3):
            if tf <= t < tf + 0.2:
                d.rounded_rectangle([W / 2 - 165, 820 - 345, W / 2 + 165, 820 + 345], 40, fill=(255, 255, 255, int(150 * (1 - (t - tf) / 0.2))))
        labels = ["VIDEO CALLS", "SELFIES", "YOUR LUNCH"]
        f = font("anton", 72)
        tw = d.textlength(labels[which], font=f)
        d.text(((W - tw) / 2, 230), labels[which], font=f, fill=CREAM)
        return cam(img, t, 5, 0.4, 1.0 + 0.02 * (t - 39.6) / 6)
    # "didn't invent your entire smartphone": the phone's parts, one with roots in space research
    parts = [("SCREEN", 280, 520), ("BATTERY", 800, 520), ("PROCESSOR", 280, 1020), ("CAMERA SENSOR", 800, 1020)]
    k = ease_out((t - 45.4) / 0.6)
    for i, (lab, x, y) in enumerate(parts):
        hot = i == 3 and t > 48.4
        col = RED if hot else (150, 140, 125)
        bx, by = lerp(W / 2, x, k), lerp(820, y, k)
        d.rounded_rectangle([bx - 190, by - 150, bx + 190, by + 150], 24, fill=(36, 32, 30), outline=col, width=6)
        if i == 3:
            chip(d, bx, by - 20, 0.42, 1.0)
        elif i == 1:
            d.rounded_rectangle([bx - 60, by - 100, bx + 60, by + 60], 12, outline=CREAM, width=6)
        elif i == 0:
            d.rectangle([bx - 100, by - 100, bx + 100, by + 60], outline=CREAM, width=6)
        else:
            d.rectangle([bx - 60, by - 80, bx + 60, by + 40], outline=CREAM, width=6)
        f = font("oswaldm", 40)
        tw = d.textlength(lab, font=f)
        d.text((bx - tw / 2, by + 80), lab, font=f, fill=col)
    al = int(255 * smoothstep(46.2, 46.8, t))
    f = font("oswaldm", 40)
    s1 = "+ MANY OTHER INVENTIONS"
    tw = d.textlength(s1, font=f)
    d.text(((W - tw) / 2, 760), s1, font=f, fill=(170, 160, 140, al))
    if t > 48.4:
        al2 = int(255 * smoothstep(48.4, 48.9, t))
        s2 = "ROOTS IN SPACE RESEARCH"
        tw = d.textlength(s2, font=f)
        d.text((800 - tw / 2 if 800 + tw / 2 < W - 20 else W - 20 - tw, 1200), s2, font=f, fill=RED + (al2,))
    return cam(img, t, 5, 0.4)


def scene_end(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    # top: a spacecraft imaging a distant world
    d.rectangle([0, 150, W, 640], fill=(16, 16, 28))
    rng = np.random.default_rng(11)
    for _ in range(40):
        x, y, r = rng.uniform(0, W), rng.uniform(160, 630), rng.uniform(1, 3)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(230, 222, 205, 180))
    lens = spacecraft(d, 260, 380, 0.5)
    d.ellipse([720, 230, 1000, 510], fill=(170, 110, 80))
    for b in range(4):
        d.arc([720, 230 + b * 40, 1000, 510 - b * 40], 200, 340, fill=(140, 85, 60), width=10)
    pulse = (t * 0.8) % 1.0
    d.polygon([lens, (720, 300), (720, 440)], fill=(255, 230, 180, int(50 + 40 * (1 - pulse))))
    # bottom: the phone and the profile-picture attempts
    phone(d, W / 2, 880, 0.78, screen=(110, 140, 170))
    n = 1 + int(np.clip((t - 54.4) / 2.6, 0, 1) * 16)
    tilt = [-6, 0, 6, 3, -3][n % 5]
    face(d, W / 2, 860, 0.64, tilt=tilt)
    f = font("anton", 56)
    lab = f"ATTEMPT {n}"
    tw = d.textlength(lab, font=f)
    d.text(((W - tw) / 2, 1140), lab, font=f, fill=RED if n == 17 else CREAM)
    if 54.4 <= t < 57.1:
        ph = ((t - 54.4) / 2.6 * 16) % 1.0
        if ph < 0.25:
            d.rounded_rectangle([W / 2 - 117, 880 - 234, W / 2 + 117, 880 + 234], 28, fill=(255, 255, 255, int(150 * (1 - ph / 0.25))))
    if t > 58.0:  # wordmark on the final line
        k2 = ease_out_back((t - 58.0) / 0.3, 2.5)
        f = font("anton", int(190 * k2) + 1)
        w = d.textlength("NO WAY.", font=f)
        cy = 270
        d.rectangle([W / 2 - 360, cy - 10, W / 2 + 360, cy + 250], fill=(20, 16, 12, int(235 * min(1, k2))))
        d.text((W / 2 - w / 2, cy + 125 - 125 * k2), "NO WAY.", font=f, fill=(245, 236, 215, 255))
        d.rectangle([W / 2 - 240 * k2, cy + 225, W / 2 + 240 * k2, cy + 238], fill=RED + (255,))
    return cam(img, t, 6, 0.4, 1.0)


SCENES = [(0.0, 6.0, scene_hook), (6.0, 15.0, scene_shrink), (15.0, 25.3, scene_chip), (25.3, 37.6, scene_split),
          (37.6, 51.2, scene_uses), (51.2, 61.01, scene_end)]

HEADS = [(6.1, 14.8, [("EARLY 1990s", AMBER), ("NASA / JPL", CREAM)]),
         (15.1, 18.5, [("ERIC FOSSUM", CREAM), ("+ TEAM", AMBER)])]


def overlay(t):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    if 0.3 <= t < 6.0:  # hook title with drawn icons (no emoji fonts)
        k = ease_out((t - 0.3) / 0.3)
        a = int(255 * k * (1 - smoothstep(5.6, 6.0, t)))
        f = font("anton", 96)
        for txt, y, col in (("SELFIES", 170, CREAM), ("SPACE RESEARCH", 400, RED)):
            tw = d.textlength(txt, font=f)
            d.text(((W - tw) / 2, y), txt, font=f, fill=col + (a,), stroke_width=7, stroke_fill=(0, 0, 0, a))
        mini_phone(d, W / 2 - 170, 345, 0.8, CREAM + (a,))
        link_icon(d, W / 2, 345, 0.9, RED + (a,))
        mini_probe(d, W / 2 + 170, 335, 0.8, CREAM + (a,))
        return layer
    for t0, t1, lines in HEADS:
        if t0 <= t < t1:
            zw.headline(d, lines, 180, t, t0 + 0.02, size=120, gap=134)
            return layer
    return None


def mix(a, b, k):
    return a * (1 - k) + b * k


def frame(idx):
    t = idx / FPS
    for i, (t0, t1, fn) in enumerate(SCENES):
        if t0 <= t < t1:
            img = fn(t)
            if i + 1 < len(SCENES) and t > t1 - 0.3:
                img = mix(img, SCENES[i + 1][2](t1), smoothstep(t1 - 0.3, t1, t))
            break
    out = grade(img, idx, t)
    if t > 60.6:
        out = out * (1 - smoothstep(60.6, 61.0, t) * 0.9)
    pil = to_img(out).convert("RGBA")
    ov = overlay(t)
    if ov is not None:
        pil = Image.alpha_composite(pil, ov)
    cap = mf.caption_layer(t)
    if cap is not None:
        pil = Image.alpha_composite(pil, cap)
    return np.asarray(pil.convert("RGB")).tobytes()


def _init():
    zw.DARK = zw.dark_bg()


if __name__ == "__main__":
    out = sys.argv[1]
    if len(sys.argv) > 2:
        _init()
        for fi in map(int, sys.argv[2:]):
            Image.frombytes("RGB", (W, H), frame(fi)).save(f"{out}_{fi:04d}.png")
        sys.exit()
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "17",
                           "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    with Pool(int(os.environ.get("JOBS", 4)), initializer=_init) as pool:
        for fb in pool.imap(frame, range(NFR), chunksize=4):
            ff.stdin.write(fb)
    ff.stdin.close()
    ff.wait()
