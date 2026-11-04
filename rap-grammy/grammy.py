"""NO WAY. #6 — They Won the First Rap Grammy—and Boycotted the Show (1989).
Reuses the molasses-flood grade/captions and the zanzibar-war helpers (headline, backgrounds, caption timing)."""
import os
import subprocess
import sys
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "zanzibar-war"))
sys.path.insert(0, os.path.join(HERE, "..", "molasses-flood"))
from common import (W, H, FPS, NFRAMES, font, to_img, from_img, cam2d, shake, grade, lerp, smoothstep,
                    ease_in_out, ease_out, ease_out_back)
import render as mf   # molasses-flood captions + paper aging
import episode as zw  # zanzibar-war: headline(), dark_bg(), paper_bg(), build_chunks()

AMBER = mf.AMBER
RED = (225, 70, 50)
GOLD = (214, 170, 70)
NARR = {"l1": 0.1, "l2": 3.1, "l3": 8.3, "l4": 12.1, "l5": 16.0, "l6": 17.45, "l7": 18.6}
DUR = {"l1": 2.83, "l2": 4.92, "l3": 2.09, "l4": 2.35, "l5": 1.22, "l6": 0.83, "l7": 0.75}
LINES = [
    ("l1", [["THE", "FIRST", "RAPPERS"], ["TO", "WIN", "A", "GRAMMY"], ["BOYCOTTED", "THE", "SHOW."]]),
    ("l2", [["IN", "1989,"], ["DJ", "JAZZY", "JEFF"], ["AND", "THE", "FRESH", "PRINCE"], ["WON", "FOR"],
            ["PARENTS", "JUST", "DON'T"], ["UNDERSTAND."]]),
    ("l3", [["BUT", "THE", "AWARD"], ["WASN'T", "BEING"], ["TELEVISED."]]),
    ("l4", [["THEY", "JOINED", "A", "BOYCOTT"], ["INSTEAD", "OF", "ATTENDING."]]),
    ("l5", [["THAT", "FRESH", "PRINCE?"]]),
    ("l6", [["WILL", "SMITH."]]),
    ("l7", [["NO", "WAY."]]),
]
zw.LINES, zw.NARR, zw.DUR = LINES, NARR, DUR
zw.SPOKEN = {"1989,": "nineteen eighty nine", "DJ": "dee jay"}
mf.CHUNKS = zw.build_chunks()
mf.KEYWORDS = {"GRAMMY", "BOYCOTTED", "1989,", "WON", "TELEVISED.", "BOYCOTT", "PRINCE?", "WILL", "SMITH.", "WAY."}


# ---------------------------------------------------------------- drawing helpers
def gramophone(d, cx, by, s=1.0):
    """Generic gold gramophone trophy (bottom centre cx, by)."""
    g, dk = GOLD, (150, 110, 40)
    d.rectangle([cx - 150 * s, by - 60 * s, cx + 150 * s, by], fill=(50, 40, 32), outline=dk, width=4)    # plinth
    d.rectangle([cx - 110 * s, by - 130 * s, cx + 110 * s, by - 60 * s], fill=g, outline=dk, width=4)     # box
    d.ellipse([cx - 90 * s, by - 150 * s, cx + 90 * s, by - 115 * s], fill=(235, 200, 110), outline=dk, width=3)  # disc
    d.line([(cx + 40 * s, by - 135 * s), (cx + 40 * s, by - 230 * s)], fill=dk, width=int(14 * s))        # tone arm
    d.polygon([(cx + 40 * s, by - 230 * s), (cx - 10 * s, by - 280 * s), (cx - 170 * s, by - 470 * s),
               (cx + 10 * s, by - 520 * s), (cx + 60 * s, by - 250 * s)], fill=g, outline=dk)             # horn
    d.ellipse([cx - 210 * s, by - 560 * s, cx + 40 * s, by - 430 * s], fill=(235, 200, 110), outline=dk, width=5)
    d.ellipse([cx - 160 * s, by - 525 * s, cx - 10 * s, by - 465 * s], fill=(120, 85, 30))
    d.line([(cx - 70 * s, by - 120 * s), (cx - 40 * s, by - 80 * s)], fill=(255, 235, 170), width=int(5 * s))  # glint


def invitation(d, cx, cy, w=560, h=320, a=255):
    d.rectangle([cx - w / 2 + 12, cy - h / 2 + 14, cx + w / 2 + 12, cy + h / 2 + 14], fill=(0, 0, 0, int(a * 0.5)))
    d.rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], fill=(236, 226, 205, a), outline=(150, 120, 60, a), width=6)
    d.rectangle([cx - w / 2 + 18, cy - h / 2 + 18, cx + w / 2 - 18, cy + h / 2 - 18], outline=(190, 150, 70, a), width=2)
    for txt, y, f in (("YOU ARE INVITED", -110, font("oswaldm", 42)), ("Awards Night", -50, font("playi", 66)),
                      ("1989", 50, font("oldb", 48))):
        tw = d.textlength(txt, font=f)
        d.text((cx - tw / 2, cy + y), txt, font=f, fill=(50, 40, 30, a))


def stamp(img, text, cx, cy, k, angle=-12, size=120):
    """Red rubber-stamp text slammed onto img (RGBA)."""
    layer = Image.new("RGBA", (900, 260), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    f = font("anton", size)
    tw = ld.textlength(text, font=f)
    ld.rectangle([450 - tw / 2 - 30, 40, 450 + tw / 2 + 30, 220], outline=RED + (235,), width=12)
    ld.text((450 - tw / 2, 50), text, font=f, fill=RED + (235,))
    sc = 1.8 - 0.8 * k
    layer = layer.rotate(angle, expand=True, resample=Image.BICUBIC)
    layer = layer.resize((int(layer.width * sc), int(layer.height * sc)), Image.BICUBIC)
    img.alpha_composite(layer, (int(cx - layer.width / 2), int(cy - layer.height / 2)))


def turntable(d, cx, cy, t):
    d.rounded_rectangle([cx - 420, cy - 260, cx + 420, cy + 260], 24, fill=(40, 36, 34), outline=(110, 100, 90), width=5)
    d.ellipse([cx - 330, cy - 230, cx + 170, cy + 230], fill=(20, 18, 17))
    for r in range(60, 230, 18):
        d.ellipse([cx - 80 - r, cy - r, cx - 80 + r, cy + r], outline=(48, 45, 43), width=2)
    d.ellipse([cx - 160, cy - 80, cx, cy + 80], fill=(200, 60, 45))
    ang = t * 3.5  # spinning label marker
    d.line([(cx - 80, cy), (cx - 80 + np.cos(ang) * 70, cy + np.sin(ang) * 70)], fill=(245, 230, 200), width=6)
    d.ellipse([cx - 88, cy - 8, cx - 72, cy + 8], fill=(220, 210, 190))
    d.line([(cx + 330, cy - 200), (cx + 300, cy + 60), (cx + 120, cy + 140)], fill=(190, 185, 175), width=12)  # tone arm
    d.ellipse([cx + 305, cy - 225, cx + 355, cy - 175], fill=(150, 145, 135))
    d.rectangle([cx + 250, cy + 170, cx + 380, cy + 210], fill=(90, 85, 80))


def crt(d, x0, y0, x1, y1):
    d.rounded_rectangle([x0, y0, x1, y1], 40, fill=(70, 60, 50), outline=(140, 125, 100), width=6)
    sx0, sy0, sx1, sy1 = x0 + 50, y0 + 50, x1 - 170, y1 - 50
    d.rounded_rectangle([sx0, sy0, sx1, sy1], 50, fill=(30, 28, 32))
    for k in range(2):  # knobs
        cy = y0 + 120 + k * 130
        d.ellipse([x1 - 130, cy - 40, x1 - 50, cy + 40], fill=(40, 35, 30), outline=(150, 135, 110), width=4)
    for k in range(5):
        d.line([(x1 - 135, y1 - 160 + k * 18), (x1 - 45, y1 - 160 + k * 18)], fill=(40, 35, 30), width=6)
    return sx0, sy0, sx1, sy1


def stage_on_tv(d, sx0, sy0, sx1, sy1, t):
    """Generic awards stage: curtains, spotlights, podium, live dot (no real people or footage)."""
    w = sx1 - sx0
    d.rectangle([sx0 + 20, sy0 + 20, sx1 - 20, sy1 - 20], fill=(60, 30, 30))
    for k in range(10):  # curtain folds
        x = sx0 + 20 + k * (w - 40) / 10
        d.line([(x, sy0 + 20), (x, sy1 - 20)], fill=(90, 45, 40), width=10)
    d.rectangle([sx0 + 20, sy1 - 120, sx1 - 20, sy1 - 20], fill=(110, 90, 70))  # stage floor
    cx = (sx0 + sx1) / 2
    for dx in (-120, 120):  # light cones
        d.polygon([(cx + dx * 1.6, sy0 + 20), (cx + dx * 1.6 + 30, sy0 + 20), (cx + dx * 0.4 + 90, sy1 - 110),
                   (cx + dx * 0.4 - 90, sy1 - 110)], fill=(255, 235, 180, 70))
    d.rectangle([cx - 45, sy1 - 230, cx + 45, sy1 - 110], fill=(160, 130, 70))  # podium
    if int(t * 2) % 2 == 0:
        d.ellipse([sx0 + 40, sy0 + 40, sx0 + 70, sy0 + 70], fill=(230, 50, 40))
    d.text((sx0 + 82, sy0 + 34), "LIVE", font=font("oswaldm", 34), fill=(240, 230, 210))
    for y in range(int(sy0 + 20), int(sy1 - 20), 6):  # scanlines
        d.line([(sx0 + 20, y), (sx1 - 20, y)], fill=(0, 0, 0, 50), width=2)


def performer(d, cx, by, facing, s=1.0, cap=False):
    """Generic stylized silhouette (no likeness). facing: +1 right, -1 left, values between = turning."""
    c = (138, 126, 110)
    fw = max(0.08, abs(facing))
    d.polygon([(cx - 70 * s * fw, by), (cx - 85 * s, by - 250 * s), (cx - 55 * s, by - 330 * s),
               (cx + 55 * s, by - 330 * s), (cx + 85 * s, by - 250 * s), (cx + 70 * s * fw, by)], fill=c)
    d.ellipse([cx - 48 * s, by - 430 * s, cx + 48 * s, by - 330 * s], fill=c)
    if cap:
        d.polygon([(cx - 50 * s, by - 405 * s), (cx + 50 * s, by - 405 * s), (cx + (50 + 55 * facing) * s, by - 395 * s),
                   (cx + 50 * s, by - 420 * s), (cx - 50 * s, by - 430 * s)], fill=c)
    else:
        d.rectangle([cx - 46 * s, by - 452 * s, cx + 46 * s, by - 410 * s], fill=c)  # flat-top haircut shape
    d.polygon([(cx + 40 * facing * s, by - 395 * s), (cx + 62 * facing * s, by - 380 * s), (cx + 40 * facing * s, by - 368 * s)], fill=c)


def boombox(d, cx, cy, t):
    d.rounded_rectangle([cx - 300, cy - 120, cx + 300, cy + 120], 20, fill=(55, 52, 50), outline=(150, 140, 125), width=5)
    d.line([(cx - 200, cy - 120), (cx - 160, cy - 190), (cx + 160, cy - 190), (cx + 200, cy - 120)], fill=(150, 140, 125), width=8)
    pulse = 1 + 0.06 * max(0, np.sin(t * 2 * np.pi * 1.5)) ** 4
    for dx in (-180, 180):
        r = 85 * pulse
        d.ellipse([cx + dx - r, cy - r, cx + dx + r, cy + r], fill=(30, 28, 27), outline=(160, 150, 135), width=5)
        d.ellipse([cx + dx - 28, cy - 28, cx + dx + 28, cy + 28], fill=(90, 85, 80))
    d.rectangle([cx - 70, cy - 60, cx + 70, cy + 20], fill=(25, 24, 23), outline=(160, 150, 135), width=3)
    d.line([(cx - 50, cy - 20), (cx + 50, cy - 20)], fill=AMBER, width=4)


def base():
    return to_img(zw.DARK).convert("RGBA")


def cam(img, t, seed, amp=2.0, zoom=1.0, cy=900):
    sx, sy, sr = shake(t, amp, 3, seed=seed)
    return from_img(cam2d(img.convert("RGB"), zoom, W / 2, cy, sr, sx, sy))


# ---------------------------------------------------------------- scenes
STAMP_T = 1.6


def scene_hook(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    k = ease_out_back(t / 0.45, 2)
    gramophone(d, W / 2 + 60, 990, 0.95 * k + 0.01)
    invitation(d, W / 2, 1110, a=int(255 * smoothstep(0.4, 0.8, t)))
    if t >= STAMP_T:
        stamp(img, "BOYCOTTED", W / 2, 1110, ease_out((t - STAMP_T) / 0.15))
    amp = 2 + (16 * np.exp(-(t - STAMP_T) * 10) if t >= STAMP_T else 0)
    return cam(img, t, 1, amp, 1.0 + 0.02 * t / 3)


def scene_record(t):
    a = t - 3.0
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    # record sleeve with artist + title (readable, not spinning)
    sx = lerp(-700, 90, ease_out(a / 0.5))
    d.rectangle([sx, 400, sx + 900, 780], fill=(200, 60, 45), outline=(120, 30, 25), width=6)
    for txt, y, f, col in (("DJ JAZZY JEFF & THE FRESH PRINCE", 430, font("anton", 58), (250, 240, 220)),
                           ("“PARENTS JUST", 530, font("anton", 92), (255, 220, 120)),
                           ("DON'T UNDERSTAND”", 640, font("anton", 92), (255, 220, 120))):
        tw = d.textlength(txt, font=f)
        d.text((sx + 450 - tw / 2, y), txt, font=f, fill=col)
    turntable(d, W / 2, 1020, t)
    return cam(img, t, 2, 2, 1.0 + 0.02 * a / 5)


def scene_tv(t):
    a = t - 8.0
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    s = crt(d, 60, 260, W - 60, 820)
    stage_on_tv(d, *s, t)
    d.text((s[0] + 30, s[3] + 10), "AWARDS BROADCAST", font=font("oswaldm", 34), fill=(200, 190, 170))
    # the rap category sits outside the TV frame
    k = ease_out_back((a - 0.6) / 0.35, 2) if a > 0.6 else 0
    if k > 0:
        y = lerp(1200, 880, min(1, k))
        d.rounded_rectangle([170, y, W - 170, y + 110], 14, fill=(236, 226, 205), outline=(150, 120, 60), width=5)
        f = font("anton", 64)
        txt = "BEST RAP PERFORMANCE"
        tw = d.textlength(txt, font=f)
        d.text((W / 2 - tw / 2, y + 16), txt, font=f, fill=(45, 35, 28))
    if a > 1.6:
        stamp(img, "NOT TELEVISED", W / 2, 1110, ease_out((a - 1.6) / 0.15), angle=-4, size=88)
    amp = 2 + (12 * np.exp(-(a - 1.6) * 10) if a > 1.6 else 0)
    return cam(img, t, 3, amp, 1.0 + 0.02 * a / 4)


TURN_T = 12.9


def scene_boycott(t):
    a = t - 12.0
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    invitation(d, W / 2, 620, 520, 290)
    p = ease_in_out((t - TURN_T) / 0.6)
    walk = 120 * ease_in_out((t - TURN_T - 0.5) / 1.8)
    for cx, side, cap in ((330, 1, True), (750, -1, False)):
        facing = side * (1 - 2 * p)  # face the card, then turn away
        performer(d, cx - side * walk, 1210, facing, 0.95, cap)
    return cam(img, t, 4, 2, 1.0 + 0.02 * a / 4)


FLIP_T = 17.45


def scene_reveal(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    boombox(d, W / 2, 1080, t)
    # "THE FRESH PRINCE" flips into "WILL SMITH" on the name
    p = (t - FLIP_T) / 0.3
    if p < 0.5:
        txt, col, sy = "THE FRESH PRINCE", (245, 236, 215), 1 - smoothstep(0, 0.5, p) if p > 0 else 1
    else:
        txt, col, sy = "WILL SMITH", AMBER, smoothstep(0.5, 1.0, p)
    k = ease_out((t - 16.0) / 0.3)
    f = font("anton", 150 if txt == "WILL SMITH" else 118)
    layer = Image.new("RGBA", (W, 260), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    tw = ld.textlength(txt, font=f)
    ld.text(((W - tw) / 2, 30), txt, font=f, fill=col + (int(255 * k),), stroke_width=9, stroke_fill=(0, 0, 0, int(255 * k)))
    hh = max(1, int(260 * max(0.02, sy)))
    layer = layer.resize((W, hh), Image.BICUBIC)
    img.alpha_composite(layer, (0, int(760 - hh / 2)))
    if t > 18.6:  # wordmark plate
        k2 = ease_out_back((t - 18.6) / 0.3, 2.5)
        f = font("anton", int(190 * k2) + 1)
        w = d.textlength("NO WAY.", font=f)
        cy = 330
        d.rectangle([W / 2 - 360, cy - 10, W / 2 + 360, cy + 250], fill=(20, 16, 12, int(225 * min(1, k2))))
        d.text((W / 2 - w / 2, cy + 125 - 125 * k2), "NO WAY.", font=f, fill=(245, 236, 215, 255))
        d.rectangle([W / 2 - 240 * k2, cy + 225, W / 2 + 240 * k2, cy + 238], fill=AMBER + (255,))
    amp = 2 + (12 * np.exp(-(t - FLIP_T) * 10) if t >= FLIP_T else 0)
    return cam(img, t, 5, amp, 1.0)


def overlay(t):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for t0, t1, lines in [(0.0, 2.95, [("FIRST RAP", (255, 255, 255)), ("GRAMMY.", AMBER)]),
                          (3.05, 7.95, [("1989", AMBER)]),
                          (12.05, 15.95, [("THEY", (255, 255, 255)), ("BOYCOTTED.", RED)])]:
        if t0 <= t < t1:
            zw.headline(d, lines, 180, t, t0 + 0.05, size=130, gap=140)
            return layer
    return None


def mix(a, b, k):
    return a * (1 - k) + b * k


SCENES = [(0.0, 3.0, scene_hook), (3.0, 8.0, scene_record), (8.0, 12.0, scene_tv),
          (12.0, 16.0, scene_boycott), (16.0, 20.01, scene_reveal)]


def frame(idx):
    t = idx / FPS
    for i, (t0, t1, fn) in enumerate(SCENES):
        if t0 <= t < t1:
            img = fn(t)
            if i + 1 < len(SCENES) and t > t1 - 0.2:
                img = mix(img, SCENES[i + 1][2](t1), smoothstep(t1 - 0.2, t1, t))
            break
    out = grade(img, idx, t)
    if t > 19.75:
        out = out * (1 - smoothstep(19.75, 20.0, t) * 0.85)
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
            Image.frombytes("RGB", (W, H), frame(fi)).save(f"{out}_{fi:03d}.png")
        sys.exit()
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "16",
                           "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    with Pool(int(os.environ.get("JOBS", 4)), initializer=_init) as pool:
        for fb in pool.imap(frame, range(NFRAMES), chunksize=4):
            ff.stdin.write(fb)
    ff.stdin.close()
    ff.wait()
