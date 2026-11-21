"""NO WAY. — Someone Created 184 Billion Bitcoin (the value overflow incident, block 74638, August 15, 2010). 53s, vertical.
Reuses molasses-flood (grade, captions), zanzibar-war (backgrounds, caption timing), bonus-army (caption grouping) and
rap-grammy (stamp). No logos: the coin is the show's own drawing."""
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

DURATION = 53.0
NFR = int(DURATION * FPS)
AMBER, RED, CREAM, GREEN = mf.AMBER, (215, 60, 45), (236, 226, 205), (120, 200, 120)
GOLD = (222, 160, 60)
VOICES = os.path.join(HERE, "voices")

NARR = {"n1": 0.1, "n2": 5.8, "n3": 11.0, "n4": 16.0, "n5": 23.5, "n6": 32.4, "n7": 40.0, "n8": 46.6, "n9": 50.0}
TEXT = {"n1": "NO WAY... SOMEONE CREATED 184 BILLION BITCOIN. IN ONE TRANSACTION.",
        "n2": "BITCOIN IS DESIGNED SO THAT ONLY 21 MILLION COINS CAN EVER EXIST.",
        "n3": "BUT ON AUGUST 15TH, 2010, SOMEONE FOUND A BUG IN BITCOIN'S CODE.",
        "n4": "THEY SENT A TRANSACTION WITH OUTPUTS SO HUGE, THE MATH OVERFLOWED. THE SAFETY CHECK FAILED, AND THE "
              "TRANSACTION WENT THROUGH.",
        "n5": "BLOCK 74,638. 184 BILLION BRAND-NEW BITCOIN. NEARLY NINE THOUSAND TIMES THE ENTIRE SUPPLY.",
        "n6": "DEVELOPERS SPOTTED IT FAST. BITCOIN'S CREATOR, SATOSHI NAKAMOTO, AND OTHERS RUSHED OUT A FIX IN ABOUT "
              "FIVE HOURS.",
        "n7": "MINERS SWITCHED TO THE PATCHED VERSION. THE HONEST CHAIN TOOK OVER, AND THE FAKE COINS WERE WIPED FROM "
              "HISTORY.",
        "n8": "WHO DID IT? TO THIS DAY, NOBODY KNOWS.",
        "n9": "NO WAY."}
zw.LINES = [(k, ba.groups(TEXT[k])) for k in NARR]
zw.NARR = NARR
zw.DUR = {k: sf.info(os.path.join(VOICES, f"{k}.wav")).duration for k in NARR}
zw.SPOKEN = {"184": "a hundred and eighty four", "21": "twenty one", "15TH,": "fifteenth", "2010,": "twenty ten",
             "74,638.": "seventy four thousand six hundred thirty eight", "BRAND-NEW": "brand new"}
mf.CHUNKS = zw.build_chunks()
mf.KEYWORDS = {"184", "BILLION", "ONE", "TRANSACTION.", "21", "MILLION", "EVER", "BUG", "OVERFLOWED.", "FAILED,",
               "74,638.", "NINE", "THOUSAND", "SATOSHI", "NAKAMOTO,", "FIVE", "HOURS.", "HONEST", "FAKE", "WIPED",
               "NOBODY", "KNOWS.", "WAY."}


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


def coin(d, cx, cy, r, a=255, spin=1.0):
    """A generic gold coin with a B and two strokes (not a logo)."""
    rx = max(4, r * abs(spin))
    d.ellipse([cx - rx, cy - r, cx + rx, cy + r], fill=GOLD + (a,), outline=(120, 80, 30, a), width=max(2, int(r / 12)))
    if abs(spin) > 0.5:
        T(d, "B", cy, int(r * 1.2), (110, 70, 25), a, x=cx)
        for dx in (-0.12, 0.12):
            d.line([(cx + dx * r, cy - r * 0.72), (cx + dx * r, cy + r * 0.72)], fill=(110, 70, 25, a), width=max(2, int(r / 14)))


def block(d, x, y, s, label, col=(60, 58, 54), a=255, out=CREAM):
    d.rounded_rectangle([x - s, y - s, x + s, y + s], int(s / 5), fill=col + (a,), outline=out + (a,), width=4)
    T(d, label, y, int(s * 0.42), CREAM, a, x=x)


def fmt(n):
    return f"{int(n):,}"


TOTAL = 184467440737


# ---------------------------------------------------------------- scenes
def s_hook(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    for i in range(14):  # coins raining
        ph = (t * 0.35 + i * 0.137) % 1.0
        x = 80 + (i * 211) % 920
        coin(d, x, -100 + ph * 1400, 46, 110, np.cos(t * 3 + i))
    k = np.clip((t - 0.4) / 3.2, 0, 1)
    n = TOTAL * (1 - (1 - k) ** 3)
    d.rectangle([0, 460, W, 950], fill=(14, 12, 10, 235))
    T(d, fmt(n), 580, 118, AMBER, stroke=5)
    T(d, "BITCOIN", 760, 90, CREAM, fade(t, 0.8), stroke=5)
    T(d, "IN ONE TRANSACTION", 880, 64, RED, fade(t, word_t("n1", 0.75)), stroke=4)
    return cam(img, t, 1, 0.5)


def s_supply(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    coin(d, W / 2, 560, 200, 255, np.cos((t - 5.8) * 1.6))
    T(d, "MAX SUPPLY", 900, 70, CREAM, fade(t, 6.0), stroke=4)
    T(d, "21,000,000", 1050, 150, AMBER, fade(t, word_t("n2", 0.6)), stroke=6)
    T(d, "BY DESIGN", 220, 80, CREAM, fade(t, 6.2), f="oswald")
    return cam(img, t, 2, 0.4)


CODE = ["for (txout in vout)", "    nValueOut += txout.nValue;", "if (nValueIn < nValueOut)",
        "    return error(\"in < out\");", "// ...", "AcceptTransaction();"]


def code_panel(d, t, bug_a=0):
    d.rounded_rectangle([60, 330, W - 60, 1000], 20, fill=(16, 18, 16, 240), outline=(90, 110, 90, 255), width=4)
    for i in range(3):
        d.ellipse([90 + i * 40, 352, 116 + i * 40, 378], fill=[(200, 80, 70), (220, 180, 70), (110, 190, 100)][i] + (255,))
    for i, line in enumerate(CODE):
        y = 450 + i * 90
        if i == 1 and bug_a:
            d.rectangle([80, y - 36, W - 80, y + 36], fill=RED + (int(bug_a * 0.45),))
        T(d, line, y, 40, (170, 220, 160), x=110, f="type", anchor="lm")


def s_bug(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    T(d, "AUG 15, 2010", 200, 120, AMBER, fade(t, 11.1), stroke=6)
    tb = word_t("n3", 0.75)
    code_panel(d, t, fade(t, tb))
    if t > tb:
        T(d, "BUG", 1110, int(120 * min(1.1, pop(t, tb))) + 1, RED, stroke=6)
    return cam(img, t, 3, 0.4)


def s_overflow(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    T(d, "ONE TRANSACTION", 200, 90, CREAM, fade(t, 16.1), stroke=5)
    for i in range(2):
        a = fade(t, 16.5 + i * 0.6)
        y = 380 + i * 150
        d.rounded_rectangle([80, y - 55, W - 80, y + 55], 14, fill=(30, 28, 24, a), outline=AMBER + (a,), width=4)
        T(d, f"OUTPUT {i + 1}:  92,233,720,368 BTC", y, 52, CREAM, a)
    tov = word_t("n4", 0.42)
    # the sum: an odometer that wraps past its maximum
    d.rounded_rectangle([80, 660, W - 80, 840], 14, fill=(14, 14, 16, 240), outline=CREAM + (200,), width=4)
    T(d, "TOTAL OUT", 620, 40, CREAM, fade(t, 17.6), f="oswald")
    if t < tov:
        k = np.clip((t - 17.8) / (tov - 17.8), 0, 1)
        val = fmt(TOTAL * k ** 2) if t > 17.8 else "0"
        T(d, val, 750, 96, AMBER)
    else:
        jitter = int(10 * np.sin(t * 60)) if t < tov + 0.5 else 0
        T(d, "OVERFLOW", 750 + jitter, 110, RED, stroke=4)
        T(d, "THE SUM WRAPPED AROUND TO A TINY NUMBER", 900, 38, CREAM, fade(t, tov + 0.3), f="oswald")
    tp = word_t("n4", 0.78)
    if t > tp:
        gm.stamp(img, "CHECK PASSED", W / 2, 1110, ease_out(min(1, (t - tp) / 0.18)), angle=-8, size=96)
    amp = 0.4 + (10 * np.exp(-(t - tov) * 6) if t > tov else 0)
    return cam(img, t, 4, amp)


def s_block(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    scroll = ease_out(np.clip((t - 23.5) / 1.6, 0, 1))
    for i in range(-3, 4):
        x = W / 2 + i * 300 - (1 - scroll) * 900
        lab = f"#{74638 + i}"
        hot = i == 0
        block(d, x, 420, 120, lab, (110, 40, 34) if hot else (60, 58, 54), 255, RED if hot else CREAM)
        if i < 3:
            d.line([(x + 120, 420), (x + 180, 420)], fill=CREAM + (200,), width=6)
    tb = word_t("n5", 0.38)
    if t > tb:
        k = pop(t, tb)
        T(d, "+184,467,440,737", 680, int(104 * min(1.1, k)) + 1, AMBER, stroke=5)
        T(d, "NEW BITCOIN", 790, 60, CREAM, fade(t, tb + 0.2), stroke=4)
    tc = word_t("n5", 0.7)
    if t > tc:  # supply comparison
        a = fade(t, tc)
        kk = ease_out(np.clip((t - tc) / 1.0, 0, 1))
        d.rectangle([120, 1000, 134, 1200], fill=CREAM + (a,))
        T(d, "21M", 1230, 34, CREAM, a, x=127, f="oswald")
        d.rectangle([200, 1200 - 200 * kk, 200 + 760 * kk, 1200], fill=RED + (int(a * 0.85),))
        T(d, "~8,800X", 1100, 90, CREAM, fade(t, tc + 0.6), x=600, stroke=5)
    return cam(img, t, 5, 0.4 + (6 * np.exp(-(t - tb) * 6) if t > tb else 0))


def s_fix(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    T(d, "SPOTTED FAST", 200, 100, CREAM, fade(t, 32.5), stroke=6)
    cx, cy, r = 300, 620, 190  # clock: about 5 hours
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(30, 28, 24, 255), outline=CREAM + (255,), width=6)
    k = np.clip((t - 33.0) / 5.0, 0, 1)
    d.pieslice([cx - r + 14, cy - r + 14, cx + r - 14, cy + r - 14], -90, -90 + 150 * k, fill=AMBER + (160,))
    ang = np.deg2rad(-90 + 150 * k)
    d.line([(cx, cy), (cx + 150 * np.cos(ang), cy + 150 * np.sin(ang))], fill=CREAM + (255,), width=8)
    T(d, "~5 HOURS", cy + r + 70, 70, AMBER, fade(t, word_t("n6", 0.8)), x=cx, stroke=4)
    ts = word_t("n6", 0.3)
    a = fade(t, ts)  # the pseudonymous creator: a hooded figure with a question mark
    sx, sy = 780, 880
    d.ellipse([sx - 120, sy - 420, sx + 120, sy - 190], fill=(50, 46, 42, a))
    d.rounded_rectangle([sx - 150, sy - 230, sx + 150, sy], 70, fill=(50, 46, 42, a))
    T(d, "?", sy - 300, 150, CREAM, a, x=sx)
    T(d, "SATOSHI NAKAMOTO", sy + 50, 48, CREAM, a, x=sx, stroke=3)
    tp = word_t("n6", 0.6)
    if t > tp:
        a2 = fade(t, tp)
        d.rounded_rectangle([140, 1080, W - 140, 1220], 16, fill=(16, 18, 16, a2), outline=GREEN + (a2,), width=4)
        T(d, "PATCH: VERSION 0.3.10", 1150, 56, GREEN, a2, f="type")
    return cam(img, t, 6, 0.4)


def s_fork(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    T(d, "THE CHAIN SPLITS", 200, 90, CREAM, fade(t, 40.1), stroke=5)
    k = np.clip((t - 40.4) / 4.5, 0, 1)
    s = 60
    block(d, 90, 670, s, "", (60, 58, 54))
    gone = smoothstep(word_t("n7", 0.72), word_t("n7", 0.72) + 0.8, t)
    # bad branch (with the 184B block), stalls at three blocks
    for i in range(3):
        x, y = 240 + i * 150, 520
        if k * 7 > i:
            a = int(255 * (1 - gone))
            block(d, x, y, s, "", (110, 40, 34) if i == 0 else (60, 58, 54), a, RED if i == 0 else CREAM)
    # honest branch keeps growing and passes it
    for i in range(6):
        x, y = 240 + i * 150, 820
        if k * 7 > i + 0.5:
            block(d, x, y, s, "", (50, 80, 50), 255, GREEN)
    if gone < 1:
        T(d, "184B FAKE COINS", 420, 52, RED, int(255 * (1 - smoothstep(0, 0.4, gone)) * smoothstep(40.6, 41.0, t)), x=390, stroke=3)
    T(d, "PATCHED CHAIN", 920, 52, GREEN, fade(t, 41.5), x=390, stroke=3)
    tw = word_t("n7", 0.55)
    T(d, "HONEST CHAIN WINS", 1040, 76, GREEN, fade(t, tw), stroke=4)
    T(d, "(BY BLOCK 74,691)", 1130, 44, CREAM, fade(t, tw + 0.3), f="oswald")
    if gone > 0.5:
        T(d, "FAKE COINS ERASED", 520, 76, RED, int(255 * smoothstep(0.5, 1, gone)), stroke=4)
    return cam(img, t, 7, 0.3)


def s_end(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    out_k = 1 - smoothstep(49.7, 50.0, t)
    T(d, "?", 600, int(420 * min(1.1, pop(t, 46.7))) + 1, AMBER, int(255 * out_k), stroke=8)
    T(d, "WHO DID IT:", 950, 70, CREAM, int(fade(t, 47.0) * out_k), stroke=4)
    T(d, "STILL UNKNOWN", 1060, 96, RED, int(fade(t, word_t("n8", 0.6)) * out_k), stroke=5)
    if t > 50.0:
        k2 = ease_out_back((t - 50.0) / 0.3, 2.5)
        f = font("anton", int(190 * k2) + 1)
        w = d.textlength("NO WAY.", font=f)
        cy = 560
        d.rectangle([W / 2 - 360, cy - 10, W / 2 + 360, cy + 250], fill=(20, 16, 12, int(235 * min(1, k2))))
        d.text((W / 2 - w / 2, cy + 125 - 125 * k2), "NO WAY.", font=f, fill=(245, 236, 215, 255))
        d.rectangle([W / 2 - 240 * k2, cy + 225, W / 2 + 240 * k2, cy + 238], fill=RED + (255,))
    return cam(img, t, 8, 0.3)


SCENES = [(0.0, 5.6, s_hook), (5.6, 10.8, s_supply), (10.8, 15.8, s_bug), (15.8, 23.3, s_overflow),
          (23.3, 32.2, s_block), (32.2, 39.8, s_fix), (39.8, 46.4, s_fork), (46.4, DURATION + 0.01, s_end)]


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
    out = grade(img, idx, t, keep_color=0.48)
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
