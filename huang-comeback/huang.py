"""NO WAY. news — "He Quit. Now a Comeback?" (Jensen Huang / Nvidia, reported Nov. 2026). 45s.
Tech-news look: charcoal, electric green, oversized white type. Reuses molasses-flood (fonts, camera, grain, captions),
zanzibar-war (caption timing) and bonus-army (caption grouping). All people are generic silhouettes; no logos."""
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
from common import (W, H, FPS, font, to_img, from_img, cam2d, shake, lerp, smoothstep, ease_in_out, ease_out,
                    ease_out_back, VIGNETTE, GRAIN)
import render as mf   # captions
import episode as zw  # build_chunks()
import bonus as ba    # groups()

DURATION = 45.0
NFR = int(DURATION * FPS)
BG = (24, 25, 28)
BG2 = (34, 36, 40)
GREEN = (60, 255, 120)
WHITE = (245, 245, 245)
GREY = (150, 155, 160)
mf.AMBER = GREEN  # caption keyword colour for this episode
VOICES = os.path.join(HERE, "voices")

NARR = {"n01": 0.1, "n02": 4.1, "n03": 9.8, "n04": 14.0, "n05": 19.5, "n06": 21.6, "n07": 24.4, "n08": 29.2,
        "n09": 36.0, "n10": 39.2, "n11": 41.1, "n12": 43.8}
TEXT = {"n01": "NO WAY. THE CEO WHO JUST RESIGNED COULD ALREADY BE PLOTTING A COMEBACK.",
        "n02": "JENSEN HUANG LEFT NVIDIA LAST WEEK AFTER 33 YEARS LEADING THE COMPANY HE CO-FOUNDED.",
        "n03": "NOW, REPORTS SAY HE'S DISCUSSED RETURNING WITH PEOPLE CLOSE TO HIM.",
        "n04": "AND A PETITION DEMANDING HIS REINSTATEMENT HAS PASSED 177,000 SIGNATURES.",
        "n05": "ELON MUSK PUBLICLY BACKED IT.",
        "n06": "EPIC GAMES BOSS TIM SWEENEY SHARED IT TOO.",
        "n07": "SUPPORTERS WANT HUANG BACK WHILE AN INDEPENDENT INVESTIGATION ESTABLISHES THE FACTS.",
        "n08": "MEANWHILE, FINANCE CHIEF COLETTE KRESS IS SERVING AS INTERIM CEO, AND NVIDIA IS SEARCHING FOR A "
               "PERMANENT REPLACEMENT.",
        "n09": "BUT SIGNATURES DON'T APPOINT A CEO. THE BOARD DOES.",
        "n10": "A COMEBACK HASN'T BEEN ANNOUNCED.",
        "n11": "AND EARNINGS ARRIVE NOVEMBER 17TH.",
        "n12": "NO WAY."}
zw.LINES = [(k, ba.groups(TEXT[k])) for k in NARR]
zw.LINES[6] = ("n07", [["SUPPORTERS", "WANT", "HUANG"], ["BACK", "WHILE", "AN"], ["INDEPENDENT"], ["INVESTIGATION"],
                       ["ESTABLISHES", "THE", "FACTS."]])
zw.NARR = NARR
zw.DUR = {k: sf.info(os.path.join(VOICES, f"{k}.wav")).duration for k in NARR}
zw.SPOKEN = {"33": "thirty three", "177,000": "one hundred seventy seven thousand", "17TH.": "seventeenth"}
mf.CHUNKS = zw.build_chunks()
mf.KEYWORDS = {"RESIGNED", "COMEBACK.", "33", "REPORTS", "177,000", "MUSK", "SWEENEY", "INDEPENDENT", "INVESTIGATION",
               "INTERIM", "CEO,", "BOARD", "DOES.", "HASN'T", "ANNOUNCED.", "17TH.", "WAY."}


# ---------------------------------------------------------------- helpers
def canvas():
    img = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(img, "RGBA")
    for x in range(0, W, 90):  # faint tech grid
        d.line([(x, 0), (x, H)], fill=(255, 255, 255, 10), width=1)
    for y in range(0, H, 90):
        d.line([(0, y), (W, y)], fill=(255, 255, 255, 10), width=1)
    return img, d


def T(d, txt, y, size, col=WHITE, a=255, x=None, stroke=0):
    f = font("anton", size)
    tw = d.textlength(txt, font=f)
    d.text(((W - tw) / 2 if x is None else x, y), txt, font=f, fill=col + (a,), stroke_width=stroke, stroke_fill=(0, 0, 0, a))
    return tw


def pill(d, txt, y, a=255, col=GREEN, size=40):
    f = font("oswald", size)
    tw = d.textlength(txt, font=f)
    d.rounded_rectangle([W / 2 - tw / 2 - 28, y, W / 2 + tw / 2 + 28, y + size + 30], 40, outline=col + (a,), width=4, fill=(0, 0, 0, int(a * 0.5)))
    d.text((W / 2 - tw / 2, y + 12), txt, font=f, fill=col + (a,))


def pop(t, t0, dur=0.25):
    return ease_out_back((t - t0) / dur, 2.2) if t >= t0 else 0.0


def glow_rect(d, box, col=GREEN, r=18, a=255):
    for k, al in ((14, 30), (8, 60), (3, 140)):
        d.rounded_rectangle([box[0] - k, box[1] - k, box[2] + k, box[3] + k], r + k, outline=col + (int(al * a / 255),), width=3)


def chip(d, cx, cy, s=1.0, a=255, glow=1.0):
    w = 300 * s
    for k in range(7):
        o = -w / 2 + 30 * s + k * (w - 60 * s) / 6
        for side in (-1, 1):
            p, q = sorted((side * (w / 2), side * (w / 2 + 34 * s)))
            d.rectangle([cx + o - 8 * s, cy + p, cx + o + 8 * s, cy + q], fill=(170, 175, 180, a))
            d.rectangle([cx + p, cy + o - 8 * s, cx + q, cy + o + 8 * s], fill=(170, 175, 180, a))
    d.rounded_rectangle([cx - w / 2, cy - w / 2, cx + w / 2, cy + w / 2], 22 * s, fill=(20, 22, 24, a), outline=GREEN + (a,), width=max(2, int(5 * s)))
    d.rounded_rectangle([cx - w / 4, cy - w / 4, cx + w / 4, cy + w / 4], 12 * s, fill=(40, 60, 46, a))
    for k in range(5):
        d.line([(cx - w / 4 + 10 * s, cy - w / 4 + (k + 1) * w / 12), (cx + w / 4 - 10 * s, cy - w / 4 + (k + 1) * w / 12)], fill=GREEN + (int(a * 0.5),), width=2)
    if glow > 0:
        glow_rect(d, [cx - w / 2, cy - w / 2, cx + w / 2, cy + w / 2], GREEN, 22, int(a * glow))


def rack(d, x0, y0, x1, y1, t, slot_open=None):
    d.rounded_rectangle([x0, y0, x1, y1], 16, fill=(30, 32, 36), outline=(70, 74, 80), width=4)
    n = 9
    sh = (y1 - y0 - 40) / n
    for i in range(n):
        y = y0 + 20 + i * sh
        d.rectangle([x0 + 20, y + 4, x1 - 20, y + sh - 4], fill=(40, 43, 48) if i != slot_open else (10, 10, 12))
        for k in range(4):
            on = (int(t * 6 + i * 3 + k * 7) % 5) != 0
            d.ellipse([x1 - 60 - k * 22, y + sh / 2 - 6, x1 - 48 - k * 22, y + sh / 2 + 6], fill=GREEN if on else (40, 70, 50))
    return y0 + 20 + slot_open * sh + sh / 2 if slot_open is not None else None


def silhouette(d, cx, by, s=1.0, col=(70, 74, 80), a=255):
    """Generic head-and-shoulders silhouette (no likeness)."""
    d.chord([cx - 230 * s, by - 260 * s, cx + 230 * s, by + 200 * s], 180, 360, fill=col + (a,))
    d.ellipse([cx - 95 * s, by - 470 * s, cx + 95 * s, by - 250 * s], fill=col + (a,))


def finish(img, idx, t):
    arr = np.asarray(img.convert("RGB"), np.float32) / 255.0
    arr = arr * (0.55 + 0.45 * VIGNETTE)
    arr = np.clip(arr + GRAIN[idx % len(GRAIN)][..., None] * 0.02, 0, 1)
    return arr


def cam(img, t, seed, amp=1.0, zoom=1.0, cy=H / 2):
    sx, sy, sr = shake(t, amp, 2, seed=seed)
    return cam2d(img.convert("RGB"), zoom, W / 2, cy, sr, sx, sy).convert("RGBA")


# ---------------------------------------------------------------- beats
def beat_hook(t, img, d):
    oy = rack(d, 180, 560, 900, 1240, t, slot_open=4)
    # chip slides out, then snaps back toward its socket
    out = ease_out((t - 0.3) / 1.3)
    back = ease_in_out((t - 2.0) / 0.6)
    x = 540 + 380 * out - 300 * back
    jx = (np.sin(t * 90) * 10) if 1.95 < t < 2.3 else 0
    chip(d, x + jx, oy, 0.6)
    k = pop(t, 0.15)
    T(d, "HE QUIT.", 170, int(150 * min(1.2, k)) + 1, WHITE)
    k2 = pop(t, 0.6)
    T(d, "NOW A COMEBACK?", 330, int(120 * min(1.2, k2)) + 1, GREEN)
    if t > 1.0:
        pill(d, "RETURN REPORTED • NOT CONFIRMED", 490, int(255 * smoothstep(1.0, 1.3, t)), size=36)
    return 2.5 * (1 if 1.95 < t < 2.4 else 0)


def beat_timeline(t, img, d):
    if t < 6.6:  # 1993 -> 2026
        p = ease_in_out((t - 4.2) / 2.2)
        y = 900
        d.line([(110, y), (970, y)], fill=(80, 84, 90), width=10)
        d.line([(110, y), (lerp(110, 970, p), y)], fill=GREEN, width=12)
        for i in range(34):
            x = lerp(110, 970, i / 33)
            hgt = 28 if i % 5 == 0 else 14
            d.line([(x, y - hgt), (x, y + hgt)], fill=(GREEN if i / 33 <= p else (90, 94, 100)) + (255,), width=4)
        T(d, "1993", 960, 90, WHITE, x=80)
        T(d, "2026", 960, 90, GREEN if p > 0.98 else GREY, x=820)
        T(d, "CO-FOUNDED NVIDIA", 1080, 46, GREY, x=80)
        yr = int(lerp(1993, 2026, p))
        T(d, str(yr), 560, 220, WHITE)
        return 0.6
    if t < 8.4:  # 33 YEARS fills the frame
        k = pop(t, 6.6, 0.3)
        T(d, "33", 380, int(560 * min(1.15, k)) + 1, GREEN)
        T(d, "YEARS", 940, int(200 * min(1.15, k)) + 1, WHITE)
        return 2.0 * np.exp(-(t - 6.6) * 6)
    k = pop(t, 8.4, 0.25)  # snaps into a RESIGNED card
    s = min(1.1, k)
    d.rounded_rectangle([W / 2 - 400 * s, 640 - 220 * s, W / 2 + 400 * s, 640 + 260 * s], 30, fill=(245, 245, 245, 255))
    T(d, "RESIGNED", int(640 - 170 * s), int(160 * s) + 1, BG)
    T(d, "33 YEARS • CO-FOUNDER", int(640 + 40 * s), int(54 * s) + 1, (40, 120, 70))
    T(d, "NOV. 12, 2026", int(640 + 130 * s), int(54 * s) + 1, (90, 94, 100))
    return 3.0 * np.exp(-(t - 8.4) * 8)


def beat_talks(t, img, d):
    silhouette(d, W / 2, 1180, 1.1)
    rng = np.random.default_rng(int(t > 12.4) + 3)
    spots = [(200, 560), (880, 600), (160, 900), (920, 930), (280, 1150), (820, 1170)]
    for i, (x, y) in enumerate(spots):
        t0 = 10.1 + i * 0.32 + (0.0 if t < 12.4 else 0)
        k = pop(t, t0, 0.2)
        if k <= 0:
            continue
        if t > 12.4:  # second sub-beat: bubbles shuffle positions
            x, y = spots[(i + 2) % len(spots)]
            x, y = lerp(spots[i][0], x, ease_in_out((t - 12.4) / 0.5)), lerp(spots[i][1], y, ease_in_out((t - 12.4) / 0.5))
        w, h = 200 * k, 110 * k
        d.line([(x, y), (W / 2, 900)], fill=GREEN + (90,), width=3)
        d.rounded_rectangle([x - w / 2, y - h / 2, x + w / 2, y + h / 2], 30, fill=(46, 50, 56, 255), outline=GREEN + (200,), width=4)
        d.polygon([(x - 20, y + h / 2), (x + 10, y + h / 2), (x - 26, y + h / 2 + 30)], fill=(46, 50, 56, 255))
        for k2 in range(3):
            on = int(t * 4 + i + k2) % 3 == 0
            d.ellipse([x - 50 + k2 * 40, y - 10, x - 30 + k2 * 40, y + 10], fill=(GREEN if on else (120, 125, 130)) + (255,))
    T(d, "RETURN DISCUSSIONS", 200, 104, WHITE)
    T(d, "REPORTED", 330, 110, GREEN)  # stays visible for the whole beat
    T(d, "PER FINANCIAL TIMES REPORT • NOV. 15", 1260, 34, GREY)
    return 0.6


def beat_petition(t, img, d):
    p = smoothstep(14.2, 18.4, t) ** 1.6  # accelerating counter
    n = int(177000 * p)
    for i in range(22):  # signature lines filling a page
        if i / 22 > p:
            break
        y = 520 + i * 15
        pts = [(140 + k * 12, y + 8 * np.sin(k * 1.7 + i)) for k in range(int(40 + (i * 7) % 20))]
        d.line(pts, fill=(90, 160, 110, 160), width=3)
    num = f"{n:,}" + ("+" if t > 18.4 else "")
    T(d, num, 880, 190, GREEN if t > 18.4 else WHITE)
    T(d, "SIGNATURES", 1130, 70, WHITE)
    T(d, "REINSTATEMENT PETITION", 230, 84, WHITE)
    if t > 18.4:
        a = int(255 * smoothstep(18.4, 18.7, t))
        T(d, "Reported Nov. 16, 2026", 360, 48, GREEN, a)
        T(d, "NAMES SELF-REPORTED • UNVERIFIED", 430, 34, GREY, a)
    return 3.0 * np.exp(-(t - 18.4) * 8) if t > 18.4 else 0.4


def beat_person(t, img, d, t0, name, role, act):
    k = pop(t, t0, 0.3)
    s = min(1.15, k)
    T(d, name.split()[0], 420, int(260 * s) + 1, WHITE)
    T(d, name.split()[1], 690, int(260 * s) + 1, WHITE)
    T(d, role, 990, 52, GREY, int(255 * smoothstep(t0 + 0.2, t0 + 0.4, t)))
    a = int(255 * smoothstep(t0 + 0.35, t0 + 0.6, t))
    f = font("anton", 96)
    tw = d.textlength(act, font=f)
    d.rounded_rectangle([W / 2 - tw / 2 - 30, 1080, W / 2 + tw / 2 + 30, 1210], 20, fill=GREEN + (a,))
    d.text((W / 2 - tw / 2, 1086), act, font=f, fill=BG + (a,))
    return 2.0 * np.exp(-(t - t0) * 7)


def beat_investigation(t, img, d):
    if t < 26.6:
        k = pop(t, 24.3)
        T(d, "SUPPORTERS:", 520, int(110 * min(1.1, k)) + 1, GREY)
        T(d, "BRING HIM BACK", 660, int(150 * min(1.1, k)) + 1, WHITE)
        for i in range(6):  # raised-hand silhouettes
            x = 140 + i * 160
            d.ellipse([x - 30, 1000, x + 30, 1060], fill=(70, 74, 80, 255))
            d.rounded_rectangle([x - 50, 1060, x + 50, 1200], 30, fill=(70, 74, 80, 255))
            d.line([(x + 40, 1080), (x + 70, 960 - 20 * np.sin(t * 6 + i))], fill=(70, 74, 80, 255), width=22)
        return 0.6
    T(d, "WHILE AN", 220, 90, GREY)
    T(d, "INDEPENDENT", 330, 150, WHITE)
    T(d, "INVESTIGATION", 500, 150, GREEN)
    T(d, "ESTABLISHES THE FACTS", 680, 64, WHITE)
    # magnifier scanning a document
    d.rounded_rectangle([300, 820, 780, 1240], 18, fill=(46, 50, 56, 255))
    for i in range(9):
        d.line([(340, 870 + i * 40), (740 - (i % 3) * 80, 870 + i * 40)], fill=(110, 115, 120, 255), width=6)
    mx = 420 + 220 * (0.5 + 0.5 * np.sin((t - 26.6) * 2.4))
    my = 960 + 80 * np.sin((t - 26.6) * 1.7)
    d.ellipse([mx - 80, my - 80, mx + 80, my + 80], outline=GREEN, width=12)
    d.line([(mx + 56, my + 56), (mx + 140, my + 140)], fill=GREEN, width=20)
    return 0.4


def boardroom(d, t):
    d.polygon([(140, 1240), (940, 1240), (800, 940), (280, 940)], fill=(44, 46, 52, 255))  # table
    for i, (x, y, s) in enumerate([(240, 1000, 0.32), (370, 960, 0.28), (710, 960, 0.28), (840, 1000, 0.32)]):
        silhouette(d, x, y, s, (80, 84, 90))
    glow_rect(d, [280, 940, 800, 950], GREEN, 4, 120)


def beat_kress(t, img, d):
    boardroom(d, t)
    if t < 32.6:
        k = pop(t, 29.3, 0.3)
        s = min(1.1, k)
        d.rounded_rectangle([W / 2 - 420 * s, 380 - 40 * s, W / 2 + 420 * s, 380 + 400 * s], 26, fill=(245, 245, 245, 255))
        T(d, "INTERIM CEO", int(380), int(90 * s) + 1, (40, 120, 70))
        T(d, "COLETTE", int(380 + 110 * s), int(120 * s) + 1, BG)
        T(d, "KRESS", int(380 + 230 * s), int(120 * s) + 1, BG)
        T(d, "NVIDIA CFO", int(380 + 410 * s), int(44 * s) + 1, (220, 225, 230))
        return 2.0 * np.exp(-(t - 29.3) * 7)
    T(d, "SEARCHING FOR A", 220, 86, GREY)
    T(d, "PERMANENT CEO", 320, 130, WHITE)
    for i in range(4):  # blank candidate cards cycling (no names)
        x = 150 + i * 205
        lit = int((t - 32.6) * 4) % 4 == i
        d.rounded_rectangle([x, 520, x + 175, 820], 18, fill=(46, 50, 56, 255), outline=(GREEN if lit else (90, 94, 100)) + (255,), width=5)
        d.ellipse([x + 52, 560, x + 122, 630], fill=(90, 94, 100, 255))
        d.text((x + 72, 680), "?", font=font("anton", 80), fill=(GREEN if lit else (120, 125, 130)) + (255,))
    return 0.4


def beat_board(t, img, d):
    if t < 37.5:
        k = pop(t, 35.9, 0.25)
        T(d, "177,000+", 300, int(170 * min(1.1, k)) + 1, GREY)
        T(d, "SIGNATURES", 500, 80, GREY)
        a = int(255 * smoothstep(36.3, 36.6, t))
        d.line([(160, 450), (920, 380)], fill=GREEN + (a,), width=14)
        T(d, "DON'T APPOINT", 700, 120, WHITE, a)
        T(d, "A CEO.", 850, 120, WHITE, a)
        return 0.5
    boardroom(d, t)
    k = pop(t, 37.5, 0.3)
    T(d, "THE BOARD", 300, int(170 * min(1.1, k)) + 1, WHITE)
    T(d, "DOES.", 500, int(190 * min(1.1, k)) + 1, GREEN)
    return 2.5 * np.exp(-(t - 37.5) * 7)


def beat_not(t, img, d):
    T(d, "COMEBACK:", 440, 130, GREY)
    k = pop(t, 39.4, 0.2)
    s = min(1.1, k)
    f = font("anton", int(150 * s) + 1)
    tw = d.textlength("NOT ANNOUNCED", font=f)
    d.rounded_rectangle([W / 2 - tw / 2 - 30, 640, W / 2 + tw / 2 + 30, 640 + 190 * s], 18, outline=WHITE, width=10)
    d.text((W / 2 - tw / 2, 650), "NOT ANNOUNCED", font=f, fill=WHITE)
    return 3.0 * np.exp(-(t - 39.4) * 8)


def beat_earnings(t, img, d):
    k = pop(t, 41.1, 0.3)
    s = min(1.1, k)
    d.rounded_rectangle([W / 2 - 280 * s, 380, W / 2 + 280 * s, 380 + 560 * s], 30, fill=(245, 245, 245, 255))
    d.rounded_rectangle([W / 2 - 280 * s, 380, W / 2 + 280 * s, 380 + 140 * s], 30, fill=GREEN)
    T(d, "NOV", int(395), int(100 * s) + 1, BG)
    T(d, "17", int(380 + 160 * s), int(320 * s) + 1, BG)
    T(d, "EARNINGS", 1010, 120, WHITE)
    chip(d, W / 2, 1270 - 40, 0.25, glow=0.5 + 0.5 * np.sin(t * 6))
    return 2.0 * np.exp(-(t - 41.1) * 7)


def beat_end(t, img, d):
    k = ease_out_back((t - 43.7) / 0.3, 2.5)
    f = font("anton", int(230 * min(1.1, k)) + 1)
    tw = d.textlength("NO WAY.", font=f)
    d.text((W / 2 - tw / 2, 640), "NO WAY.", font=f, fill=WHITE)
    bw = 520 * ease_out((t - 43.8) / 0.4)
    d.rectangle([W / 2 - bw / 2, 940, W / 2 + bw / 2, 954], fill=GREEN)
    return 2.0 * np.exp(-(t - 43.7) * 8)


BEATS = [(0.0, 4.0, beat_hook), (4.0, 9.8, beat_timeline), (9.8, 14.0, beat_talks), (14.0, 19.3, beat_petition),
         (19.3, 21.6, lambda t, i, d: beat_person(t, i, d, 19.35, "ELON MUSK", "TESLA CEO", "PUBLICLY BACKED IT")),
         (21.6, 24.2, lambda t, i, d: beat_person(t, i, d, 21.65, "TIM SWEENEY", "EPIC GAMES CEO", "SHARED IT")),
         (24.2, 29.1, beat_investigation), (29.1, 35.8, beat_kress), (35.8, 39.1, beat_board), (39.1, 41.0, beat_not),
         (41.0, 43.6, beat_earnings), (43.6, 45.01, beat_end)]


def frame(idx):
    t = idx / FPS
    for t0, t1, fn in BEATS:
        if t0 <= t < t1:
            img, d = canvas()
            amp = fn(t, img, d)
            # quick whip-in at each beat change
            zin = 1.0 + 0.06 * (1 - smoothstep(t0, t0 + 0.18, t)) if t0 > 0 else 1.0
            img = cam(img, t, int(t0 * 10), amp, zin)
            break
    arr = finish(img, idx, t)
    if t > 44.6:
        arr = arr * (1 - smoothstep(44.6, 45.0, t) * 0.9)
    pil = to_img(arr).convert("RGBA")
    cap = mf.caption_layer(t)
    if cap is not None:
        pil = Image.alpha_composite(pil, cap)
    return np.asarray(pil.convert("RGB")).tobytes()


if __name__ == "__main__":
    out = sys.argv[1]
    if len(sys.argv) > 2:
        for fi in map(int, sys.argv[2:]):
            Image.frombytes("RGB", (W, H), frame(fi)).save(f"{out}_{fi:04d}.png")
        sys.exit()
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "17",
                           "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    with Pool(int(os.environ.get("JOBS", 4))) as pool:
        for fb in pool.imap(frame, range(NFR), chunksize=4):
            ff.stdin.write(fb)
    ff.stdin.close()
    ff.wait()
