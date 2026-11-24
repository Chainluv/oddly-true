"""NO WAY. — Numbers That Shouldn't Be Real #1: the China National Highway 110 traffic jam (August 2010). 42.5s, vertical.
CLAUDE.md structure: hook on frame 0, three escalating beats, a new visual every 2-3s, looping ending, series tag,
safe-zone captions. Brand visuals: day counter, distance ruler, map with a growing red jam line, price-tag counter,
capacity bars. Maps are stylized reconstructions; trucks and people are generic shapes. Reuses molasses-flood (grade,
captions), zanzibar-war (backgrounds, caption timing), bonus-army (caption grouping) and rap-grammy (stamp)."""
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

DURATION = 42.5
NFR = int(DURATION * FPS)
SERIES = "NUMBERS THAT SHOULDN'T BE REAL #1"
AMBER, RED, CREAM, GREEN = mf.AMBER, (215, 60, 45), (236, 226, 205), (120, 200, 120)
ASPHALT, LANE, DIRT, COAL = (52, 50, 48), (200, 190, 150), (92, 80, 62), (30, 28, 28)
TRUCKS = [(196, 160, 90), (150, 70, 60), (90, 120, 140), (160, 160, 150), (110, 130, 90)]
VOICES = os.path.join(HERE, "voices")

NARR = {"n1": 0.1, "n2": 3.25, "n3": 11.7, "n4": 18.6, "n5": 26.1, "n6": 36.0, "n7": 40.9}
TEXT = {"n1": "THIS TRAFFIC JAM LASTED 12 DAYS.",
        "n2": "AUGUST, 2010. NORTHERN CHINA. HIGHWAY 110 BACKS UP FOR MORE THAN 100 KILOMETERS. OVER 60 MILES OF "
              "TRUCKS, BUMPER TO BUMPER.",
        "n3": "CARS MOVE ABOUT ONE KILOMETER A DAY. SOME DRIVERS ARE STUCK FOR FIVE DAYS STRAIGHT. THEY PLAY CARDS ON "
              "THE HIGHWAY.",
        "n4": "THEN LOCALS SHOW UP SELLING FOOD AND WATER. WATER THAT NORMALLY COSTS ONE YUAN? UP TO FIFTEEN. INSTANT "
              "NOODLES? MORE THAN TRIPLE.",
        "n5": "THE CAUSE: ROAD WORK CUT THE HIGHWAY'S CAPACITY IN HALF, ON A ROAD ALREADY CARRYING 60% MORE TRAFFIC "
              "THAN IT WAS BUILT FOR. MOSTLY COAL TRUCKS, HEADING TO BEIJING.",
        "n6": "SO NEXT TIME YOU'RE STUCK IN TRAFFIC, REMEMBER: THIS JAM LASTED 12 DAYS.",
        "n7": "NO WAY."}
zw.LINES = [(k, ba.groups(TEXT[k])) for k in NARR]
zw.NARR = NARR
zw.DUR = {k: sf.info(os.path.join(VOICES, f"{k}.wav")).duration for k in NARR}
zw.SPOKEN = {"12": "twelve", "2010.": "twenty ten", "110": "one ten", "100": "a hundred", "60": "sixty", "60%": "sixty percent"}
mf.CHUNKS = zw.build_chunks()
mf.KEYWORDS = {"12", "DAYS.", "2010.", "110", "100", "KILOMETERS.", "60", "MILES", "ONE", "KILOMETER", "DAY.", "FIVE",
               "CARDS", "FOOD", "WATER.", "YUAN?", "FIFTEEN.", "TRIPLE.", "HALF,", "60%", "COAL", "BEIJING.", "WAY."}


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


def truck(d, x, y, s=1.0, col=(196, 160, 90), coal=False, a=255):
    """Top-down truck pointing up: cab at the top, trailer behind."""
    w, L = 34 * s, 96 * s
    d.rounded_rectangle([x - w / 2, y - L / 2, x + w / 2, y - L / 2 + 26 * s], int(6 * s), fill=(220, 214, 200, a))   # cab
    d.rectangle([x - w / 2, y - L / 2 + 30 * s, x + w / 2, y + L / 2], fill=col + (a,))                               # trailer
    if coal:
        d.rectangle([x - w / 2 + 4, y - L / 2 + 36 * s, x + w / 2 - 4, y + L / 2 - 6], fill=COAL + (a,))


def road(d, t, x0=330, x1=750, top=200, bot=H, a=255, crawl=0.0, density=1.0, coal=False):
    d.rectangle([0, top, W, bot], fill=DIRT + (a,))
    d.rectangle([x0, top, x1, bot], fill=ASPHALT + (a,))
    lanes = 3
    lw = (x1 - x0) / lanes
    for i in range(1, lanes):
        x = x0 + i * lw
        for y in range(top, bot, 80):
            d.line([(x, y), (x, y + 40)], fill=LANE + (int(a * 0.7),), width=5)
    rng = np.random.default_rng(7)
    gap = int(112 / density)
    for i in range(lanes):
        cx = x0 + lw * (i + 0.5)
        off = rng.uniform(0, gap)
        for k, y in enumerate(np.arange(top - 120, bot + 120, gap)):
            yy = y + off - crawl * (0.8 + 0.2 * i) % gap
            truck(d, cx + rng.uniform(-6, 6), yy, 1.0, TRUCKS[(k + i) % len(TRUCKS)], coal and k % 3 != 1, a)
    d.rectangle([0, 1200, W, 1520], fill=(12, 10, 10, int(a * 0.32)))  # calm band behind the captions


def day_counter(d, day, x, y, a=255, size=1.0, label="DAY"):
    d.rounded_rectangle([x - 150 * size, y - 70 * size, x + 150 * size, y + 70 * size], int(14 * size),
                        fill=(14, 12, 10, int(a * 0.9)), outline=AMBER + (a,), width=4)
    T(d, f"{label} {day}", y, int(86 * size), AMBER, a, x=x)


# Stylized map (reconstruction): Inner Mongolia to the northwest, Hebei, Beijing to the southeast.
LON0, LON1, LAT0, LAT1 = 111.4, 117.2, 39.2, 42.3
MX0, MX1, MY0, MY1 = 60, 1020, 300, 1180


def P(lon, lat):
    return (MX0 + (lon - LON0) / (LON1 - LON0) * (MX1 - MX0), MY0 + (LAT1 - lat) / (LAT1 - LAT0) * (MY1 - MY0))


ROUTE = [(113.1, 41.03), (113.7, 40.95), (114.3, 40.85), (114.88, 40.8), (115.5, 40.5), (115.95, 40.3), (116.4, 39.9)]
BORDER = [(113.6, 42.3), (113.9, 41.6), (114.0, 41.0), (114.1, 40.6), (114.6, 40.2), (114.4, 39.2)]


def route_pts(k):
    pts = [P(*q) for q in ROUTE]
    seg = np.cumsum([0] + [np.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1)])
    L = seg[-1] * k
    out = [pts[0]]
    for i in range(len(pts) - 1):
        if seg[i + 1] <= L:
            out.append(pts[i + 1])
        else:
            f = (L - seg[i]) / (seg[i + 1] - seg[i])
            out.append((lerp(pts[i][0], pts[i + 1][0], f), lerp(pts[i][1], pts[i + 1][1], f)))
            break
    return out


def china_map(d, t, a=255):
    d.rectangle([MX0, MY0, MX1, MY1], fill=(70, 62, 50, a))
    d.polygon([P(*q) for q in BORDER] + [P(LON0, LAT0), P(LON0, LAT1)], fill=(84, 74, 58, a))
    d.line([P(*q) for q in BORDER], fill=(150, 140, 120, int(a * 0.8)), width=4)
    d.line([P(*q) for q in ROUTE], fill=(120, 112, 96, a), width=10, joint="curve")
    d.rectangle([MX0, MY0, MX1, MY1], outline=CREAM + (int(a * 0.5),), width=3)
    T(d, "INNER MONGOLIA", P(112.5, 41.9)[1], 36, (210, 200, 180), int(a * 0.85), x=P(112.5, 41.9)[0], f="oswald")
    T(d, "HEBEI", P(115.6, 41.6)[1], 36, (210, 200, 180), int(a * 0.85), x=P(115.6, 41.6)[0], f="oswald")
    for lab, lon, lat, dy in (("BEIJING", 116.4, 39.9, -40), ("ZHANGJIAKOU", 114.88, 40.8, 44), ("JINING", 113.1, 41.03, 44)):
        p = P(lon, lat)
        d.ellipse([p[0] - 12, p[1] - 12, p[0] + 12, p[1] + 12], fill=CREAM + (a,), outline=(20, 16, 12, a), width=3)
        T(d, lab, p[1] + dy, 32, CREAM, a, x=p[0], stroke=3)
    T(d, "STYLIZED MAP", MY1 - 24, 24, (190, 175, 160), int(a * 0.7), x=MX0 + 100, f="oswald")


def price_tag(d, x, y, txt, s=1.0, col=AMBER, a=255, rot=0):
    d.polygon([(x - 160 * s, y - 80 * s), (x + 120 * s, y - 80 * s), (x + 190 * s, y), (x + 120 * s, y + 80 * s),
               (x - 160 * s, y + 80 * s)], fill=(236, 226, 205, a))
    d.ellipse([x + 100 * s, y - 14 * s, x + 128 * s, y + 14 * s], fill=(18, 14, 11, a))
    T(d, txt, y, int(100 * s), (30, 24, 20), a, x=x - 20 * s)


# ---------------------------------------------------------------- scenes
def s_hook(t, text=True):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    road(d, t, crawl=t * 6)
    d.rectangle([0, 260, W, 760], fill=(10, 10, 14, 200))
    if text:  # fully visible on frame 0
        T(d, "THIS TRAFFIC JAM", 360, 104, CREAM, stroke=7)
        T(d, "LASTED 12 DAYS", 500, 124, AMBER, stroke=7)
        day_counter(d, 1, W / 2, 660, 255, 0.75)
    return cam(img, t, 1, 0.4, 1.0 + 0.03 * min(t, 3) / 3)


def s_size(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    if t < 7.3:  # trucks packing in, distance ruler growing
        dens = 0.5 + 0.6 * ease_out(np.clip((t - 3.3) / 2.5, 0, 1))
        road(d, t, x0=200, x1=620, density=dens, crawl=t * 4)
        k = ease_in_out(np.clip((t - 3.6) / 3.2, 0, 1))
        y1, y0 = 1180, 1180 - 880 * k
        d.line([(800, 1180), (800, y0)], fill=AMBER + (255,), width=8)
        for i in range(int(10 * k) + 1):
            y = 1180 - i * 88
            d.line([(780, y), (820, y)], fill=AMBER + (255,), width=5)
        km = 100 * k
        d.rectangle([700, 240, 1060, 420], fill=(12, 10, 10, 225))
        T(d, f"{km:.0f}+ KM" if k >= 1 else f"{km:.0f} KM", 300, 84, AMBER, x=880)
        T(d, f"{km * 0.621:.0f}+ MILES" if k >= 1 else f"{km * 0.621:.0f} MILES", 380, 48, CREAM, x=880, f="oswald")
    else:  # the map: the jam drawn as a red line along G110
        china_map(d, t)
        k = ease_in_out(np.clip((t - 7.5) / 2.6, 0, 1))
        pts = route_pts(k)
        if len(pts) > 1:
            d.line(pts, fill=RED + (255,), width=16, joint="curve")
            ex, ey = pts[-1]
            r = 20 + 16 * ((t * 2) % 1)
            d.ellipse([ex - r, ey - r, ex + r, ey + r], outline=RED + (int(220 * (1 - (t * 2) % 1)),), width=5)
        T(d, "HIGHWAY 110 (G110)", 1110, 50, RED, fade(t, 7.6), x=W / 2 + 120, stroke=3)
        T(d, "AUGUST 14, 2010", 230, 70, CREAM, fade(t, 7.4), stroke=4)
    return cam(img, t, 2, 0.4)


def s_speed(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    if t < 14.7:  # one car crawling along a 100 km bar
        T(d, "SPEED", 260, 90, CREAM, stroke=5)
        x0, x1, y = 100, 980, 720
        d.rounded_rectangle([x0, y - 30, x1, y + 30], 30, fill=(70, 62, 50, 255), outline=CREAM + (200,), width=3)
        prog = 0.012 * np.clip((t - 11.7) / 3.0, 0, 1)
        d.rounded_rectangle([x0, y - 30, x0 + 60 + (x1 - x0) * prog, y + 30], 30, fill=RED + (255,))
        cx = x0 + 60 + (x1 - x0) * prog
        d.rounded_rectangle([cx - 30, y - 70, cx + 30, y - 38], 8, fill=AMBER + (255,))
        T(d, "0 KM", y + 70, 36, CREAM, x=x0 + 40, f="oswald")
        T(d, "100 KM", y + 70, 36, CREAM, x=x1 - 60, f="oswald")
        T(d, "1 KM / DAY", 960, 120, AMBER, fade(t, word_t("n3", 0.2), 0.15), stroke=6)
    else:  # day counter to 5, drivers playing cards beside the trucks
        road(d, t, x0=420, x1=840, crawl=0)
        day = int(1 + 4 * np.clip((t - 14.8) / 1.6, 0, 1))
        day_counter(d, day, 230, 420, 255, 0.8)
        T(d, "STUCK", 290, 60, CREAM, x=230, stroke=4)
        tc = word_t("n3", 0.72)
        a = fade(t, tc)
        for i, (x, y) in enumerate(((210, 720), (210, 980))):  # card games on the roadside
            d.ellipse([x - 150, y - 66, x + 150, y + 66], fill=(40, 70, 44, a), outline=(20, 30, 20, a), width=4)
            for j in range(4):
                cx = x - 84 + j * 56
                d.rounded_rectangle([cx - 22, y - 34, cx + 22, y + 30], 6, fill=(236, 226, 205, a), outline=(40, 30, 24, a))
                T(d, ["A", "K", "7", "Q"][j], y - 2, 34, RED if j % 2 else (30, 24, 20), a, x=cx, f="oswald")
            for dx in (-170, 170):
                d.ellipse([x + dx - 26, y - 26, x + dx + 26, y + 26], fill=(150, 130, 120, a))
        T(d, "PLAYING CARDS", 1140, 54, AMBER, a, x=210, stroke=3)
    return cam(img, t, 3, 0.4)


def s_hustle(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    tw = word_t("n4", 0.42)
    if t < tw:  # vendors walking along the jam
        road(d, t, x0=540, x1=960, crawl=0)
        T(d, "THE LOCALS", 260, 96, CREAM, stroke=6)
        T(d, "SELLING FOOD + WATER", 370, 56, AMBER, fade(t, 18.8), stroke=4)
        for i in range(5):
            y = 560 + i * 150
            x = lerp(-80, 300 + 40 * (i % 2), ease_out(np.clip((t - 18.7 - i * 0.2) / 1.4, 0, 1)))
            d.ellipse([x - 22, y - 90, x + 22, y - 46], fill=(170, 150, 130, 255))
            d.rounded_rectangle([x - 28, y - 44, x + 28, y + 30], 10, fill=(170, 150, 130, 255))
            d.rectangle([x + 30, y - 20, x + 90, y + 20], fill=(90, 140, 190, 255))  # crate of bottles
            for j in range(3):
                d.rectangle([x + 36 + j * 18, y - 34, x + 46 + j * 18, y - 20], fill=(150, 200, 230, 255))
    elif t < word_t("n4", 0.72):  # price tag counter
        T(d, "A BOTTLE OF WATER", 270, 80, CREAM, stroke=5)
        k = np.clip((t - tw - 0.6) / 0.9, 0, 1)
        price = int(1 + 14 * k ** 2)
        hit = tw + 1.5
        jit = 14 * np.sin(t * 60) * np.exp(-(t - hit) * 6) if t > hit else 0
        price_tag(d, W / 2 + jit, 640, f"¥{price}", 1.4)
        T(d, "NORMALLY ¥1", 880, 56, CREAM, stroke=3)
        if t > hit:
            T(d, "UP TO ¥15", 980, 80, RED, fade(t, hit, 0.12), stroke=5)
    else:  # noodles x3
        T(d, "INSTANT NOODLES", 270, 80, CREAM, stroke=5)
        tn = word_t("n4", 0.72)
        for i in range(3):
            a = fade(t, tn + 0.2 + i * 0.25)
            x = 260 + i * 280
            d.polygon([(x - 90, 520), (x + 90, 520), (x + 70, 760), (x - 70, 760)], fill=(225, 80, 60, a))
            d.rectangle([x - 96, 500, x + 96, 530], fill=(236, 226, 205, a))
            for j in range(3):
                d.arc([x - 60 + j * 10, 460, x + 40 + j * 10, 520], 200, 340, fill=(240, 210, 120, a), width=5)
        T(d, "MORE THAN 3X", 900, 110, AMBER, fade(t, tn + 1.0), stroke=6)
    return cam(img, t, 4, 0.4)


def s_cause(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    tc = word_t("n5", 0.62)
    if t < tc:  # capacity vs traffic bars
        T(d, "THE CAUSE", 240, 100, CREAM, stroke=6)
        x0, bw = 140, 640  # 100% width = 640 px
        t1, t2 = 26.4, word_t("n5", 0.38)
        cap = 1.0 - 0.5 * ease_in_out(np.clip((t - t1 - 0.6) / 1.2, 0, 1))
        y = 520
        T(d, "ROAD CAPACITY", y - 70, 44, CREAM, x=x0, anchor="lm", f="oswald")
        d.rectangle([x0, y - 34, x0 + bw, y + 34], outline=(120, 112, 96, 255), width=3)
        d.rectangle([x0, y - 34, x0 + bw * cap, y + 34], fill=GREEN + (255,))
        T(d, f"{cap * 100:.0f}%", y, 52, CREAM, x=x0 + bw + 90, f="anton")
        if cap < 0.9:
            T(d, "ROAD WORK", y + 70, 40, RED, fade(t, t1 + 1.0), x=x0 + bw * 0.75, f="oswald")
        y = 800
        traffic = 1.0 + 0.6 * ease_out(np.clip((t - t2) / 1.2, 0, 1)) if t > t2 else 1.0
        T(d, "TRAFFIC", y - 70, 44, CREAM, fade(t, t2 - 0.6), x=x0, anchor="lm", f="oswald")
        if t > t2 - 0.6:
            d.rectangle([x0, y - 34, x0 + bw, y + 34], outline=(120, 112, 96, 255), width=3)
            d.rectangle([x0, y - 34, x0 + min(bw * traffic, W - x0 - 10), y + 34], fill=RED + (255,))
            T(d, f"{traffic * 100:.0f}%", y + 80, 52, CREAM, x=x0 + 60)
            if traffic > 1.05:
                T(d, "OVER DESIGN LIMIT", y + 80, 40, RED, x=x0 + 420, f="oswald")
        d.line([(x0 + bw, 430), (x0 + bw, 900)], fill=CREAM + (160,), width=3)
        T(d, "DESIGNED FOR", 960, 32, CREAM, x=x0 + bw, f="oswald")
    else:  # coal trucks to Beijing
        china_map(d, t)
        pts = route_pts(1.0)
        d.line(pts, fill=RED + (200,), width=14, joint="curve")
        k = np.clip((t - tc) / 3.0, 0, 1)
        for i in range(6):
            f = (k * 0.8 + i * 0.12) % 1.0
            p = route_pts(max(0.02, f))[-1]
            d.rectangle([p[0] - 22, p[1] - 14, p[0] + 22, p[1] + 14], fill=(196, 160, 90, 255))
            d.rectangle([p[0] - 18, p[1] - 10, p[0] + 18, p[1] + 2], fill=COAL + (255,))
        T(d, "COAL", 230, 100, CREAM, stroke=6)
        bj = P(116.4, 39.9)
        T(d, "TO BEIJING", bj[1] + 80, 60, AMBER, fade(t, tc + 0.5), x=bj[0] - 60, stroke=4)
    return cam(img, t, 5, 0.4)


def s_loop(t):
    if t < 39.8:  # day counter runs to 12, then CLEARED
        img = base()
        d = ImageDraw.Draw(img, "RGBA")
        road(d, t, crawl=max(0, t - 38.2) * 300, density=1.0 - 0.5 * smoothstep(38.2, 39.6, t))
        d.rectangle([0, 260, W, 760], fill=(10, 10, 14, 200))
        day = int(5 + 7 * np.clip((t - 36.1) / 2.2, 0, 1))
        day_counter(d, day, W / 2, 470, 255, 1.2)
        if t > 38.4:
            T(d, "CLEARED: AUG 26", 660, 70, GREEN, fade(t, 38.4, 0.15), stroke=4)
        return cam(img, t, 6, 0.4)
    img = to_img(s_hook(3.0, text=t < 40.85)).convert("RGBA")  # back to the jam: the loop
    d = ImageDraw.Draw(img, "RGBA")
    if t > 40.9:
        k2 = ease_out_back((t - 40.9) / 0.25, 2.5)
        f = font("anton", int(170 * k2) + 1)
        w = d.textlength("NO WAY.", font=f)
        cy = 400
        d.rectangle([W / 2 - 330, cy - 10, W / 2 + 330, cy + 230], fill=(20, 16, 12, int(235 * min(1, k2))))
        d.text((W / 2 - w / 2, cy + 115 - 115 * k2), "NO WAY.", font=f, fill=(245, 236, 215, 255))
        d.rectangle([W / 2 - 220 * k2, cy + 205, W / 2 + 220 * k2, cy + 218], fill=RED + (255,))
    return from_img(img.convert("RGB"))


SCENES = [(0.0, 3.1, s_hook), (3.1, 11.4, s_size), (11.4, 18.35, s_speed), (18.35, 25.85, s_hustle),
          (25.85, 35.8, s_cause), (35.8, DURATION + 0.01, s_loop)]


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
    if t > 42.0:  # dissolve into frame 0 so the rewatch is seamless
        if FIRST is None:
            FIRST = s_hook(0.0)
        k = smoothstep(42.0, 42.47, t)
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
