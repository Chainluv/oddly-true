"""NO WAY. — America Sent Troops Against Its Own Veterans (Bonus Army, 1932). ~65s, serious tone.
Reuses molasses-flood (grade, captions), zanzibar-war (headline, backgrounds, caption timing), rap-grammy (stamp)
and eiffel-con (1920s figures, paperwork). All documents shown are illustrative reconstructions."""
import os
import subprocess
import sys
from multiprocessing import Pool

import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
for sub in ("eiffel-con", "rap-grammy", "zanzibar-war", "molasses-flood"):
    sys.path.insert(0, os.path.join(HERE, "..", sub))
from common import (W, H, FPS, NOISE2, tex, font, to_img, from_img, cam2d, shake, grade, lerp, smoothstep,
                    ease_in_out, ease_out, ease_out_back)
import render as mf   # captions
import episode as zw  # headline(), dark_bg(), paper_bg(), build_chunks()
import grammy as gm   # stamp()
import eiffel as ef   # man(), papers()

DURATION = 65.0
NFR = int(DURATION * FPS)
AMBER, RED, CREAM = mf.AMBER, (215, 60, 45), (236, 226, 205)
VOICES = os.path.join(HERE, "voices")

# narration: id -> start time (deliberate pauses between lines)
NARR = {"n01": 0.3, "n02": 6.0, "n03": 11.0, "n04": 14.2, "n05": 18.2, "n06": 22.4, "n07": 25.2, "n08": 28.0,
        "n09": 31.4, "n10": 33.9, "n11": 36.2, "n12": 41.8, "n13": 44.3, "n14": 46.3, "n15": 48.5, "n16": 52.4,
        "n17": 60.0, "n18": 63.8}
TEXT = {"n01": "AMERICA ONCE SENT TROOPS TO DRIVE ITS OWN WAR VETERANS OUT OF WASHINGTON.",
        "n02": "IN 1932, THOUSANDS OF WORLD WAR ONE VETERANS ARRIVED IN THE CAPITAL.",
        "n03": "THE GREAT DEPRESSION HAD WRECKED JOBS AND SAVINGS.",
        "n04": "THEY WANTED A MILITARY SERVICE BONUS, PAID EARLY.",
        "n05": "THE CATCH? THEIR CERTIFICATES WEREN'T DUE UNTIL 1945.",
        "n06": "THIRTEEN YEARS AWAY.",
        "n07": "THEY CALLED THEMSELVES THE BONUS ARMY.",
        "n08": "SOME BROUGHT THEIR FAMILIES, AND BUILT MAKESHIFT CAMPS.",
        "n09": "THE HOUSE VOTED FOR EARLY PAYMENT.",
        "n10": "THE SENATE REJECTED IT.",
        "n11": "THEN, ON JULY 28TH, AFTER A DEADLY CLASH WITH POLICE, FEDERAL TROOPS MOVED IN.",
        "n12": "TEAR GAS DROVE PEOPLE OUT.",
        "n13": "CAMPS BURNED.",
        "n14": "THE MEN HAD SERVED THEIR COUNTRY.",
        "n15": "NOW ITS ARMY WAS CLEARING THEM FROM THE CAPITAL.",
        "n16": "IN 1936, CONGRESS FINALLY AUTHORIZED EARLY PAYMENT, OVERRIDING PRESIDENT ROOSEVELT'S VETO.",
        "n17": "A FINANCIAL CRISIS HAD BECOME A CRISIS OF TRUST.",
        "n18": "NO WAY."}


def groups(text, n=3):
    w = text.split()
    return [w[i:i + n] for i in range(0, len(w), n)]


zw.LINES = [(k, groups(TEXT[k])) for k in NARR]
zw.NARR = NARR
zw.DUR = {k: sf.info(os.path.join(VOICES, f"{k}.wav")).duration for k in NARR}
zw.SPOKEN = {"1932,": "nineteen thirty two", "1945.": "nineteen forty five", "1936,": "nineteen thirty six",
             "28TH,": "twenty eighth"}
mf.CHUNKS = zw.build_chunks()
mf.KEYWORDS = {"TROOPS", "VETERANS", "1932,", "BONUS,", "EARLY.", "1945.", "THIRTEEN", "BONUS", "ARMY.", "FAMILIES,",
               "HOUSE", "SENATE", "REJECTED", "28TH,", "POLICE,", "FEDERAL", "TEAR", "GAS", "BURNED.", "SERVED",
               "ARMY", "1936,", "VETO.", "TRUST.", "WAY."}


# ---------------------------------------------------------------- art helpers
def capitol(d, cx, by, s=1.0, col=(70, 62, 55)):
    """Capitol silhouette: wings, colonnade, drum, dome, statue."""
    d.rectangle([cx - 480 * s, by - 120 * s, cx + 480 * s, by], fill=col)
    d.rectangle([cx - 200 * s, by - 170 * s, cx + 200 * s, by - 120 * s], fill=col)
    d.polygon([(cx - 120 * s, by - 170 * s), (cx + 120 * s, by - 170 * s), (cx, by - 215 * s)], fill=col)
    d.rectangle([cx - 130 * s, by - 310 * s, cx + 130 * s, by - 170 * s], fill=col)
    for k in range(-5, 6):
        d.line([(cx + k * 22 * s, by - 300 * s), (cx + k * 22 * s, by - 180 * s)], fill=(40, 36, 33), width=max(1, int(4 * s)))
    d.chord([cx - 125 * s, by - 470 * s, cx + 125 * s, by - 230 * s], 180, 360, fill=col)
    d.rectangle([cx - 22 * s, by - 520 * s, cx + 22 * s, by - 460 * s], fill=col)
    d.ellipse([cx - 14 * s, by - 545 * s, cx + 14 * s, by - 515 * s], fill=col)


def soldier(d, cx, by, s=1.0, col=(118, 116, 100)):
    """WWI-era infantry silhouette: brodie helmet, rifle at port arms."""
    d.polygon([(cx - 55 * s, by), (cx - 62 * s, by - 250 * s), (cx - 45 * s, by - 300 * s),
               (cx + 45 * s, by - 300 * s), (cx + 62 * s, by - 250 * s), (cx + 55 * s, by)], fill=col)
    d.ellipse([cx - 36 * s, by - 375 * s, cx + 36 * s, by - 300 * s], fill=col)
    d.ellipse([cx - 70 * s, by - 372 * s, cx + 70 * s, by - 350 * s], fill=col)             # helmet brim
    d.chord([cx - 42 * s, by - 400 * s, cx + 42 * s, by - 345 * s], 180, 360, fill=col)
    d.line([(cx - 70 * s, by - 120 * s), (cx + 60 * s, by - 330 * s)], fill=(60, 56, 50), width=max(2, int(12 * s)))  # rifle
    d.ellipse([cx - 10 * s, by - 200 * s, cx + 30 * s, by - 160 * s], fill=(80, 76, 70))     # gas-mask canister


def veteran(d, cx, by, s=1.0, facing=1, col=(178, 166, 146), kind=0):
    if kind == 2:  # child
        d.polygon([(cx - 35 * s, by), (cx - 40 * s, by - 150 * s), (cx + 40 * s, by - 150 * s), (cx + 35 * s, by)], fill=col)
        d.ellipse([cx - 30 * s, by - 210 * s, cx + 30 * s, by - 150 * s], fill=col)
        return
    hat = "homburg" if kind == 0 else "cap"
    ef.man(d, cx, by, s, hat, facing, col=col)


def shack(d, x, by, w, h, burn=0.0, t=0.0, ruin=False):
    if ruin:
        for k in range(4):
            x0 = x + k * w / 3.5
            d.line([(x0, by), (x0 + 10, by - h * (0.4 + 0.3 * ((k * 7) % 3) / 2))], fill=(30, 26, 24), width=10)
        d.line([(x, by - h * 0.35), (x + w, by - h * 0.55)], fill=(30, 26, 24), width=8)
        return
    d.rectangle([x, by - h, x + w, by], fill=(118, 102, 84))
    for k in range(1, 5):
        d.line([(x + k * w / 5, by - h), (x + k * w / 5 + 4, by)], fill=(90, 76, 62), width=3)
    d.polygon([(x - 10, by - h), (x + w + 10, by - h - 18), (x + w + 10, by - h + 12), (x - 10, by - h + 20)], fill=(80, 74, 68))
    d.rectangle([x + w * 0.35, by - h * 0.6, x + w * 0.6, by], fill=(40, 34, 30))
    if burn > 0:
        fl = 0.75 + 0.25 * np.sin(t * 17 + x)
        fh = h * 0.9 * burn * fl
        d.polygon([(x + 5, by - h * 0.2), (x + w * 0.25, by - h - fh * 0.8), (x + w * 0.45, by - h - fh * 0.3),
                   (x + w * 0.65, by - h - fh), (x + w - 5, by - h * 0.2)], fill=(230, 110, 40, 220))
        d.polygon([(x + w * 0.2, by - h * 0.4), (x + w * 0.4, by - h - fh * 0.4), (x + w * 0.6, by - h * 0.4)], fill=(255, 210, 120, 220))


def tent(d, x, by, w, h):
    d.polygon([(x, by), (x + w / 2, by - h), (x + w, by)], fill=(196, 184, 160))
    d.polygon([(x + w * 0.4, by), (x + w / 2, by - h * 0.5), (x + w * 0.6, by)], fill=(60, 54, 48))


def smoke_layer(t, strength, tint=(205, 200, 190), speed=40, y0=600, y1=1350):
    """Drifting gas/smoke band (procedural), returned as RGBA."""
    yy, xx = np.mgrid[0:H // 4, 0:W // 4].astype(np.float32)
    n = tex(NOISE2, xx * 0.8 + t * speed / 4, yy * 0.8 - t * 4)
    band = smoothstep(y0 / 4, y0 / 4 + 60, yy) * (1 - smoothstep(y1 / 4 - 40, y1 / 4, yy))
    a = np.clip((n - 0.35) * 2.0, 0, 1) * band * strength
    img = np.zeros((H // 4, W // 4, 4), np.uint8)
    img[..., :3] = tint
    img[..., 3] = (a * 220).astype(np.uint8)
    return Image.fromarray(img, "RGBA").resize((W, H), Image.BILINEAR)


def certificate(d, cx, cy, s=1.0, highlight=0.0):
    w, h = 820 * s, 520 * s
    d.rectangle([cx - w / 2 + 14, cy - h / 2 + 16, cx + w / 2 + 14, cy + h / 2 + 16], fill=(0, 0, 0, 120))
    d.rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], fill=CREAM, outline=(90, 70, 50), width=8)
    d.rectangle([cx - w / 2 + 22, cy - h / 2 + 22, cx + w / 2 - 22, cy + h / 2 - 22], outline=(150, 120, 80), width=3)

    def C(txt, y, f, col=(45, 35, 28)):
        tw = d.textlength(txt, font=f)
        d.text((cx - tw / 2, cy + y * s), txt, font=f, fill=col)
    C("BONUS CERTIFICATE", -210, font("oldb", int(52 * s)))
    C("World War Veterans", -145, font("playi", int(56 * s)))
    C("SERVICE BONUS — DEFERRED", -70, font("oldb", int(34 * s)))
    if highlight > 0:
        d.rectangle([cx - 300 * s, cy + 10 * s, cx + 300 * s, cy + 125 * s], outline=RED + (int(255 * highlight),), width=max(3, int(8 * s)))
    C("PAYABLE: 1945", 20, font("anton", int(88 * s)), RED)
    C("illustrative reconstruction", 160, font("oldi", int(26 * s)), (120, 100, 80))


def bill(d, cx, cy):
    w, h = 820, 900
    d.rectangle([cx - w / 2 + 14, cy - h / 2 + 16, cx + w / 2 + 14, cy + h / 2 + 16], fill=(0, 0, 0, 120))
    d.rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], fill=CREAM, outline=(90, 70, 50), width=6)
    for txt, y, f in (("U.S. CONGRESS  ·  1936", -390, font("oldb", 44)), ("Veterans' Bonus", -320, font("playi", 66)),
                      ("EARLY PAYMENT OF ADJUSTED", -220, font("oldb", 34)), ("SERVICE CERTIFICATES", -175, font("oldb", 34))):
        tw = d.textlength(txt, font=f)
        d.text((cx - tw / 2, cy + y), txt, font=f, fill=(45, 35, 28))
    for k in range(9):
        d.line([(cx - 330, cy - 100 + k * 34), (cx + 330 - (k % 3) * 70, cy - 100 + k * 34)], fill=(160, 145, 120), width=4)
    d.text((cx - 330, cy + 380), "illustrative reconstruction", font=font("oldi", 26), fill=(120, 100, 80))


def base():
    return to_img(zw.DARK).convert("RGBA")


def cam(img, t, seed, amp=1.5, zoom=1.0, cy=900):
    sx, sy, sr = shake(t, amp, 2, seed=seed)
    return from_img(cam2d(img.convert("RGB"), zoom, W / 2, cy, sr, sx, sy))


# ---------------------------------------------------------------- scenes
def scene_open(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, 1180, W, H], fill=(40, 36, 32))
    capitol(d, W / 2, 1180, 1.0)
    adv = 120 * ease_in_out(t / 6)
    for i, x in enumerate((90, 200, 310)):                       # veterans, left, facing right
        veteran(d, x, 1260 + (i % 2) * 20, 0.75, 1, kind=i % 2)
    for i, x in enumerate((760, 860, 960, 1060)):                # troops approaching from the right
        soldier(d, x - adv + (i % 2) * 20, 1270 + (i % 2) * 15, 0.8)
    return cam(img, t, 1, 1.5, 1.0 + 0.03 * t / 6)


def scene_travel(t):
    a = t - 6.0
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    if a < 5.0:  # veterans on the road toward Washington
        d.rectangle([0, 1080, W, H], fill=(52, 46, 40))
        d.polygon([(380, 1080), (700, 1080), (W + 200, H), (-200, H)], fill=(80, 72, 62))
        capitol(d, 820, 1080, 0.35, col=(90, 82, 72))
        for k in range(9):
            ph = (a * 0.12 + k / 9) % 1.0
            s = 0.25 + ph * 0.75
            x = lerp(560, 200 + (k % 3) * 340, ph)
            veteran(d, x, lerp(1090, 1500, ph), s, 1, kind=k % 2)
        d.text((80, 360), "TO WASHINGTON", font=font("oswaldm", 56), fill=CREAM)
    else:        # shuttered business + shrinking savings
        b = a - 5.0
        d.rectangle([90, 420, 990, 1040], fill=(120, 106, 90))
        d.rectangle([90, 420, 990, 500], fill=(70, 62, 55))
        d.text((240, 432), "GENERAL STORE", font=font("oldb", 52), fill=CREAM)
        for x0 in (140, 560):
            d.rectangle([x0, 560, x0 + 380, 900], fill=(40, 36, 32))
            for k in range(4):
                d.polygon([(x0 - 10, 600 + k * 80), (x0 + 390, 640 + k * 80), (x0 + 390, 670 + k * 80), (x0 - 10, 630 + k * 80)], fill=(150, 125, 95))
        d.rectangle([420, 700, 660, 790], fill=CREAM, outline=RED, width=6)
        d.text((452, 708), "CLOSED", font=font("anton", 64), fill=RED)
        lvl = lerp(1.0, 0.12, ease_in_out(b / 3.0))
        d.text((140, 1080), "SAVINGS", font=font("oswaldm", 50), fill=CREAM)
        d.rectangle([140, 1150, 940, 1210], outline=CREAM, width=4)
        d.rectangle([146, 1156, 146 + 788 * lvl, 1204], fill=RED if lvl < 0.4 else AMBER)
    return cam(img, t, 2, 1.2, 1.0 + 0.02 * a / 10)


def scene_certificate(t):
    a = t - 16.2
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    k = ease_out(a / 0.5)
    hl = smoothstep(19.8, 20.4, t)
    certificate(d, W / 2, lerp(1300, 680, k), 1.1, hl)
    if t > 20.6:  # the gap: 1932 -> 1945
        g = ease_in_out((t - 20.6) / 2.2)
        y = 1080
        x0, x1 = 120, 960
        d.line([(x0, y), (x1, y)], fill=(120, 110, 95), width=6)
        d.line([(x0, y), (lerp(x0, x1, g), y)], fill=RED, width=10)
        for i in range(14):
            x = lerp(x0, x1, i / 13)
            d.line([(x, y - 18), (x, y + 18)], fill=CREAM if i / 13 <= g else (120, 110, 95), width=4)
        d.text((x0 - 20, y + 30), "1932", font=font("anton", 64), fill=CREAM)
        d.text((x1 - 110, y + 30), "1945", font=font("anton", 64), fill=RED if g > 0.98 else (150, 140, 125))
    return cam(img, t, 3, 1.2, 1.0 + 0.02 * a / 8)


def camp(d, t, burn=0.0, ruin=False, people=True):
    d.rectangle([0, 1150, W, H], fill=(58, 50, 42))
    capitol(d, 820, 1000, 0.4, col=(84, 76, 68))
    for i, (x, w, h) in enumerate(((40, 210, 170), (300, 180, 150), (540, 230, 190), (820, 200, 160))):
        shack(d, x, 1180, w, h, burn * (1 if i % 2 == 0 else 0.7), t, ruin)
    if not ruin:
        tent(d, 230, 1250, 170, 140)
        tent(d, 700, 1260, 190, 150)
    if people:
        for i, (x, kind) in enumerate(((150, 0), (380, 1), (430, 2), (620, 0), (900, 1), (960, 2))):
            veteran(d, x, 1360 + (i % 2) * 25, 0.6, 1 if i % 2 else -1, kind=kind)


def scene_camp(t):
    a = t - 25.0
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    camp(d, t)
    return cam(img, t, 4, 1.0, 1.0 + 0.03 * a / 10)


def scene_votes(t):  # the camp with the two votes stamped over it
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    camp(d, t)
    d.rectangle([0, 0, W, H], fill=(0, 0, 0, 90))
    if t > 32.2:
        gm.stamp(img, "HOUSE: PASSED", W / 2, 520, ease_out((t - 32.2) / 0.15), angle=-4, size=100)
    if t > 34.6:
        gm.stamp(img, "SENATE: REJECTED", W / 2, 800, ease_out((t - 34.6) / 0.15), angle=3, size=100)
    amp = 1 + sum(10 * np.exp(-(t - s) * 10) for s in (32.2, 34.6) if t > s)
    return cam(img, t, 5, amp, 1.03)


def scene_clash(t):
    """July 28: police line first (no graphic violence), then federal troops, gas, burning shelters."""
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    troops_in = smoothstep(39.6, 40.6, t)
    camp(d, t, burn=smoothstep(43.8, 45.2, t), people=False)
    if t < 40.2:  # police confrontation, suggested only: two lines, tension
        for i, x in enumerate((140, 250, 360)):
            veteran(d, x, 1380, 0.7, 1, kind=i % 2)
        for i, x in enumerate((700, 820, 940)):
            ef.man(d, x, 1380, 0.7, "cap", -1, col=(60, 66, 84))
            d.rectangle([x - 30, 1380 - 0.7 * 300, x - 10, 1380 - 0.7 * 280], fill=(220, 200, 120))  # badge
    else:
        # veterans retreating left, troops advancing from the right
        r = ease_in_out((t - 40.2) / 4)
        for i, x in enumerate((140, 250, 360)):
            veteran(d, x - 260 * r, 1380, 0.7, -1, kind=i % 2)
        for i, x in enumerate((760, 870, 980)):
            soldier(d, x - 240 * r + (1 - troops_in) * 400, 1400 + (i % 2) * 15, 0.85)
    gas = smoothstep(41.6, 43.0, t)
    if gas > 0:
        img.alpha_composite(smoke_layer(t, gas, (210, 206, 196), 50, 900, 1500))
    smoke = smoothstep(44.0, 45.5, t)
    if smoke > 0:
        img.alpha_composite(smoke_layer(t + 9, smoke * 0.8, (60, 56, 52), 20, 500, 1150))
    return cam(img, t, 6, 1.5 + 2 * troops_in, 1.0 + 0.04 * (t - 35.8) / 10)


def scene_ruins(t):
    a = t - 46.0
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    camp(d, t, ruin=True, people=False)
    img.alpha_composite(smoke_layer(t + 9, 0.6, (60, 56, 52), 12, 500, 1150))
    for i, x in enumerate((300, 420)):  # two veterans looking at what's left
        veteran(d, x, 1380, 0.65, 1, kind=0)
    return cam(img, t, 7, 0.8, 1.0 + 0.05 * a / 5.5)


def scene_1936(t):
    a = t - 51.5
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    bill(d, W / 2, lerp(1300, 820, ease_out(a / 0.6)))
    if t > 55.6:
        gm.stamp(img, "EARLY PAYMENT AUTHORIZED", W / 2, 870, ease_out((t - 55.6) / 0.15), angle=-3, size=70)
    if t > 57.4:
        gm.stamp(img, "VETO OVERRIDDEN", W / 2, 1080, ease_out((t - 57.4) / 0.15), angle=4, size=96)
    amp = 1 + sum(10 * np.exp(-(t - s) * 10) for s in (55.6, 57.4) if t > s)
    return cam(img, t, 8, amp, 1.0 + 0.02 * a / 8)


def scene_end(t):
    a = t - 59.4
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    capitol(d, W / 2, 1250, 1.05, col=(56, 50, 45))
    certificate(d, W / 2, 1120, 0.85)
    if t > 63.8:  # wordmark plate during the final line
        k2 = ease_out_back((t - 63.8) / 0.3, 2.5)
        f = font("anton", int(190 * k2) + 1)
        w = d.textlength("NO WAY.", font=f)
        cy = 520
        d.rectangle([W / 2 - 360, cy - 10, W / 2 + 360, cy + 250], fill=(20, 16, 12, int(235 * min(1, k2))))
        d.text((W / 2 - w / 2, cy + 125 - 125 * k2), "NO WAY.", font=f, fill=(245, 236, 215, 255))
        d.rectangle([W / 2 - 240 * k2, cy + 225, W / 2 + 240 * k2, cy + 238], fill=RED + (255,))
    return cam(img, t, 9, 0.8, 1.0 + 0.03 * a / 5.6)


SCENES = [(0.0, 6.0, scene_open), (6.0, 16.2, scene_travel), (16.2, 25.0, scene_certificate),
          (25.0, 31.6, scene_camp), (31.6, 35.8, scene_votes), (35.8, 46.0, scene_clash), (46.0, 51.5, scene_ruins),
          (51.5, 59.4, scene_1936), (59.4, 65.01, scene_end)]

HEADS = [(0.1, 5.9, [("WASHINGTON,", CREAM), ("1932.", RED)]),
         (22.3, 24.9, [("13 YEARS", CREAM), ("TO WAIT.", RED)]),
         (25.1, 31.4, [("THE BONUS", CREAM), ("ARMY.", AMBER)]),
         (35.9, 39.8, [("JULY 28,", CREAM), ("1932.", RED)]),
         (51.6, 55.4, [("1936.", AMBER)]),
         (60.0, 63.7, [("A CRISIS", CREAM), ("OF TRUST.", RED)])]


def overlay(t):
    for t0, t1, lines in HEADS:
        if t0 <= t < t1:
            layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            zw.headline(ImageDraw.Draw(layer), lines, 180, t, t0 + 0.02, size=130, gap=140)
            return layer
    return None


def mix(a, b, k):
    return a * (1 - k) + b * k


def frame(idx):
    t = idx / FPS
    for i, (t0, t1, fn) in enumerate(SCENES):
        if t0 <= t < t1:
            img = fn(t)
            if i + 1 < len(SCENES) and t > t1 - 0.35:  # slower dissolves for the serious tone
                img = mix(img, SCENES[i + 1][2](t1), smoothstep(t1 - 0.35, t1, t))
            break
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
