"""NO WAY. — America's Forgotten Attacks #1: the Black Tom explosion (Jersey City, July 30, 1916). 48s, vertical.
Follows the CLAUDE.md structure: hook on frame 0, three escalating beats, a new visual every 2-3s, a looping ending,
a persistent series tag and safe-zone captions. Maps are stylized reconstructions; the statue is a generic silhouette.
Reuses molasses-flood (grade, captions), zanzibar-war (backgrounds, caption timing, clock), bonus-army (caption
grouping) and rap-grammy (stamp)."""
import os
import subprocess
import sys
from multiprocessing import Pool

import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
for sub in ("bonus-army", "rap-grammy", "zanzibar-war", "molasses-flood"):
    sys.path.insert(0, os.path.join(HERE, "..", sub))
from common import W, H, FPS, font, to_img, from_img, cam2d, shake, grade, lerp, smoothstep, ease_in_out, ease_out, ease_out_back
import render as mf   # captions
import episode as zw  # dark_bg(), build_chunks()
import bonus as ba    # groups()
import grammy as gm   # stamp()

DURATION = 48.0
NFR = int(DURATION * FPS)
SERIES = "AMERICA'S FORGOTTEN ATTACKS #1"
AMBER, RED, CREAM = mf.AMBER, (215, 60, 45), (236, 226, 205)
FIRE, SEA, LAND, COPPER = (250, 170, 70), (34, 52, 62), (78, 70, 58), (120, 160, 140)
VOICES = os.path.join(HERE, "voices")

NARR = {"n1": 0.1, "n2": 3.8, "n3": 12.35, "n4": 16.15, "n5": 21.5, "n6": 26.8, "n7": 33.5, "n8": 40.4, "n9": 45.4}
TEXT = {"n1": "THIS IS WHY YOU CAN'T GO UP THE STATUE OF LIBERTY'S TORCH.",
        "n2": "JULY 30TH, 1916. 2:08 A.M. GERMAN SABOTEURS BLEW UP A MUNITIONS DEPOT ON BLACK TOM ISLAND, IN JERSEY "
              "CITY.",
        "n3": "ABOUT TWO MILLION POUNDS OF AMMUNITION WENT UP AT ONCE.",
        "n4": "THE BLAST WAS FELT IN PHILADELPHIA. WINDOWS SHATTERED UP TO 25 MILES AWAY.",
        "n5": "IT HIT LIKE A MAGNITUDE FIVE EARTHQUAKE. AND AMERICA WASN'T EVEN IN THE WAR YET.",
        "n6": "SHRAPNEL TORE INTO LADY LIBERTY. HER TORCH ARM WAS DAMAGED, AND THE TORCH HAS BEEN CLOSED TO THE PUBLIC "
              "EVER SINCE.",
        "n7": "IN 1939, GERMANY WAS FOUND RESPONSIBLE. THE LAST PAYMENT DIDN'T COME UNTIL 1979.",
        "n8": "SIXTY-THREE YEARS TO PAY FOR ONE NIGHT. AND THAT'S WHY THE TORCH IS STILL CLOSED.",
        "n9": "NO WAY."}
zw.LINES = [(k, ba.groups(TEXT[k])) for k in NARR]
zw.NARR = NARR
zw.DUR = {k: sf.info(os.path.join(VOICES, f"{k}.wav")).duration for k in NARR}
zw.SPOKEN = {"30TH,": "thirtieth", "1916.": "nineteen sixteen", "2:08": "two oh eight", "A.M.": "a m", "25": "twenty five",
             "1939,": "nineteen thirty nine", "1979.": "nineteen seventy nine", "SIXTY-THREE": "sixty three"}
mf.CHUNKS = zw.build_chunks()
mf.KEYWORDS = {"TORCH.", "1916.", "2:08", "GERMAN", "SABOTEURS", "BLACK", "TOM", "TWO", "MILLION", "POUNDS",
               "PHILADELPHIA.", "25", "MILES", "EARTHQUAKE.", "WAR", "YET.", "SHRAPNEL", "LIBERTY.", "CLOSED", "EVER",
               "SINCE.", "1939,", "GERMANY", "1979.", "SIXTY-THREE", "YEARS", "ONE", "NIGHT.", "STILL", "WAY."}


def word_t(pid, frac):
    return NARR[pid] + zw.DUR[pid] * frac


# ---------------------------------------------------------------- helpers
def base():
    return to_img(zw.DARK).convert("RGBA")


def cam(img, t, seed, amp=0.6, zoom=1.0, cy=H / 2, cx=W / 2):
    sx, sy, sr = shake(t, amp, 1.8, seed=seed)
    return from_img(cam2d(img.convert("RGB"), zoom, cx, cy, sr, sx, sy))


def T(d, txt, y, size, col=CREAM, a=255, x=W / 2, f="anton", stroke=0, anchor="mm"):
    if a <= 2:
        return
    d.text((x, y), txt, font=font(f, size), fill=col + (a,), anchor=anchor, stroke_width=stroke, stroke_fill=(8, 8, 10, a))


def fade(t, t0, dur=0.3):
    return int(255 * smoothstep(t0, t0 + dur, t))


def pop(t, t0, dur=0.3):
    return ease_out_back(np.clip((t - t0) / dur, 0, 1), 2.2) if t > t0 else 0.0


def statue(d, cx, by, s, col=COPPER, a=255, shake_arm=0.0):
    """Generic Statue of Liberty silhouette: robe, crown, raised torch arm, tablet."""
    c = col + (a,)
    d.polygon([(cx - 120 * s, by), (cx - 95 * s, by - 520 * s), (cx - 60 * s, by - 600 * s), (cx + 60 * s, by - 600 * s),
               (cx + 90 * s, by - 520 * s), (cx + 110 * s, by)], fill=c)
    d.ellipse([cx - 48 * s, by - 700 * s, cx + 48 * s, by - 596 * s], fill=c)
    for k in range(7):  # crown rays
        ang = np.deg2rad(-160 + k * 23.3)
        x0, y0 = cx + 40 * s * np.cos(ang), by - 660 * s + 40 * s * np.sin(ang)
        d.polygon([(x0 - 8 * s, y0), (x0 + 8 * s, y0), (cx + 95 * s * np.cos(ang), by - 660 * s + 95 * s * np.sin(ang))], fill=c)
    ax, ay = cx + 70 * s + shake_arm, by - 1000 * s  # raised arm and torch
    d.line([(cx + 55 * s, by - 560 * s), (ax, ay)], fill=c, width=int(46 * s))
    d.polygon([(ax - 34 * s, ay), (ax + 34 * s, ay), (ax + 22 * s, ay + 70 * s), (ax - 22 * s, ay + 70 * s)], fill=c)
    d.rectangle([ax - 44 * s, ay - 16 * s, ax + 44 * s, ay + 4 * s], fill=c)          # torch balcony
    d.polygon([(ax - 30 * s, ay - 16 * s), (ax, ay - 110 * s), (ax + 30 * s, ay - 16 * s)], fill=(235, 190, 90, a))  # flame
    d.polygon([(cx - 90 * s, by - 380 * s), (cx - 30 * s, by - 420 * s), (cx - 20 * s, by - 280 * s),
               (cx - 80 * s, by - 250 * s)], fill=(int(col[0] * 0.8), int(col[1] * 0.8), int(col[2] * 0.8), a))  # tablet
    return ax, ay


def padlock(d, x, y, s, a=255):
    d.arc([x - 40 * s, y - 90 * s, x + 40 * s, y - 10 * s], 180, 360, fill=CREAM + (a,), width=int(14 * s))
    d.line([(x - 40 * s, y - 50 * s), (x - 40 * s, y - 20 * s)], fill=CREAM + (a,), width=int(14 * s))
    d.line([(x + 40 * s, y - 50 * s), (x + 40 * s, y - 20 * s)], fill=CREAM + (a,), width=int(14 * s))
    d.rounded_rectangle([x - 62 * s, y - 24 * s, x + 62 * s, y + 70 * s], int(12 * s), fill=AMBER + (a,))
    d.ellipse([x - 10 * s, y + 10 * s, x + 10 * s, y + 30 * s], fill=(40, 30, 20, a))


# Stylized regional map (a reconstruction, not to survey accuracy)
LON0, LON1, LAT0, LAT1 = -76.0, -72.8, 39.35, 41.4
MX0, MX1, MY0, MY1 = 40, 1040, 300, 1180


def P(lat, lon):
    return (MX0 + (lon - LON0) / (LON1 - LON0) * (MX1 - MX0), MY0 + (LAT1 - lat) / (LAT1 - LAT0) * (MY1 - MY0))


BLACK_TOM, PHILLY, MANHATTAN = (40.69, -74.05), (39.95, -75.16), (40.76, -73.98)
OCEAN = [(40.47, -74.0), (40.3, -73.98), (40.0, -74.05), (39.75, -74.12), (39.5, -74.3), (39.35, -74.42),
         (39.35, -72.8), (40.72, -72.8), (40.63, -73.3), (40.59, -73.75), (40.57, -73.97), (40.5, -74.05)]
DELAWARE = [(41.4, -75.05), (40.9, -75.1), (40.55, -75.05), (40.22, -74.77), (40.0, -74.97), (39.95, -75.14),
            (39.8, -75.35), (39.55, -75.55), (39.35, -75.5)]
HUDSON = [(41.4, -73.95), (41.0, -73.92), (40.75, -74.0), (40.69, -74.03), (40.6, -74.05)]


def region_map(d, a=255):
    d.rectangle([MX0, MY0, MX1, MY1], fill=LAND + (a,))
    d.polygon([P(*q) for q in OCEAN], fill=SEA + (a,))
    d.line([P(*q) for q in DELAWARE], fill=SEA + (a,), width=10, joint="curve")
    d.line([P(*q) for q in HUDSON], fill=SEA + (a,), width=12, joint="curve")
    d.rectangle([MX0, MY0, MX1, MY1], outline=CREAM + (int(a * 0.6),), width=3)
    for lab, la, lo in (("PENNSYLVANIA", 40.95, -75.55), ("NEW JERSEY", 40.2, -74.55), ("NEW YORK", 41.2, -74.4)):
        T(d, lab, P(la, lo)[1], 34, (200, 190, 170), int(a * 0.8), x=P(la, lo)[0], f="oswald")
    T(d, "STYLIZED MAP", MY1 - 24, 24, (190, 175, 160), int(a * 0.7), x=MX1 - 110, f="oswald")


def dot(d, p, r, col, a=255, label=None, dy=-44):
    d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=col + (a,), outline=(20, 16, 12, a), width=3)
    if label:
        T(d, label, p[1] + dy, 36, CREAM, a, x=p[0], stroke=3)


# ---------------------------------------------------------------- scenes
def s_hook(t, text=True):
    """Frame 0: the hook on screen at full opacity. Also the loop target."""
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    for r in range(6, 0, -1):  # night glow behind the torch
        rr = r * 90
        d.ellipse([620 - rr, 420 - rr, 620 + rr, 420 + rr], fill=(60, 50, 40, 22))
    statue(d, 520, 1500, 1.15)
    if text:
        T(d, "WHY YOU CAN'T GO UP", 290, 92, CREAM, stroke=6)
        T(d, "THE TORCH", 410, 130, AMBER, stroke=7)
    a = fade(t, 1.6)
    padlock(d, 860, 760, 1.0, a)
    T(d, "CLOSED", 900, 60, RED, a, x=860, stroke=4)
    return cam(img, t, 1, 0.4, 1.0 + 0.04 * min(t, 3.8) / 3.8, cy=700)


def s_night(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    if t < 7.2:  # 2:08 a.m. clock
        cx, cy, r = W / 2, 720, 260
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(236, 226, 205, 255), outline=(40, 30, 24, 255), width=10)
        for k in range(12):
            ang = np.deg2rad(k * 30 - 90)
            d.line([(cx + 0.82 * r * np.cos(ang), cy + 0.82 * r * np.sin(ang)),
                    (cx + 0.94 * r * np.cos(ang), cy + 0.94 * r * np.sin(ang))], fill=(40, 30, 24, 255), width=8)
        mins = 8 + (t - 3.8) * 0.1
        for ln, ang, w in ((0.5, (2 + mins / 60) * 30 - 90, 16), (0.78, mins * 6 - 90, 10)):
            a_ = np.deg2rad(ang)
            d.line([(cx, cy), (cx + ln * r * np.cos(a_), cy + ln * r * np.sin(a_))], fill=(30, 24, 20, 255), width=w)
        d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=RED + (255,))
        T(d, "JULY 30, 1916", 300, 100, CREAM, fade(t, 3.85, 0.2), stroke=6)
        T(d, "2:08 A.M.", 1080, 110, AMBER, fade(t, word_t("n2", 0.3), 0.2), stroke=6)
    else:  # the harbor: Black Tom next to the statue
        k = ease_in_out(np.clip((t - 7.2) / 4.5, 0, 1))
        d.rectangle([0, 300, W, 1180], fill=SEA + (255,))
        d.polygon([(0, 300), (330, 300), (360, 700), (300, 1180), (0, 1180)], fill=LAND + (255,))       # Jersey City
        d.polygon([(760, 300), (1080, 300), (1080, 800), (900, 780), (820, 560)], fill=LAND + (255,))   # Manhattan
        d.polygon([(330, 760), (520, 740), (530, 800), (330, 830)], fill=LAND + (255,))                  # Black Tom pier
        d.ellipse([560, 900, 640, 960], fill=LAND + (255,))                                              # Liberty Island
        statue(d, 600, 935, 0.12)
        T(d, "JERSEY CITY", 360, 40, CREAM, x=170, f="oswald")
        T(d, "MANHATTAN", 360, 40, CREAM, x=920, f="oswald")
        T(d, "STATUE OF LIBERTY", 1010, 34, CREAM, x=600, f="oswald")
        for i in range(int(14 * min(1, (t - 7.4) / 1.6))):  # munitions stacked on the pier
            x, y = 350 + (i % 7) * 24, 770 + (i // 7) * 24
            d.rectangle([x, y, x + 20, y + 20], fill=(150, 110, 60, 255), outline=(60, 40, 20, 255))
        a = fade(t, 7.5)
        T(d, "BLACK TOM ISLAND", 690, 52, AMBER, a, x=430, stroke=4)
        T(d, "MUNITIONS DEPOT", 880, 38, CREAM, fade(t, 8.2), x=430, f="oswald")
        ts = word_t("n2", 0.55)
        if t > ts:
            T(d, "GERMAN SABOTEURS", 290, 70, RED, fade(t, ts), stroke=5)
            for j in range(3):  # little figures slipping onto the pier
                x = lerp(120, 390 + j * 40, ease_out(np.clip((t - ts) / 1.5, 0, 1)))
                d.ellipse([x - 9, 806, x + 9, 824], fill=(20, 18, 16, 255))
                d.rectangle([x - 8, 824, x + 8, 856], fill=(20, 18, 16, 255))
        return cam(img, t, 2, 0.3, 1.0 + 0.1 * k, cy=800, cx=lerp(W / 2, 480, k))
    return cam(img, t, 2, 0.3)


def s_blast(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    k = np.clip((t - 12.35) / 0.6, 0, 1)
    d.rectangle([0, 0, W, H], fill=(255, 230, 170, int(255 * (1 - k))))  # the flash
    cy = 820
    for r in range(8, 0, -1):  # fireball
        rr = (60 + r * 55) * (0.4 + 0.6 * ease_out(min(1, (t - 12.35) / 1.2))) * (1 + 0.03 * np.sin(t * 20 + r))
        col = (255, int(120 + 15 * r), 50)
        d.ellipse([W / 2 - rr, cy - rr * 0.85, W / 2 + rr, cy + rr * 0.85], fill=col + (int(40 + 18 * (8 - r)),))
    rng = np.random.default_rng(int(t * 30))
    for _ in range(40):  # sparks
        ang, dist = rng.uniform(0, 2 * np.pi), rng.uniform(100, 520)
        x, y = W / 2 + dist * np.cos(ang), cy + dist * np.sin(ang) * 0.8
        d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(255, 220, 140, 220))
    t0 = word_t("n3", 0.2)
    v = 2_000_000 * (1 - (1 - np.clip((t - t0) / 1.6, 0, 1)) ** 3) if t > t0 else 0
    d.rectangle([60, 250, W - 60, 420], fill=(12, 10, 10, 220))
    T(d, f"{v:,.0f} LBS", 335, 110, AMBER, stroke=5)
    T(d, "OF AMMUNITION", 480, 56, CREAM, fade(t, t0 + 0.3), stroke=4)
    amp = 3 + 22 * np.exp(-(t - 12.35) * 2.5)
    return cam(img, t, 3, amp)


def s_shock(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    region_map(d)
    src = P(*BLACK_TOM)
    pxd = np.hypot(P(*PHILLY)[0] - src[0], P(*PHILLY)[1] - src[1])
    for i in range(4):  # spreading pulses
        r = ((t - 16.0) * 260 - i * 180)
        if r > 0:
            a = int(220 * max(0, 1 - r / 1100))
            d.ellipse([src[0] - r, src[1] - r, src[0] + r, src[1] + r], outline=FIRE + (a,), width=8)
    r25 = 25 / 70 * pxd * 0.83  # 25 miles at this map scale (Jersey City to Philadelphia is about 80 mi)
    tw = word_t("n4", 0.55)
    if t > tw:
        a = fade(t, tw)
        d.ellipse([src[0] - r25, src[1] - r25, src[0] + r25, src[1] + r25], outline=RED + (a,), width=6)
        T(d, "WINDOWS BROKEN: 25 MI", src[1] - r25 - 30, 40, RED, a, x=src[0] - 40, stroke=3)
    dot(d, src, 16, FIRE, 255, "BLACK TOM", 46)
    tp = word_t("n4", 0.2)
    dot(d, P(*PHILLY), 14, CREAM, fade(t, tp), "FELT IN PHILADELPHIA", -46)
    if t > tp:
        rr = 30 + 30 * ((t - tp) * 2 % 1)
        q = P(*PHILLY)
        d.ellipse([q[0] - rr, q[1] - rr, q[0] + rr, q[1] + rr], outline=CREAM + (int(200 * (1 - (t - tp) * 2 % 1)),), width=4)
    T(d, "THE SHOCKWAVE", 220, 90, CREAM, stroke=5)
    return cam(img, t, 4, 0.5)


def s_quake(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    tq = word_t("n5", 0.5)
    if t < tq + 0.6:  # seismograph
        d.rectangle([60, 520, W - 60, 980], fill=(236, 226, 205, 255))
        for y in range(560, 980, 60):
            d.line([(60, y), (W - 60, y)], fill=(190, 180, 160, 255), width=2)
        n = int(np.clip((t - 21.4) / 2.0, 0, 1) * 200)
        pts = []
        for i in range(n):
            x = 70 + i * 4.7
            amp = 8 + 200 * np.exp(-((i - 70) / 18.0) ** 2) * (i > 60)
            pts.append((x, 750 + amp * np.sin(i * 1.9)))
        if len(pts) > 1:
            d.line(pts, fill=(30, 26, 24, 255), width=4)
        T(d, "LIKE A MAGNITUDE ~5", 400, 80, AMBER, fade(t, 21.6), stroke=5)
        T(d, "EARTHQUAKE", 1080, 90, CREAM, fade(t, 22.4), stroke=5)
    else:  # timeline: the U.S. wasn't at war yet
        T(d, "AMERICA WASN'T AT WAR YET", 300, 70, CREAM, stroke=5)
        y = 760
        d.line([(100, y), (980, y)], fill=CREAM + (255,), width=6)
        for yr, lab in ((1914, "WWI BEGINS"), (1916, "BLACK TOM"), (1917, "U.S. ENTERS")):
            x = 100 + (yr - 1914) / 3.5 * 880
            col = FIRE if yr == 1916 else (RED if yr == 1917 else CREAM)
            tt = tq + 0.6 + (yr - 1914) * 0.5
            a = fade(t, tt)
            d.ellipse([x - 16, y - 16, x + 16, y + 16], fill=col + (a,))
            T(d, str(yr), y - 70, 64, col, a, x=x, stroke=3)
            T(d, lab, y + 70, 36, CREAM, a, x=x, f="oswald")
        T(d, "APRIL 1917", 980, 60, RED, fade(t, tq + 2.4), x=W / 2 + 200, stroke=4)
    return cam(img, t, 5, 0.4 + (10 * np.exp(-(t - 22.3) * 4) if 22.3 < t < tq + 0.6 else 0))


def s_statue(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    hit = word_t("n6", 0.1)
    arm = 14 * np.sin(t * 40) * np.exp(-(t - hit - 0.6) * 3) if t > hit + 0.6 else 0
    statue(d, 470, 1500, 1.1, shake_arm=arm)
    rng = np.random.default_rng(3)
    for i in range(12):  # shrapnel streaking in from the left (Black Tom's side)
        ti = hit + i * 0.08
        if t > ti:
            k = min(1, (t - ti) / 0.4)
            ty = rng.uniform(500, 1400)
            tx = 470 + rng.uniform(-60, 80)
            x = lerp(-50, tx, k)
            if k < 1:
                d.line([(x - 60, ty + 10), (x, ty)], fill=FIRE + (230,), width=5)
            else:
                d.ellipse([tx - 7, ty - 7, tx + 7, ty + 7], fill=(40, 30, 24, 255))
    T(d, "SHRAPNEL HIT LADY LIBERTY", 250, 66, CREAM, fade(t, hit), stroke=5)
    tc = word_t("n6", 0.6)
    if t > tc:
        a = fade(t, tc)
        padlock(d, 850, 700, 1.0, a)
        T(d, "TORCH CLOSED", 850, 54, RED, a, x=850, stroke=4)
        T(d, "SINCE 1916", 920, 46, CREAM, fade(t, tc + 0.4), x=850, stroke=3)
    return cam(img, t, 6, 0.4 + (8 * np.exp(-(t - hit - 0.6) * 5) if t > hit + 0.6 else 0), cy=900)


def s_pay(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    T(d, "WHO PAYS?", 250, 100, CREAM, stroke=6)
    y = 700
    k = ease_in_out(np.clip((t - 33.6) / 5.5, 0, 1))
    x1 = 100 + 880 * k
    d.line([(100, y), (980, y)], fill=(90, 84, 74, 255), width=6)
    d.line([(100, y), (x1, y)], fill=AMBER + (255,), width=10)
    for yr, lab in ((1916, "BLAST"), (1939, "RULED RESPONSIBLE"), (1979, "LAST PAYMENT")):
        x = 100 + (yr - 1916) / 63 * 880
        if x1 >= x - 2:
            col = RED if yr == 1979 else CREAM
            d.ellipse([x - 16, y - 16, x + 16, y + 16], fill=col + (255,))
            T(d, str(yr), y - 70, 58, col, x=min(max(x, 90), 990), stroke=3)
            T(d, lab, y + 60, 32, CREAM, x=min(max(x, 120), 960), f="oswald")
    T(d, f"{1916 + int(63 * k)}", 960, 150, AMBER, fade(t, 33.6), stroke=6)
    ts = word_t("n7", 0.45)
    if t > ts:
        gm.stamp(img, "GERMANY RESPONSIBLE", W / 2, 460, ease_out(min(1, (t - ts) / 0.18)), angle=-6, size=80)
    return cam(img, t, 7, 0.4)


def s_loop(t):
    """'63 years' counter, then back to the hook composition with the wordmark, dissolving into frame 0."""
    if t < word_t("n8", 0.5):
        img = base()
        d = ImageDraw.Draw(img, "RGBA")
        k = np.clip((t - 40.4) / 1.4, 0, 1)
        T(d, f"{int(63 * k)}", 650, 330, AMBER, stroke=10)
        T(d, "YEARS TO PAY", 900, 90, CREAM, stroke=5)
        T(d, "FOR ONE NIGHT", 1010, 70, CREAM, fade(t, word_t("n8", 0.3)), stroke=4)
        return cam(img, t, 8, 0.4)
    img = to_img(s_hook(3.8, text=t < 45.3)).convert("RGBA")  # the torch again: the loop
    d = ImageDraw.Draw(img, "RGBA")
    if t > 45.4:
        k2 = ease_out_back((t - 45.4) / 0.3, 2.5)
        f = font("anton", int(170 * k2) + 1)
        w = d.textlength("NO WAY.", font=f)
        cy = 620
        d.rectangle([W / 2 - 330, cy - 10, W / 2 + 330, cy + 230], fill=(20, 16, 12, int(235 * min(1, k2))))
        d.text((W / 2 - w / 2, cy + 115 - 115 * k2), "NO WAY.", font=f, fill=(245, 236, 215, 255))
        d.rectangle([W / 2 - 220 * k2, cy + 205, W / 2 + 220 * k2, cy + 218], fill=RED + (255,))
    return from_img(img.convert("RGB"))


SCENES = [(0.0, 3.7, s_hook), (3.7, 12.2, s_night), (12.2, 16.0, s_blast), (16.0, 21.3, s_shock),
          (21.3, 26.6, s_quake), (26.6, 33.3, s_statue), (33.3, 40.2, s_pay), (40.2, DURATION + 0.01, s_loop)]


def series_tag(pil):
    d = ImageDraw.Draw(pil, "RGBA")
    f = font("oswald", 34)
    w = d.textlength(SERIES, font=f)
    d.rounded_rectangle([W / 2 - w / 2 - 22, 92, W / 2 + w / 2 + 22, 146], 10, fill=(14, 12, 10, 200),
                        outline=RED + (230,), width=3)
    d.text((W / 2, 119), SERIES, font=f, fill=CREAM + (255,), anchor="mm")


FIRST = None


def frame(idx):
    global FIRST
    t = idx / FPS
    img = None
    for i, (t0, t1, fn) in enumerate(SCENES):
        if t0 <= t < t1:
            img = fn(t)
            if i + 1 < len(SCENES) and t > t1 - 0.3:
                k = smoothstep(t1 - 0.3, t1, t)
                img = img * (1 - k) + SCENES[i + 1][2](t1) * k
            break
    if t > 47.3:  # dissolve into frame 0 so the rewatch is seamless
        if FIRST is None:
            FIRST = s_hook(0.0)
        img = img * (1 - smoothstep(47.3, 47.95, t)) + FIRST * smoothstep(47.3, 47.95, t)
    out = grade(img, idx, t, keep_color=0.5)
    pil = to_img(out).convert("RGBA")
    cap = mf.caption_layer(t)
    if cap is not None:
        pil = Image.alpha_composite(pil, cap)
    series_tag(pil)
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
