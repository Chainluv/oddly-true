"""NO WAY. long-form — The Great Molasses Flood (~8:20, 1920x1080, 30 fps).
Scenes are keyed to narration paragraphs from timeline.json (written by narrate.py). Reuses the molasses-flood
engines (3D street + wave, tank, aerial map, grade), zanzibar-war (clock), rap-grammy (stamp), eiffel-con (figures).
Usage: python3 long.py out.mp4 [--from SEC --to SEC]   |   python3 long.py prefix --frames N ..."""
import os
os.environ.setdefault("OT_W", "1920")
os.environ.setdefault("OT_H", "1080")
import json  # noqa: E402
import re  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
from multiprocessing import Pool  # noqa: E402

import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
for sub in ("eiffel-con", "rap-grammy", "zanzibar-war", "molasses-flood"):
    sys.path.insert(0, os.path.join(HERE, "..", sub))
from common import (W, H, FPS, NOISE2, tex, font, to_img, from_img, cam2d, shake, grade, lerp, smoothstep,  # noqa: E402
                    ease_in_out, ease_out, ease_out_back)
import street as stt  # noqa: E402
import tank as tk  # noqa: E402
import aerial as ae  # noqa: E402
import episode as zw  # noqa: E402  draw_clock, dark_bg, paper_bg
import grammy as gm  # noqa: E402  stamp
import eiffel as ef  # noqa: E402  man

TL = json.load(open(os.path.join(HERE, "timeline.json")))
DURATION = TL["duration"]
NFR = int(DURATION * FPS)
PARA = {p["id"]: p for p in TL["paragraphs"]}
ORDER = [p["id"] for p in TL["paragraphs"]]
STARTS = [p["start"] for p in TL["paragraphs"]]
SEC = TL["sections"]
CHAPTERS = TL.get("chapters", [])

AMBER, RED, CREAM = (255, 184, 64), (210, 60, 45), (238, 226, 206)
INK = (40, 32, 26)
MOL = (40, 20, 8)
DARK = None
AERIAL = None


# ---------------------------------------------------------------- helpers
def base():
    return to_img(DARK).convert("RGBA")


def T(d, txt, x, y, size, col=CREAM, a=255, anchor="mm", f="anton", stroke=0):
    fn = font(f, size)
    d.text((x, y), txt, font=fn, fill=col + (a,), anchor=anchor, stroke_width=stroke, stroke_fill=(10, 8, 6, a))


def card(d, x, y, w, h, a=255, fill=(22, 18, 15), outline=CREAM):
    d.rounded_rectangle([x - w / 2, y - h / 2, x + w / 2, y + h / 2], 18, fill=fill + (int(a * 0.92),), outline=outline + (a,), width=4)


def fade_in(local, t0, dur=0.4):
    return smoothstep(t0, t0 + dur, local)


def cam(img, t, seed, amp=0.6, zoom=1.0, cx=W / 2, cy=H / 2):
    sx, sy, sr = shake(t, amp, 1.5, seed=seed)
    if isinstance(img, np.ndarray):
        img = to_img(img)
    return from_img(cam2d(img.convert("RGB"), zoom, cx, cy, sr, sx, sy))


def sentence_t(pid, i):
    """Start time of sentence i of paragraph pid (absolute)."""
    s = PARA[pid]["sentences"]
    return s[min(i, len(s) - 1)][0]


# ---------------------------------------------------------------- street engine shots (landscape)
def street(t, wave_z=None, cam_z=0.0, wave_h=30, flood_h=None, flood_front=None, ch=5.0, yh=640, f=900,
           collapsed=None, el_gap=None, sprites=None, spray=False, fog=380, camX=-3.0, flood_speed=30):
    st = stt.Street(f=f, yh=yh, ch=ch, camX=camX, camZ=cam_z, time=t, wave_z=wave_z, wave_h=wave_h, flood_h=flood_h,
                    flood_front=flood_front, flood_speed=flood_speed, el_gap=el_gap, collapsed=collapsed or [], fog=fog)
    img = st.render()
    if sprites:
        img = stt.draw_sprites(img, st, sprites)
    if spray and wave_z is not None:
        img = stt.draw_spray(img, st, n=110)
    return img


PEOPLE = [dict(kind=0, X=-19, Z=40, h=5.8), dict(kind=1, X=-21, Z=55, h=5.6), dict(kind="cart", X=-6, Z=72, h=6.5),
          dict(kind=2, X=8, Z=36, h=5.8), dict(kind=0, X=20, Z=90, h=5.8), dict(kind=1, X=-20, Z=115, h=5.6),
          dict(kind=2, X=12, Z=60, h=5.8)]


def bw_photo(img_arr, local, push=0.06, label=None):
    """Turn a render into an aged black-and-white 'photo' print with a border."""
    g = img_arr.mean(axis=2, keepdims=True)
    g = np.clip((g - 0.5) * 1.15 + 0.5, 0, 1)
    tone = g * np.array([1.0, 0.97, 0.9], np.float32)
    im = to_img(tone)
    im = cam2d(im, 1.0 + push * local / 10, W / 2, H / 2)
    canvas = Image.new("RGB", (W, H), (20, 18, 16))
    shrink = im.resize((int(W * 0.8), int(H * 0.8)))
    canvas.paste((225, 216, 196), [int(W * 0.1) - 18, int(H * 0.1) - 18, int(W * 0.9) + 18, int(H * 0.9) + 18])
    canvas.paste(shrink, (int(W * 0.1), int(H * 0.1)))
    if label:
        d = ImageDraw.Draw(canvas)
        d.text((W * 0.1, H * 0.1 - 58), label, font=font("oldi", 30), fill=(170, 160, 140))
    return from_img(canvas)


# ---------------------------------------------------------------- reusable illustrations
def map_scene(t, local, show_tank=0.0, zoom=1.0, people=True):
    img = to_img(zw.paper_bg(6, (0.84, 0.78, 0.64))).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    shore = [(1280, 0), (1220, 200), (1300, 420), (1240, 640), (1330, 860), (1290, 1080)]
    d.polygon(shore + [(W, H), (W, 0)], fill=(150, 170, 178))
    d.line(shore, fill=(70, 60, 50), width=5)
    for i in range(6):  # wharves
        y = 120 + i * 160
        d.rectangle([1260, y, 1520, y + 50], fill=(170, 150, 120), outline=(70, 60, 50), width=3)
    rng = np.random.default_rng(4)
    for bx in range(0, 9):  # crowded tenement blocks
        for by in range(0, 7):
            x0, y0 = 120 + bx * 125 + (by % 2) * 18, 80 + by * 140
            if x0 > 1150:
                continue
            d.rectangle([x0, y0, x0 + 100, y0 + 112], fill=(150, 122, 100), outline=(90, 74, 60), width=2)
            if people:
                for k in range(3):
                    hx, hy = x0 + 18 + k * 30, y0 + 30 + rng.integers(0, 50)
                    d.rectangle([hx, hy, hx + 14, hy + 14], fill=(110, 86, 70))
    d.line([(1215, 0), (1170, 300), (1210, 560), (1160, 820), (1200, 1080)], fill=(210, 200, 175), width=34)  # Commercial St
    T(d, "COMMERCIAL ST.", 1110, 470, 30, (70, 60, 50), f="oldb", anchor="mm")
    T(d, "NORTH END", 560, 70, 64, (70, 52, 40), f="oldb")
    T(d, "BOSTON HARBOR", 1660, 980, 44, (60, 80, 90), f="oldi")
    if show_tank > 0:
        k = ease_out_back(show_tank, 2)
        tx, ty, r = 1150, 600, 60 * k
        d.ellipse([tx - r, ty - r, tx + r, ty + r], fill=(80, 70, 62), outline=RED, width=6)
        T(d, "TANK", tx, ty + r + 30, 34, RED, f="oswald")
    return cam(img, t, 11, 0.3, zoom, cx=lerp(W / 2, 1150, (zoom - 1) / 1.5 if zoom > 1 else 0),
               cy=lerp(H / 2, 600, (zoom - 1) / 1.5 if zoom > 1 else 0))


def tank_shot(t, ttime, zoom=0.62, cxw=540, cyw=1000, amp=0.0):
    img = tk.render(ttime, zoom=zoom, cxw=cxw, cyw=cyw)
    return cam(img, t, 12, amp)


def cross_section(d, cx, cy, w, h, fill, cold=0.0, warm=0.0, pressure=0.0, t=0.0):
    """Cutaway of the tank: molasses level, cold/warm layers, pressure arrows, strained rivets."""
    bulge = 18 * pressure * (0.8 + 0.2 * np.sin(t * 4))
    d.rounded_rectangle([cx - w / 2 - bulge, cy - h / 2, cx + w / 2 + bulge, cy + h / 2], 20, outline=CREAM, width=8)
    top = cy + h / 2 - h * fill
    if cold > 0:
        d.rectangle([cx - w / 2 + 6 - bulge, top + h * fill * 0.4, cx + w / 2 - 6 + bulge, cy + h / 2 - 6], fill=(50, 40, 60, 255))
        d.rectangle([cx - w / 2 + 6 - bulge, top, cx + w / 2 - 6 + bulge, top + h * fill * 0.4], fill=(110, 60, 20, int(255 * warm)) if warm > 0 else MOL + (255,))
        if warm <= 0:
            d.rectangle([cx - w / 2 + 6 - bulge, top, cx + w / 2 - 6 + bulge, cy + h / 2 - 6], fill=(50, 40, 60, 255))
    else:
        d.rectangle([cx - w / 2 + 6 - bulge, top, cx + w / 2 - 6 + bulge, cy + h / 2 - 6], fill=MOL + (255,))
    for k in range(7):  # rivet rows
        y = cy - h / 2 + 20 + k * (h - 40) / 6
        for sx in (-1, 1):
            hot = pressure > 0.5 and (k + int(t * 3)) % 3 == 0
            x = cx + sx * (w / 2 + bulge)
            d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=(255, 90, 60) if hot else (170, 160, 150))
    if pressure > 0:
        for k in range(5):
            y = cy - h / 3 + k * h / 6
            L = 70 * pressure
            for sx in (-1, 1):
                x0 = cx + sx * (w / 2 - 80)
                d.line([(x0, y), (x0 + sx * L, y)], fill=AMBER, width=8)
                d.polygon([(x0 + sx * L, y - 16), (x0 + sx * (L + 26), y), (x0 + sx * L, y + 16)], fill=AMBER)


def thermometer(d, x, y, h, frac, label_lo, label_hi, a=255):
    d.rounded_rectangle([x - 26, y - h, x + 26, y], 26, outline=CREAM + (a,), width=6)
    d.ellipse([x - 48, y - 20, x + 48, y + 76], outline=CREAM + (a,), width=6, fill=(200, 60, 40, a))
    d.rectangle([x - 12, y - h * frac, x + 12, y + 10], fill=(200, 60, 40, a))
    for k in range(6):
        yy = y - 20 - k * (h - 40) / 5
        d.line([(x + 30, yy), (x + 52, yy)], fill=CREAM + (a,), width=4)
    T(d, label_lo, x + 70, y - 20, 34, CREAM, a, anchor="lm", f="oswald")
    T(d, label_hi, x + 70, y - h + 20, 34, CREAM, a, anchor="lm", f="oswald")


def icon_barrel(d, x, y, s=1.0, col=(120, 80, 50)):
    d.rounded_rectangle([x - 60 * s, y - 80 * s, x + 60 * s, y + 80 * s], 30 * s, fill=col, outline=CREAM, width=5)
    for k in (-40, 0, 40):
        d.line([(x - 58 * s, y + k * s), (x + 58 * s, y + k * s)], fill=(70, 50, 34), width=5)


def icon_flask(d, x, y, s=1.0):
    d.polygon([(x - 22 * s, y - 80 * s), (x + 22 * s, y - 80 * s), (x + 22 * s, y - 30 * s), (x + 70 * s, y + 70 * s),
               (x - 70 * s, y + 70 * s), (x - 22 * s, y - 30 * s)], outline=CREAM, width=5, fill=(60, 80, 90))
    d.polygon([(x - 50 * s, y + 30 * s), (x + 50 * s, y + 30 * s), (x + 68 * s, y + 68 * s), (x - 68 * s, y + 68 * s)], fill=(170, 200, 210))


def icon_shell(d, x, y, s=1.0):
    d.rectangle([x - 34 * s, y - 20 * s, x + 34 * s, y + 80 * s], fill=(170, 140, 70), outline=CREAM, width=4)
    d.chord([x - 34 * s, y - 110 * s, x + 34 * s, y + 10 * s], 180, 360, fill=(120, 110, 100), outline=CREAM, width=4)


def arrow(d, x0, x1, y, a=255, col=AMBER):
    d.line([(x0, y), (x1 - 30, y)], fill=col + (a,), width=10)
    d.polygon([(x1 - 40, y - 24), (x1, y), (x1 - 40, y + 24)], fill=col + (a,))


def calendar(d, x, y, month, day, a=255, flip=0.0):
    d.rounded_rectangle([x - 190, y - 220, x + 190, y + 220], 26, fill=(236, 228, 210, a))
    d.rounded_rectangle([x - 190, y - 220, x + 190, y - 100], 26, fill=RED + (a,))
    T(d, month, x, y - 160, 64, CREAM, a)
    T(d, day, x, y + 50, 190, INK, a)
    if flip > 0:
        d.polygon([(x - 190, y - 100), (x + 190, y - 100), (x + 190 - 60 * flip, y - 100 + 320 * (1 - flip)),
                   (x - 190 + 60 * flip, y - 100 + 320 * (1 - flip))], fill=(250, 245, 232, int(a * (1 - flip))))


def courtroom(d):
    d.rectangle([0, 0, W, H], fill=(46, 36, 30))
    for x in range(0, W, 160):
        d.rectangle([x + 10, 60, x + 140, 560], fill=(56, 44, 36), outline=(70, 56, 46), width=3)
    d.rectangle([560, 520, 1360, 760], fill=(92, 64, 44), outline=(130, 96, 66), width=6)  # bench
    d.rectangle([600, 470, 1320, 520], fill=(110, 78, 54))
    ef.man(d, 960, 520, 0.55, "homburg", 1, col=(40, 34, 30))  # judge silhouette behind the bench
    d.rectangle([0, 760, W, H], fill=(60, 46, 36))
    for i in range(10):  # gallery rows
        d.rectangle([60 + i * 185, 880, 210 + i * 185, 1000], fill=(78, 58, 44))


def figure_grid(d, n, x0, y0, cols, cell, a=255, col=CREAM):
    for i in range(n):
        x, y = x0 + (i % cols) * cell, y0 + (i // cols) * cell
        d.ellipse([x - cell * 0.16, y - cell * 0.42, x + cell * 0.16, y - cell * 0.1], fill=col + (a,))
        d.rounded_rectangle([x - cell * 0.26, y - cell * 0.08, x + cell * 0.26, y + cell * 0.36], int(cell * 0.12), fill=col + (a,))


def park(d, t):
    d.rectangle([0, 0, W, 520], fill=(150, 170, 185))
    for i, (x, h) in enumerate(((80, 260), (260, 360), (420, 300), (1500, 420), (1680, 300), (1820, 380))):
        d.rectangle([x, 520 - h, x + 140, 520], fill=(110, 120, 132))
        for wy in range(520 - h + 20, 500, 40):
            for wx in range(x + 16, x + 130, 34):
                d.rectangle([wx, wy, wx + 14, wy + 20], fill=(170, 185, 200))
    d.rectangle([0, 520, W, H], fill=(86, 128, 70))
    d.polygon([(960, 600), (1360, 800), (960, 1000), (560, 800)], fill=(170, 130, 90))  # infield
    d.polygon([(960, 640), (1280, 800), (960, 960), (640, 800)], fill=(96, 140, 76))
    for bx, by in ((960, 640), (1280, 800), (960, 960), (640, 800)):
        d.rectangle([bx - 14, by - 14, bx + 14, by + 14], fill=(240, 240, 235))
    # the small plaque most people walk past
    d.rectangle([1640, 860, 1650, 940], fill=(60, 60, 60))
    d.rectangle([1600, 820, 1690, 870], fill=(120, 100, 60), outline=(200, 180, 120), width=3)
    for i, x in enumerate((1300, 1460)):  # walkers passing the plaque
        xx = x + ((t * 40 + i * 200) % 500) - 250
        ef.man(d, xx, 1020, 0.38, "cap" if i else "homburg", 1, col=(60, 66, 60))


# ---------------------------------------------------------------- per-paragraph scenes
def s_c1(t, L):
    img = street(t, None, cam_z=-L * 1.2, sprites=[dict(s, Z=s["Z"] - L * 0.8) for s in PEOPLE])
    return bw_photo(img, L, 0.08, "Boston, January 15, 1919 — illustration")


def s_c2(t, L):
    T0 = sentence_t("c2", 2) - PARA["c2"]["start"]
    if L < T0:
        img = street(t, None, cam_z=-L, sprites=PEOPLE)
        out = cam(img, t, 2, 1.0 + 12 * smoothstep(T0 - 2.2, T0 - 1.6, L) * np.exp(-max(0, L - (T0 - 1.6)) * 2))
        return out
    a = L - T0
    wz = 140 * (1 - (a / 6.5) ** 1.2) + 4
    img = street(t, wz, cam_z=-a * 3, wave_h=30, sprites=PEOPLE, spray=True)
    return cam(img, t, 2, 3 + 8 * smoothstep(3, 6, a))


def s_c3(t, L):
    img = street(t, None, flood_h=3.0, flood_front=None, flood_speed=8, ch=4.0, yh=560)
    out = cam(img, t, 3, 0.4, 1.0 + 0.04 * L / 6)
    return out


def s_title(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    k = ease_out_back(L / 0.4, 2.4)
    T(d, "NO WAY.", W / 2, 430, int(230 * min(1.1, k)) + 1, CREAM)
    a = int(255 * fade_in(L, 0.5))
    d.rectangle([W / 2 - 300 * k, 560, W / 2 + 300 * k, 570], fill=RED + (255,))
    T(d, "THE GREAT MOLASSES FLOOD", W / 2, 650, 86, AMBER, a)
    T(d, "BOSTON • 1919", W / 2, 750, 46, (200, 190, 170), a, f="oswald")
    return cam(img, t, 4, 0.3)


def s_chapter(t, L, title, n):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    a = int(255 * fade_in(L, 0.0, 0.35) * (1 - smoothstep(2.25, 2.6, L)))
    T(d, f"PART {n}", W / 2, 440, 48, RED, a, f="oswald")
    T(d, title, W / 2, 540, 140, CREAM, a)
    w = 260 * ease_out(L / 0.6)
    d.rectangle([W / 2 - w, 640, W / 2 + w, 648], fill=AMBER + (a,))
    return cam(img, t, 5, 0.2, 1.0 + 0.02 * L)


def s_t1(t, L):
    out = map_scene(t, L, 0.0, 1.0 + 0.05 * L / 10)
    img = to_img(out).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    a = int(255 * fade_in(L, sentence_t("t1", 0) - PARA["t1"]["start"] + 3.0))
    card(d, 560, 850, 860, 110, a)
    T(d, "ITALIAN & IRISH IMMIGRANT FAMILIES", 560, 850, 52, CREAM, a)
    return from_img(img)


def s_t2(t, L):
    s1 = sentence_t("t2", 1) - PARA["t2"]["start"]
    if L < s1:
        return map_scene(t, L, smoothstep(0.5, 1.5, L), lerp(1.0, 2.2, ease_in_out((L - 1.0) / (s1 - 1.0))))
    a = L - s1
    out = tank_shot(t, 3.0, zoom=0.66 + 0.02 * a / 8, cyw=1000)
    img = to_img(out).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    k = fade_in(a, 0.3)
    al = int(255 * k)
    # dimension markers (tank spans world 20..1060 x, 260..1640 y; screen via zoom ~0.66 around (540,1000))
    z = 0.66 + 0.02 * a / 8

    def S(xw, yw):
        return ((xw - 540) * z + W / 2, (yw - 1000) * z + H / 2)
    x0, y0 = S(20, 1640)
    x1, y1 = S(1060, 260)
    d.line([(x1 + 40, y1), (x1 + 40, y0)], fill=AMBER + (al,), width=6)
    T(d, "50 FT", x1 + 60, (y0 + y1) / 2, 64, AMBER, al, anchor="lm")
    d.line([(x0, y0 + 30), (x1, y0 + 30)], fill=AMBER + (al,), width=6)
    T(d, "90 FT ACROSS", (x0 + x1) / 2, y0 + 30 + 10, 50, AMBER, al, anchor="mt") if y0 + 90 < H else None
    k2 = int(255 * fade_in(a, 3.0))
    card(d, 330, 220, 560, 170, k2)
    T(d, "PURITY DISTILLING CO.", 330, 190, 50, CREAM, k2)
    T(d, "part of United States Industrial Alcohol", 330, 250, 30, (200, 190, 170), k2, f="oldi")
    return from_img(img)


def s_t3(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    xs = [420, 960, 1500]
    labels = ["MOLASSES", "INDUSTRIAL ALCOHOL", "WWI MUNITIONS"]
    for i, (x, lab) in enumerate(zip(xs, labels)):
        k = fade_in(L, 1.0 + i * 2.2)
        if k <= 0:
            continue
        a = int(255 * k)
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer, "RGBA")
        [icon_barrel, icon_flask, icon_shell][i](ld, x, 470, 1.4)
        layer.putalpha(layer.getchannel("A").point(lambda v: int(v * k)))
        img.alpha_composite(layer)
        T(d, lab, x, 690, 50, CREAM, a)
        if i < 2:
            arrow(d, x + 150, xs[i + 1] - 150, 470, int(255 * fade_in(L, 2.0 + i * 2.2)))
    T(d, "FERMENT", 690, 420, 34, AMBER, int(255 * fade_in(L, 2.0)), f="oswald")
    pk = fade_in(L, PARA["t3"]["dur"] - 2.4)
    if pk > 0:
        card(d, W / 2, 880, 640, 120, int(255 * pk), outline=AMBER)
        T(d, "VERY PROFITABLE", W / 2, 880, 72, AMBER, int(255 * pk))
    return cam(img, t, 6, 0.3, 1.0 + 0.02 * L / 10)


def s_t4(t, L):
    s2 = sentence_t("t4", 3) - PARA["t4"]["start"]
    img = Image.new("RGBA", (W, H), (26, 50, 92, 255))
    d = ImageDraw.Draw(img, "RGBA")
    for x in range(0, W, 60):
        d.line([(x, 0), (x, H)], fill=(60, 90, 140), width=1)
    for y in range(0, H, 60):
        d.line([(0, y), (W, y)], fill=(60, 90, 140), width=1)
    rot = 180 * smoothstep(4.5, 6.0, L) if L < s2 else 180
    bp = Image.new("RGBA", (900, 700), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bp)
    bd.rectangle([200, 120, 700, 620], outline=(220, 235, 255), width=6)
    bd.ellipse([200, 80, 700, 160], outline=(220, 235, 255), width=6)
    for k in range(6):
        bd.line([(200, 180 + k * 80), (700, 180 + k * 80)], fill=(160, 190, 230), width=2)
    bd.line([(120, 120), (120, 620)], fill=(220, 235, 255), width=3)
    bd.text((40, 340), "50'", font=font("oswald", 40), fill=(220, 235, 255))
    bd.text((400, 640), "TANK — 1915", font=font("oswald", 34), fill=(220, 235, 255))
    bp = bp.rotate(rot, resample=Image.BICUBIC)
    img.alpha_composite(bp, (1000, 200))
    ef.man(d, 520, 940, 1.0, "homburg", 1, col=(30, 34, 46))
    a = int(255 * fade_in(L, 1.5))
    card(d, 520, 140, 820, 150, a)
    T(d, "COMPANY TREASURER", 520, 115, 56, CREAM, a)
    T(d, "no engineering background", 520, 172, 32, (200, 190, 170), a, f="oldi")
    if L > s2 + 0.3:
        gm.stamp(img, "NEVER WATER-TESTED", W / 2 + 200, 560, ease_out((L - s2 - 0.3) / 0.15), angle=-6, size=96)
    amp = 0.3 + (10 * np.exp(-(L - s2 - 0.3) * 8) if L > s2 + 0.3 else 0)
    return cam(img, t, 7, amp)


def s_t5(t, L):
    return tank_shot(t, 3.2, zoom=1.6 - 0.1 * L / 3, cxw=520, cyw=1100, amp=0.4)


def s_t6(t, L):
    s2 = sentence_t("t6", 2) - PARA["t6"]["start"]
    s3 = sentence_t("t6", 3) - PARA["t6"]["start"]
    if L < s2:
        out = tank_shot(t, 3.2, zoom=0.9, cxw=540, cyw=1350, amp=0.3 + 4 * smoothstep(s2 - 4.5, s2 - 3.5, L) * (L < s2 - 1.5))
        img = to_img(out).convert("RGBA")
        d = ImageDraw.Draw(img, "RGBA")
        for i, x in enumerate((360, 520, 1400, 1560)):  # neighbours collecting molasses
            ef.man(d, x, 1040, 0.55, "cap" if i % 2 else "homburg", 1 if x < 960 else -1, col=(50, 44, 40))
            bx = x + (40 if x < 960 else -40)
            d.polygon([(bx - 26, 960), (bx + 26, 960), (bx + 20, 1010), (bx - 20, 1010)], fill=(120, 120, 126), outline=(200, 200, 205))
        return from_img(img)
    # the fix: paint it brown
    out = tank_shot(t, 3.2, zoom=0.7, cxw=540, cyw=1000)
    img = to_img(out).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    k = smoothstep(s3 - 0.3, s3 + 3.0, L)
    left, right = W / 2 - 520 * 0.7, W / 2 + 520 * 0.7
    px = lerp(left, right, k)
    d.rectangle([left, 160, px, 980], fill=(92, 54, 30, 215))
    d.rectangle([px - 10, 380, px + 30, 640], fill=(200, 190, 170))  # roller
    d.line([(px + 10, 640), (px + 10, 900)], fill=(120, 90, 60), width=12)
    a = int(255 * fade_in(L, s3))
    card(d, W / 2, 110, 760, 120, a, outline=RED)
    T(d, "PAINTED BROWN", W / 2, 110, 80, CREAM, a)
    return from_img(img)


def s_s1(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    s1 = sentence_t("s1", 2) - PARA["s1"]["start"]
    if L < s1:
        flip = (L * 2.0) % 1.0 if L < 3.0 else 0.0
        mo = ["OCT", "NOV", "DEC", "JAN"][min(3, int(L * 2.0) // 2)] if L < 3.0 else "JAN"
        calendar(d, 560, 540, mo + (" 1918" if mo != "JAN" else " 1919"), "15" if mo == "JAN" else "", 255, flip)
        a = int(255 * fade_in(L, 3.4))
        T(d, "WAR: OVER", 1300, 420, 90, CREAM, a)
        T(d, "NEXT THREAT:", 1300, 560, 60, (200, 190, 170), int(255 * fade_in(L, 4.6)))
        T(d, "PROHIBITION", 1300, 660, 110, RED, int(255 * fade_in(L, 5.2)))
        return cam(img, t, 8, 0.3)
    a = int(255 * fade_in(L, s1))
    T(d, "AMENDMENT BANNING ALCOHOL", W / 2, 300, 72, CREAM, a)
    T(d, "ABOUT TO BE RATIFIED", W / 2, 400, 90, RED, a)
    # hourglass: time running out to make alcohol
    hx, hy = W / 2, 720
    d.polygon([(hx - 140, hy - 200), (hx + 140, hy - 200), (hx + 12, hy), (hx + 140, hy + 200), (hx - 140, hy + 200), (hx - 12, hy)], outline=CREAM, width=6)
    p = smoothstep(s1, PARA["s1"]["dur"], L)
    top = hy - 200 + 380 * p * 0.5
    d.polygon([(hx - 140 * (1 - p * 0.6), top), (hx + 140 * (1 - p * 0.6), top), (hx + 10, hy - 8), (hx - 10, hy - 8)], fill=AMBER)
    d.polygon([(hx - 140, hy + 200), (hx + 140, hy + 200), (hx + 60 * p, hy + 200 - 160 * p), (hx - 60 * p, hy + 200 - 160 * p)], fill=AMBER)
    d.line([(hx, hy), (hx, hy + 200)], fill=AMBER, width=4)
    return cam(img, t, 8, 0.3)


def s_s2(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    fill = lerp(0.2, 0.92, ease_out(L / 2.5))
    cross_section(d, 700, 560, 520, 700, fill)
    k = fade_in(L, 1.2)
    T(d, "2.3 MILLION", 1380, 470, 120, AMBER, int(255 * k))
    T(d, "GALLONS", 1380, 600, 90, CREAM, int(255 * k))
    T(d, "CLOSE TO FULL", 1380, 700, 44, (200, 190, 170), int(255 * fade_in(L, 2.0)), f="oswald")
    return cam(img, t, 9, 0.3)


def s_s3(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    s3 = sentence_t("s3", 3) - PARA["s3"]["start"]
    if L < s3:
        # temperature: near zero, then past 40 on the 15th (illustrative curve)
        x0, x1, yb = 300, 1300, 860
        d.line([(x0, yb), (x1, yb)], fill=(120, 110, 100), width=4)
        d.line([(x0, yb), (x0, 260)], fill=(120, 110, 100), width=4)
        for v, lab in ((0, "0°F"), (40, "40°F")):
            y = yb - v * 12
            d.line([(x0 - 14, y), (x1, y)], fill=(80, 72, 66), width=2)
            T(d, lab, x0 - 30, y, 34, CREAM, anchor="rm", f="oswald")
        p = smoothstep(1.5, s3 - 0.6, L)
        pts = []
        for i in range(60):
            s = i / 59
            if s > p:
                break
            v = 3 + 2 * np.sin(s * 9) if s < 0.6 else lerp(3, 43, smoothstep(0.6, 0.95, s))
            pts.append((lerp(x0, x1, s), yb - v * 12))
        if len(pts) > 1:
            d.line(pts, fill=RED, width=8)
        T(d, "DAYS BEFORE", 520, 905, 40, (190, 180, 160), f="oswald")
        T(d, "JAN. 15", 1180, 905, 40, AMBER, f="oswald")
        thermometer(d, 1620, 820, 520, lerp(0.12, 0.8, smoothstep(s3 * 0.6, s3 - 0.6, L)), "COLD", "WARM")
        T(d, "ILLUSTRATIVE", 300, 220, 30, (160, 150, 135), f="oswald", anchor="lm")
        return cam(img, t, 10, 0.3)
    a = L - s3
    cross_section(d, 760, 560, 520, 700, 0.92, cold=1.0, warm=smoothstep(0.3, 2.0, a), t=t)
    d.line([(1020, 160), (1200, 160), (1200, 60)], fill=(150, 140, 130), width=22)  # fill pipe
    T(d, "WARMER MOLASSES", 1420, 330, 64, AMBER, int(255 * fade_in(a, 0.6)))
    T(d, "ON TOP OF", 1420, 430, 44, CREAM, int(255 * fade_in(a, 1.2)), f="oswald")
    T(d, "COLD MOLASSES", 1420, 530, 64, (170, 160, 210), int(255 * fade_in(a, 1.6)))
    return cam(img, t, 10, 0.3)


def s_s4(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    p = smoothstep(0.0, PARA["s4"]["dur"], L)
    cross_section(d, 760, 560, 520, 700, 0.92, pressure=p, t=t)
    for i, w in enumerate(["EXPANDS", "FERMENTS", "PRESSURE"]):
        T(d, w, 1480, 360 + i * 130, 90, [CREAM, AMBER, RED][i], int(255 * fade_in(L, 0.3 + i * 1.3)))
    k = fade_in(L, PARA["s4"]["dur"] * 0.55)
    T(d, "STEEL TOO THIN • RIVETS FAILING", W / 2, 1000, 44, CREAM, int(255 * k), f="oswald")
    return cam(img, t, 13, 0.3 + 2.5 * p * (0.5 + 0.5 * np.sin(t * 7)) * 0.4)


def s_w1(t, L):
    img = base().convert("RGB")
    m = 20 + 10 * smoothstep(0.2, 2.6, L)
    zw.draw_clock(img, W / 2, 560, 300, m * 6, 12 * 30 + m * 0.5)
    img = img.convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    T(d, "12:30 PM", 1500, 560, 96, AMBER, int(255 * fade_in(L, 2.6)))
    return cam(img, t, 14, 0.3 + (10 * np.exp(-(L - 3.0) * 6) if L > 3.0 else 0))


def s_w2(t, L):
    s1 = sentence_t("w2", 1) - PARA["w2"]["start"]
    # tank.render's internal clock: cracks 3.7->5.1 burst; map the rivet sentence onto it
    ttime = 3.0 + (L / max(1e-3, s1 + 0.6)) * 2.1 if L < s1 + 0.6 else 5.1 + (L - s1 - 0.6) * 0.5
    out = tank_shot(t, ttime, zoom=0.75 + 0.15 * ease_in_out(L / (s1 + 0.6)), cyw=1150, amp=1 + 6 * smoothstep(s1 * 0.6, s1, L))
    img = to_img(out).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    if L > s1 + 1.2:
        a = int(255 * fade_in(L, s1 + 1.2))
        card(d, W / 2, 140, 720, 130, a, outline=AMBER)
        T(d, "~13,000 TONS", W / 2, 140, 90, AMBER, a)
    if ttime >= 5.1 and ttime < 5.25:
        d.rectangle([0, 0, W, H], fill=(255, 245, 225, int(200 * (1 - (ttime - 5.1) / 0.15))))
    return from_img(img)


def s_w3(t, L):
    s2 = sentence_t("w3", 3) - PARA["w3"]["start"]
    if L < s2:
        img = base()
        d = ImageDraw.Draw(img, "RGBA")
        k = ease_out(L / 1.2)
        d.rectangle([520, 860 - 400 * k, 760, 860], fill=(120, 160, 190))
        d.rectangle([1160, 860 - 560 * k, 1400, 860], fill=MOL)
        T(d, "WATER", 640, 920, 48, CREAM)
        T(d, "MOLASSES", 1280, 920, 48, CREAM)
        T(d, "~40% HEAVIER", W / 2, 200, 100, AMBER, int(255 * fade_in(L, 1.0)))
        T(d, "same volume, compared", W / 2, 1010, 30, (170, 160, 140), f="oldi")
        return cam(img, t, 15, 0.3)
    a = L - s2
    wz = 120 - a * 16
    img = street(t, wz, cam_z=-a * 2, wave_h=25, spray=True, ch=4.5)
    out = cam(img, t, 15, 2 + 4 * smoothstep(2, 6, a))
    pil = to_img(out).convert("RGBA")
    d = ImageDraw.Draw(pil, "RGBA")
    card(d, 330, 130, 520, 150, 255, outline=AMBER)
    T(d, "~25 FT HIGH", 330, 112, 64, AMBER)
    T(d, "estimates vary", 330, 168, 30, (200, 190, 170), f="oldi")
    al = int(255 * fade_in(a, 2.5))
    card(d, W - 330, 130, 440, 120, al, outline=AMBER)
    T(d, "~35 MPH", W - 330, 130, 76, AMBER, al)
    return from_img(pil)


def s_w4(t, L):
    s2 = sentence_t("w4", 3) - PARA["w4"]["start"]
    s4 = sentence_t("w4", 4) - PARA["w4"]["start"]
    if L < s2:  # flattened buildings, el wrecked, firehouse shoved
        img = street(t, None, flood_h=2.0, flood_speed=20, el_gap=(45, 85), collapsed=[(1, 1), (0, 3)], fog=300,
                     camX=lerp(-5, 2, L / s2), cam_z=L)
        img = stt.draw_beam(img, stt.Street(f=900, yh=640, ch=5.0, camX=lerp(-5, 2, L / s2), camZ=L),
                            (15 - 7, 17, 45, 6), (15 - 4, 0.5, 70), 1.3)
        return cam(img, t, 16, 1.0)
    if L < s4:  # wagons, horses, people swept away (distant, non-graphic)
        a = L - s2
        sp = [dict(kind="cart", X=-4 + a * 2, Z=60 - a * 6, h=6.5, Y=-1.0), dict(kind="plank", X=4, Z=50 - a * 9, h=7, ang=a, Y=1.5),
              dict(kind="plank", X=-10, Z=70 - a * 8, h=8, ang=-a, Y=1.5)]
        img = street(t, 30 - a * 4, flood_h=4.0, flood_front=None, wave_h=12, sprites=sp, ch=5.5, flood_speed=40)
        return cam(img, t, 16, 4.0)
    # the firehouse rescue: cutting through floorboards (illustration)
    a = L - s4
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, 760, W, H], fill=MOL)
    fh = Image.new("RGBA", (700, 560), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fh)
    fd.rectangle([40, 80, 660, 540], fill=(140, 100, 74), outline=(80, 56, 42), width=6)
    fd.rectangle([250, 300, 450, 540], fill=(40, 32, 28))
    fd.text((200, 110), "FIREHOUSE", font=font("oswald", 70), fill=CREAM)
    fh = fh.rotate(-9, resample=Image.BICUBIC, expand=True)
    img.alpha_composite(fh, (520, 250))
    for i, x in enumerate((420, 1500)):
        ef.man(d, x, 900, 0.7, "cap", 1 if x < 960 else -1, col=(50, 46, 42))
        sx = x + (60 if x < 960 else -60)
        d.line([(sx, 760), (sx + 30 * np.sin(t * 10 + i), 860)], fill=(200, 200, 205), width=8)  # saw
    for k in range(8):
        d.line([(560 + k * 100, 800), (600 + k * 100, 800)], fill=(150, 110, 70), width=14)  # floorboards
    a2 = int(255 * fade_in(a, 0.6))
    card(d, W / 2, 110, 980, 120, a2)
    T(d, "HOURS OF CUTTING THROUGH FLOORBOARDS", W / 2, 110, 54, CREAM, a2)
    return cam(img, t, 16, 0.4)


def s_w5(t, L):
    img = street(t, None, flood_h=3.0, flood_speed=4, ch=4.2, yh=520, el_gap=(45, 85), collapsed=[(1, 1)])
    return cam(img, t, 17, 0.2, 1.0 + 0.05 * L / 4)


def s_r1(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    p = smoothstep(0, PARA["r1"]["dur"], L)
    speed = lerp(1.0, 0.08, p)
    for k in range(9):  # flow lines slowing down as the molasses cools
        y = 280 + k * 70
        off = (t * 260 * speed + k * 140) % 400
        for x in range(-400, W + 400, 400):
            xx = x + off
            d.line([(xx, y), (xx + 240 * speed + 30, y)], fill=(int(lerp(150, 70, p)), int(lerp(90, 70, p)), int(lerp(40, 110, p)), 255), width=14)
    thermometer(d, 1720, 900, 560, lerp(0.7, 0.15, p), "COLD", "WARM")
    T(d, "COLD MOLASSES THICKENS", W / 2, 140, 84, CREAM, int(255 * fade_in(L, PARA["r1"]["dur"] * 0.6)))
    return cam(img, t, 18, 0.2)


def s_r2(t, L):
    sp = [dict(kind=k % 3, X=x, Z=z, h=5.8, Y=-1.2 - 0.05 * L) for k, (x, z) in enumerate(((-8, 30), (4, 40), (-14, 55), (10, 65)))]
    img = street(t, None, flood_h=3.0, flood_speed=1.0, sprites=sp, ch=5.0, fog=260)
    return cam(img, t, 19, 0.2, 1.0 + 0.04 * L / 8)


def s_r3(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, 760, W, H], fill=MOL)
    d.rectangle([0, 620, W, 760], fill=(60, 70, 80))  # harbor
    d.polygon([(1250, 650), (1800, 650), (1760, 720), (1290, 720)], fill=(40, 40, 46))  # training ship
    for x in (1380, 1520, 1660):
        d.line([(x, 650), (x, 360)], fill=(40, 40, 46), width=8)
    T(d, "TRAINING SHIP", 1525, 760, 30, (170, 165, 160), f="oswald")
    groups = [("SAILORS", "cap"), ("POLICE", "homburg"), ("FIREFIGHTERS", "cap"), ("RED CROSS", "homburg")]
    for i, (lab, hat) in enumerate(groups):
        k = fade_in(L, 0.8 + i * 1.0)
        if k <= 0:
            continue
        x = 220 + i * 280
        ef.man(d, x, 850, 0.7, hat, 1, col=(70, 64, 58) + (int(255 * k),))
        T(d, lab, x, 900, 34, CREAM, int(255 * k), f="oswald")
        if lab == "RED CROSS":
            d.rectangle([x - 12, 760 - 24, x + 12, 760 + 24], fill=RED)
            d.rectangle([x - 24, 760 - 12, x + 24, 760 + 12], fill=RED)
    a = int(255 * fade_in(L, sentence_t("r3", 1) - PARA["r3"]["start"]))
    card(d, W / 2, 130, 760, 120, a)
    T(d, "WAIST-DEEP IN PLACES", W / 2, 130, 70, CREAM, a)
    T(d, "RESCUE WORK WENT ON FOR DAYS", W / 2, 260, 44, AMBER, int(255 * fade_in(L, sentence_t("r3", 2) - PARA["r3"]["start"])), f="oswald")
    return cam(img, t, 20, 0.3)


def s_r4(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    T(d, "21", W / 2 - 360, 470, 300, CREAM, int(255 * fade_in(L, 0.2, 0.8)))
    T(d, "DIED", W / 2 - 360, 680, 80, (200, 190, 170), int(255 * fade_in(L, 0.5, 0.8)))
    T(d, "~150", W / 2 + 360, 470, 300, CREAM, int(255 * fade_in(L, 2.4, 0.8)))
    T(d, "INJURED", W / 2 + 360, 680, 80, (200, 190, 170), int(255 * fade_in(L, 2.6, 0.8)))
    s2 = sentence_t("r4", 2) - PARA["r4"]["start"]
    T(d, "ONE VICTIM FOUND NEARLY FOUR MONTHS LATER", W / 2, 880, 46, AMBER, int(255 * fade_in(L, s2, 0.8)), f="oswald")
    return cam(img, t, 21, 0.1, 1.0 + 0.02 * L / 8)


def s_k1(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, 640, W, H], fill=MOL)
    d.rectangle([0, 520, 700, 640], fill=(70, 86, 96))
    d.polygon([(80, 560), (560, 560), (520, 620), (120, 620)], fill=(150, 40, 36))  # fireboat
    d.rectangle([300, 500, 380, 560], fill=(170, 160, 150))
    for k in range(5):  # salt-water hose streams
        ph = (t * 1.5 + k * 0.2) % 1.0
        pts = [(380, 500)] + [(380 + s * 900, 500 - 260 * s * (1 - s) * 4 + 140 * s) for s in np.linspace(0.1, 1, 10)]
        d.line(pts, fill=(170, 200, 220, 160), width=10 - k)
    rng = np.random.default_rng(int(t * 10))
    for _ in range(30):
        x, y = rng.uniform(1100, 1500), rng.uniform(640, 760)
        d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=(170, 200, 220, 200))
    card(d, 1380, 200, 760, 150, 255, outline=(170, 200, 220))
    T(d, "SALT WATER", 1380, 175, 80, (170, 210, 230))
    T(d, "fresh water barely touched it", 1380, 245, 32, (200, 190, 170), f="oldi")
    return cam(img, t, 22, 0.3)


def s_k2(t, L):
    s1 = sentence_t("k2", 1) - PARA["k2"]["start"]
    if L < s1:
        img = base()
        d = ImageDraw.Draw(img, "RGBA")
        d.rectangle([0, 820, W, H], fill=(60, 54, 48))
        x = W - (L / s1) * (W + 900) + 300
        d.rounded_rectangle([x, 470, x + 820, 800], 30, fill=(120, 40, 36), outline=CREAM, width=5)  # streetcar
        for k in range(6):
            d.rectangle([x + 40 + k * 125, 520, x + 130 + k * 125, 640], fill=(40, 34, 30))
        for k in range(2):
            d.ellipse([x + 120 + k * 520, 770, x + 200 + k * 520, 850], fill=(30, 28, 26))
        for k in range(14):  # tracked footprints
            fx = 100 + k * 130
            d.ellipse([fx, 900 + (k % 2) * 40, fx + 40, 960 + (k % 2) * 40], fill=MOL + (int(220 * smoothstep(0.2 + k * 0.15, 0.6 + k * 0.15, L)),))
        T(d, "TRACKED EVERYWHERE", W / 2, 160, 96, CREAM, int(255 * fade_in(L, 0.5)))
        return cam(img, t, 23, 0.3)
    a = L - s1
    out = AERIAL.render(min(1.0, a / 6), t)
    img = to_img(out).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    card(d, W / 2, 120, 900, 130, 255, outline=AMBER)
    T(d, "HARBOR RAN BROWN FOR MONTHS", W / 2, 120, 66, AMBER)
    return from_img(img)


def s_k3(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, 0, W, 700], fill=(150, 120, 80))
    d.ellipse([1500, 100, 1720, 320], fill=(255, 220, 140))
    for i in range(8):  # tenement row
        x = 40 + i * 240
        d.rectangle([x, 380 - (i % 3) * 40, x + 220, 1000], fill=(120, 86, 66), outline=(80, 56, 44), width=4)
        for fl in range(4):
            for c in range(3):
                d.rectangle([x + 24 + c * 66, 420 - (i % 3) * 40 + fl * 130, x + 64 + c * 66, 490 - (i % 3) * 40 + fl * 130], fill=(50, 40, 34))
    for k in range(6):  # the smell, rising on hot days
        x = 300 + k * 260
        pts = [(x + 30 * np.sin(y * 0.03 + t * 2 + k), y) for y in range(900, 300, -20)]
        d.line(pts, fill=AMBER + (150,), width=8)
    T(d, "DECADES LATER", W / 2, 140, 96, CREAM, int(255 * fade_in(L, 0.4)))
    T(d, "on hot summer days", W / 2, 230, 40, (60, 40, 30), int(255 * fade_in(L, 1.2)), f="oldi")
    return cam(img, t, 24, 0.2, 1.0 + 0.03 * L / 6)


def s_b1(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    courtroom(d)
    k = ease_out_back(L / 0.4, 2)
    T(d, "WHO WAS RESPONSIBLE?", W / 2, 200, int(110 * min(1.1, k)) + 1, CREAM, stroke=6)
    return cam(img, t, 25, 0.2, 1.0 + 0.03 * L / 4)


def s_b2(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse([760, 340, 1160, 740], fill=(30, 28, 26), outline=CREAM, width=6)  # bomb icon
    d.line([(1080, 380), (1180, 260)], fill=CREAM, width=10)
    if int(t * 6) % 2 == 0:
        d.ellipse([1165, 240, 1205, 280], fill=AMBER)
    T(d, "?", 960, 560, 300, RED, int(255 * fade_in(L, 1.0)))
    T(d, "THE COMPANY'S CLAIM:", W / 2, 120, 50, (200, 190, 170), f="oswald")
    T(d, "ANARCHISTS BOMBED IT", W / 2, 210, 96, CREAM, int(255 * fade_in(L, 0.6)))
    s2 = sentence_t("b2", 2) - PARA["b2"]["start"]
    T(d, "1919: A WAVE OF REAL ANARCHIST BOMBINGS", W / 2, 860, 44, AMBER, int(255 * fade_in(L, s2)), f="oswald")
    return cam(img, t, 26, 0.3)


def s_b3(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    n = int(119 * smoothstep(0.4, 4.0, L))
    figure_grid(d, n, 220, 300, 17, 52)
    T(d, "119 PLAINTIFFS", 1500, 380, 100, CREAM, int(255 * fade_in(L, 1.0)))
    T(d, "vs.", 1500, 500, 50, (200, 190, 170), int(255 * fade_in(L, 3.0)), f="oldi")
    T(d, "UNITED STATES", 1500, 590, 64, RED, int(255 * fade_in(L, 3.4)))
    T(d, "INDUSTRIAL ALCOHOL", 1500, 670, 64, RED, int(255 * fade_in(L, 3.4)))
    s2 = sentence_t("b3", 2) - PARA["b3"]["start"]
    T(d, "AN EARLY CLASS-ACTION-STYLE LAWSUIT", W / 2, 880, 46, AMBER, int(255 * fade_in(L, s2)), f="oswald")
    return cam(img, t, 27, 0.2)


def s_b4(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    n = int(26 * smoothstep(0.3, 5.0, L))
    for i in range(n):  # testimony piling up
        y = 900 - i * 22
        d.rectangle([300 + (i % 3) * 4, y, 640 + (i % 3) * 4, y + 18], fill=(230, 222, 204), outline=(140, 130, 110))
    T(d, "COURT-APPOINTED AUDITOR", 470, 200, 44, (200, 190, 170), f="oswald")
    T(d, "THOUSANDS OF WITNESSES", 1260, 300, 70, CREAM, int(255 * fade_in(L, 1.2)))
    for i, lab in enumerate(["METAL", "PRESSURE", "RIVETS"]):
        k = fade_in(L, 3.5 + i * 0.8)
        x = 1000 + i * 260
        d.ellipse([x - 70, 480, x + 70, 620], outline=AMBER + (int(255 * k),), width=6)
        T(d, lab, x, 680, 40, AMBER, int(255 * k), f="oswald")
    T(d, "ENGINEERS & SCIENTISTS", 1260, 800, 52, CREAM, int(255 * fade_in(L, 3.2)))
    return cam(img, t, 28, 0.2)


def s_b5(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    courtroom(d)
    d.rectangle([0, 0, W, H], fill=(0, 0, 0, 120))
    s1 = sentence_t("b5", 1) - PARA["b5"]["start"]
    if L > 1.4:
        gm.stamp(img, "NO BOMB", W / 2, 360, ease_out((L - 1.4) / 0.15), angle=-5, size=150)
    d = ImageDraw.Draw(img, "RGBA")
    T(d, "TANK TOO WEAK FOR WHAT IT HELD", W / 2, 700, 64, CREAM, int(255 * fade_in(L, s1)))
    T(d, "CORNERS WERE CUT", W / 2, 800, 64, AMBER, int(255 * fade_in(L, s1 + 2.0)))
    return cam(img, t, 29, 0.3 + (12 * np.exp(-(L - 1.4) * 8) if L > 1.4 else 0))


def s_b6(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    v = int(628000 * smoothstep(0.4, 3.2, L) ** 0.7)
    T(d, f"${v:,}", W / 2, 430, 220, AMBER)
    T(d, "IN DAMAGES", W / 2, 620, 80, CREAM, int(255 * fade_in(L, 1.0)))
    T(d, "MILLIONS IN TODAY'S MONEY", W / 2, 800, 52, (200, 190, 170), int(255 * fade_in(L, PARA["b6"]["dur"] * 0.6)), f="oswald")
    return cam(img, t, 30, 0.2)


def s_l1(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    for i in range(12):  # modern skyline
        x = i * 165
        h = 260 + (i * 97) % 380
        d.rectangle([x, 900 - h, x + 140, 900], fill=(70, 78, 92))
        for wy in range(900 - h + 24, 880, 44):
            for wx in range(x + 18, x + 130, 36):
                if (wx + wy + i) % 3:
                    d.rectangle([wx, wy, wx + 16, wy + 22], fill=(230, 210, 150, 200))
    d.rectangle([0, 900, W, H], fill=(36, 34, 36))
    T(d, "WHY IT STILL MATTERS", W / 2, 140, 100, CREAM, int(255 * fade_in(L, 0.4)))
    return cam(img, t, 31, 0.2, 1.0 + 0.03 * L / 5)


def s_l2(t, L):
    img = Image.new("RGBA", (W, H), (26, 50, 92, 255))
    d = ImageDraw.Draw(img, "RGBA")
    for x in range(0, W, 60):
        d.line([(x, 0), (x, H)], fill=(60, 90, 140), width=1)
    for y in range(0, H, 60):
        d.line([(0, y), (W, y)], fill=(60, 90, 140), width=1)
    d.rectangle([260, 260, 900, 860], outline=(220, 235, 255), width=6)  # building plan
    d.line([(260, 560), (900, 560)], fill=(220, 235, 255), width=4)
    d.line([(580, 260), (580, 860)], fill=(220, 235, 255), width=4)
    steps = ["CALCULATIONS CHECKED", "PLANS SIGNED OFF", "PROJECTS INSPECTED"]
    for i, s in enumerate(steps):
        t0 = 1.5 + i * 2.6
        if L > t0:
            k = ease_out((L - t0) / 0.2)
            y = 330 + i * 200
            d.rounded_rectangle([1040, y - 70, 1760, y + 70], 16, outline=(120, 230, 140, int(255 * k)), width=6)
            T(d, s, 1400, y, 56, (220, 245, 225), int(255 * k))
    T(d, "MASSACHUSETTS, THEN OTHER STATES", W / 2, 120, 50, CREAM, int(255 * fade_in(L, 0.5)), f="oswald")
    a = int(255 * fade_in(L, sentence_t("l2", 1) - PARA["l2"]["start"]))
    T(d, "TRACES BACK, IN PART, TO THIS TANK", W / 2, 915, 52, AMBER, a, f="oswald")
    return cam(img, t, 32, 0.2)


def s_l3(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    park(d, t)
    s1 = sentence_t("l3", 1) - PARA["l3"]["start"]
    if L > s1:
        k = fade_in(L, s1)
        d.ellipse([1560, 780, 1730, 950], outline=AMBER + (int(255 * k),), width=6)
        T(d, "A SMALL PLAQUE", 1645, 720, 44, AMBER, int(255 * k), f="oswald")
    T(d, "THE SAME SPOT TODAY (ILLUSTRATION)", 420, 80, 34, (40, 50, 60), f="oswald")
    z = 1.0 + (0.5 * ease_in_out((L - s1) / 3) if L > s1 else 0)
    return cam(img, t, 33, 0.2, z, cx=lerp(W / 2, 1645, min(1, max(0, (L - s1) / 3))), cy=lerp(H / 2, 860, min(1, max(0, (L - s1) / 3))))


def s_o1(t, L):
    img = street(t, None, flood_h=1.4, flood_speed=1.0, el_gap=(45, 85), collapsed=[(1, 1)], fog=260, ch=6.0, yh=560)
    out = bw_photo(img, L, 0.06, "North End, January 1919 — illustration")
    pil = to_img(out).convert("RGBA")
    d = ImageDraw.Draw(pil, "RGBA")
    T(d, "21 LIVES", W / 2, 190, 90, CREAM, int(255 * fade_in(L, 0.4)), stroke=6)
    return from_img(pil)


def s_o2(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    items = [("A WAVE OF MOLASSES", 0.0), ("A COVER-UP STORY ABOUT BOMBERS", 1.6), ("A LAWSUIT THAT MADE BUILDINGS SAFER", 3.6)]
    for i, (s, t0) in enumerate(items):
        k = fade_in(L, t0)
        y = 380 + i * 170
        T(d, s, W / 2, y, 72, [AMBER, CREAM, CREAM][i], int(255 * k))
    return cam(img, t, 34, 0.2)


def s_o3(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    k = ease_out_back(L / 0.3, 2.5)
    T(d, "NO WAY.", W / 2, 500, int(240 * min(1.1, k)) + 1, CREAM)
    w = 320 * ease_out(L / 0.5)
    d.rectangle([W / 2 - w, 640, W / 2 + w, 652], fill=RED)
    return cam(img, t, 35, 0.2)


def s_o4(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    T(d, "NO WAY.", W / 2, 180, 110, CREAM)
    d.rectangle([W / 2 - 180, 250, W / 2 + 180, 258], fill=RED)
    k = fade_in(L, 0.6)
    d.rounded_rectangle([W / 2 - 220, 330, W / 2 + 220, 430], 20, fill=RED + (int(255 * k),))
    T(d, "SUBSCRIBE", W / 2, 380, 64, CREAM, int(255 * k))
    for x in (520, 1400):  # space reserved for YouTube end-screen videos
        d.rounded_rectangle([x - 300, 540, x + 300, 880], 20, outline=(120, 110, 100, int(200 * k)), width=4)
        T(d, "WATCH NEXT", x, 710, 44, (140, 130, 115), int(255 * k), f="oswald")
    return cam(img, t, 36, 0.1)


SCENE = {"c1": s_c1, "c2": s_c2, "c3": s_c3, "t1": s_t1, "t2": s_t2, "t3": s_t3, "t4": s_t4, "t5": s_t5, "t6": s_t6,
         "s1": s_s1, "s2": s_s2, "s3": s_s3, "s4": s_s4, "w1": s_w1, "w2": s_w2, "w3": s_w3, "w4": s_w4, "w5": s_w5,
         "w6": s_w5, "r1": s_r1, "r2": s_r2, "r3": s_r3, "r4": s_r4, "k1": s_k1, "k2": s_k2, "k3": s_k3, "b1": s_b1,
         "b2": s_b2, "b3": s_b3, "b4": s_b4, "b5": s_b5, "b6": s_b6, "l1": s_l1, "l2": s_l2, "l3": s_l3, "o1": s_o1,
         "o2": s_o2, "o3": s_o3, "o4": s_o4}
SECTION_LOOK = {"trap": "cold", "cold": "photo", "outro": "photo"}


def scene_at(t):
    """Return (rgb float array, section) for time t."""
    for i, (c0, c1, title) in enumerate(CHAPTERS):
        if c0 <= t < c1:
            return s_chapter(t, t - c0, title, i + 1), "chapter"
    if SEC["title"][0] <= t < SEC["title"][1]:
        return s_title(t, t - SEC["title"][0]), "title"
    import bisect
    i = max(0, bisect.bisect_right(STARTS, t) - 1)
    pid = ORDER[i]
    p = PARA[pid]
    # paragraph scenes continue through the pause after them; w6 continues w5's shot
    if pid == "w6":
        return SCENE["w5"](t, t - PARA["w5"]["start"]), p["section"]
    return SCENE[pid](t, t - p["start"]), p["section"]


# ---------------------------------------------------------------- subtitles (sentence chunks, lower third)
SUBS = []
for p in TL["paragraphs"]:
    for s0, s1, text in p["sentences"]:
        words = text.split()
        chunks, cur = [], []
        for w in words:
            if len(" ".join(cur + [w])) > 46 and cur:
                chunks.append(cur)
                cur = []
            cur.append(w)
        if cur:
            chunks.append(cur)
        tot = sum(len(" ".join(c)) for c in chunks)
        tt = s0
        for c in chunks:
            dd = (s1 - s0) * len(" ".join(c)) / tot
            SUBS.append([tt, tt + dd, " ".join(c)])
            tt += dd
for i in range(len(SUBS) - 1):  # hold each subtitle until the next one (max +0.6s)
    SUBS[i][1] = min(SUBS[i + 1][0], SUBS[i][1] + 0.6)


def subtitle(t):
    for s0, s1, text in SUBS:
        if s0 <= t < s1:
            layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            d = ImageDraw.Draw(layer)
            f = font("oswaldm", 50)
            tw = d.textlength(text, font=f)
            d.rounded_rectangle([W / 2 - tw / 2 - 26, 958, W / 2 + tw / 2 + 26, 1036], 14, fill=(0, 0, 0, 170))
            d.text((W / 2, 997), text, font=f, fill=(250, 246, 236), anchor="mm")
            return layer
    return None


def write_srt(path):
    def ts(x):
        h, m = int(x // 3600), int(x % 3600 // 60)
        s = x % 60
        return f"{h:02d}:{m:02d}:{int(s):02d},{int((s % 1) * 1000):03d}"
    with open(path, "w") as fh:
        for i, (s0, s1, text) in enumerate(SUBS, 1):
            fh.write(f"{i}\n{ts(s0)} --> {ts(s1)}\n{text}\n\n")


def frame(idx):
    t = idx / FPS
    img, section = scene_at(t)
    if t > 0.4:  # short dissolve at every scene change
        boundaries = [c[0] for c in CHAPTERS] + [SEC["title"][0], SEC["title"][1]] + [p["start"] for p in TL["paragraphs"]]
        for b in boundaries:
            if b <= t < b + 0.4 and b > 0.5:
                old, _ = scene_at(b - 0.01)
                img = old * (1 - smoothstep(b, b + 0.4, t)) + img * smoothstep(b, b + 0.4, t)
                break
    look = SECTION_LOOK.get(section)
    out = grade(img, idx, t, bw=0.85 if look == "photo" else 0.0, keep_color=0.32, grain=0.035, flicker=0.02,
                dust=look == "photo")
    if look == "cold":  # the trap: a cold blue shift
        out = np.clip(out * np.array([0.82, 0.9, 1.12], np.float32), 0, 1)
    out = out * (smoothstep(0.0, 0.6, t)) * (1 - smoothstep(DURATION - 1.2, DURATION, t))
    pil = to_img(out).convert("RGBA")
    sub = subtitle(t)
    if sub is not None:
        pil = Image.alpha_composite(pil, sub)
    return np.asarray(pil.convert("RGB")).tobytes()


def _init():
    global DARK, AERIAL
    DARK = zw.dark_bg()
    AERIAL = ae.Aerial()


if __name__ == "__main__":
    out = sys.argv[1]
    if "--frames" in sys.argv:
        _init()
        for fi in map(int, sys.argv[sys.argv.index("--frames") + 1:]):
            Image.frombytes("RGB", (W, H), frame(fi)).save(f"{out}_{fi:05d}.png")
        sys.exit()
    if "--srt" in sys.argv:
        write_srt(out)
        sys.exit()
    f0 = int(float(sys.argv[sys.argv.index("--from") + 1]) * FPS) if "--from" in sys.argv else 0
    f1 = int(float(sys.argv[sys.argv.index("--to") + 1]) * FPS) if "--to" in sys.argv else NFR
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                           "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    with Pool(int(os.environ.get("JOBS", 4)), initializer=_init) as pool:
        for fb in pool.imap(frame, range(f0, min(f1, NFR)), chunksize=4):
            ff.stdin.write(fb)
    ff.stdin.close()
    ff.wait()
