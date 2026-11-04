"""NO WAY. #7 — He Sold the Eiffel Tower. He Didn't Own It. (Victor Lustig, 1925).
Reuses molasses-flood (grade, captions), zanzibar-war (headline, backgrounds) and rap-grammy (rubber stamp).
All paperwork is a stylized reconstruction; no real document, price or quotation is shown."""
import os
import subprocess
import sys
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
for sub in ("rap-grammy", "zanzibar-war", "molasses-flood"):
    sys.path.insert(0, os.path.join(HERE, "..", sub))
from common import (W, H, FPS, NFRAMES, font, to_img, from_img, cam2d, shake, grade, lerp, smoothstep,
                    ease_in_out, ease_out, ease_out_back)
import render as mf   # captions
import episode as zw  # headline(), dark_bg(), paper_bg(), build_chunks()
import grammy as gm   # stamp()

AMBER = mf.AMBER
RED = (225, 70, 50)
NARR = {"l1": 0.1, "l2": 3.0, "l3": 8.2, "l4": 11.3, "l5": 15.0, "l6": 17.0, "l7": 19.1}
DUR = {"l1": 2.3, "l2": 5.06, "l3": 1.24, "l4": 3.0, "l5": 1.75, "l6": 1.94, "l7": 0.75}
LINES = [
    ("l1", [["NO", "WAY", "SOMEBODY"], ["BOUGHT", "THE"], ["EIFFEL", "TOWER."]]),
    ("l2", [["IN", "1925,"], ["CON", "ARTIST"], ["VICTOR", "LUSTIG"], ["POSED", "AS", "A"], ["GOVERNMENT", "OFFICIAL"],
            ["AND", "SOLD", "IT"], ["FOR", "SCRAP."]]),
    ("l3", [["A", "DEALER", "PAID", "HIM."]]),
    ("l4", [["ACCORDING", "TO", "THE", "STORY,"], ["THE", "BUYER", "WAS"], ["TOO", "EMBARRASSED"], ["TO", "REPORT", "IT."]]),
    ("l5", [["LUSTIG", "EVEN"], ["TRIED", "AGAIN."]]),
    ("l6", [["BRO", "DIDN'T", "OWN"], ["A", "SINGLE", "BOLT."]]),
    ("l7", [["NO", "WAY."]]),
]
zw.LINES, zw.NARR, zw.DUR = LINES, NARR, DUR
zw.SPOKEN = {"1925,": "nineteen twenty five"}
mf.CHUNKS = zw.build_chunks()
mf.KEYWORDS = {"EIFFEL", "TOWER.", "1925,", "LUSTIG", "OFFICIAL", "SCRAP.", "PAID", "EMBARRASSED", "AGAIN.",
               "BOLT.", "WAY."}


# ---------------------------------------------------------------- drawing helpers
def tower(d, cx, by, h, col=(150, 134, 110), line=(205, 190, 165), reveal=1.0, schematic=False):
    """Eiffel Tower: tapering lattice, three platforms, arch, antenna. reveal clips from the bottom up."""
    top = by - h
    clip = by - h * reveal

    def X(y):  # half-width at height y (concave profile)
        u = (by - y) / h
        return h * 0.36 * (1 - u) ** 2.4 + h * 0.012

    ys = np.linspace(by, top + h * 0.06, 80)
    left = [(cx - X(y), y) for y in ys if y >= clip]
    right = [(cx + X(y), y) for y in ys if y >= clip]
    if len(left) < 2:
        return
    if not schematic:
        d.polygon(left + right[::-1], fill=col)
        # arch between the legs
        aw = X(by - h * 0.14) * 0.85
        d.chord([cx - aw, by - h * 0.2, cx + aw, by + h * 0.08], 180, 360, fill=(32, 28, 26))
    else:
        d.line(left, fill=line, width=4)
        d.line(right, fill=line, width=4)
        aw = X(by - h * 0.14) * 0.85
        d.arc([cx - aw, by - h * 0.2, cx + aw, by + h * 0.08], 180, 360, fill=line, width=3)
    # lattice cross-bracing
    for k in range(14):
        y0 = by - h * (0.02 + k * 0.062)
        y1 = y0 - h * 0.062
        if y1 < clip or y1 < top + h * 0.08:
            break
        for s in (-1, 1):
            d.line([(cx + s * X(y0), y0), (cx - s * X(y1) * 0.3 + s * X(y1) * 0.7, y1)], fill=line, width=2)
            d.line([(cx + s * X(y0) * 0.3, y0), (cx + s * X(y1), y1)], fill=line, width=2)
    for u in (0.2, 0.42, 0.8):  # platforms
        y = by - h * u
        if y >= clip:
            w = X(y) + h * 0.03
            d.rectangle([cx - w, y - h * 0.012, cx + w, y + h * 0.008], fill=line if schematic else (45, 40, 36), outline=line)
    if top + h * 0.06 >= clip:
        d.line([(cx, top + h * 0.06), (cx, top)], fill=line, width=5)


def skyline(d, by):
    """1920s Paris rooftops: mansard roofs, chimneys, dormers."""
    x = -20
    k = 0
    while x < W:
        w = 120 + (k * 53) % 90
        hgt = 140 + (k * 37) % 80
        c = (58 + k % 3 * 6, 52, 47)
        d.rectangle([x, by - hgt, x + w, by], fill=c)
        d.polygon([(x - 6, by - hgt), (x + 14, by - hgt - 50), (x + w - 14, by - hgt - 50), (x + w + 6, by - hgt)], fill=(44, 40, 38))
        for dx in range(18, w - 20, 34):
            d.rectangle([x + dx, by - hgt - 36, x + dx + 14, by - hgt - 12], fill=(120, 105, 80))
        d.rectangle([x + w - 30, by - hgt - 85, x + w - 14, by - hgt - 40], fill=(44, 40, 38))
        for wy in range(int(by - hgt + 20), int(by - 20), 40):
            for dx in range(14, w - 14, 30):
                d.rectangle([x + dx, wy, x + dx + 12, wy + 20], fill=(150, 130, 90) if (k + dx + wy) % 7 == 0 else (35, 32, 30))
        x += w + 4
        k += 1


def man(d, cx, by, s=1.0, hat="homburg", facing=1, suitcase=False, col=(150, 136, 118)):
    """Generic 1920s figure silhouette (no likeness)."""
    c = col
    d.polygon([(cx - 75 * s, by), (cx - 85 * s, by - 280 * s), (cx - 60 * s, by - 340 * s),
               (cx + 60 * s, by - 340 * s), (cx + 85 * s, by - 280 * s), (cx + 75 * s, by)], fill=c)        # suit
    d.polygon([(cx - 18 * s, by - 340 * s), (cx + 18 * s, by - 340 * s), (cx, by - 260 * s)], fill=(230, 222, 205))  # shirt
    d.polygon([(cx - 6 * s, by - 330 * s), (cx + 6 * s, by - 330 * s), (cx, by - 270 * s)], fill=(140, 40, 35))     # tie
    d.ellipse([cx - 45 * s, by - 440 * s, cx + 45 * s, by - 340 * s], fill=c)                                     # head
    d.polygon([(cx + 38 * facing * s, by - 400 * s), (cx + 60 * facing * s, by - 385 * s), (cx + 38 * facing * s, by - 372 * s)], fill=c)
    if hat == "homburg":
        d.rectangle([cx - 40 * s, by - 480 * s, cx + 40 * s, by - 425 * s], fill=(40, 36, 34))
        d.ellipse([cx - 68 * s, by - 438 * s, cx + 68 * s, by - 418 * s], fill=(40, 36, 34))
    else:  # flat cap
        d.chord([cx - 50 * s, by - 470 * s, cx + 50 * s, by - 410 * s], 180, 360, fill=(70, 62, 55))
        d.polygon([(cx, by - 440 * s), (cx + 70 * facing * s, by - 432 * s), (cx, by - 425 * s)], fill=(70, 62, 55))
    if suitcase:
        sx = cx + 70 * facing * s
        d.rectangle([sx - 55 * s, by - 160 * s, sx + 55 * s, by - 70 * s], fill=(110, 70, 45), outline=(60, 40, 25), width=4)
        d.rectangle([sx - 18 * s, by - 178 * s, sx + 18 * s, by - 160 * s], outline=(60, 40, 25), width=5)


def papers(d, x, y, rot=0, label=True):
    """Stylized 'official' notice (reconstruction, generic text)."""
    w, h = 420, 300
    d.rectangle([x - w / 2 + 10, y - h / 2 + 12, x + w / 2 + 10, y + h / 2 + 12], fill=(0, 0, 0, 110))
    d.rectangle([x - w / 2, y - h / 2, x + w / 2, y + h / 2], fill=(236, 228, 208), outline=(120, 100, 70), width=4)
    for txt, dy, f in (("OFFICIAL NOTICE", -120, font("oldb", 36)), ("Tour Eiffel", -72, font("playi", 46)),
                       ("SALE FOR SCRAP", -8, font("oldb", 32))):
        tw = d.textlength(txt, font=f)
        d.text((x - tw / 2, y + dy), txt, font=f, fill=(45, 35, 28))
    for k in range(4):
        d.line([(x - 160, y + 50 + k * 22), (x + 160 - (k % 2) * 60, y + 50 + k * 22)], fill=(150, 135, 110), width=3)
    d.ellipse([x + 120, y + 70, x + 180, y + 130], outline=(150, 50, 40), width=4)


def money(d, x, y, n=5):
    for i in range(n):
        d.rounded_rectangle([x - 90 + i * 6, y - 45 - i * 10, x + 90 + i * 6, y + 45 - i * 10], 8,
                            fill=(150, 160, 120), outline=(70, 80, 55), width=3)
        d.ellipse([x - 22 + i * 6, y - 22 - i * 10, x + 22 + i * 6, y + 22 - i * 10], outline=(70, 80, 55), width=3)


def bolt(d, cx, cy, s=1.0):
    g, dk, hi = (150, 145, 135), (80, 76, 70), (210, 205, 195)
    d.polygon([(cx - 110 * s, cy - 60 * s), (cx - 55 * s, cy - 120 * s), (cx + 55 * s, cy - 120 * s),
               (cx + 110 * s, cy - 60 * s), (cx + 55 * s, cy), (cx - 55 * s, cy)], fill=g, outline=dk, width=5)  # hex head
    d.line([(cx - 55 * s, cy - 120 * s), (cx - 110 * s, cy - 60 * s)], fill=hi, width=4)
    d.rectangle([cx - 38 * s, cy, cx + 38 * s, cy + 330 * s], fill=g, outline=dk, width=4)                     # shank
    for k in range(9):
        y = cy + 120 * s + k * 24 * s
        d.line([(cx - 38 * s, y), (cx + 38 * s, y + 12 * s)], fill=dk, width=4)


def base():
    return to_img(zw.DARK).convert("RGBA")


def cam(img, t, seed, amp=2.0, zoom=1.0):
    sx, sy, sr = shake(t, amp, 3, seed=seed)
    return from_img(cam2d(img.convert("RGB"), zoom, W / 2, 900, sr, sx, sy))


# ---------------------------------------------------------------- scenes
SOLD_T = 1.2


def scene_hook(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    tower(d, W / 2, 1180, 780, reveal=ease_out(t / 1.0))
    skyline(d, 1240)
    if t >= SOLD_T:
        gm.stamp(img, "SOLD", W / 2, 860, ease_out((t - SOLD_T) / 0.15), angle=-14, size=170)
    amp = 2 + (16 * np.exp(-(t - SOLD_T) * 10) if t >= SOLD_T else 0)
    return cam(img, t, 1, amp, 1.0 + 0.02 * t / 3)


FAKE_T = 6.5


def desk_scene(t, slide_t0, papers_n=1):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, 960, W, 1260], fill=(92, 62, 42))
    d.rectangle([0, 960, W, 980], fill=(120, 85, 58))
    for k in range(6):
        d.line([(0, 1000 + k * 44), (W, 1010 + k * 44)], fill=(80, 54, 37), width=2)
    return img, d


def scene_desk(t):
    a = t - 3.0
    img, d = desk_scene(t, 4.6)
    man(d, 260, 1000, 1.25, "homburg", 1)                               # con man behind the desk
    p = ease_in_out((t - 4.6) / 1.0)
    papers(d, lerp(330, 680, p), 1080)
    if t >= FAKE_T:
        gm.stamp(img, "FAKE", lerp(330, 680, p), 1080, ease_out((t - FAKE_T) / 0.15), angle=10, size=130)
    amp = 2 + (14 * np.exp(-(t - FAKE_T) * 10) if t >= FAKE_T else 0)
    return cam(img, t, 2, amp, 1.0 + 0.02 * a / 5)


def scene_pay(t):
    a = t - 8.0
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    # tower -> schematic with a scrap tag (the tower itself stays standing)
    k = smoothstep(8.9, 9.6, t)
    d.rectangle([150, 220, W - 150, 860], fill=(int(lerp(26, 40, k)), int(lerp(23, 52, k)), int(lerp(21, 70, k))))
    if k < 1:
        tower(d, W / 2, 830, 560, col=(150, 134, 110, int(255 * (1 - k))))
    if k > 0:
        tower(d, W / 2, 830, 560, line=(200, 215, 230, int(255 * k)), schematic=True)
        for gx in range(170, W - 150, 60):
            d.line([(gx, 230), (gx, 850)], fill=(70, 85, 105, int(120 * k)), width=1)
    if t > 9.6:
        kt = ease_out_back((t - 9.6) / 0.3, 2)
        tx, ty = W / 2 + 150, 520
        d.line([(W / 2 + 40, 470), (tx, ty)], fill=(200, 190, 170), width=3)
        d.polygon([(tx, ty - 40 * kt), (tx + 260 * kt, ty - 40 * kt), (tx + 300 * kt, ty), (tx + 260 * kt, ty + 40 * kt),
                   (tx, ty + 40 * kt)], fill=(230, 215, 170), outline=(120, 100, 60))
        if kt > 0.8:
            d.text((tx + 22, ty - 28), "SCRAP METAL", font=font("anton", 46), fill=(60, 40, 25))
    # dealer hands over money to the con man
    man(d, 200, 1250, 0.9, "homburg", 1)
    man(d, 880, 1250, 0.9, "cap", -1, col=(118, 108, 95))
    p = ease_in_out((t - 8.3) / 1.0)
    money(d, lerp(780, 330, p), 1010 - np.sin(p * np.pi) * 80)
    return cam(img, t, 3, 2, 1.0 + 0.02 * a / 3)


def scene_leave(t):
    a = t - 11.2
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    tower(d, 860, 1150, 520)
    skyline(d, 1240)
    papers(d, 230, 760)
    # dealer glances between the papers (left) and the tower (right)
    facing = 1 if int(a / 0.7) % 2 else -1
    man(d, 520, 1240, 0.95, "cap", facing, col=(118, 108, 95))
    # Lustig walks off with a suitcase
    x = lerp(700, W + 220, ease_in_out((t - 11.8) / 2.4))
    man(d, x, 1240, 0.95, "homburg", 1, suitcase=True)
    return cam(img, t, 4, 2, 1.0 + 0.02 * a / 3.8)


BOLT_T = 17.0


def scene_again(t):
    if t < BOLT_T:
        a = t - 15.0
        img = base()
        d = ImageDraw.Draw(img, "RGBA")
        tower(d, 840, 1150, 560)
        skyline(d, 1240)
        x = lerp(-200, 330, ease_out(a / 0.8))
        man(d, x, 1240, 0.95, "homburg", 1)
        papers(d, x + 210, 960)
        amp = 2 + (12 * np.exp(-(t - 15.9) * 10) if t >= 15.9 else 0)
        return cam(img, t, 5, amp)
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    k = ease_out_back((t - BOLT_T) / 0.35, 2)
    bolt(d, W / 2, 720, 0.9 * k + 0.01)
    f = font("anton", 120)
    al = int(255 * smoothstep(17.3, 17.6, t))
    tw = d.textlength("NOT EVEN HIS", font=f)
    d.text(((W - tw) / 2, 1050), "NOT EVEN HIS", font=f, fill=AMBER + (al,), stroke_width=9, stroke_fill=(0, 0, 0, al))
    if t > 19.0:  # wordmark plate
        k2 = ease_out_back((t - 19.0) / 0.3, 2.5)
        f = font("anton", int(190 * k2) + 1)
        w = d.textlength("NO WAY.", font=f)
        cy = 330
        d.rectangle([W / 2 - 360, cy - 10, W / 2 + 360, cy + 250], fill=(20, 16, 12, int(230 * min(1, k2))))
        d.text((W / 2 - w / 2, cy + 125 - 125 * k2), "NO WAY.", font=f, fill=(245, 236, 215, 255))
        d.rectangle([W / 2 - 240 * k2, cy + 225, W / 2 + 240 * k2, cy + 238], fill=AMBER + (255,))
    return cam(img, t, 6, 2)


def overlay(t):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for t0, t1, lines in [(2.0, 2.95, [("BY WHO?", AMBER)]),
                          (3.05, 7.95, [("PARIS,", (255, 255, 255)), ("1925.", AMBER)]),
                          (11.25, 14.95, [("TOO EMBARRASSED", (255, 255, 255)), ("TO REPORT IT?", AMBER)]),
                          (15.9, 16.95, [("HE TRIED", (255, 255, 255)), ("AGAIN.", RED)])]:
        if t0 <= t < t1:
            sz = 112 if len(lines[0][0]) > 12 else 130
            zw.headline(d, lines, 180, t, t0 + 0.02, size=sz, gap=sz + 10)
            return layer
    return None


def mix(a, b, k):
    return a * (1 - k) + b * k


SCENES = [(0.0, 3.0, scene_hook), (3.0, 8.0, scene_desk), (8.0, 11.2, scene_pay),
          (11.2, 15.0, scene_leave), (15.0, 20.01, scene_again)]


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
