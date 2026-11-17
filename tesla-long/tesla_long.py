"""NO WAY. long-form — Nikola Tesla: The Man vs. the Brand (~8:06, 1920x1080, 30 fps).
Scenes keyed to narration paragraphs in timeline.json (narrate.py). Reuses the molasses long-form helpers
(molasses-long/long.py), the Tesla short's motor/Roadster/figure (tesla-name/tesla.py), and shared stamp/clock/figures.
Usage: python3 tesla_long.py out.mp4 [--from S --to S] | prefix --frames N .. | out.srt --srt"""
import os
os.environ.setdefault("OT_W", "1920")
os.environ.setdefault("OT_H", "1080")
import bisect  # noqa: E402
import json  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
from multiprocessing import Pool  # noqa: E402

import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
for sub in ("molasses-long", "tesla-name", "eiffel-con", "rap-grammy", "zanzibar-war", "molasses-flood"):
    sys.path.insert(0, os.path.join(HERE, "..", sub))
from common import W, H, FPS, font, to_img, from_img, grade, lerp, smoothstep, ease_in_out, ease_out, ease_out_back  # noqa: E402
import long as lf  # noqa: E402  helpers: T, card, fade_in, cam, base, arrow, calendar, courtroom, figure_grid, s_o4
import tesla as tn  # noqa: E402  roadster, tesla_figure, motor
import episode as zw  # noqa: E402
import grammy as gm  # noqa: E402
import eiffel as ef  # noqa: E402

T, card, fade_in, cam, arrow = lf.T, lf.card, lf.fade_in, lf.cam, lf.arrow
AMBER, RED, CREAM, INK = lf.AMBER, lf.RED, lf.CREAM, lf.INK
BLUE = (150, 190, 230)

TL = json.load(open(os.path.join(HERE, "timeline.json")))
DURATION = TL["duration"]
NFR = int(DURATION * FPS)
PARA = {p["id"]: p for p in TL["paragraphs"]}
ORDER = [p["id"] for p in TL["paragraphs"]]
STARTS = [p["start"] for p in TL["paragraphs"]]
SEC = TL["sections"]
CHAPTERS = TL.get("chapters", [])


def base():
    return lf.base()


def st(pid, i):
    """Sentence i start of paragraph pid, relative to the paragraph start."""
    s = PARA[pid]["sentences"]
    return s[min(i, len(s) - 1)][0] - PARA[pid]["start"]


def dur(pid):
    return PARA[pid]["dur"]


def fin(img, t, seed, amp=0.3, zoom=1.0, cx=W / 2, cy=H / 2):
    return cam(img, t, seed, amp, zoom, cx, cy)


# ---------------------------------------------------------------- illustration helpers
def hotel_room(d, t, dim=1.0, pigeons=1):
    k = dim
    d.rectangle([0, 0, W, H], fill=(int(58 * k), int(46 * k), int(40 * k)))
    d.rectangle([0, 820, W, H], fill=(int(44 * k), int(34 * k), int(30 * k)))
    d.rectangle([1180, 160, 1640, 640], fill=(20, 26, 44), outline=(int(120 * k), int(100 * k), int(80 * k)), width=10)
    rng = np.random.default_rng(3)
    for _ in range(40):  # city lights
        x, y = rng.uniform(1190, 1630), rng.uniform(300, 630)
        d.rectangle([x, y, x + 6, y + 9], fill=(230, 200, 120, int(200 * k)))
    d.line([(1410, 160), (1410, 640)], fill=(int(120 * k), int(100 * k), int(80 * k)), width=8)
    d.rectangle([1160, 640, 1660, 670], fill=(int(130 * k), int(110 * k), int(90 * k)))
    for i in range(pigeons):  # pigeons on the sill
        x = 1250 + i * 120
        d.ellipse([x, 600, x + 60, 640], fill=(200, 200, 205))
        d.ellipse([x + 44, 588, x + 70, 612], fill=(200, 200, 205))
        d.polygon([(x + 68, 598), (x + 82, 602), (x + 68, 606)], fill=(220, 160, 90))
    d.rectangle([200, 640, 820, 840], fill=(int(120 * k), int(110 * k), int(100 * k)))  # bed
    d.rectangle([200, 600, 300, 700], fill=(int(220 * k), int(212 * k), int(196 * k)))
    d.rectangle([180, 840, 230, 900], fill=(int(70 * k), int(54 * k), int(44 * k)))
    d.rectangle([790, 840, 840, 900], fill=(int(70 * k), int(54 * k), int(44 * k)))
    d.rectangle([880, 300, 1060, 820], fill=(int(90 * k), int(66 * k), int(50 * k)), outline=(int(60 * k), int(44 * k), int(34 * k)), width=6)  # door
    d.ellipse([1030, 560, 1046, 576], fill=(200, 170, 100))
    T(d, "3327", 970, 380, 44, (220, 200, 150), int(255 * k), f="oswald")


def browser(d, url, typed=1.0, note=None, a=255):
    d.rounded_rectangle([260, 200, 1660, 860], 24, fill=(236, 232, 224), outline=(120, 110, 100), width=4)
    d.rectangle([260, 200, 1660, 270], fill=(210, 204, 194))
    for i, c in enumerate([(220, 90, 80), (230, 180, 80), (110, 180, 100)]):
        d.ellipse([290 + i * 40, 222, 316 + i * 40, 248], fill=c)
    d.rounded_rectangle([420, 214, 1600, 258], 20, fill=(250, 248, 244))
    shown = url[:int(len(url) * typed + 0.999)]
    T(d, shown, 450, 236, 34, INK, a, anchor="lm", f="oswaldm")
    if note:
        T(d, note, 960, 560, 72, INK, a)


def roadster_scene(t, x=W / 2, by=820, s=1.4, moving=True, label=None, road=True):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    if road:
        d.rectangle([0, by + 30, W, H], fill=(40, 38, 36))
        for k in range(8):
            xx = (k * 300 - (t * 900 if moving else 0)) % (W + 300) - 150
            d.rectangle([xx, by + 110, xx + 160, by + 124], fill=(200, 190, 160))
    tn.roadster(d, x, by, s, -t * 8 if moving else 0)
    if label:
        T(d, label, W / 2, 140, 80, CREAM, 255)
    return img, d


def tower(d, cx, by, s=1.0, tilt=0.0, rings=0.0, t=0.0, a=255):
    """Wardenclyffe-style tower: lattice base, mushroom dome (stylized)."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    col = (150, 130, 105, 255)
    h = 560 * s
    for k in range(12):
        y0, y1 = by - k * h / 12, by - (k + 1) * h / 12
        w0, w1 = 120 * s - k * 6 * s, 120 * s - (k + 1) * 6 * s
        ld.line([(cx - w0, y0), (cx + w1, y1)], fill=col, width=4)
        ld.line([(cx + w0, y0), (cx - w1, y1)], fill=col, width=4)
        ld.line([(cx - w0, y0), (cx + w0, y0)], fill=col, width=3)
    ld.line([(cx - 120 * s, by), (cx - 48 * s, by - h)], fill=col, width=8)
    ld.line([(cx + 120 * s, by), (cx + 48 * s, by - h)], fill=col, width=8)
    ld.chord([cx - 140 * s, by - h - 120 * s, cx + 140 * s, by - h + 40 * s], 180, 360, fill=(170, 150, 120, 255))
    if rings > 0:
        for k in range(4):
            ph = (t * 0.6 + k / 4) % 1.0
            r = 160 * s + ph * 500 * s
            ld.ellipse([cx - r, by - h - 40 * s - r * 0.35, cx + r, by - h - 40 * s + r * 0.35], outline=AMBER + (int(160 * (1 - ph) * rings),), width=5)
    if tilt:
        layer = layer.rotate(tilt, center=(cx + 120 * s, by), resample=Image.BICUBIC)
    if a < 255:
        layer.putalpha(layer.getchannel("A").point(lambda v: int(v * a / 255)))
    return layer


def big_card(d, lines, y0=420, gap=120, t0=0.0, L=0.0, step=0.5):
    for i, (txt, size, col) in enumerate(lines):
        T(d, txt, W / 2, y0 + i * gap, size, col, int(255 * fade_in(L, t0 + i * step)))


def myth_fact(img, d, L, myth, fact, t_fact, title):
    T(d, title, W / 2, 140, 60, (200, 190, 170), f="oswald")
    k = fade_in(L, 0.3)
    card(d, 520, 520, 760, 360, int(255 * k), outline=RED)
    T(d, "MYTH", 520, 400, 54, RED, int(255 * k), f="oswald")
    for i, line in enumerate(myth):
        T(d, line, 520, 490 + i * 70, 54, CREAM, int(255 * k))
    if L > t_fact:
        k2 = fade_in(L, t_fact)
        card(d, 1400, 520, 760, 360, int(255 * k2), outline=(120, 200, 140))
        T(d, "WHAT WE KNOW", 1400, 400, 54, (120, 200, 140), int(255 * k2), f="oswald")
        for i, line in enumerate(fact):
            T(d, line, 1400, 490 + i * 70, 50, CREAM, int(255 * k2))


# ---------------------------------------------------------------- scenes
def s_c1(t, L):
    img, d = roadster_scene(t)
    T(d, "THE MOST FAMOUS NAME IN ELECTRIC CARS", W / 2, 150, 70, CREAM, int(255 * fade_in(L, 0.2)))
    T(d, "BELONGS TO A MAN WHO DIED BROKE", W / 2, 250, 70, AMBER, int(255 * fade_in(L, dur("c1") * 0.55)))
    return fin(img, t, 1, 0.4)


def s_c2(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    hotel_room(d, t, 0.8, pigeons=2)
    z = 1.0 + 0.6 * ease_in_out((L - st("c2", 2)) / 3.0) if L > st("c2", 2) else 1.0
    out = to_img(fin(img, t, 2, 0.2, z, cx=lerp(W / 2, 970, (z - 1) / 0.6), cy=lerp(H / 2, 420, (z - 1) / 0.6))).convert("RGBA")
    d = ImageDraw.Draw(out, "RGBA")  # the date card stays fixed on screen while the camera pushes in
    k = fade_in(L, 0.2)
    card(d, 520, 170, 760, 150, int(255 * k))
    T(d, "JANUARY 7, 1943", 520, 145, 64, CREAM, int(255 * k))
    T(d, "HOTEL NEW YORKER • ROOM 3327", 520, 210, 32, (200, 190, 170), int(255 * k), f="oswald")
    return from_img(out)


def s_c3(t, L):
    s1 = st("c3", 1)
    if L < s1:
        img, d = roadster_scene(t, moving=False)
        T(d, "2003 • CALIFORNIA", W / 2, 150, 70, CREAM, int(255 * fade_in(L, 0.2)))
        return fin(img, t, 3, 0.3)
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    pts = [(200 + i * 75, 860 - (np.exp(i / 6.0) - 1) * 40 - 25 * np.sin(i * 1.3)) for i in range(int(min(20, (L - s1) * 12)) + 1)]
    if len(pts) > 1:
        d.line(pts, fill=(120, 210, 140), width=10)
    T(d, "ONE OF THE MOST VALUABLE", W / 2, 180, 72, CREAM, int(255 * fade_in(L, s1 + 0.3)))
    T(d, "CAR COMPANIES ON EARTH", W / 2, 280, 72, AMBER, int(255 * fade_in(L, s1 + 0.6)))
    T(d, "illustrative", 1700, 900, 30, (160, 150, 135), f="oldi")
    return fin(img, t, 3, 0.2)


def s_c5(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    browser(d, "tesla.com", min(1, L / 1.2))
    if L > 1.4:
        T(d, "?", 960, 560, 260, RED, int(255 * fade_in(L, 1.4)))
    T(d, "WE'LL GET TO THAT", W / 2, 950 - 40, 46, AMBER, int(255 * fade_in(L, st("c5", 2))), f="oswald")
    return fin(img, t, 4, 0.2)


def s_c4(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    for i, w in enumerate(["THE MAN", "THE MYTHS", "THE BRAND"]):
        T(d, w, 400 + i * 560, 520, 96, [CREAM, AMBER, RED][i], int(255 * fade_in(L, st("c4", 1) + i * 0.6)))
    return fin(img, t, 5, 0.2)


def s_title(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    k = ease_out_back(L / 0.4, 2.4)
    T(d, "NO WAY.", W / 2, 420, int(220 * min(1.1, k)) + 1, CREAM)
    d.rectangle([W / 2 - 300 * k, 545, W / 2 + 300 * k, 555], fill=RED + (255,))
    a = int(255 * fade_in(L, 0.5))
    T(d, "NIKOLA TESLA", W / 2, 640, 96, AMBER, a)
    T(d, "THE MAN VS. THE BRAND", W / 2, 740, 50, (200, 190, 170), a, f="oswald")
    return fin(img, t, 6, 0.2)


def s_chapter(t, L, title, n):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    a = int(255 * fade_in(L, 0.0, 0.3) * (1 - smoothstep(1.3, 1.6, L)))
    T(d, f"PART {n}", W / 2, 440, 48, RED, a, f="oswald")
    T(d, title, W / 2, 540, 130, CREAM, a)
    w = 260 * ease_out(L / 0.6)
    d.rectangle([W / 2 - w, 640, W / 2 + w, 648], fill=AMBER + (a,))
    return fin(img, t, 7, 0.2, 1.0 + 0.02 * L)


def s_m1(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, 760, W, H], fill=(70, 80, 56))
    for i in range(9):  # village
        x = 160 + i * 180
        h = 120 + (i * 37) % 60
        d.rectangle([x, 760 - h, x + 140, 760], fill=(200, 186, 160))
        d.polygon([(x - 10, 760 - h), (x + 70, 760 - h - 70), (x + 150, 760 - h)], fill=(150, 70, 50))
    d.rectangle([880, 420, 960, 760], fill=(220, 210, 190))  # church tower
    d.polygon([(870, 420), (920, 320), (970, 420)], fill=(150, 70, 50))
    big_card(d, [("1856", 110, AMBER), ("A VILLAGE IN TODAY'S CROATIA", 50, CREAM), ("SERBIAN FAMILY • FATHER: A PRIEST", 40, (200, 190, 170))],
             140, 90, 0.3, L, 0.8)
    return fin(img, t, 8, 0.2, 1.0 + 0.03 * L / 8)


def s_m2(t, L):
    img = to_img(zw.paper_bg(6, (0.84, 0.78, 0.64))).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([520, 0, 1400, H], fill=(150, 170, 178))
    d.polygon([(0, 200), (520, 160), (560, 500), (500, 900), (0, 960)], fill=(190, 170, 130), outline=(90, 70, 50))
    d.polygon([(1400, 120), (1920, 100), (1920, 980), (1380, 900), (1420, 500)], fill=(190, 170, 130), outline=(90, 70, 50))
    T(d, "EUROPE", 260, 560, 54, (80, 60, 40), f="oldb")
    T(d, "NEW YORK", 1660, 520, 54, (80, 60, 40), f="oldb")
    p = smoothstep(st("m2", 0) + 2.0, dur("m2") - 1.0, L)
    pts = [(lerp(540, 1400, s_), 500 - 160 * np.sin(np.pi * s_)) for s_ in np.linspace(0, p, max(2, int(40 * p)))]
    for i in range(0, len(pts) - 1, 2):
        d.line([pts[i], pts[i + 1]], fill=RED, width=8)
    if p > 0.02:
        x, y = pts[-1]
        d.polygon([(x - 40, y), (x + 40, y), (x + 26, y + 22), (x - 26, y + 22)], fill=(40, 34, 30))
    T(d, "1884", W / 2, 120, 96, INK, int(255 * fade_in(L, 1.0)))
    return fin(img, t, 9, 0.2)


def s_m7(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    tn.tesla_figure(d, 520, 1020, 1.4)
    d.ellipse([820, 180, 1600, 780], fill=(40, 34, 30), outline=AMBER, width=5)
    for k, (x, y) in enumerate([(760, 760), (720, 820)]):
        d.ellipse([x - 22 + k * 8, y - 22 + k * 8, x + 22 - k * 8, y + 22 - k * 8], outline=AMBER, width=4)
    tn.motor(d, 1210, 480, 220, t, field_ang=(t * 2.5) % 6.283, rotor_ang=t * 2.2)
    T(d, "TESTED MACHINES IN HIS HEAD", 1210, 880, 54, CREAM, int(255 * fade_in(L, 0.8)))
    T(d, "(SO HE CLAIMED)", 1210, 950, 36, (200, 190, 170), int(255 * fade_in(L, 1.4)), f="oswald")
    return fin(img, t, 10, 0.2)


def s_m3(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    for i in range(7):  # light bulbs
        x = 300 + i * 220
        on = (int(t * 3) + i) % 3 != 0
        d.ellipse([x - 60, 300, x + 60, 420], fill=(250, 230, 160) if on else (90, 84, 70))
        d.rectangle([x - 26, 420, x + 26, 470], fill=(150, 140, 120))
    d.rectangle([560, 620, 1360, 860], fill=(70, 66, 60), outline=(150, 140, 120), width=5)  # dynamo
    d.ellipse([820, 620, 1100, 860], fill=(110, 100, 86), outline=(160, 150, 130), width=5)
    T(d, "THOMAS EDISON", W / 2, 140, 96, CREAM, int(255 * fade_in(L, 0.3)))
    return fin(img, t, 11, 0.2)


def s_m4(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    s1 = st("m4", 1)
    T(d, "ACCORDING TO TESLA", W / 2, 180, 50, (200, 190, 170), int(255 * fade_in(L, s1)), f="oswald")
    if L > s1:
        k = ease_out_back((L - s1) / 0.35, 2)
        T(d, "$50,000", W / 2, 440, int(220 * min(1.1, k)) + 1, AMBER)
        T(d, "TO IMPROVE HIS GENERATORS", W / 2, 620, 54, CREAM, int(255 * fade_in(L, s1 + 0.6)))
    s2 = st("m4", 2)
    if L > s2 + 1.0:
        T(d, "… \"AMERICAN HUMOR\"?", W / 2, 800, 64, RED, int(255 * fade_in(L, s2 + 1.0)))
    return fin(img, t, 12, 0.2)


def s_m5(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    T(d, "$50,000", W / 2, 360, 160, (110, 100, 86))
    if L > 1.0:
        gm.stamp(img, "DISPUTED", W / 2, 380, ease_out((L - 1.0) / 0.15), angle=-8, size=110)
    d = ImageDraw.Draw(img, "RGBA")
    T(d, "HE QUIT WITHIN THE YEAR", W / 2, 720, 72, CREAM, int(255 * fade_in(L, st("m5", 1))))
    return fin(img, t, 13, 0.3 + (10 * np.exp(-(L - 1.0) * 8) if L > 1.0 else 0))


def s_m6(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, 760, W, H], fill=(70, 56, 44))
    d.polygon([(1100, 760), (1300, 640), (1500, 760)], fill=(96, 76, 58))  # dirt pile
    x = 900
    ef.man(d, x, 860, 1.0, "cap", 1, col=(50, 46, 42))
    ang = np.sin(t * 3) * 0.4
    hx, hy = x + 70, 640
    d.line([(hx, hy), (hx + 160 * np.cos(ang), hy + 220 * np.cos(ang * 0.5))], fill=(120, 100, 80), width=10)
    d.ellipse([hx + 140 * np.cos(ang) - 30, hy + 200 - 20, hx + 140 * np.cos(ang) + 30, hy + 240], fill=(150, 150, 155))
    T(d, "DIGGING DITCHES", W / 2, 160, 96, CREAM, int(255 * fade_in(L, st("m6", 1))))
    T(d, "(BY HIS OWN ACCOUNT)", W / 2, 260, 40, (200, 190, 170), int(255 * fade_in(L, st("m6", 1) + 0.4)), f="oswald")
    return fin(img, t, 14, 0.2)


def s_o1(t, L):
    img = to_img(zw.paper_bg(7, (0.88, 0.84, 0.72))).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    tn.motor(d, 700, 540, 300, t, sketch=1.0)
    T(d, "AN AC MOTOR", 1400, 360, 90, INK)
    for i, s in enumerate(["NO BRUSHES", "NO SPARKING CONTACTS", "ALMOST NOTHING TO WEAR OUT"]):
        T(d, s, 1400, 490 + i * 80, 46, (110, 60, 40), int(255 * fade_in(L, 2.0 + i * 1.2)), f="oswald")
    return fin(img, t, 15, 0.2)


def s_o2(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    spin = smoothstep(st("o2", 1), st("o2", 1) + 1.0, L)
    fa = (t * 3.0 * spin) % 6.283 - 1.57
    ra = (t * 2.6 * smoothstep(st("o2", 2), st("o2", 2) + 1.5, L))
    tn.motor(d, 760, 540, 380, t, field_ang=fa if spin > 0 else None, rotor_ang=ra)
    for k, col in enumerate([(220, 90, 70), (110, 190, 110), (110, 150, 220)]):  # three out-of-step currents
        pts = [(1300 + x, 300 + k * 170 + 50 * np.sin(x * 0.02 - t * 4 - k * 2.094)) for x in range(0, 500, 10)]
        d.line(pts, fill=col, width=6)
    T(d, "ROTATING MAGNETIC FIELD", W / 2, 90, 70, AMBER, int(255 * fade_in(L, 0.3)))
    T(d, "SIMPLIFIED", 1550, 900, 44, RED, f="anton")
    return fin(img, t, 16, 0.2)


def s_o3(t, L):
    img = to_img(zw.paper_bg(8, (0.88, 0.84, 0.72))).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([560, 120, 1360, 960], fill=(240, 234, 220), outline=(90, 70, 50), width=6)
    T(d, "UNITED STATES PATENT", 960, 210, 54, INK, f="oldb")
    T(d, "1888", 960, 290, 60, (110, 80, 50), f="oldb")
    tn.motor(d, 960, 560, 200, t, sketch=1.0)
    T(d, "AC INDUCTION MOTOR", 960, 840, 50, INK, f="oswald")
    T(d, "illustrative reconstruction", 600, 930, 26, (130, 110, 90), anchor="lm", f="oldi")
    return fin(img, t, 17, 0.2, 1.0 + 0.04 * L / 6)


def s_o4(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    ef.man(d, 620, 960, 1.2, "homburg", 1, col=(70, 64, 58))
    tn.tesla_figure(d, 1300, 960, 1.2)
    k = fade_in(L, 0.5)
    card(d, 620, 200, 680, 140, int(255 * k))
    T(d, "GEORGE WESTINGHOUSE", 620, 200, 56, CREAM, int(255 * k))
    s2 = st("o4", 2)
    if L > s2:
        a = int(255 * fade_in(L, s2))
        card(d, W / 2, 520, 820, 150, a, outline=AMBER)
        T(d, "REMEMBER THIS MOTOR", W / 2, 520, 72, AMBER, a)
    return fin(img, t, 18, 0.2)


def s_x1(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, 0, W / 2, H], fill=(46, 38, 32))
    T(d, "DC", 480, 420, 260, (200, 190, 170))
    T(d, "EDISON", 480, 640, 64, CREAM)
    T(d, "AC", 1440, 420, 260, AMBER)
    T(d, "TESLA + WESTINGHOUSE", 1440, 640, 54, CREAM)
    T(d, "VS", W / 2, 420, 90, RED, int(255 * fade_in(L, 0.8)))
    return fin(img, t, 19, 0.3)


def s_x2(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    T(d, "THE WAR OF THE CURRENTS", W / 2, 160, 96, CREAM, int(255 * fade_in(L, 0.2)))
    s1 = st("x2", 1)
    k = fade_in(L, s1)
    d.polygon([(960, 320), (1240, 800), (680, 800)], fill=(230, 190, 60, int(255 * k)), outline=(40, 30, 20, int(255 * k)))
    T(d, "!", 960, 640, 260, (40, 30, 20), int(255 * k))
    T(d, "\"AC IS DEADLY\"", W / 2, 900, 60, RED, int(255 * k))
    return fin(img, t, 20, 0.3)


def s_x8(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([660, 640, 1260, 700], fill=(90, 70, 52))  # stage
    for i in range(9):  # crowd (no animals shown)
        x = 300 + i * 160
        d.ellipse([x - 30, 820, x + 30, 880], fill=(60, 56, 52))
        d.rounded_rectangle([x - 50, 880, x + 50, 1000], 30, fill=(60, 56, 52))
    T(d, "PUBLIC DEMONSTRATIONS", W / 2, 180, 84, CREAM, int(255 * fade_in(L, 0.3)))
    T(d, "TO MAKE AC LOOK DANGEROUS", W / 2, 280, 52, AMBER, int(255 * fade_in(L, 1.0)), f="oswald")
    return fin(img, t, 21, 0.2)


def s_x9(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, 900, W, H], fill=(60, 46, 36))
    tn.tesla_figure(d, 960, 900, 1.4)
    for dx in (-150, 150):  # glowing lamps in his hands
        gx, gy = 960 + dx, 520
        for r, a in ((90, 40), (60, 80), (30, 220)):
            d.ellipse([gx - r, gy - r, gx + r, gy + r], fill=(255, 230, 160, a))
    T(d, "SHOWMANSHIP", W / 2, 160, 96, CREAM, int(255 * fade_in(L, 0.3)))
    T(d, "HIGH-FREQUENCY CURRENT • LAMPS LIT IN HIS HANDS", W / 2, 260, 44, AMBER, int(255 * fade_in(L, st("x9", 1))), f="oswald")
    return fin(img, t, 22, 0.2)


def s_x3(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    for row, (lab, reach, col) in enumerate([("DC (THEN)", 0.28, (200, 190, 170)), ("AC", 1.0, AMBER)]):
        y = 420 + row * 300
        d.rectangle([160, y - 60, 300, y + 60], fill=(80, 74, 66))
        T(d, lab, 230, y - 100, 44, col, f="oswald")
        p = min(reach, smoothstep(0.5, 3.0, L))
        d.line([(300, y), (300 + 1400 * p, y)], fill=col, width=10)
        for k in range(8):
            x = 300 + 175 * k
            if (x - 300) / 1400 <= p:
                d.line([(x, y - 30), (x, y + 30)], fill=col, width=4)
        if row == 1 and p > 0.98:
            d.rectangle([1700, y - 80, 1800, y + 60], fill=(200, 180, 140))
            T(d, "FAR-AWAY TOWN", 1750, y + 100, 34, CREAM, f="oswald")
    T(d, "LONG DISTANCE", W / 2, 140, 90, CREAM, int(255 * fade_in(L, 0.3)))
    return fin(img, t, 23, 0.2)


def s_x4(t, L):
    img = Image.new("RGBA", (W, H), (14, 16, 30, 255))
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, 760, W, H], fill=(30, 34, 50))
    for i, (x, w, h) in enumerate(((200, 380, 260), (640, 640, 340), (1340, 380, 260))):
        d.rectangle([x, 760 - h, x + w, 760], fill=(236, 232, 220))
        for k in range(int(w / 40)):
            d.rectangle([x + 10 + k * 40, 760 - h + 40, x + 26 + k * 40, 760 - 20], fill=(210, 205, 195))
        d.chord([x + w * 0.25, 760 - h - w * 0.25, x + w * 0.75, 760 - h + w * 0.25], 180, 360, fill=(236, 232, 220))
    rng = np.random.default_rng(5)
    for _ in range(180):  # electric lights outlining the White City
        x, y = rng.uniform(180, 1740), rng.uniform(400, 760)
        tw = 0.6 + 0.4 * np.sin(t * 5 + x)
        d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(255, 230, 150, int(255 * tw)))
    T(d, "1893 • CHICAGO WORLD'S FAIR", W / 2, 150, 80, CREAM, int(255 * fade_in(L, 0.3)))
    T(d, "LIT BY ALTERNATING CURRENT", W / 2, 920, 52, AMBER, int(255 * fade_in(L, 1.5)), f="oswald")
    return fin(img, t, 24, 0.2, 1.0 + 0.03 * L / 6)


def s_x5(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, 300, 520, 1000], fill=(110, 130, 140))  # the falls
    for k in range(18):
        x = 20 + k * 28
        off = (t * 300 + k * 40) % 120
        for y in range(300 + int(off), 1000, 120):
            d.line([(x, y), (x, y + 60)], fill=(220, 235, 240), width=6)
    d.rectangle([0, 1000, 600, H], fill=(200, 215, 220))
    for x in (700, 1000, 1300):  # power line towers
        d.line([(x, 900), (x, 500)], fill=(150, 140, 120), width=8)
        d.line([(x - 50, 520), (x + 50, 520)], fill=(150, 140, 120), width=6)
    p = smoothstep(st("x5", 1), st("x5", 1) + 2.5, L)
    d.line([(560, 520), (lerp(560, 1620, p), 520)], fill=AMBER, width=6)
    for i in range(6):  # Buffalo
        x = 1580 + i * 50
        d.rectangle([x, 900 - (i * 37) % 140 - 120, x + 40, 900], fill=(170, 150, 120))
        if p > 0.98:
            d.rectangle([x + 10, 900 - (i * 37) % 140 - 100, x + 22, 900 - (i * 37) % 140 - 86], fill=(255, 220, 140))
    T(d, "BUFFALO", 1720, 950, 44, CREAM, f="oswald")
    T(d, "NIAGARA FALLS • 1896", W / 2 + 200, 160, 80, CREAM, int(255 * fade_in(L, 0.4)))
    T(d, "20+ MILES", 1150, 450, 60, AMBER, int(255 * fade_in(L, st("x5", 1) + 2.0)))
    return fin(img, t, 25, 0.2)


def s_x6(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle([760, 320, 1160, 820], 30, fill=(236, 232, 224), outline=(150, 140, 130), width=6)
    for y in (430, 640):
        d.rounded_rectangle([880, y, 1040, y + 140], 40, fill=(226, 222, 214), outline=(150, 140, 130), width=4)
        d.rectangle([915, y + 40, 935, y + 90], fill=(60, 56, 52))
        d.rectangle([985, y + 40, 1005, y + 90], fill=(60, 56, 52))
        d.ellipse([945, y + 100, 975, y + 130], fill=(60, 56, 52))
    T(d, "AC WON", W / 2, 160, 110, AMBER, int(255 * fade_in(L, 0.2)))
    T(d, "IT'S IN YOUR WALL RIGHT NOW", W / 2, 920, 52, CREAM, int(255 * fade_in(L, st("x6", 1))), f="oswald")
    return fin(img, t, 26, 0.2)


def s_x7(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    for i in range(int(min(12, L * 8))):
        d.rectangle([660 + (i % 4) * 160, 760 - (i // 4) * 70, 800 + (i % 4) * 160, 820 - (i // 4) * 70], fill=(130, 160, 110), outline=(70, 90, 60), width=3)
    T(d, "SHOULD HAVE BEEN RICH?", W / 2, 260, 100, CREAM, int(255 * fade_in(L, 0.3)))
    return fin(img, t, 27, 0.2)


def s_f1(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([360, 200, 1000, 900], fill=(236, 228, 210), outline=(90, 70, 50), width=6)
    T(d, "ROYALTY AGREEMENT", 680, 280, 50, INK, f="oldb")
    for k in range(8):
        d.line([(420, 360 + k * 50), (940 - (k % 3) * 100, 360 + k * 50)], fill=(160, 145, 120), width=5)
    s2 = st("f1", 2)
    if L > s2:
        d.line([(400, 260), (960, 860)], fill=RED, width=14)
        d.line([(960, 260), (400, 860)], fill=RED, width=14)
        k = fade_in(L, s2 + 1.0)
        T(d, "~$216,000", 1450, 470, 130, AMBER, int(255 * k))
        T(d, "LUMP SUM • 1897", 1450, 600, 54, CREAM, int(255 * k), f="oswald")
    T(d, "illustrative reconstruction", 380, 940, 26, (150, 135, 115), anchor="lm", f="oldi")
    return fin(img, t, 28, 0.2)


def s_f2(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    k = ease_out(L / 1.0)
    d.rectangle([560, 860 - 80 * k, 760, 860], fill=AMBER)
    T(d, "LUMP SUM", 660, 895, 40, CREAM, f="oswald")
    k2 = fade_in(L, st("f2", 1))
    for y in range(int(860 - 620 * k2), 860, 26):
        d.line([(1160, y), (1360, y)], fill=(200, 190, 170, 180), width=3)
    d.rectangle([1160, 860 - 620 * k2, 1360, 860], outline=(200, 190, 170, int(255 * k2)), width=4)
    T(d, "WHAT ROYALTIES COULD HAVE BECOME", 1260, 895, 36, CREAM, int(255 * k2), f="oswald")
    T(d, "?", 1260, 160, 120, RED, int(255 * k2))
    T(d, "illustrative scale", 1700, 960, 28, (160, 150, 135), f="oldi")
    return fin(img, t, 29, 0.2)


def s_f7(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, 860, W, H], fill=(40, 34, 30))
    d.rectangle([620, 360, 1300, 860], fill=(110, 86, 70))
    for c in range(5):
        for r in range(3):
            fl = 0.6 + 0.4 * np.sin(t * 9 + c + r)
            d.rectangle([660 + c * 128, 400 + r * 150, 740 + c * 128, 500 + r * 150], fill=(int(240 * fl), int(130 * fl), 40))
    for k in range(6):  # smoke
        r = 80 + k * 30
        d.ellipse([900 + k * 40 - r, 300 - k * 60 - r, 900 + k * 40 + r, 300 - k * 60 + r], fill=(70, 66, 62, 120))
    T(d, "1895: HIS LAB BURNS", W / 2, 120, 84, CREAM, int(255 * fade_in(L, 0.3)))
    return fin(img, t, 30, 0.3)


def s_f3(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, 880, W, H], fill=(70, 80, 56))
    img.alpha_composite(tower(d, 1300, 880, 1.0))
    d = ImageDraw.Draw(img, "RGBA")
    T(d, "WARDENCLYFFE", 560, 300, 96, CREAM, int(255 * fade_in(L, st("f3", 1))))
    T(d, "LONG ISLAND", 560, 400, 48, (200, 190, 170), int(255 * fade_in(L, st("f3", 1) + 0.4)), f="oswald")
    k = fade_in(L, dur("f3") * 0.7)
    card(d, 560, 640, 640, 170, int(255 * k), outline=AMBER)
    T(d, "$150,000", 560, 620, 90, AMBER, int(255 * k))
    T(d, "FROM J.P. MORGAN", 560, 690, 36, CREAM, int(255 * k), f="oswald")
    return fin(img, t, 31, 0.2)


def s_f4(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, 880, W, H], fill=(70, 80, 56))
    s1 = st("f4", 1)
    rings = 1.0 - smoothstep(s1, s1 + 1.5, L)
    img.alpha_composite(tower(d, 960, 880, 1.0, rings=rings, t=t))
    d = ImageDraw.Draw(img, "RGBA")
    if L < s1 + 0.3:
        T(d, "WIRELESS POWER", W / 2, 120, 84, AMBER, int(255 * fade_in(L, 0.3) * (1 - smoothstep(s1, s1 + 0.3, L))))
    if L > s1:
        T(d, "FUNDING: STOPPED", W / 2, 120, 84, RED, int(255 * fade_in(L, s1 + 0.5)))
    return fin(img, t, 32, 0.2)


def s_f5(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, 880, W, H], fill=(70, 80, 56))
    s1 = st("f5", 1)
    tilt = -80 * ease_in_out((L - s1 - 1.0) / 1.6) if L > s1 + 1.0 else 0
    img.alpha_composite(tower(d, 960, 880, 1.0, tilt=tilt))
    d = ImageDraw.Draw(img, "RGBA")
    T(d, "1917: DEMOLISHED FOR SCRAP", W / 2, 120, 80, CREAM, int(255 * fade_in(L, s1 + 0.6)))
    return fin(img, t, 33, 0.3 + (8 * np.exp(-(L - s1 - 2.6) * 6) if L > s1 + 2.6 else 0))


def s_f6(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    off = (L * 120) % 480
    for i in range(6):  # hotel facades sliding by
        x = i * 480 - off
        d.rectangle([x + 20, 200, x + 440, 900], fill=(110, 92, 80), outline=(70, 56, 46), width=5)
        for r in range(5):
            for c in range(4):
                d.rectangle([x + 60 + c * 95, 260 + r * 120, x + 110 + c * 95, 330 + r * 120], fill=(230, 200, 130) if (i + r + c) % 4 else (40, 34, 30))
        T(d, "HOTEL", x + 230, 230, 34, CREAM, f="oswald")
    T(d, "HOTEL TO HOTEL", W / 2, 990 - 30, 60, AMBER, int(255 * fade_in(L, 0.4)))
    return fin(img, t, 34, 0.2)


def s_f8(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    hotel_room(d, t, 0.85, pigeons=0)
    x = 1350
    d.ellipse([x, 590, x + 90, 650], fill=(250, 250, 252))
    d.ellipse([x + 66, 572, x + 104, 610], fill=(250, 250, 252))
    d.polygon([(x + 102, 586), (x + 122, 592), (x + 102, 598)], fill=(220, 160, 90))
    for r, a in ((140, 30), (90, 50)):
        d.ellipse([x + 45 - r, 610 - r, x + 45 + r, 610 + r], fill=(255, 255, 255, a))
    T(d, "ONE WHITE PIGEON", 520, 160, 80, CREAM, int(255 * fade_in(L, 0.5)))
    return fin(img, t, 35, 0.1, 1.0 + 0.3 * ease_in_out(L / 4), cx=lerp(W / 2, 1400, min(1, L / 4)), cy=lerp(H / 2, 620, min(1, L / 4)))


def s_y1(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    T(d, "MYTH", 700, 500, 200, RED, int(255 * fade_in(L, 0.3)))
    T(d, "VS.", W / 2, 500, 90, CREAM, int(255 * fade_in(L, 0.8)))
    T(d, "FACT", 1220, 500, 200, (120, 200, 140), int(255 * fade_in(L, 1.2)))
    return fin(img, t, 36, 0.2)


def s_y2(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    myth_fact(img, d, L, ["TORE UP A CONTRACT", "WORTH BILLIONS"], ["A LUMP-SUM BUYOUT", "INSTEAD OF ROYALTIES"], st("y2", 1), "MYTH #1")
    return fin(img, t, 37, 0.2)


def s_y3(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    myth_fact(img, d, L, ["HE BUILT", "A DEATH RAY"], ["HE CLAIMED A DESIGN", "NO EVIDENCE IT WAS BUILT"], st("y3", 2), "MYTH #2")
    return fin(img, t, 38, 0.2)


def s_y4(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    myth_fact(img, d, L, ["SUPREME COURT NAMED", "HIM INVENTOR OF RADIO"], ["1943: PARTS OF MARCONI'S", "PATENT STRUCK DOWN"], st("y4", 1), "MYTH #3")
    return fin(img, t, 39, 0.2)


def s_y5(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    s1 = st("y5", 1)
    T(d, "\"HE INVENTED EVERYTHING\"", W / 2, 180, 72, CREAM, int(255 * fade_in(L, 0.2)))
    if L > s1:
        gm.stamp(img, "NO", W / 2, 190, ease_out((L - s1) / 0.15), angle=-6, size=110)
    d = ImageDraw.Draw(img, "RGBA")
    s3 = st("y5", 3)
    k = fade_in(L, s3)
    T(d, "T", W / 2, 560, 300, AMBER, int(255 * k))
    T(d, "THE TESLA • A SCIENTIFIC UNIT OF MAGNETISM", W / 2, 820, 46, CREAM, int(255 * k), f="oswald")
    return fin(img, t, 40, 0.3 + (6 * np.exp(-(L - s1) * 8) if L > s1 else 0))


def s_y6(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    hotel_room(d, t, 0.6, pigeons=1)
    s1 = st("y6", 1)
    for i in range(3):  # boxes of papers taken away
        k = fade_in(L, s1 + i * 0.4)
        x = 240 + i * 200
        d.rectangle([x, 860, x + 170, 990], fill=(160, 130, 90, int(255 * k)), outline=(90, 70, 50, int(255 * k)), width=4)
    T(d, "PAPERS TAKEN BY THE GOVERNMENT", 560, 160, 56, CREAM, int(255 * fade_in(L, s1)))
    return fin(img, t, 41, 0.1)


def s_n1(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, 0, W, 760], fill=(200, 150, 90))
    d.ellipse([1500, 140, 1700, 340], fill=(255, 220, 140))
    for x in (200, 1720):  # palms
        d.line([(x, 760), (x + 20, 420)], fill=(70, 50, 34), width=16)
        for a in (-150, -110, -60, -20, 20):
            r = np.deg2rad(a)
            d.line([(x + 20, 420), (x + 20 + np.cos(r) * 120, 420 + np.sin(r) * -40 + 40)], fill=(60, 80, 40), width=12)
    d.rectangle([0, 760, W, H], fill=(70, 66, 60))
    d.rectangle([700, 480, 1220, 760], fill=(200, 186, 160))  # garage startup
    d.rectangle([780, 560, 1140, 760], fill=(60, 56, 52))
    ef.man(d, 860, 760, 0.55, "cap", 1, col=(40, 36, 32))
    ef.man(d, 1060, 760, 0.55, "homburg", -1, col=(40, 36, 32))
    s1 = st("n1", 1)
    T(d, "JULY 1, 2003", W / 2, 120, 96, INK, int(255 * fade_in(L, s1)))
    T(d, "MARTIN EBERHARD • MARC TARPENNING", W / 2, 900, 52, CREAM, int(255 * fade_in(L, st("n1", 2))))
    return fin(img, t, 42, 0.2)


def s_n2(t, L):
    img, d = roadster_scene(t, x=1180, by=820, s=1.3, moving=False)
    T(d, "TESLA MOTORS", 520, 160, 110, CREAM, int(255 * fade_in(L, 0.4)))
    T(d, "NAME CREDITED TO EBERHARD", 520, 270, 40, (200, 190, 170), int(255 * fade_in(L, 0.8)), f="oswald")
    s3 = st("n2", 3)
    if L > s3:
        k = fade_in(L, s3)
        rx, ry = 1180 + 215 * 1.3 - 90, 820 - 40 * 1.3 - 160
        tn.motor(d, rx, ry, 110, t, field_ang=(t * 3) % 6.283, rotor_ang=t * 2.5)
        T(d, "AC INDUCTION MOTOR", 520, 520, 64, AMBER, int(255 * k))
        T(d, "SAME IDEA: 1888 → 2008".replace("→", "TO"), 520, 610, 46, CREAM, int(255 * fade_in(L, s3 + 1.0)), f="oswald")
    return fin(img, t, 43, 0.2)


def s_n3(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    T(d, "2004", W / 2, 220, 110, CREAM, int(255 * fade_in(L, 0.2)))
    k = fade_in(L, st("n3", 1))
    card(d, W / 2, 520, 820, 220, int(255 * k), outline=AMBER)
    T(d, "$6.5 MILLION", W / 2, 490, 100, AMBER, int(255 * k))
    T(d, "ELON MUSK LEADS THE FIRST BIG ROUND", W / 2, 580, 40, CREAM, int(255 * k), f="oswald")
    T(d, "CHAIRMAN, LATER CEO", W / 2, 800, 60, CREAM, int(255 * fade_in(L, st("n3", 2))))
    return fin(img, t, 44, 0.2)


def s_n7(t, L):
    img, d = roadster_scene(t)
    T(d, "2008: THE ROADSTER", W / 2, 140, 90, CREAM, int(255 * fade_in(L, 0.3)))
    T(d, "ABOUT 2,500 EVER BUILT", W / 2, 240, 56, AMBER, int(255 * fade_in(L, st("n7", 1))), f="oswald")
    return fin(img, t, 45, 0.4)


def s_n8(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    tn.roadster(d, W / 2, 820, 1.6, 0, col=(200, 190, 170), line=True)
    n = int(smoothstep(0.5, dur("n8") - 0.5, L) * 400)
    for i in range(n):  # battery cells filling the chassis
        x = 560 + (i % 40) * 20
        y = 700 - (i // 40) * 20
        d.ellipse([x, y, x + 16, y + 16], fill=(120, 200, 140), outline=(40, 80, 50))
    T(d, "LOTUS-BASED CHASSIS", W / 2, 140, 72, CREAM, int(255 * fade_in(L, 0.3)))
    T(d, "THOUSANDS OF LAPTOP-STYLE CELLS", W / 2, 240, 52, AMBER, int(255 * fade_in(L, dur("n8") * 0.5)), f="oswald")
    return fin(img, t, 46, 0.2)


def s_n4(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    lf.courtroom(d)
    d.rectangle([0, 0, W, H], fill=(0, 0, 0, 110))
    if L > st("n4", 1):
        gm.stamp(img, "LAWSUIT", W / 2, 300, ease_out((L - st("n4", 1)) / 0.15), angle=-6, size=110)
    d = ImageDraw.Draw(img, "RGBA")
    if L > st("n4", 2):
        k = fade_in(L, st("n4", 2))
        lf.figure_grid(d, 5, 760, 640, 5, 100, int(255 * k))
        T(d, "2009: FIVE CO-FOUNDERS", W / 2, 820, 64, AMBER, int(255 * k))
    return fin(img, t, 47, 0.3)


def s_n5(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    s1, s2, s3 = st("n5", 1), st("n5", 2), st("n5", 3)
    if L < s3:
        browser(d, "tesla.com", min(1, max(0, (L - s1) / 1.2)))
        if L > s2:
            T(d, "OWNED BY SOMEONE ELSE", 960, 520, 70, INK, int(255 * fade_in(L, s2)))
            T(d, "SINCE 1992", 960, 620, 90, RED, int(255 * fade_in(L, s2 + 0.6)))
    else:
        browser(d, "tesla.com", 1.0)
        T(d, "2016: FINALLY THEIRS", 960, 500, 80, (40, 120, 70), int(255 * fade_in(L, s3)))
        s4 = st("n5", 4)
        T(d, "$11 MILLION (PER MUSK)", 960, 640, 70, INK, int(255 * fade_in(L, s4)))
    return fin(img, t, 48, 0.2)


def s_n6(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    T(d, "2017", W / 2, 220, 90, (200, 190, 170), int(255 * fade_in(L, 0.2)))
    k = smoothstep(0.8, 1.4, L)
    if L < 2.4:
        T(d, "TESLA", W / 2 - 30, 520, 200, CREAM, int(255 * (1 - smoothstep(2.0, 2.4, L))), anchor="rm")
        T(d, "MOTORS", W / 2 + 30, 520, 200, (200, 190, 170), int(255 * (1 - smoothstep(1.6, 2.2, L))), anchor="lm")
        if k > 0:
            d.line([(W / 2 + 30, 520), (W / 2 + 30 + 620 * k, 520)], fill=RED, width=16)
    else:
        T(d, "TESLA", W / 2, 520, 220, AMBER, int(255 * fade_in(L, 2.4)))
    return fin(img, t, 49, 0.2)


def s_q1(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    hotel_room(d, t, 0.55, pigeons=1)
    T(d, "DIED BROKE • 1943", 560, 160, 64, CREAM, int(255 * fade_in(L, st("q1", 1))))
    return fin(img, t, 50, 0.1, 1.0 + 0.04 * L / 4)


def s_q2(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hotel_room(ImageDraw.Draw(layer, "RGBA"), t, 0.5, pigeons=1)
    img.alpha_composite(layer.crop((0, 0, W // 2, H)), (0, 0))
    tn.roadster(d, 1440, 760, 0.9, -t * 6)
    d.line([(W / 2, 0), (W / 2, H)], fill=AMBER, width=6)
    T(d, "1888: THE MOTOR", 480, 980 - 40, 50, CREAM, f="oswald")
    T(d, "TODAY: THE BRAND", 1440, 980 - 40, 50, AMBER, f="oswald")
    T(d, "TESLA", 1440, 300, 160, CREAM, int(255 * fade_in(L, 1.0)))
    return fin(img, t, 51, 0.2)


def s_q3(t, L):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    k = ease_out_back(L / 0.3, 2.5)
    T(d, "NO WAY.", W / 2, 500, int(240 * min(1.1, k)) + 1, CREAM)
    w = 320 * ease_out(L / 0.5)
    d.rectangle([W / 2 - w, 640, W / 2 + w, 652], fill=RED)
    return fin(img, t, 52, 0.2)


def s_q4(t, L):
    return lf.s_o4(t, L)


SCENE = {k[2:]: v for k, v in globals().items() if k.startswith("s_") and k not in ("s_chapter", "s_title")}
CONTINUE = {}


def scene_at(t):
    for i, (c0, c1, title) in enumerate(CHAPTERS):
        if c0 <= t < c1:
            return s_chapter(t, t - c0, title, i + 1), "chapter"
    if SEC["title"][0] <= t < SEC["title"][1]:
        return s_title(t, t - SEC["title"][0]), "title"
    i = max(0, bisect.bisect_right(STARTS, t) - 1)
    pid = ORDER[i]
    p = PARA[pid]
    if pid in CONTINUE:
        src = CONTINUE[pid]
        return SCENE[src](t, t - PARA[src]["start"]), p["section"]
    return SCENE[pid](t, t - p["start"]), p["section"]


# ---------------------------------------------------------------- subtitles + srt
SUBS = []
for p in TL["paragraphs"]:
    for s0, s1, text in p["sentences"]:
        words = text.split()
        chunks, cur = [], []
        for w_ in words:
            if len(" ".join(cur + [w_])) > 46 and cur:
                chunks.append(cur)
                cur = []
            cur.append(w_)
        if cur:
            chunks.append(cur)
        tot = sum(len(" ".join(c)) for c in chunks)
        tt = s0
        for c in chunks:
            dd = (s1 - s0) * len(" ".join(c)) / tot
            SUBS.append([tt, tt + dd, " ".join(c)])
            tt += dd
for i in range(len(SUBS) - 1):
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


BOUNDS = [c[0] for c in CHAPTERS] + [SEC["title"][0], SEC["title"][1]] + [p["start"] for p in TL["paragraphs"]]


def frame(idx):
    t = idx / FPS
    img, section = scene_at(t)
    for b in BOUNDS:
        if b <= t < b + 0.35 and b > 0.5:
            old, _ = scene_at(b - 0.01)
            k = smoothstep(b, b + 0.35, t)
            img = old * (1 - k) + img * k
            break
    out = grade(img, idx, t, keep_color=0.36, grain=0.035, flicker=0.02, dust=False)
    out = out * smoothstep(0.0, 0.6, t) * (1 - smoothstep(DURATION - 1.2, DURATION, t))
    pil = to_img(out).convert("RGBA")
    sub = subtitle(t)
    if sub is not None:
        pil = Image.alpha_composite(pil, sub)
    return np.asarray(pil.convert("RGB")).tobytes()


def _init():
    lf._init()


if __name__ == "__main__":
    out = sys.argv[1]
    if "--srt" in sys.argv:
        write_srt(out)
        sys.exit()
    if "--frames" in sys.argv:
        _init()
        for fi in map(int, sys.argv[sys.argv.index("--frames") + 1:]):
            Image.frombytes("RGB", (W, H), frame(fi)).save(f"{out}_{fi:05d}.png")
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
