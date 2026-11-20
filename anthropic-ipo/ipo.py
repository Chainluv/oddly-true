"""NO WAY. — The $1.5 Trillion Breakup (Anthropic's 2026 IPO). About 73s, vertical.
Reuses molasses-flood (grade, captions), zanzibar-war (backgrounds, caption timing), bonus-army (caption grouping),
rap-grammy (stamp) and eiffel-con (money). People are generic shapes with name labels, never likenesses, and there
are no company logos: names are set in the show's own type."""
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
import episode as zw  # dark_bg(), build_chunks()
import bonus as ba    # groups()
import grammy as gm   # stamp()
import eiffel as ef   # money()

DURATION = 73.0
NFR = int(DURATION * FPS)
AMBER, RED, CREAM, GREEN = mf.AMBER, (215, 60, 45), (236, 226, 205), (120, 190, 110)
VOICES = os.path.join(HERE, "voices")

NARR = {"n1": 0.1, "n2": 5.9, "n3": 13.6, "n4": 23.3, "n5": 32.7, "n6": 42.3, "n7": 54.8, "n8": 62.5, "n9": 70.1}
TEXT = {"n1": "NO WAY... THE BIGGEST AI IPO IN HISTORY STARTED WITH A BREAKUP AT OPENAI.",
        "n2": "IN LATE 2020, DARIO AMODEI AND HIS SISTER DANIELA LEFT OPENAI, WHERE THEY HELD SENIOR LEADERSHIP POSITIONS.",
        "n3": "THEY HAD CONCERNS ABOUT THE DIRECTION OF AI DEVELOPMENT, AND WANTED TO BUILD POWERFUL AI WITH SAFETY AT ITS "
              "CORE. SO IN 2021, THEY FOUNDED ANTHROPIC.",
        "n4": "AND HERE'S WHERE THINGS GET CRAZY. ONE OF THEIR EARLY INVESTORS? SAM BANKMAN-FRIED. THE SAME CRYPTO "
              "BILLIONAIRE WHOSE FTX EMPIRE LATER COLLAPSED IN SCANDAL.",
        "n5": "BUT ANTHROPIC KEPT GROWING. AMAZON AND GOOGLE POURED BILLIONS INTO THE COMPANY. AND ITS AI ASSISTANT, "
              "CLAUDE, BECAME A SERIOUS RIVAL TO CHATGPT.",
        "n6": "THEN CAME NOVEMBER 19TH, 2026. ANTHROPIC HIT THE NASDAQ UNDER THE TICKER ANT, PRICING ITS SHARES AT $83, "
              "FOR A STAGGERING VALUATION OF AROUND $1.5 TRILLION.",
        "n7": "AND HERE'S THE TWIST. ITS SEVEN CO-FOUNDERS STRUCTURED THE COMPANY TO KEEP MAJORITY VOTING CONTROL, EVEN "
              "AFTER GOING PUBLIC.",
        "n8": "THEY LEFT OPENAI TO BUILD AI THEIR WAY. ABOUT FIVE YEARS LATER, WALL STREET PUT A TRILLION-DOLLAR PRICE "
              "TAG ON IT.",
        "n9": "NO WAY."}
zw.LINES = [(k, ba.groups(TEXT[k])) for k in NARR]
zw.NARR = NARR
zw.DUR = {k: sf.info(os.path.join(VOICES, f"{k}.wav")).duration for k in NARR}
zw.SPOKEN = {"2020,": "twenty twenty", "2021,": "twenty twenty one", "19TH,": "nineteenth", "2026.": "twenty twenty six",
             "ANT,": "A N T", "$83,": "eighty three dollars", "$1.5": "one point five", "AI": "A I",
             "IPO": "I P O", "FTX": "F T X", "BANKMAN-FRIED.": "bankman fried", "TRILLION-DOLLAR": "trillion dollar"}
mf.CHUNKS = zw.build_chunks()
mf.KEYWORDS = {"BIGGEST", "IPO", "BREAKUP", "OPENAI.", "2020,", "SISTER", "SAFETY", "CORE.", "2021,", "ANTHROPIC.",
               "CRAZY.", "BANKMAN-FRIED.", "FTX", "COLLAPSED", "AMAZON", "GOOGLE", "BILLIONS", "CLAUDE,", "RIVAL",
               "NASDAQ", "ANT,", "$83,", "$1.5", "TRILLION.", "TWIST.", "SEVEN", "MAJORITY", "VOTING", "CONTROL,",
               "FIVE", "TRILLION-DOLLAR", "WAY."}


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


def person(d, cx, by, s=1.0, col=(170, 150, 130), a=255):
    """Generic figure: round head, rounded body. No likeness."""
    c = col + (a,)
    d.rounded_rectangle([cx - 70 * s, by - 280 * s, cx + 70 * s, by], int(50 * s), fill=c)
    d.ellipse([cx - 48 * s, by - 390 * s, cx + 48 * s, by - 294 * s], fill=c)


def building(d, x0, x1, top, bottom, label, a=255, col=(70, 66, 62)):
    d.rectangle([x0, top, x1, bottom], fill=col + (a,), outline=(120, 112, 100, a), width=4)
    for yy in range(int(top) + 50, int(bottom) - 120, 80):
        for xx in range(int(x0) + 30, int(x1) - 50, 70):
            d.rectangle([xx, yy, xx + 34, yy + 44], fill=(200, 170, 110, int(a * 0.5)))
    T(d, label, top - 40, 54, CREAM, a, x=(x0 + x1) / 2, stroke=3)


def chart(d, x0, y0, x1, y1, pts, k, col, width=10):
    """Draws the first fraction k of a polyline given in unit coords (0..1)."""
    n = max(2, int(len(pts) * k))
    P = [(lerp(x0, x1, u), lerp(y1, y0, v)) for u, v in pts[:n]]
    d.line(P, fill=col + (255,), width=width, joint="curve")
    return P[-1]


# ---------------------------------------------------------------- scenes
def s_hook(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    k = pop(t, 0.2)
    T(d, "$1.5", 420, int(260 * min(1.1, k)) + 1, AMBER, stroke=8)
    T(d, "TRILLION", 640, int(170 * min(1.1, k)) + 1, CREAM, stroke=6)
    T(d, "THE BIGGEST AI IPO IN HISTORY", 800, 54, CREAM, fade(t, 1.4), f="oswald")
    tb = word_t("n1", 0.75)  # "breakup": the screen cracks in two
    if t > tb:
        kk = ease_out((t - tb) / 0.5)
        pts = [(W / 2 + 40 * np.sin(i * 1.7), 880 + i * 45) for i in range(10)]
        d.line(pts, fill=RED + (255,), width=8)
        T(d, "A BREAKUP", 1180, int(110 * min(1.1, pop(t, tb))) + 1, RED, stroke=6, x=W / 2 - 60 * kk)
    return cam(img, t, 1, 0.5, 1.0 + 0.02 * t / 6)


def s_leave(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    building(d, 120, 640, 420, 1180, "OPENAI")
    d.rectangle([300, 980, 440, 1180], fill=(30, 26, 24))  # door
    T(d, "LATE 2020", 150, 110, AMBER, fade(t, 6.0), stroke=6)
    walk = ease_in_out((t - 6.6) / 4.5)
    for i, (name, dx) in enumerate([("DARIO AMODEI", 0), ("DANIELA AMODEI", 170)]):
        x = lerp(370, 760 + dx, walk) if t > 6.6 else 370
        a = int(255 * smoothstep(6.4, 6.9, t))
        bob = 8 * abs(np.sin(t * 6 + i)) if 6.6 < t < 11.1 else 0
        person(d, x, 1180 - bob, 0.75 - 0.05 * i, a=a)
    T(d, "DARIO & DANIELA AMODEI", 265, 66, CREAM, fade(t, 7.0), stroke=4)
    T(d, "SENIOR LEADERSHIP", 1660, 52, AMBER, fade(t, word_t("n2", 0.75)), stroke=3)
    return cam(img, t, 2, 0.4)


def s_safety(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    cx, cy = W / 2, 720
    for r in range(5, 0, -1):  # a glowing core
        rr = r * 70 * (1 + 0.04 * np.sin(t * 2 + r))
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=AMBER + (int(40 + 30 * (5 - r)),), width=6)
    a = fade(t, word_t("n3", 0.45))
    d.polygon([(cx, cy - 120), (cx + 100, cy - 80), (cx + 90, cy + 40), (cx, cy + 120), (cx - 90, cy + 40),
               (cx - 100, cy - 80)], fill=(40, 34, 28, a), outline=CREAM + (a,))
    T(d, "SAFETY", cy, 60, CREAM, a)
    tf = word_t("n3", 0.78)
    T(d, "AT ITS CORE", 1130, 70, AMBER, int(a * (1 - smoothstep(tf - 0.2, tf, t))), stroke=4)
    T(d, "CONCERNS ABOUT AI'S DIRECTION", 230, 58, CREAM, fade(t, 13.8), stroke=4)
    if t > tf:
        gm.stamp(img, "FOUNDED 2021", W / 2, 420, ease_out(min(1, (t - tf) / 0.18)), angle=-8, size=110)
        T(d, "ANTHROPIC", 1150, 110, CREAM, fade(t, tf + 0.2), stroke=6)
    return cam(img, t, 3, 0.4 + (8 * np.exp(-(t - tf) * 7) if t > tf else 0))


def s_sbf(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    T(d, "EARLY INVESTOR", 220, 96, CREAM, fade(t, word_t("n4", 0.25)), stroke=6)
    ts = word_t("n4", 0.35)
    a = fade(t, ts)
    person(d, 330, 1100, 0.9, col=(150, 140, 125), a=a)
    T(d, "SAM BANKMAN-FRIED", 1160, 46, CREAM, a, f="oswald", x=330)
    if t > ts + 0.4:
        for i in range(3):
            ef.money(d, 700, 1000 - i * 120 * ease_out((t - ts - 0.4) / 0.6), 4)
        T(d, "~$500M (2022)", 640, 56, GREEN, fade(t, ts + 0.6), x=700, stroke=3)
    tc = word_t("n4", 0.78)
    if t > tc:  # crypto empire crashes
        gm.stamp(img, "FTX COLLAPSED", W / 2, 420, ease_out(min(1, (t - tc - 0.5) / 0.18)) if t > tc + 0.5 else 0,
                 angle=-10, size=100) if t > tc + 0.5 else None
    return cam(img, t, 4, 0.4)


def s_growth(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    tv = word_t("n5", 0.68)
    if t < tv:
        T(d, "KEPT GROWING", 220, 100, CREAM, fade(t, 32.8), stroke=6)
        for i, (name, amt, h, t0) in enumerate([("AMAZON", "$8B", 560, word_t("n5", 0.25)),
                                                ("GOOGLE", "BILLIONS", 420, word_t("n5", 0.33))]):
            x = 330 + i * 420
            k = ease_out(np.clip((t - t0) / 0.8, 0, 1))
            d.rectangle([x - 110, 1200 - h * k, x + 110, 1200], fill=AMBER + (220,))
            T(d, name, 1240, 52, CREAM, fade(t, t0), x=x, stroke=3)
            T(d, amt, 1200 - h * k - 50, 60, CREAM, fade(t, t0 + 0.4), x=x, stroke=4)
        d.line([(120, 1200), (960, 1200)], fill=CREAM + (200,), width=4)
    else:
        k = pop(t, tv)
        T(d, "CLAUDE", 520, int(150 * min(1.1, k)) + 1, AMBER, stroke=6)
        T(d, "VS", 720, int(90 * min(1.1, k)) + 1, CREAM, stroke=5)
        T(d, "CHATGPT", 900, int(150 * min(1.1, pop(t, tv + 0.5))) + 1, CREAM, stroke=6)
        T(d, "A SERIOUS RIVAL", 1150, 60, CREAM, fade(t, tv + 0.9), f="oswald")
    return cam(img, t, 5, 0.4)


def s_ipo(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    T(d, "NOV 19, 2026", 200, 110, AMBER, fade(t, 42.4), stroke=6)
    tn = word_t("n6", 0.22)
    if t > tn:  # ticker board
        a = fade(t, tn)
        d.rounded_rectangle([90, 340, 990, 760], 24, fill=(14, 14, 16, a), outline=CREAM + (a,), width=5)
        T(d, "NASDAQ", 410, 54, CREAM, a, f="oswald")
        T(d, "ANT", 540, 150, GREEN, a, x=330)
        tp = word_t("n6", 0.52)
        p = 83.0 * ease_out(np.clip((t - tp) / 0.8, 0, 1)) if t > tp else 0.0
        T(d, f"${p:.2f}", 540, 120, GREEN, fade(t, tp), x=720)
        T(d, "IPO PRICE", 680, 44, CREAM, fade(t, tp), x=720, f="oswald")
        tick = "   ANT  83.00   |   NASDAQ   |" * 4
        T(d, tick, 860, 44, GREEN, a, x=W / 2 - (t * 120 % 600), f="oswald")
    tv = word_t("n6", 0.75)
    if t > tv:
        k = pop(t, tv)
        T(d, "~$1.5 TRILLION", 1060, int(120 * min(1.1, k)) + 1, AMBER, stroke=6)
        T(d, "VALUATION AT THE IPO PRICE", 1170, 40, CREAM, fade(t, tv + 0.4), f="oswald")
    return cam(img, t, 6, 0.4 + (6 * np.exp(-(t - tv) * 6) if t > tv else 0))


def s_twist(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    T(d, "THE TWIST", 200, 120, RED, fade(t, 54.9), stroke=6)
    cx, cy, r = W / 2, 720, 300
    k = ease_out(np.clip((t - word_t("n7", 0.4)) / 1.2, 0, 1))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(70, 66, 62, 255))
    if k > 0:
        d.pieslice([cx - r, cy - r, cx + r, cy + r], -90, -90 + 360 * 0.501 * k, fill=AMBER + (255,))
        T(d, "50.1%", cy - 40, 110, (20, 16, 12), int(255 * k), x=cx + 150)
    T(d, "7 CO-FOUNDERS", 1110, 76, AMBER, fade(t, word_t("n7", 0.3)), stroke=4)
    T(d, "KEEP VOTING CONTROL", 1200, 56, CREAM, fade(t, word_t("n7", 0.6)), stroke=3)
    T(d, "PER ANTHROPIC'S IPO FILING", 1640, 36, (190, 175, 160), fade(t, word_t("n7", 0.6)), f="oswald")
    return cam(img, t, 7, 0.3)


def s_end(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    out_k = 1 - smoothstep(69.8, 70.1, t)
    a1 = int(fade(t, 62.6) * out_k)
    T(d, "2021", 380, 150, CREAM, a1, x=260, stroke=6)
    T(d, "LEFT TO BUILD", 500, 40, CREAM, a1, x=260, f="oswald")
    t2 = word_t("n8", 0.45)
    a2 = int(fade(t, t2) * out_k)
    if a2 > 2:
        d.line([(450, 380), (450 + 180 * ease_out(np.clip((t - t2) / 0.5, 0, 1)), 380)], fill=AMBER + (a2,), width=10)
    T(d, "2026", 380, 150, AMBER, a2, x=800, stroke=6)
    T(d, "$1T+ PRICE TAG", 500, 40, AMBER, a2, x=800, f="oswald")
    T(d, "~5 YEARS", 680, 120, CREAM, int(fade(t, t2 + 0.3) * out_k), stroke=6)
    if t > 70.1:
        k2 = ease_out_back((t - 70.1) / 0.3, 2.5)
        f = font("anton", int(190 * k2) + 1)
        w = d.textlength("NO WAY.", font=f)
        cy = 560
        d.rectangle([W / 2 - 360, cy - 10, W / 2 + 360, cy + 250], fill=(20, 16, 12, int(235 * min(1, k2))))
        d.text((W / 2 - w / 2, cy + 125 - 125 * k2), "NO WAY.", font=f, fill=(245, 236, 215, 255))
        d.rectangle([W / 2 - 240 * k2, cy + 225, W / 2 + 240 * k2, cy + 238], fill=RED + (255,))
    return cam(img, t, 8, 0.3)


SCENES = [(0.0, 5.7, s_hook), (5.7, 13.4, s_leave), (13.4, 23.1, s_safety), (23.1, 32.5, s_sbf),
          (32.5, 42.1, s_growth), (42.1, 54.6, s_ipo), (54.6, 62.3, s_twist), (62.3, DURATION + 0.01, s_end)]


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
    out = grade(img, idx, t, keep_color=0.45)
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
