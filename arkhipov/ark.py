"""NO WAY. — No Way One Man Stopped a Nuclear War (Vasili Arkhipov, submarine B-59, October 1962). 50s, vertical.
Reuses molasses-flood (grade, captions), zanzibar-war (headline, backgrounds, caption timing), bonus-army (caption
grouping), rap-grammy (stamp) and eiffel-con (figures). Stylized reconstruction; the officers' vote is labeled as
coming from later crew accounts."""
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
from common import (W, H, FPS, NOISE2, tex, font, to_img, from_img, cam2d, shake, grade, lerp, smoothstep,
                    ease_in_out, ease_out, ease_out_back)
import render as mf   # captions
import episode as zw  # headline(), dark_bg(), build_chunks()
import bonus as ba    # groups()
import grammy as gm   # stamp()
import eiffel as ef   # man()

DURATION = 50.0
NFR = int(DURATION * FPS)
AMBER, RED, CREAM = mf.AMBER, (215, 60, 45), (236, 226, 205)
SEA, DEEP = (30, 46, 58), (10, 16, 24)
VOICES = os.path.join(HERE, "voices")

NARR = {"n1": 0.1, "n2": 6.0, "n3": 15.6, "n4": 25.6, "n5": 34.8, "n6": 43.0, "n7": 47.2}
TEXT = {"n1": "NO WAY THE WORLD ALMOST ENDED IN 1962... AND ONE MAN HELPED STOP IT FROM HAPPENING.",
        "n2": "DURING THE CUBAN MISSILE CRISIS, A SOVIET SUBMARINE WAS HIDING DEEP UNDERWATER WHILE AMERICAN NAVY SHIPS "
              "DROPPED PRACTICE DEPTH CHARGES TO FORCE IT TO SURFACE.",
        "n3": "THE SOVIET CREW HAD LOST CONTACT WITH MOSCOW. WITH EXPLOSIONS SURROUNDING THEM, THE CAPTAIN FEARED WAR HAD "
              "ALREADY STARTED. HE WANTED TO LAUNCH A NUCLEAR TORPEDO.",
        "n4": "BUT THERE WAS A PROBLEM. LAUNCHING REQUIRED AGREEMENT FROM THREE SENIOR OFFICERS. TWO WERE READY TO PROCEED. "
              "THE THIRD, VASILI ARKHIPOV, REFUSED.",
        "n5": "HE HELPED CONVINCE THE CAPTAIN TO SURFACE INSTEAD. AND THE AMERICANS HAD NO IDEA HOW CLOSE THEY'D COME TO A "
              "NUCLEAR CONFRONTATION.",
        "n6": "ONE DECISION. MILLIONS OF LIVES POTENTIALLY AT STAKE.",
        "n7": "NO WAY."}
zw.LINES = [(k, ba.groups(TEXT[k])) for k in NARR]
zw.NARR = NARR
zw.DUR = {k: sf.info(os.path.join(VOICES, f"{k}.wav")).duration for k in NARR}
zw.SPOKEN = {"1962...": "nineteen sixty two"}
mf.CHUNKS = zw.build_chunks()
mf.KEYWORDS = {"WORLD", "ENDED", "1962...", "ONE", "MAN", "CUBAN", "MISSILE", "CRISIS,", "SOVIET", "SUBMARINE",
               "DEPTH", "CHARGES", "MOSCOW.", "WAR", "NUCLEAR", "TORPEDO.", "THREE", "OFFICERS.", "TWO", "ARKHIPOV,",
               "REFUSED.", "SURFACE", "NO", "IDEA", "DECISION.", "MILLIONS", "WAY."}


def word_t(pid, frac):
    return NARR[pid] + zw.DUR[pid] * frac


# ---------------------------------------------------------------- art
def base():
    return to_img(zw.DARK).convert("RGBA")


def cam(img, t, seed, amp=0.6, zoom=1.0, cy=H / 2):
    sx, sy, sr = shake(t, amp, 1.8, seed=seed)
    return from_img(cam2d(img.convert("RGB") if not isinstance(img, np.ndarray) else to_img(img), zoom, W / 2, cy, sr, sx, sy))


def T(d, txt, y, size, col=CREAM, a=255, x=W / 2, f="anton", stroke=0, anchor="mm"):
    if a <= 2:
        return
    d.text((x, y), txt, font=font(f, size), fill=col + (a,), anchor=anchor, stroke_width=stroke, stroke_fill=(8, 8, 10, a))


def ocean(d, t, surface=520):
    """Sky above, water column below getting darker with depth."""
    d.rectangle([0, 0, W, surface], fill=(60, 66, 72))
    for y in range(surface, H, 8):
        k = (y - surface) / (H - surface)
        c = tuple(int(lerp(a, b, k)) for a, b in zip(SEA, DEEP))
        d.rectangle([0, y, W, y + 8], fill=c)
    pts = [(x, surface + 6 * np.sin(x * 0.02 + t * 2)) for x in range(0, W + 20, 20)]
    d.line(pts, fill=(120, 140, 150), width=4)


def destroyer(d, x, y, s=1.0):
    c = (28, 30, 34)
    d.polygon([(x - 220 * s, y), (x + 240 * s, y), (x + 200 * s, y + 46 * s), (x - 190 * s, y + 46 * s)], fill=c)
    d.rectangle([x - 80 * s, y - 60 * s, x + 60 * s, y], fill=c)
    d.rectangle([x - 40 * s, y - 120 * s, x - 10 * s, y - 60 * s], fill=c)
    d.line([(x + 20 * s, y - 60 * s), (x + 20 * s, y - 160 * s)], fill=c, width=max(2, int(6 * s)))
    d.rectangle([x + 130 * s, y - 24 * s, x + 170 * s, y], fill=c)


def submarine(d, x, y, s=1.0, col=(46, 50, 54)):
    d.rounded_rectangle([x - 300 * s, y - 50 * s, x + 300 * s, y + 50 * s], int(50 * s), fill=col)
    d.rounded_rectangle([x - 60 * s, y - 110 * s, x + 70 * s, y - 40 * s], int(16 * s), fill=col)   # sail
    d.polygon([(x + 290 * s, y), (x + 360 * s, y - 40 * s), (x + 360 * s, y + 40 * s)], fill=col)  # tail fin
    for k in range(5):
        d.ellipse([x - 220 * s + k * 90 * s, y - 8 * s, x - 204 * s + k * 90 * s, y + 8 * s], fill=(70, 74, 78))


def depth_charge_scene(d, t, t0, surface=520, sub_y=1300):
    """Cans fall from the ships and burst well around the sub (practice charges, non-lethal signal)."""
    for i in range(10):
        ti = t0 + i * 0.75
        a = t - ti
        if a < 0:
            continue
        x = 220 + (i * 173) % 660
        if a < 1.6:
            y = lerp(surface + 20, sub_y - 330 + (i % 3) * 70, a / 1.6)
            d.rectangle([x - 14, y - 22, x + 14, y + 22], fill=(80, 84, 88))
        elif a < 2.3:
            k = (a - 1.6) / 0.7
            y = sub_y - 330 + (i % 3) * 70
            r = 30 + 110 * k
            al = int(170 * (1 - k))
            d.ellipse([x - r, y - r, x + r, y + r], outline=(215, 225, 225, al), width=6)
            d.ellipse([x - r * 0.45, y - r * 0.45, x + r * 0.45, y + r * 0.45], fill=(230, 220, 190, int(al * 0.6)))
            for j in range(6):  # rising bubbles
                bx = x + 50 * np.sin(j * 2.1 + i)
                by = y - 140 * k * (0.5 + j / 8)
                d.ellipse([bx - 6, by - 6, bx + 6, by + 6], outline=(200, 210, 210, al), width=2)


# ---------------------------------------------------------------- scenes
def s_hook(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    ocean(d, t, 1080)
    submarine(d, W / 2 + 40, 1720, 0.9)
    k = ease_out_back(t / 0.4, 2)
    T(d, "OCTOBER", 380, int(110 * min(1.1, k)) + 1, CREAM, stroke=6)
    T(d, "1962", 560, int(260 * min(1.1, k)) + 1, RED, stroke=8)
    a = int(255 * smoothstep(2.6, 3.0, t))
    T(d, "THE WORLD ALMOST ENDED", 800, 70, CREAM, a, stroke=5)
    return cam(img, t, 1, 0.6, 1.0 + 0.03 * t / 6)


def s_setup(t):
    a = t - 6.0
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    ocean(d, t)
    destroyer(d, 320, 500, 0.75)
    destroyer(d, 820, 495, 0.6)
    depth_charge_scene(d, t, 9.6, sub_y=1060)
    submarine(d, W / 2, 1060, 0.9)
    T(d, "CUBAN MISSILE CRISIS", 200, 76, CREAM, int(255 * smoothstep(6.1, 6.5, t)), stroke=5)
    if t > 9.6:
        T(d, "PRACTICE DEPTH CHARGES", 1640, 56, AMBER, int(255 * smoothstep(9.6, 10.0, t)), stroke=4)
        T(d, "SIGNALS TO SURFACE", 1720, 40, CREAM, int(255 * smoothstep(10.0, 10.4, t)), f="oswald")
    amp = 0.5 + sum(4 * np.exp(-(t - (9.6 + i * 0.75 + 1.6)) * 6) for i in range(10) if t > 9.6 + i * 0.75 + 1.6)
    return cam(img, t, 2, amp, 1.0 + 0.02 * a / 10)


def sub_interior(d, t, flick=1.0):
    k = 0.65 + 0.35 * flick
    d.rectangle([0, 0, W, H], fill=(int(60 * k), int(16 * k), int(14 * k)))
    for i in range(7):  # pipes
        y = 160 + i * 80
        d.rectangle([0, y, W, y + 26], fill=(int(90 * k), int(40 * k), int(34 * k)))
    for i in range(4):  # gauges
        x = 170 + i * 250
        d.ellipse([x - 70, 740, x + 70, 880], fill=(int(40 * k), int(20 * k), int(18 * k)), outline=(int(180 * k), int(120 * k), int(90 * k)), width=5)
        ang = np.deg2rad(200 + 140 * (0.5 + 0.5 * np.sin(t * 2 + i)))
        d.line([(x, 810), (x + 55 * np.cos(ang), 810 + 55 * np.sin(ang))], fill=(240, 120, 90), width=5)
    d.rectangle([0, 1180, W, H], fill=(int(30 * k), int(10 * k), int(10 * k)))


def s_escalation(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    boom = [17.8, 19.2, 20.3, 21.6]
    flick = 1.0 - 0.6 * max([np.exp(-(t - b) * 5) for b in boom if t > b] + [0])
    sub_interior(d, t, flick)
    if t < 21.0:  # the radio: no contact with Moscow
        d.rounded_rectangle([290, 920, 790, 1120], 20, fill=(30, 26, 24), outline=CREAM, width=5)
        for x in range(320, 760, 8):
            d.line([(x, 1020), (x, 1020 + 30 * np.sin(x * 0.7 + t * 40) * np.sin(x * 0.13))], fill=(150, 200, 150), width=2)
        T(d, "NO CONTACT: MOSCOW", 380, 86, CREAM, int(255 * smoothstep(15.7, 16.1, t)), stroke=6)
    else:  # the nuclear torpedo
        k = ease_out((t - 21.0) / 0.6)
        x0 = lerp(-700, 90, k)
        d.rounded_rectangle([x0, 980, x0 + 820, 1100], 60, fill=(110, 112, 110), outline=(40, 40, 40), width=6)
        d.polygon([(x0 + 820, 990), (x0 + 900, 1040), (x0 + 820, 1090)], fill=(110, 112, 110))
        d.rectangle([x0 + 40, 990, x0 + 120, 1090], fill=(180, 160, 60))
        T(d, "NUCLEAR TORPEDO", 380, 96, RED, int(255 * smoothstep(word_t("n3", 0.8), word_t("n3", 0.85), t)), stroke=6)
        T(d, "THE CAPTAIN FEARED WAR HAD STARTED", 500, 44, CREAM, int(255 * smoothstep(21.0, 21.4, t)), f="oswald")
    amp = 0.6 + sum(14 * np.exp(-(t - b) * 6) for b in boom if t > b)
    return cam(img, t, 3, amp)


def s_twist(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    sub_interior(d, t, 0.8)
    d.rectangle([0, 0, W, H], fill=(0, 0, 0, 110))
    T(d, "3 SENIOR OFFICERS", 220, 96, CREAM, int(255 * smoothstep(26.6, 27.0, t)), stroke=6)
    T(d, "MUST AGREE TO LAUNCH", 320, 60, AMBER, int(255 * smoothstep(27.0, 27.4, t)), stroke=4)
    votes = [(250, "YES", 29.4), (540, "YES", 30.2), (830, "NO", 31.8)]
    for x, v, tv in votes:
        ef.man(d, x, 1010, 0.95, "cap", 1 if x < 540 else -1, col=(150, 120, 110))
        if t > tv:
            k = ease_out_back((t - tv) / 0.25, 2)
            col = RED if v == "YES" else CREAM
            d.rounded_rectangle([x - 100 * k, 440, x + 100 * k, 560], 18, fill=(20, 16, 14, 230), outline=col, width=6)
            T(d, v, 500, int(80 * min(1.1, k)) + 1, col, x=x)
    if t > 31.8:
        a = int(255 * smoothstep(31.8, 32.2, t))
        T(d, "VASILI ARKHIPOV", 1075, 62, CREAM, a, x=760, stroke=4)
    T(d, "PER LATER CREW ACCOUNTS", 385, 32, (190, 175, 160), int(255 * smoothstep(27.0, 27.4, t)), f="oswald")
    return cam(img, t, 4, 0.4 + (10 * np.exp(-(t - 31.8) * 7) if t > 31.8 else 0))


def s_payoff(t):
    a = t - 34.6
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    ocean(d, t, 760)
    destroyer(d, 260, 740, 0.6)
    destroyer(d, 840, 735, 0.5)
    rise = ease_in_out(a / 3.0)
    y = lerp(1180, 760, rise)
    submarine(d, W / 2, y, 0.9)
    if rise > 0.95:
        for k in range(8):  # surface wash
            x = 280 + k * 70
            d.arc([x - 40, 740, x + 40, 800], 200, 340, fill=(200, 210, 215), width=4)
    T(d, "SURFACED", 300, 120, CREAM, int(255 * smoothstep(36.0, 36.4, t)), stroke=6)
    t2 = word_t("n5", 0.45)
    if t > t2:
        al = int(255 * smoothstep(t2, t2 + 0.4, t))
        T(d, "THE AMERICANS HAD NO IDEA", 1600, 64, AMBER, al, stroke=4)
        T(d, "IT CARRIED A NUCLEAR TORPEDO", 1690, 50, CREAM, al, stroke=4)
    return cam(img, t, 5, 0.4, 1.0 + 0.03 * a / 8)


def s_end(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    out_k = 1 - smoothstep(46.9, 47.2, t)
    T(d, "ONE", 520, 200, CREAM, int(255 * smoothstep(43.0, 43.3, t) * out_k), stroke=6)
    T(d, "DECISION.", 730, 170, RED, int(255 * smoothstep(43.3, 43.6, t) * out_k), stroke=6)
    T(d, "MILLIONS OF LIVES", 960, 72, CREAM, int(255 * smoothstep(44.3, 44.7, t) * out_k), stroke=4)
    T(d, "POTENTIALLY AT STAKE", 1050, 60, AMBER, int(255 * smoothstep(44.7, 45.1, t) * out_k), stroke=4)
    if t > 47.2:
        k2 = ease_out_back((t - 47.2) / 0.3, 2.5)
        f = font("anton", int(190 * k2) + 1)
        w = d.textlength("NO WAY.", font=f)
        cy = 560
        d.rectangle([W / 2 - 360, cy - 10, W / 2 + 360, cy + 250], fill=(20, 16, 12, int(235 * min(1, k2))))
        d.text((W / 2 - w / 2, cy + 125 - 125 * k2), "NO WAY.", font=f, fill=(245, 236, 215, 255))
        d.rectangle([W / 2 - 240 * k2, cy + 225, W / 2 + 240 * k2, cy + 238], fill=RED + (255,))
    return cam(img, t, 6, 0.3)


SCENES = [(0.0, 5.9, s_hook), (5.9, 15.4, s_setup), (15.4, 25.4, s_escalation), (25.4, 34.6, s_twist),
          (34.6, 42.8, s_payoff), (42.8, 50.01, s_end)]


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
    out = grade(img, idx, t, keep_color=0.42)
    if t > 49.6:
        out = out * (1 - smoothstep(49.6, 50.0, t) * 0.9)
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
