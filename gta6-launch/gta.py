"""NO WAY. — GTA 6's $3.79 Billion Day (Grand Theft Auto VI launch, November 19, 2026). 60s, vertical.
Reuses molasses-flood (grade, captions), zanzibar-war (backgrounds, caption timing), bonus-army (caption grouping) and
rap-grammy (stamp). No game art, logos or screenshots: a generic sunset skyline and the show's own type only."""
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

DURATION = 60.0
NFR = int(DURATION * FPS)
AMBER, RED, CREAM, GREEN = mf.AMBER, (215, 60, 45), (236, 226, 205), (120, 200, 120)
PINK, TEAL = (225, 95, 150), (70, 190, 190)
VOICES = os.path.join(HERE, "voices")

NARR = {"n1": 0.1, "n2": 6.2, "n3": 13.4, "n4": 18.4, "n5": 23.0, "n6": 32.1, "n7": 37.3, "n8": 46.3, "n9": 53.2,
        "n10": 56.9}
TEXT = {"n1": "NO WAY... A VIDEO GAME JUST MADE MORE MONEY IN ONE DAY THAN ANY MOVIE, ALBUM, OR SHOW IN HISTORY.",
        "n2": "GRAND THEFT AUTO VI LAUNCHED ON NOVEMBER 19TH, 2026. THE LAST ONE CAME OUT IN 2013.",
        "n3": "ITS FIRST TRAILER SMASHED YOUTUBE RECORDS. THEN THE GAME WAS DELAYED. TWICE.",
        "n4": "SO WHEN IT FINALLY DROPPED, FANS DIDN'T JUST BUY IT. THEY STAMPEDED.",
        "n5": "PUBLISHER TAKE-TWO SAYS GTA VI PULLED IN $3.79 BILLION IN DAY-ONE SALES. A RECORD FOR ANY ENTERTAINMENT "
              "LAUNCH, EVER.",
        "n6": "BEFORE IT EVEN CAME OUT, IT HAD ALREADY SOLD 32.5 MILLION COPIES.",
        "n7": "FOR COMPARISON, GTA V MADE ABOUT $800 MILLION ON ITS FIRST DAY. THAT WAS A RECORD TOO. VI MADE NEARLY "
              "FIVE TIMES AS MUCH.",
        "n8": "ONE ANALYTICS FIRM ESTIMATED LOWER, AROUND $2.4 BILLION. EVEN THAT IS TRIPLE GTA V.",
        "n9": "THIRTEEN YEARS OF WAITING. ONE DAY OF BUYING.",
        "n10": "NO WAY."}
zw.LINES = [(k, ba.groups(TEXT[k])) for k in NARR]
zw.NARR = NARR
zw.DUR = {k: sf.info(os.path.join(VOICES, f"{k}.wav")).duration for k in NARR}
zw.SPOKEN = {"VI": "six", "V": "five", "19TH,": "nineteenth", "2026.": "twenty twenty six", "2013.": "twenty thirteen",
             "TAKE-TWO": "take two", "GTA": "G T A", "$3.79": "three point seven nine", "DAY-ONE": "day one",
             "32.5": "thirty two and a half", "$800": "eight hundred dollars", "$2.4": "two point four"}
mf.CHUNKS = zw.build_chunks()
mf.KEYWORDS = {"ONE", "DAY", "HISTORY.", "VI", "2026.", "2013.", "YOUTUBE", "RECORDS.", "DELAYED.", "TWICE.",
               "STAMPEDED.", "$3.79", "BILLION", "RECORD", "EVER.", "32.5", "MILLION", "$800", "FIVE", "TIMES",
               "$2.4", "TRIPLE", "THIRTEEN", "YEARS", "WAY."}


def word_t(pid, frac):
    return NARR[pid] + zw.DUR[pid] * frac


# ---------------------------------------------------------------- helpers
def base():
    return to_img(zw.DARK).convert("RGBA")


def cam(img, t, seed, amp=0.6, zoom=1.0, cy=H / 2):
    sx, sy, sr = shake(t, amp, 1.8, seed=seed)
    return from_img(cam2d(img.convert("RGB"), zoom, W / 2, cy, sr, sx, sy))


def T(d, txt, y, size, col=CREAM, a=255, x=W / 2, f="anton", stroke=0, anchor="mm"):
    if a <= 2:
        return
    d.text((x, y), txt, font=font(f, size), fill=col + (a,), anchor=anchor, stroke_width=stroke, stroke_fill=(8, 8, 10, a))


def fade(t, t0, dur=0.35):
    return int(255 * smoothstep(t0, t0 + dur, t))


def pop(t, t0, dur=0.3):
    return ease_out_back(np.clip((t - t0) / dur, 0, 1), 2.2) if t > t0 else 0.0


def money(v):
    if v >= 1e9:
        return f"${v / 1e9:.2f}B"
    return f"${v / 1e6:.0f}M"


def sunset(d, t, horizon=1180, a=255):
    """Generic coastal sunset: banded sky, sun, palm and skyline silhouettes."""
    top, bot = (40, 26, 52), (230, 120, 90)
    for y in range(0, horizon, 10):
        k = y / horizon
        d.rectangle([0, y, W, y + 10], fill=tuple(int(lerp(a_, b_, k ** 1.4)) for a_, b_ in zip(top, bot)) + (a,))
    r = 220
    for i in range(6):  # striped sun
        y0 = horizon - 360 + i * 60
        d.chord([W / 2 - r, horizon - 360 - r + 120, W / 2 + r, horizon - 360 + r + 120], 180, 360, fill=(245, 170, 90, a))
    for i in range(5):
        y = horizon - 200 + i * 34
        d.rectangle([W / 2 - r, y, W / 2 + r, y + 10 + i * 3], fill=top + (a,))
    rng = np.random.default_rng(4)
    x = 0
    while x < W:  # skyline
        w = rng.integers(60, 130)
        h = rng.integers(120, 420)
        d.rectangle([x, horizon - h, x + w, horizon], fill=(24, 16, 30, a))
        x += w + rng.integers(0, 20)
    for px, s in ((120, 1.0), (930, 0.85)):  # palms
        sway = 10 * np.sin(t * 1.2 + px)
        d.line([(px, horizon), (px + 20 * s + sway, horizon - 420 * s)], fill=(16, 10, 20, a), width=int(18 * s))
        cx, cy = px + 20 * s + sway, horizon - 420 * s
        for ang in range(0, 360, 45):
            rr = np.deg2rad(ang + 10 * np.sin(t + ang))
            d.line([(cx, cy), (cx + 170 * s * np.cos(rr), cy + 70 * s * np.sin(rr) + 40 * s)], fill=(16, 10, 20, a), width=int(14 * s))
    d.rectangle([0, horizon, W, H], fill=(14, 10, 18, a))


def runner(d, x, by, s, ph, col=(150, 130, 120), a=255):
    """Generic running figure."""
    c = col + (a,)
    d.ellipse([x - 22 * s, by - 190 * s, x + 22 * s, by - 146 * s], fill=c)
    d.line([(x, by - 146 * s), (x + 8 * s, by - 70 * s)], fill=c, width=int(26 * s))
    sw = np.sin(ph)
    d.line([(x + 8 * s, by - 70 * s), (x + 8 * s + 40 * s * sw, by)], fill=c, width=int(18 * s))
    d.line([(x + 8 * s, by - 70 * s), (x + 8 * s - 40 * s * sw, by)], fill=c, width=int(18 * s))
    d.line([(x, by - 130 * s), (x - 40 * s * sw, by - 80 * s)], fill=c, width=int(14 * s))


def game_box(d, x, y, s, a=255):
    d.rounded_rectangle([x - 70 * s, y - 95 * s, x + 70 * s, y + 95 * s], int(10 * s), fill=(60, 30, 50, a), outline=CREAM + (a,), width=3)
    d.rectangle([x - 70 * s, y - 95 * s, x + 70 * s, y - 60 * s], fill=(30, 30, 34, a))
    T(d, "VI", y + 10 * s, int(80 * s), PINK, a, x=x)


# ---------------------------------------------------------------- scenes
def s_hook(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    sunset(d, t)
    d.rectangle([0, 300, W, 900], fill=(10, 8, 12, 150))
    k = pop(t, 0.3)
    T(d, "$3.79B", 500, int(240 * min(1.1, k)) + 1, AMBER, stroke=8)
    T(d, "IN ONE DAY", 690, int(110 * min(1.1, k)) + 1, CREAM, stroke=6)
    T(d, "MORE THAN ANY MOVIE, ALBUM OR SHOW", 830, 48, CREAM, fade(t, word_t("n1", 0.6)), f="oswald")
    return cam(img, t, 1, 0.5, 1.0 + 0.02 * t / 6)


def s_wait(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    k = np.clip((t - 6.6) / 4.5, 0, 1)
    yr = int(2013 + 13 * ease_in_out(k))
    d.rounded_rectangle([290, 380, 790, 880], 30, fill=(236, 226, 205, 255))
    d.rectangle([290, 380, 790, 500], fill=RED + (255,))
    T(d, "YEAR", 440, 60, CREAM)
    T(d, str(yr), 690, 190, (30, 26, 24))
    T(d, "GTA V: 2013", 200, 70, CREAM, fade(t, 6.4), stroke=4)
    T(d, "GTA VI: NOV 19, 2026", 1000, 76, AMBER, fade(t, 11.2), stroke=4)
    T(d, "13 YEARS", 1130, 90, CREAM, fade(t, 11.6), stroke=5)
    return cam(img, t, 2, 0.4)


def s_hype(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    td = word_t("n3", 0.5)
    if t < td:  # the trailer
        d.rounded_rectangle([90, 330, 990, 840], 20, fill=(20, 18, 22, 255), outline=CREAM + (200,), width=4)
        sunset(d, t, 840, 120)
        d.rounded_rectangle([90, 330, 990, 840], 20, outline=CREAM + (255,), width=4)
        d.polygon([(500, 520), (500, 650), (610, 585)], fill=CREAM + (230,))
        T(d, "TRAILER 1", 220, 80, CREAM, fade(t, 13.5), stroke=4)
        T(d, "YOUTUBE RECORD", 960, 76, AMBER, fade(t, word_t("n3", 0.25)), stroke=4)
        T(d, "MOST VIEWED IN 24 HOURS (NON-MUSIC)", 1050, 36, CREAM, fade(t, word_t("n3", 0.3)), f="oswald")
    else:
        T(d, "RELEASE DATE", 220, 80, CREAM, stroke=4)
        for i, (lab, tt) in enumerate([("2025", td + 0.1), ("MAY 2026", td + 0.6), ("NOV 19, 2026", td + 1.6)]):
            y = 440 + i * 220
            a = fade(t, tt)
            T(d, lab, y, 110, AMBER if i == 2 else CREAM, a, stroke=5)
            if i < 2 and t > tt + 0.4:
                kk = ease_out(min(1, (t - tt - 0.4) / 0.2))
                w = d.textlength(lab, font=font("anton", 110))
                d.line([(W / 2 - w / 2 - 20, y), (W / 2 - w / 2 - 20 + (w + 40) * kk, y)], fill=RED + (255,), width=12)
        if t > td + 1.0:
            gm.stamp(img, "DELAYED TWICE", W / 2, 1130, ease_out(min(1, (t - td - 1.0) / 0.18)), angle=-8, size=90)
    return cam(img, t, 3, 0.4)


def s_stampede(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    sunset(d, t, 1180, 150)
    rng = np.random.default_rng(9)
    for i in range(26):
        sp = rng.uniform(260, 420)
        x = (rng.uniform(-400, 1000) + (t - 18.4) * sp) % 1500 - 200
        by = 1180 - rng.uniform(0, 80)
        runner(d, x, by, rng.uniform(0.8, 1.2), t * 14 + i, (rng.integers(110, 170),) * 3)
    T(d, "LAUNCH DAY", 260, 110, CREAM, fade(t, 18.5), stroke=6)
    T(d, "THEY STAMPEDED", 420, 80, AMBER, fade(t, word_t("n4", 0.7)), stroke=5)
    return cam(img, t, 4, 1.4)


def s_record(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    T(d, "DAY ONE SALES", 230, 90, CREAM, fade(t, 23.1), stroke=5)
    t0 = word_t("n5", 0.3)
    k = np.clip((t - t0) / 2.0, 0, 1)
    v = 3.79e9 * (1 - (1 - k) ** 3)
    d.rectangle([0, 360, W, 640], fill=(12, 10, 10, 230))
    T(d, f"${v:,.0f}", 500, 110, AMBER if k >= 1 else CREAM, stroke=4)
    T(d, "PER TAKE-TWO (RETAIL, INCL. PRE-ORDERS)", 690, 38, (200, 185, 165), fade(t, t0 + 0.5), f="oswald")
    tr = word_t("n5", 0.75)
    if t > tr:
        gm.stamp(img, "ENTERTAINMENT RECORD", W / 2, 960, ease_out(min(1, (t - tr) / 0.18)), angle=-6, size=78)
    return cam(img, t, 5, 0.4 + (6 * np.exp(-(t - tr) * 6) if t > tr else 0))


def s_preorder(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    T(d, "BEFORE RELEASE", 220, 96, CREAM, fade(t, 32.2), stroke=5)
    k = np.clip((t - 32.6) / 3.0, 0, 1)
    n = int(35 * k)
    for i in range(n):
        col, row = i % 7, i // 7
        game_box(d, 150 + col * 130, 1100 - row * 150, 0.75)
    T(d, f"{32.5 * k:.1f}M COPIES", 400, 110, AMBER, fade(t, 32.6), stroke=6)
    return cam(img, t, 6, 0.4)


def bars(d, t, items, top=380, bottom=1150):
    vmax = 3.79e9
    n = len(items)
    gap = (W - 160) / n
    for i, (lab, v, col, t0) in enumerate(items):
        if t < t0:
            continue
        k = ease_out(np.clip((t - t0) / 0.9, 0, 1))
        x = 80 + gap * (i + 0.5)
        h = (bottom - top - 120) * v / vmax * k
        d.rectangle([x - gap * 0.32, bottom - h, x + gap * 0.32, bottom], fill=col + (235,))
        T(d, money(v * k), bottom - h - 50, 60, CREAM, x=x, stroke=4)
        T(d, lab, bottom + 50, 44, CREAM, fade(t, t0), x=x, f="oswald")
    d.line([(80, bottom), (W - 80, bottom)], fill=CREAM + (220,), width=4)


def s_compare(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    T(d, "DAY ONE", 200, 100, CREAM, fade(t, 37.4), stroke=5)
    bars(d, t, [("GTA V (2013)", 0.8e9, (130, 120, 110), word_t("n7", 0.2)),
                ("GTA VI (2026)", 3.79e9, AMBER, word_t("n7", 0.72))])
    T(d, "~5X", 640, 160, PINK, fade(t, word_t("n7", 0.85)), x=W / 2 - 40, stroke=6)
    return cam(img, t, 7, 0.4)


def s_estimate(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    T(d, "ANOTHER ESTIMATE", 200, 90, CREAM, fade(t, 46.4), stroke=5)
    bars(d, t, [("GTA V", 0.8e9, (130, 120, 110), 46.0), ("SENSOR TOWER", 2.36e9, TEAL, word_t("n8", 0.3)),
                ("TAKE-TWO", 3.79e9, AMBER, 46.0)])
    T(d, "STILL ~3X GTA V", 340, 64, TEAL, fade(t, word_t("n8", 0.7)), stroke=4)
    return cam(img, t, 8, 0.3)


def s_end(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    sunset(d, t, 1180, int(120 * (1 - smoothstep(56.6, 56.9, t))) + 1)
    out_k = 1 - smoothstep(56.6, 56.9, t)
    T(d, "13 YEARS", 250, 160, CREAM, int(fade(t, 53.3) * out_k), stroke=7)
    T(d, "OF WAITING.", 390, 80, CREAM, int(fade(t, 53.6) * out_k), stroke=5)
    T(d, "1 DAY", 540, 160, AMBER, int(fade(t, word_t("n9", 0.55)) * out_k), stroke=7)
    T(d, "OF BUYING.", 680, 80, AMBER, int(fade(t, word_t("n9", 0.7)) * out_k), stroke=5)
    if t > 56.9:
        k2 = ease_out_back((t - 56.9) / 0.3, 2.5)
        f = font("anton", int(190 * k2) + 1)
        w = d.textlength("NO WAY.", font=f)
        cy = 560
        d.rectangle([W / 2 - 360, cy - 10, W / 2 + 360, cy + 250], fill=(20, 16, 12, int(235 * min(1, k2))))
        d.text((W / 2 - w / 2, cy + 125 - 125 * k2), "NO WAY.", font=f, fill=(245, 236, 215, 255))
        d.rectangle([W / 2 - 240 * k2, cy + 225, W / 2 + 240 * k2, cy + 238], fill=RED + (255,))
    return cam(img, t, 9, 0.3)


SCENES = [(0.0, 6.0, s_hook), (6.0, 13.2, s_wait), (13.2, 18.2, s_hype), (18.2, 22.8, s_stampede),
          (22.8, 31.9, s_record), (31.9, 37.1, s_preorder), (37.1, 46.1, s_compare), (46.1, 53.0, s_estimate),
          (53.0, DURATION + 0.01, s_end)]


def frame(idx):
    t = idx / FPS
    img = None
    for i, (t0, t1, fn) in enumerate(SCENES):
        if t0 <= t < t1:
            img = fn(t)
            if i + 1 < len(SCENES) and t > t1 - 0.3:
                k = smoothstep(t1 - 0.3, t1, t)
                img = img * (1 - k) + SCENES[i + 1][2](t1) * k
            break
    out = grade(img, idx, t, keep_color=0.55)
    if t > DURATION - 0.4:
        out = out * (1 - smoothstep(DURATION - 0.4, DURATION, t) * 0.9)
    pil = to_img(out).convert("RGBA")
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
