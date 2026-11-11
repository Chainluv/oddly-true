"""NO WAY. — He Died One Minute Before the Ceasefire (Henry Gunther, 11 Nov 1918). ~65s, serious tone.
Reuses molasses-flood (grade, captions), zanzibar-war (clock, headline, backgrounds, caption timing) and
bonus-army (soldier silhouette, smoke). All documents and maps are stylized reconstructions."""
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
from common import (W, H, FPS, font, to_img, from_img, cam2d, shake, grade, lerp, smoothstep, ease_in_out, ease_out)
import render as mf   # captions
import episode as zw  # draw_clock(), headline(), dark_bg(), paper_bg(), build_chunks()
import bonus as ba    # soldier(), smoke_layer()

DURATION = 65.0
NFR = int(DURATION * FPS)
AMBER, RED, CREAM = mf.AMBER, (205, 50, 40), (236, 226, 205)
VOICES = os.path.join(HERE, "voices")

NARR = {"n01": 0.3, "n02": 3.0, "n03": 7.2, "n04": 10.2, "n05": 14.0, "n06": 18.2, "n07": 22.8, "n08": 28.2,
        "n09": 33.0, "n10": 36.3, "n11": 42.4, "n12": 47.3, "n13": 49.1, "n14": 53.2, "n15": 58.4, "n16": 62.2}
TEXT = {"n01": "HE SURVIVED YEARS OF WORLD WAR.",
        "n02": "HE DIED ONE MINUTE BEFORE THE CEASEFIRE.",
        "n03": "NOVEMBER 11TH, 1918.",
        "n04": "GERMANY AND THE ALLIES HAD SIGNED AN ARMISTICE THAT MORNING.",
        "n05": "BUT IT DIDN'T TAKE EFFECT IMMEDIATELY.",
        "n06": "THE FIGHTING ON THE WESTERN FRONT WAS SCHEDULED TO STOP AT ELEVEN.",
        "n07": "UNTIL THEN, SOLDIERS WERE STILL DYING.",
        "n08": "AMONG THEM WAS HENRY GUNTHER, AN AMERICAN SOLDIER FROM BALTIMORE.",
        "n09": "AT 10:59, HE WAS KILLED IN FRANCE.",
        "n10": "HE IS GENERALLY RECOGNIZED AS THE LAST AMERICAN SOLDIER KILLED IN ACTION IN WORLD WAR ONE.",
        "n11": "ONE MINUTE LATER, THE CEASEFIRE TOOK EFFECT.",
        "n12": "THINK ABOUT THAT GAP.",
        "n13": "AN AGREEMENT ALREADY EXISTED. BUT THE DEADLINE HADN'T ARRIVED.",
        "n14": "NOVEMBER 11TH LATER BECAME ARMISTICE DAY, AND, IN AMERICA, VETERANS DAY.",
        "n15": "BEHIND THAT DATE IS A MAN WHO MISSED THE SILENCE BY ONE MINUTE.",
        "n16": "HIS NAME WAS HENRY GUNTHER."}

zw.LINES = [(k, ba.groups(TEXT[k])) for k in NARR]
zw.NARR = NARR
zw.DUR = {k: sf.info(os.path.join(VOICES, f"{k}.wav")).duration for k in NARR}
zw.SPOKEN = {"11TH,": "eleventh", "1918.": "nineteen eighteen", "10:59,": "ten fifty nine"}
mf.CHUNKS = zw.build_chunks()
mf.KEYWORDS = {"CEASEFIRE.", "1918.", "ARMISTICE", "MORNING.", "IMMEDIATELY.", "ELEVEN.", "DYING.", "HENRY", "GUNTHER,",
               "10:59,", "FRANCE.", "LAST", "AMERICAN", "LATER,", "GAP.", "AGREEMENT", "DEADLINE", "DAY,", "DAY.",
               "SILENCE", "MINUTE.", "GUNTHER."}

T_1059 = 33.5   # "ten fifty-nine"
T_1100 = 43.3   # "one minute later" -> ceasefire
SILENCE = (T_1100 + 0.4, 47.2)


def clock_time(t):
    """Displayed time in minutes after 10:00, advancing toward 11:00 across the episode."""
    keys = [(0.0, 59.0), (7.0, 59.0), (15.6, 40.0), (18.0, 46.0), (28.0, 57.0), (T_1059, 59.0), (T_1100, 60.0)]
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, m0), (t1, m1) in zip(keys, keys[1:]):
        if t < t1:
            return lerp(m0, m1, (t - t0) / (t1 - t0))
    return 60.0


def draw_clock(img, cx, cy, r, minutes, sec_t=None):
    zw.draw_clock(img, cx, cy, r, (minutes % 60) * 6, (10 + minutes / 60) * 30)
    if sec_t is not None:  # red second hand, ticking once per second
        a = np.deg2rad(int(sec_t) % 60 * 6)
        d = ImageDraw.Draw(img)
        d.line([(cx, cy), (cx + np.sin(a) * r * 0.85, cy - np.cos(a) * r * 0.85)], fill=RED, width=5)
        d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=RED)


def time_text(minutes):
    m = int(np.floor(minutes + 1e-6))
    return "11:00" if m >= 60 else f"10:{m:02d}"


def base():
    return to_img(zw.DARK).convert("RGBA")


def cam(img, t, seed, amp=0.8, zoom=1.0, cy=900):
    sx, sy, sr = shake(t, amp, 1.5, seed=seed)
    return from_img(cam2d(img.convert("RGB"), zoom, W / 2, cy, sr, sx, sy))


def field(d, horizon=1150):
    d.rectangle([0, horizon, W, H], fill=(48, 42, 36))
    for x in range(-40, W + 40, 120):  # barbed-wire posts
        d.line([(x, horizon + 40), (x + 6, horizon - 60)], fill=(28, 25, 22), width=8)
    for k in range(2):
        pts = [(x, horizon - 30 - k * 22 + 8 * np.sin(x * 0.07)) for x in range(-40, W + 40, 20)]
        d.line(pts, fill=(28, 25, 22), width=3)


# ---------------------------------------------------------------- scenes
def scene_open(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    field(d)
    ba.soldier(d, W / 2, 1240, 1.15, col=(110, 106, 94))
    f = font("anton", 260)
    tw = d.textlength("10:59", font=f)
    d.text(((W - tw) / 2, 260), "10:59", font=f, fill=RED + (255,))
    a = smoothstep(3.6, 5.2, t)
    f2 = font("anton", 84)
    tw = d.textlength("CEASEFIRE: 11:00", font=f2)
    d.text(((W - tw) / 2, 590), "CEASEFIRE: 11:00", font=f2, fill=CREAM + (int(255 * a),))
    return cam(img, t, 1, 0.6, 1.0 + 0.04 * t / 7)


def doc(d, cx, cy):
    w, h = 800, 920
    d.rectangle([cx - w / 2 + 14, cy - h / 2 + 16, cx + w / 2 + 14, cy + h / 2 + 16], fill=(0, 0, 0, 120))
    d.rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], fill=CREAM, outline=(90, 70, 50), width=6)
    for txt, y, f in (("ARMISTICE", -380, font("oldb", 84)), ("Cessation of hostilities", -270, font("playi", 52)),
                      ("on land and in the air", -200, font("oldi", 40))):
        tw = d.textlength(txt, font=f)
        d.text((cx - tw / 2, cy + y), txt, font=f, fill=(45, 35, 28))
    for k in range(10):
        d.line([(cx - 320, cy - 110 + k * 36), (cx + 320 - (k % 3) * 80, cy - 110 + k * 36)], fill=(160, 145, 120), width=4)
    for x in (cx - 260, cx + 60):  # signature scribbles (no real names)
        d.line([(x + 6 * k, cy + 330 + 14 * np.sin(k * 1.3)) for k in range(30)], fill=(60, 50, 90), width=4)
    d.text((cx - 320, cy + 400), "illustrative reconstruction", font=font("oldi", 26), fill=(120, 100, 80))


def scene_morning(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    if t < 15.6:
        k = ease_out((t - 9.2) / 0.7)
        if t > 9.2:
            doc(d, W / 2, lerp(1500, 930, k))
        return cam(img, t, 2, 0.6, 1.0 + 0.02 * (t - 7) / 9)
    rgb = img.convert("RGB")
    draw_clock(rgb, W / 2, 830, 330, clock_time(t), t)
    return cam(rgb, t, 2, 0.6, 1.02)


# Western Front (stylized): coastline, borders, front line from the North Sea coast to the Swiss border
COAST = [(60, 380), (200, 300), (340, 260), (430, 150), (520, 60)]
FRONT = [(470, 140), (520, 300), (560, 420), (650, 520), (760, 600), (820, 760), (860, 900), (900, 1020), (980, 1120)]


def scene_front(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    if t < 22.6:  # map
        p = to_img(zw.paper_bg(8, (0.86, 0.8, 0.66))).crop((0, 0, W, 1200))
        img.paste(p, (0, 0))
        d = ImageDraw.Draw(img, "RGBA")
        d.polygon([(0, 0), (520, 0)] + COAST[::-1] + [(0, 380)], fill=(170, 185, 190))
        d.line(COAST, fill=(60, 50, 40), width=5)
        prog = smoothstep(18.4, 20.4, t)
        n = max(2, int(len(FRONT) * prog))
        d.line(FRONT[:n], fill=RED, width=14, joint="curve")
        for txt, x, y, s in (("BELGIUM", 600, 250, 46), ("FRANCE", 250, 760, 64), ("GERMANY", 820, 330, 46),
                             ("WESTERN FRONT", 600, 1080, 44), ("North Sea", 90, 120, 40)):
            fnt = font("oldb" if s != 40 else "oldi", s)
            d.text((x, y), txt, font=fnt, fill=(60, 48, 36) if txt != "WESTERN FRONT" else RED)
        d.text((60, 1140), "stylized map", font=font("oldi", 26), fill=(110, 95, 80))
    else:         # restrained battlefield silhouettes
        field(d, 1100)
        for i, x in enumerate((180, 330, 520, 760, 900)):
            ba.soldier(d, x, 1180 + (i % 2) * 30, 0.55 + 0.1 * (i % 2), col=(96, 92, 82))
        img.alpha_composite(ba.smoke_layer(t, 0.5, (90, 86, 80), 10, 600, 1100))
        d = ImageDraw.Draw(img, "RGBA")
    rgb = img.convert("RGB")
    draw_clock(rgb, 170 if t < 22.6 else W - 170, 1000 if t < 22.6 else 330, 100, clock_time(t), t)
    return cam(rgb, t, 3, 0.6, 1.0 + 0.03 * (t - 18) / 10)


def scene_gunther(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    field(d, 1150)
    img.alpha_composite(ba.smoke_layer(t, 0.45, (150, 146, 136), 6, 700, 1250))
    d = ImageDraw.Draw(img, "RGBA")
    # a lone silhouette moving slowly forward in France; movement stops at 10:59, then he fades into the mist
    walk = min(t, T_1059) - 28.5
    x = 300 + max(0, walk) * 45
    vis = 1 - smoothstep(T_1059 + 0.6, T_1059 + 3.0, t)
    if vis > 0:
        fig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ba.soldier(ImageDraw.Draw(fig), x, 1250, 0.95, col=(120, 116, 104))
        fig.putalpha(fig.getchannel("A").point(lambda v: int(v * vis)))
        img.alpha_composite(fig)
    rgb = img.convert("RGB")
    draw_clock(rgb, W - 170, 600, 110, clock_time(t), t if t < T_1059 else T_1059)
    if t >= T_1059:
        f = font("anton", 110)
        dd = ImageDraw.Draw(rgb)
        dd.text((90, 1030), "10:59", font=f, fill=RED)
    dim = 1 - 0.25 * smoothstep(T_1059, T_1059 + 0.5, t)
    return cam(rgb, t, 4, 0.4 if t < T_1059 else 0.0, 1.0 + 0.02 * (t - 28) / 12) * dim


def scene_eleven(t):
    img = base().convert("RGB")
    m = clock_time(t)
    draw_clock(img, W / 2, 760, 280, m, t if t < T_1100 else T_1100)
    d = ImageDraw.Draw(img, "RGBA")
    f = font("anton", 150)
    txt = time_text(m)
    tw = d.textlength(txt, font=f)
    d.text(((W - tw) / 2, 230), txt, font=f, fill=CREAM if txt == "11:00" else RED)
    if t > 49.2:
        a = smoothstep(49.2, 49.8, t)
        b = smoothstep(51.2, 51.8, t)
        f2 = font("anton", 58)
        d.text((150, 1085), "AGREEMENT: SIGNED", font=f2, fill=CREAM + (int(255 * a),))
        d.text((150, 1150), "DEADLINE: 11:00", font=f2, fill=RED + (int(255 * b),))
    return cam(img, t, 5, 0.3, 1.0 + 0.03 * (t - 40) / 12)


def scene_days(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    if t < 58.2:  # ARMISTICE DAY -> VETERANS DAY
        p = (t - 55.8) / 0.4
        if p < 0.5:
            txt, col, sy = "ARMISTICE DAY", CREAM, 1 - smoothstep(0, 0.5, p) if p > 0 else 1
        else:
            txt, col, sy = "VETERANS DAY", AMBER, smoothstep(0.5, 1.0, p)
        k = ease_out((t - 53.0) / 0.5)
        layer = Image.new("RGBA", (W, 260), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        f = font("anton", 140)
        tw = ld.textlength(txt, font=f)
        ld.text(((W - tw) / 2, 30), txt, font=f, fill=col + (int(255 * k),))
        hh = max(1, int(260 * max(0.02, sy)))
        layer = layer.resize((W, hh), Image.BICUBIC)
        img.alpha_composite(layer, (0, int(760 - hh / 2)))
        f3 = font("oldb", 44)
        sub = "NOVEMBER 11"
        tw = d.textlength(sub, font=f3)
        d.text(((W - tw) / 2, 940), sub, font=f3, fill=(170, 160, 140, int(255 * k)))
        return cam(img, t, 6, 0.3, 1.0)
    # final card: his name and the time, small branding beneath
    a = ease_out((t - 58.4) / 1.2)
    f = font("anton", 150)
    tw = d.textlength("HENRY GUNTHER", font=f)
    d.text(((W - tw) / 2, 640), "HENRY GUNTHER", font=f, fill=CREAM + (int(255 * a),))
    d.rectangle([W / 2 - 260 * a, 860, W / 2 + 260 * a, 866], fill=RED + (255,))
    b = smoothstep(59.4, 60.4, t)
    f2 = font("anton", 64)
    s = "10:59 A.M. — NOVEMBER 11, 1918"
    tw = d.textlength(s, font=f2)
    d.text(((W - tw) / 2, 900), s, font=f2, fill=RED + (int(255 * b),))
    c = smoothstep(63.6, 64.2, t)
    f3 = font("anton", 54)
    tw = d.textlength("NO WAY.", font=f3)
    d.text(((W - tw) / 2, 1560), "NO WAY.", font=f3, fill=(170, 160, 140, int(255 * c)))
    return cam(img, t, 7, 0.0, 1.0 + 0.02 * (t - 58.2) / 7)


SCENES = [(0.0, 7.0, scene_open), (7.0, 18.0, scene_morning), (18.0, 28.0, scene_front),
          (28.0, 40.0, scene_gunther), (40.0, 52.9, scene_eleven), (52.9, 65.01, scene_days)]

HEADS = [(7.1, 9.2, [("NOVEMBER 11,", CREAM), ("1918.", RED)]),
         (11.4, 15.4, [("SIGNED THAT", CREAM), ("MORNING.", AMBER)]),
         (28.2, 33.4, [("HENRY GUNTHER", CREAM), ("BALTIMORE, MARYLAND", (190, 180, 160))])]


def overlay(t):
    for t0, t1, lines in HEADS:
        if t0 <= t < t1:
            layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            sz = 96 if len(lines[1][0]) > 14 else 130
            zw.headline(ImageDraw.Draw(layer), lines, 180, t, t0 + 0.02, size=sz, gap=sz + 14)
            return layer
    return None


def mix(a, b, k):
    return a * (1 - k) + b * k


def frame(idx):
    t = idx / FPS
    for i, (t0, t1, fn) in enumerate(SCENES):
        if t0 <= t < t1:
            img = fn(t)
            if i + 1 < len(SCENES) and t > t1 - 0.4:
                img = mix(img, SCENES[i + 1][2](t1), smoothstep(t1 - 0.4, t1, t))
            break
    if 15.3 < t < 15.9:  # document dissolves into the clock
        img = mix(scene_morning(15.29), scene_morning(15.9), smoothstep(15.3, 15.9, t))
    out = grade(img, idx, t)
    if t > 64.6:
        out = out * (1 - smoothstep(64.6, 65.0, t) * 0.9)
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
