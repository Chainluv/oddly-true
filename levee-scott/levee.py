"""NO WAY. — Petty Crimes, Massive Damage #1: James Scott and the West Quincy levee (1993). 50s, vertical.
CLAUDE.md structure: hook on frame 0, three escalating beats, a new visual every 2-3s, looping ending, series tag,
safe-zone captions. His guilt is disputed: everything he allegedly said is attributed ("witnesses say", "allegedly").
Maps are stylized reconstructions; people are generic icons. Reuses molasses-flood (grade, captions), zanzibar-war
(backgrounds, caption timing), bonus-army (caption grouping) and rap-grammy (stamp)."""
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

DURATION = 50.0
NFR = int(DURATION * FPS)
SERIES = "PETTY CRIMES, MASSIVE DAMAGE #1"
AMBER, RED, CREAM, GREEN = mf.AMBER, (215, 60, 45), (236, 226, 205), (120, 200, 120)
WATER, DEEPW, LAND, SAND = (60, 110, 150), (40, 80, 120), (84, 76, 60), (190, 160, 110)
VOICES = os.path.join(HERE, "voices")

NARR = {"n1": 0.1, "n2": 5.3, "n3": 9.5, "n4": 14.8, "n5": 21.45, "n6": 26.5, "n7": 31.85, "n8": 35.6, "n9": 42.2,
        "n10": 45.4, "n11": 49.0}
TEXT = {"n1": "THIS MAN WAS CONVICTED OF FLOODING A WHOLE TOWN... ALLEGEDLY SO HIS WIFE COULDN'T COME HOME.",
        "n2": "SUMMER, 1993. THE MISSISSIPPI IS IN A HISTORIC FLOOD.",
        "n3": "IN WEST QUINCY, MISSOURI, A 23-YEAR-OLD NAMED JAMES SCOTT HELPS SANDBAG THE LEVEE.",
        "n4": "JULY 16TH, THE LEVEE BREAKS. 14,000 ACRES FLOOD. THE BRIDGE TO QUINCY CLOSES FOR 71 DAYS.",
        "n5": "A POLICE SERGEANT SEES SCOTT ON TV, TALKING ABOUT MOVING SANDBAGS ON THAT LEVEE.",
        "n6": "WITNESSES SAY HE BRAGGED HE'D BREAK IT, TO STRAND HIS WIFE ACROSS THE RIVER, SO HE COULD PARTY.",
        "n7": "HE GOT A LIFE SENTENCE. OVERTURNED. THEN CONVICTED AGAIN.",
        "n8": "BUT HIS DEFENSE SAYS IT COULD HAVE FAILED ON ITS OWN, LIKE OVER A THOUSAND LEVEES THAT SUMMER. SCOTT "
              "STILL SAYS HE DIDN'T DO IT.",
        "n9": "AND HE'S SCHEDULED TO WALK FREE IN 2028.",
        "n10": "SO... DID ONE MAN REALLY FLOOD A TOWN TO KEEP HIS WIFE AWAY?",
        "n11": "NO WAY."}
zw.LINES = [(k, ba.groups(TEXT[k])) for k in NARR]
zw.NARR = NARR
zw.DUR = {k: sf.info(os.path.join(VOICES, f"{k}.wav")).duration for k in NARR}
zw.SPOKEN = {"1993.": "nineteen ninety three", "23-YEAR-OLD": "twenty three year old", "16TH,": "sixteenth",
             "14,000": "fourteen thousand", "71": "seventy one", "2028.": "twenty twenty eight", "TV,": "tee vee"}
mf.CHUNKS = zw.build_chunks()
mf.KEYWORDS = {"FLOODING", "TOWN...", "ALLEGEDLY", "WIFE", "1993.", "FLOOD.", "JAMES", "SCOTT", "BREAKS.", "14,000",
               "ACRES", "71", "DAYS.", "SERGEANT", "TV,", "SANDBAGS", "WITNESSES", "SAY", "STRAND", "PARTY.", "LIFE",
               "OVERTURNED.", "AGAIN.", "OWN,", "THOUSAND", "DIDN'T", "FREE", "2028.", "REALLY", "AWAY?", "WAY."}


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


# Stylized river map: Missouri on the left, Illinois on the right, the Mississippi running down the middle.
MAP_TOP, MAP_BOT = 260, 1180


def river_x(y, t=0.0):
    return 560 + 70 * np.sin((y - MAP_TOP) / 210.0) + 4 * np.sin(t * 2 + y * 0.05)


BREAK = (0, 760)  # x is computed from the west bank at y=760
BRIDGE_Y = 600


def river_map(d, t, width=150, a=255, flood=0.0, labels=True, bridge_dark=False):
    d.rectangle([0, MAP_TOP, W, MAP_BOT], fill=LAND + (a,))
    ys = np.arange(MAP_TOP, MAP_BOT + 10, 10)
    west = [(river_x(y, t) - width / 2, y) for y in ys]
    east = [(river_x(y, t) + width / 2, y) for y in ys[::-1]]
    if flood > 0:  # water spreading across the Missouri floodplain from the break
        bx, by = river_x(760, t) - width / 2, 760
        r = 520 * flood
        for k in range(5, 0, -1):
            rr = r * k / 5
            d.ellipse([bx - rr * 1.2, by - rr, bx + rr * 0.2, by + rr], fill=WATER + (int(a * 0.32),))
    d.polygon(west + east, fill=WATER + (a,))
    d.line(west, fill=SAND + (a,), width=10)  # the levee on the Missouri bank
    bx0, bx1 = river_x(BRIDGE_Y, t) - width / 2 - 60, river_x(BRIDGE_Y, t) + width / 2 + 60
    col = (70, 64, 56) if bridge_dark else CREAM
    d.rectangle([bx0, BRIDGE_Y - 8, bx1, BRIDGE_Y + 8], fill=col + (a,))
    for x in np.linspace(bx0 + 20, bx1 - 20, 5):
        d.line([(x, BRIDGE_Y + 8), (x, BRIDGE_Y + 30)], fill=col + (a,), width=4)
    if labels:
        T(d, "MISSOURI", MAP_TOP + 50, 46, CREAM, int(a * 0.85), x=200, f="oswald")
        T(d, "ILLINOIS", MAP_TOP + 50, 46, CREAM, int(a * 0.85), x=880, f="oswald")
        T(d, "WEST QUINCY", BRIDGE_Y - 50, 34, CREAM, a, x=230, f="oswald")
        T(d, "QUINCY", BRIDGE_Y - 50, 34, CREAM, a, x=870, f="oswald")
        T(d, "STYLIZED MAP", MAP_BOT - 26, 24, (190, 175, 160), int(a * 0.7), x=150, f="oswald")


def person(d, x, by, s, col, a=255, dress=False):
    c = col + (a,)
    d.ellipse([x - 26 * s, by - 170 * s, x + 26 * s, by - 118 * s], fill=c)
    if dress:
        d.polygon([(x - 18 * s, by - 116 * s), (x + 18 * s, by - 116 * s), (x + 46 * s, by), (x - 46 * s, by)], fill=c)
    else:
        d.rounded_rectangle([x - 32 * s, by - 116 * s, x + 32 * s, by], int(14 * s), fill=c)


def sandbag(d, x, y, w=96, h=44, col=SAND, a=255, out=(110, 90, 60)):
    d.rounded_rectangle([x - w / 2, y - h / 2, x + w / 2, y + h / 2], 18, fill=col + (a,), outline=out + (a,), width=3)
    d.line([(x - w / 2 + 12, y), (x + w / 2 - 12, y)], fill=out + (int(a * 0.5),), width=2)


# ---------------------------------------------------------------- scenes
def s_hook(t, text=True):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    river_map(d, t, a=150, labels=False)
    d.rectangle([0, 300, W, 760], fill=(10, 10, 14, 190))
    if text:
        T(d, "HE FLOODED A TOWN", 420, 108, CREAM, stroke=7)  # fully visible on frame 0
        T(d, "TO KEEP HIS WIFE AWAY?", 560, 92, AMBER, stroke=6)
        T(d, "ALLEGEDLY", 680, 48, RED, stroke=3, f="oswald")
    return cam(img, t, 1, 0.4, 1.0 + 0.03 * min(t, 5) / 5, cy=700)


def s_1993(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    k = ease_in_out(np.clip((t - 5.3) / 4.0, 0, 1))
    river_map(d, t, width=110 + 120 * k)
    gx, gy0, gy1 = 960, 430, 1100  # water-level gauge rising
    d.rectangle([gx - 40, gy0, gx + 40, gy1], fill=(20, 18, 16, 230), outline=CREAM + (255,), width=3)
    lvl = lerp(gy1, gy0 + 60, k)
    if lvl < gy1 - 6:
        d.rectangle([gx - 34, lvl, gx + 34, gy1 - 4], fill=(90, 150, 200, 255))
    for i in range(8):
        y = gy1 - i * 90
        d.line([(gx - 40, y), (gx - 20, y)], fill=CREAM + (255,), width=3)
    T(d, "RIVER", gy0 - 30, 32, CREAM, x=gx, f="oswald")
    gm.stamp(img, "1993", 330, 430, ease_out(min(1, (t - 5.4) / 0.18)) if t > 5.4 else 0.0, angle=-8, size=130) \
        if t > 5.4 else None
    T(d, "HISTORIC FLOOD", 1110, 70, AMBER, fade(t, word_t("n2", 0.6)), x=440, stroke=4)
    return cam(img, t, 2, 0.4)


def s_sandbags(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, 900, W, 1180], fill=WATER + (255,))  # water side
    T(d, "THE LEVEE", 280, 100, CREAM, stroke=6)
    T(d, "WEST QUINCY, MISSOURI", 390, 50, AMBER, fade(t, 9.6), stroke=3)
    n = int(np.clip((t - 9.6) / 3.2, 0, 1) * 36)
    hl = 21
    for i in range(n):  # wall stacked block by block
        row, col = i // 9, i % 9
        x = 80 + col * 104 + (52 if row % 2 else 0)
        y = 1050 - row * 46
        if x > W - 60:
            continue
        hot = i == hl and t > word_t("n3", 0.6)
        sandbag(d, x, y, col=(240, 190, 90) if hot else SAND)
    ts = word_t("n3", 0.6)
    if t > ts:
        a = fade(t, ts)
        x = 80 + (hl % 9) * 104 + (52 if (hl // 9) % 2 else 0)
        y = 1050 - (hl // 9) * 46
        d.line([(x, y - 30), (x, 640)], fill=AMBER + (a,), width=4)
        T(d, "JAMES SCOTT, 23", 600, 64, AMBER, a, x=min(max(x, 260), 820), stroke=4)
        T(d, "VOLUNTEER", 530, 40, CREAM, a, x=min(max(x, 260), 820), f="oswald")
    return cam(img, t, 3, 0.4)


def s_break(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    tb = word_t("n4", 0.2)
    fl = ease_out(np.clip((t - tb - 0.3) / 3.0, 0, 1)) if t > tb else 0.0
    tbr = word_t("n4", 0.7)
    river_map(d, t, width=230, flood=fl, bridge_dark=t > tbr)
    T(d, "JULY 16, 1993", 205, 60, CREAM, fade(t, 14.85, 0.15), stroke=4)
    bx, by = river_x(760, t) - 115, 760
    if t > tb:  # crack
        k = min(1, (t - tb) / 0.4)
        pts = [(bx + 12 * np.sin(i * 2.1), by - 70 + i * 14 * k) for i in range(11)]
        d.line(pts, fill=RED + (255,), width=8)
        T(d, "BREAK", by - 120, 60, RED, fade(t, tb, 0.15), x=bx - 150, stroke=4)
    if t > tb + 0.3:
        acres = 14000 * fl
        d.rectangle([40, 880, 600, 1020], fill=(12, 10, 10, 220))
        T(d, f"{acres:,.0f} ACRES", 950, 76, AMBER, stroke=4, x=320)
    if t > tbr:
        a = fade(t, tbr)
        days = int(71 * np.clip((t - tbr) / 1.4, 0, 1))
        T(d, "BRIDGE CLOSED", BRIDGE_Y - 130, 54, RED, a, x=740, stroke=4)
        T(d, f"{days} DAY" + ("" if days == 1 else "S"), BRIDGE_Y + 80, 64, CREAM, a, x=760, stroke=4)
    amp = 0.4 + (12 * np.exp(-(t - tb) * 5) if t > tb else 0)
    return cam(img, t, 4, amp)


def s_tv(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle([90, 360, 990, 1060], 60, fill=(60, 52, 44, 255))   # retro TV
    d.rounded_rectangle([150, 420, 830, 1000], 40, fill=(30, 40, 48, 255))
    sx0, sy0, sx1, sy1 = 150, 420, 830, 1000
    d.rectangle([sx0, 760, sx1, sy1], fill=WATER + (255,))
    for i in range(7):
        sandbag(d, 220 + i * 92, 745, 88, 40)
    person(d, 490, 725, 1.5, (24, 20, 18))
    rng = np.random.default_rng(int(t * 20))
    for _ in range(140):  # static
        x, y = rng.uniform(sx0, sx1), rng.uniform(sy0, sy1)
        d.point((x, y), fill=(200, 200, 200, 90))
    for y in range(sy0, sy1, 6):
        d.line([(sx0, y), (sx1, y)], fill=(0, 0, 0, 40))
    if int(t * 2) % 2 == 0:
        d.rounded_rectangle([180, 450, 300, 500], 8, fill=RED + (255,))
        T(d, "LIVE", 475, 34, CREAM, x=240)
    for k in range(2):
        d.ellipse([880, 520 + k * 120, 950, 590 + k * 120], fill=(30, 26, 22, 255))
    T(d, "ON THE LOCAL NEWS", 215, 70, CREAM, stroke=5)
    tp = word_t("n5", 0.25)
    if t > tp:
        a = fade(t, tp)
        d.rounded_rectangle([150, 900, 830, 990], 8, fill=(14, 12, 10, int(a * 0.85)))
        T(d, "SAYS HE MOVED SANDBAGS", 945, 46, CREAM, a, x=490, f="oswald")
    ts = word_t("n5", 0.05)
    T(d, "A POLICE SGT. GETS SUSPICIOUS", 300, 46, AMBER, fade(t, ts), stroke=3)
    return cam(img, t, 5, 0.4, 1.0 + 0.05 * np.clip((t - 21.4) / 5, 0, 1), cy=700)


def s_split(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    river_map(d, t, width=230, labels=False)
    T(d, "MISSOURI", MAP_TOP + 50, 46, CREAM, x=200, f="oswald")
    T(d, "ILLINOIS", MAP_TOP + 50, 46, CREAM, x=880, f="oswald")
    T(d, "WITNESSES SAY", 400, 70, AMBER, fade(t, 26.55, 0.15), stroke=4)
    tw = word_t("n6", 0.45)
    a = fade(t, tw)
    person(d, 200, 900, 1.6, (215, 150, 170), a, dress=True)
    T(d, "HIS WIFE", 980, 46, CREAM, a, x=200, stroke=3)
    T(d, "STRANDED?", 1040, 40, RED, fade(t, tw + 0.5), x=200, f="oswald")
    person(d, 880, 900, 1.6, (150, 170, 200), fade(t, 26.7))
    T(d, "SCOTT", 980, 46, CREAM, fade(t, 26.7), x=880, stroke=3)
    tp = word_t("n6", 0.82)
    if t > tp:  # party
        for i in range(6):
            ang = t * 3 + i * 1.05
            x, y = 880 + 120 * np.cos(ang), 700 + 60 * np.sin(ang)
            col = [AMBER, RED, GREEN][i % 3]
            d.ellipse([x - 12, y - 12, x + 12, y + 12], fill=col + (fade(t, tp),))
        T(d, "PARTY", 1040, 44, AMBER, fade(t, tp), x=880, f="oswald")
    return cam(img, t, 6, 0.4)


def s_court(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    tg = 31.9  # gavel
    k = np.clip((t - tg) / 0.35, 0, 1)
    ang = np.deg2rad(lerp(-60, 0, ease_in_out(k)))
    px, py = 700, 760
    hx, hy = px - 300 * np.cos(ang), py - 300 * np.sin(ang)
    d.line([(px, py), (hx, hy)], fill=(120, 80, 50, 255), width=26)
    d.polygon([(hx - 70 * np.sin(ang) - 40 * np.cos(ang), hy + 70 * np.cos(ang) - 40 * np.sin(ang)),
               (hx + 70 * np.sin(ang) - 40 * np.cos(ang), hy - 70 * np.cos(ang) - 40 * np.sin(ang)),
               (hx + 70 * np.sin(ang) + 40 * np.cos(ang), hy - 70 * np.cos(ang) + 40 * np.sin(ang)),
               (hx - 70 * np.sin(ang) + 40 * np.cos(ang), hy + 70 * np.cos(ang) + 40 * np.sin(ang))], fill=(140, 95, 60, 255))
    d.rounded_rectangle([250, 860, 830, 920], 12, fill=(110, 75, 50, 255))
    if t > tg + 0.35:
        T(d, "LIFE SENTENCE", 330, 100, RED, fade(t, tg + 0.35, 0.15), stroke=6)
    to = word_t("n7", 0.45)
    if t > to:
        T(d, "1994", 1000, 70, CREAM, x=300, stroke=4)
        d.line([(230, 1000), (370, 1000)], fill=RED + (255,), width=8)
        T(d, "OVERTURNED", 1080, 38, RED, x=300, f="oswald")
    tc = word_t("n7", 0.72)
    if t > tc:
        T(d, "1998", 1000, 70, AMBER, fade(t, tc, 0.15), x=780, stroke=4)
        T(d, "CONVICTED AGAIN", 1080, 38, AMBER, fade(t, tc, 0.15), x=780, f="oswald")
    return cam(img, t, 7, 0.4 + (14 * np.exp(-(t - tg - 0.35) * 8) if t > tg + 0.35 else 0))


def s_levees(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    T(d, "1993: THE WHOLE MIDWEST", 270, 66, CREAM, stroke=4)
    rivers = [[(540 + 120 * np.sin(y / 160), y) for y in range(380, 1180, 20)],                   # Mississippi
              [(540 + 120 * np.sin(y / 160) - (y - 760) * 0.9, y) for y in range(760, 980, 20)],  # Missouri
              [(540 + 120 * np.sin(y / 160) + (700 - y) * 0.7, y) for y in range(420, 700, 20)]]  # Illinois
    for r in rivers:
        d.line(r, fill=WATER + (255,), width=12, joint="curve")
    k = np.clip((t - 35.9) / 3.2, 0, 1)
    rng = np.random.default_rng(11)
    pts = [p for r in rivers for p in r]
    for i in range(int(120 * k)):
        x, y = pts[rng.integers(len(pts))]
        x += rng.uniform(-40, 40)
        y += rng.uniform(-20, 20)
        d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=RED + (220,))
    d.rectangle([140, 400, 940, 540], fill=(12, 10, 10, 220))
    T(d, f"{int(1083 * k):,} LEVEES", 470, 92, AMBER, stroke=4)
    T(d, "OVERTOPPED OR DAMAGED (USGS)", 580, 34, CREAM, fade(t, 36.2), f="oswald")
    td = word_t("n8", 0.78)
    if t > td:
        gm.stamp(img, "SCOTT DENIES IT", W / 2, 1060, ease_out(min(1, (t - td) / 0.18)), angle=-6, size=86)
    else:
        T(d, "DEFENSE: IT COULD FAIL ON ITS OWN", 1080, 46, CREAM, fade(t, 35.7), stroke=3)
    return cam(img, t, 8, 0.4)


def s_release(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    y = 760
    k = ease_in_out(np.clip((t - 42.3) / 2.2, 0, 1))
    d.line([(100, y), (980, y)], fill=(90, 84, 74, 255), width=6)
    d.line([(100, y), (100 + 880 * k, y)], fill=AMBER + (255,), width=10)
    for yr, lab in ((1993, "THE FLOOD"), (2026, "FIRST PAROLE HEARING"), (2028, "SCHEDULED RELEASE")):
        x = 100 + (yr - 1993) / 35 * 880
        if 100 + 880 * k >= x - 2:
            col = GREEN if yr == 2028 else CREAM
            d.ellipse([x - 16, y - 16, x + 16, y + 16], fill=col + (255,))
            T(d, str(yr), y - 70, 60, col, x=min(max(x, 90), 990), stroke=3)
            T(d, lab, y + 60 + (50 if yr == 2026 else 0), 32, CREAM, x=min(max(x, 130), 950), f="oswald")
    T(d, "WALKS FREE IN 2028?", 360, 86, GREEN, fade(t, word_t("n9", 0.5)), stroke=5)
    T(d, "PER MISSOURI DEPT. OF CORRECTIONS", 1000, 32, (200, 185, 165), fade(t, 43.0), f="oswald")
    return cam(img, t, 9, 0.4)


def s_guilty(t):
    if t < 48.9:
        img = base()
        d = ImageDraw.Draw(img, "RGBA")
        k = pop(t, 45.5)
        T(d, "GUILTY?", 560, int(230 * min(1.1, k)) + 1, CREAM, stroke=9)
        for i, (lab, col) in enumerate((("YES", RED), ("NO", GREEN))):
            a = fade(t, 46.4 + i * 0.3)
            x = 330 + i * 420
            d.rounded_rectangle([x - 150, 820, x + 150, 960], 30, fill=col + (int(a * 0.9),), outline=CREAM + (a,), width=4)
            T(d, lab, 890, 80, CREAM, a, x=x, stroke=3)
        T(d, "TELL ME IN THE COMMENTS", 1060, 42, CREAM, fade(t, 47.2), f="oswald")
        return cam(img, t, 10, 0.4)
    img = to_img(s_hook(5.0, text=False)).convert("RGBA")  # back to the opening map: the loop
    d = ImageDraw.Draw(img, "RGBA")
    k2 = ease_out_back((t - 48.9) / 0.25, 2.5)
    f = font("anton", int(170 * k2) + 1)
    w = d.textlength("NO WAY.", font=f)
    cy = 420
    d.rectangle([W / 2 - 330, cy - 10, W / 2 + 330, cy + 230], fill=(20, 16, 12, int(235 * min(1, k2))))
    d.text((W / 2 - w / 2, cy + 115 - 115 * k2), "NO WAY.", font=f, fill=(245, 236, 215, 255))
    d.rectangle([W / 2 - 220 * k2, cy + 205, W / 2 + 220 * k2, cy + 218], fill=RED + (255,))
    return from_img(img.convert("RGB"))


SCENES = [(0.0, 5.2, s_hook), (5.2, 9.4, s_1993), (9.4, 14.7, s_sandbags), (14.7, 21.35, s_break),
          (21.35, 26.4, s_tv), (26.4, 31.75, s_split), (31.75, 35.5, s_court), (35.5, 42.1, s_levees),
          (42.1, 45.3, s_release), (45.3, DURATION + 0.01, s_guilty)]


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
            if i + 1 < len(SCENES) and t > t1 - 0.25:
                k = smoothstep(t1 - 0.25, t1, t)
                img = img * (1 - k) + SCENES[i + 1][2](t1) * k
            break
    if t > 49.55:  # dissolve into frame 0 so the rewatch is seamless
        if FIRST is None:
            FIRST = s_hook(0.0)
        k = smoothstep(49.55, 49.97, t)
        img = img * (1 - k) + FIRST * k
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
