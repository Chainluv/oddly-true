"""NO WAY. — Why Tesla Is Called Tesla—And Who Actually Named It. 45s.
Reuses molasses-flood (grade, captions), zanzibar-war (headline, backgrounds, caption timing), bonus-army (caption
grouping) and eiffel-con (figure silhouettes). All imagery is stylized; the motor diagram is simplified."""
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
import episode as zw  # headline(), dark_bg(), paper_bg(), build_chunks()
import bonus as ba    # groups()
import eiffel as ef   # man()

DURATION = 45.0
NFR = int(DURATION * FPS)
AMBER, RED, CREAM = mf.AMBER, (215, 60, 45), (236, 226, 205)
INK = (45, 35, 28)
VOICES = os.path.join(HERE, "voices")

NARR = {"n01": 0.2, "n02": 3.0, "n03": 7.0, "n04": 11.5, "n05": 15.1, "n06": 20.8, "n07": 25.4, "n08": 30.9,
        "n09": 37.5, "n10": 43.6}
TEXT = {"n01": "WHY DID ELON NAME HIS CAR COMPANY TESLA?",
        "n02": "PLOT TWIST: HE DIDN'T CHOOSE THE NAME.",
        "n03": "MARTIN EBERHARD AND MARC TARPENNING STARTED TESLA MOTORS IN 2003.",
        "n04": "MUSK JOINED AS A MAJOR INVESTOR THE FOLLOWING YEAR.",
        "n05": "THE NAME HONORED NIKOLA TESLA, WHOSE NINETEENTH-CENTURY WORK HELPED PIONEER THE AC INDUCTION MOTOR.",
        "n06": "HERE'S THE CONNECTION: THE ORIGINAL TESLA ROADSTER USED AN AC INDUCTION MOTOR.",
        "n07": "IT TURNS A ROTATING MAGNETIC FIELD INTO MOTION. NO GASOLINE COMBUSTION REQUIRED.",
        "n08": "SO THE NAME WASN'T JUST A TRIBUTE TO A FAMOUS INVENTOR. IT CONNECTED DIRECTLY TO THE ENGINEERING "
               "BEHIND THE FIRST CAR.",
        "n09": "THE COMPANY FEELS FUTURISTIC. ITS NAMESAKE WAS WORKING ON THAT PRINCIPLE MORE THAN A CENTURY EARLIER.",
        "n10": "NO WAY."}
zw.LINES = [(k, ba.groups(TEXT[k])) for k in NARR]
zw.NARR = NARR
zw.DUR = {k: sf.info(os.path.join(VOICES, f"{k}.wav")).duration for k in NARR}
zw.SPOKEN = {"2003.": "two thousand three", "AC": "ay see"}
mf.CHUNKS = zw.build_chunks()
mf.KEYWORDS = {"TESLA?", "DIDN'T", "CHOOSE", "EBERHARD", "TARPENNING", "2003.", "INVESTOR", "NIKOLA", "TESLA,",
               "INDUCTION", "MOTOR.", "ROADSTER", "ROTATING", "MAGNETIC", "FIELD", "MOTION.", "DIRECTLY",
               "FIRST", "CAR.", "CENTURY", "EARLIER.", "WAY."}


# ---------------------------------------------------------------- props
def roadster(d, cx, by, s=1.0, wheel_ang=0.0, col=CREAM, line=False):
    """Generic low two-seat electric sports car, side view (stylized, not a technical drawing)."""
    body = [(cx - 330 * s, by - 60 * s), (cx - 320 * s, by - 120 * s), (cx - 150 * s, by - 140 * s),
            (cx - 70 * s, by - 215 * s), (cx + 80 * s, by - 220 * s), (cx + 170 * s, by - 150 * s),
            (cx + 330 * s, by - 125 * s), (cx + 345 * s, by - 70 * s), (cx + 330 * s, by - 40 * s), (cx - 330 * s, by - 40 * s)]
    if line:
        d.line(body + [body[0]], fill=col, width=max(2, int(6 * s)))
    else:
        d.polygon(body, fill=col)
        d.polygon([(cx - 55 * s, by - 200 * s), (cx + 70 * s, by - 204 * s), (cx + 140 * s, by - 148 * s), (cx - 120 * s, by - 142 * s)], fill=(40, 38, 42))
        d.line([(cx - 300 * s, by - 95 * s), (cx + 300 * s, by - 90 * s)], fill=(180, 170, 150), width=max(2, int(4 * s)))
    for wx in (-205, 215):
        x, y, r = cx + wx * s, by - 40 * s, 62 * s
        d.ellipse([x - r, y - r, x + r, y + r], fill=(24, 22, 24), outline=(150, 140, 125), width=max(2, int(5 * s)))
        for k in range(5):
            a = wheel_ang + k * 2 * np.pi / 5
            d.line([(x, y), (x + np.cos(a) * r * 0.75, y + np.sin(a) * r * 0.75)], fill=(170, 160, 145), width=max(2, int(5 * s)))
    return (cx + 215 * s, by - 40 * s)  # rear wheel centre (car faces left)


def tesla_figure(d, cx, by, s=1.0, col=(150, 138, 118)):
    """Stylized 19th-century inventor silhouette: tall, slim, parted hair, moustache, tailcoat."""
    d.polygon([(cx - 60 * s, by), (cx - 70 * s, by - 300 * s), (cx - 50 * s, by - 370 * s), (cx + 50 * s, by - 370 * s),
               (cx + 70 * s, by - 300 * s), (cx + 60 * s, by)], fill=col)
    d.polygon([(cx - 14 * s, by - 370 * s), (cx + 14 * s, by - 370 * s), (cx, by - 300 * s)], fill=CREAM)
    d.ellipse([cx - 40 * s, by - 470 * s, cx + 40 * s, by - 365 * s], fill=col)
    d.chord([cx - 44 * s, by - 480 * s, cx + 44 * s, by - 420 * s], 180, 360, fill=(40, 36, 34))
    d.line([(cx, by - 478 * s), (cx, by - 452 * s)], fill=col, width=max(1, int(3 * s)))      # centre part
    d.chord([cx + 2 * s, by - 405 * s, cx + 52 * s, by - 388 * s], 180, 360, fill=(40, 36, 34))  # moustache


def motor(d, cx, cy, r, t, field_ang=None, rotor_ang=0.0, sketch=0.0):
    """Simplified induction motor: stator ring with 6 coils, squirrel-cage rotor. sketch=1 -> pencil-line style."""
    ink = (60, 50, 40) if sketch > 0.5 else (200, 190, 170)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=ink, width=max(2, int(r * 0.06)))
    for k in range(6):
        a = k * np.pi / 3
        lit = 0.0
        if field_ang is not None:
            diff = np.angle(np.exp(1j * (a - field_ang)))
            lit = max(0.0, np.cos(diff)) ** 4
        x, y = cx + np.cos(a) * r * 0.78, cy + np.sin(a) * r * 0.78
        cw = r * 0.16
        col = (int(lerp(150, 255, lit)), int(lerp(110, 176, lit)), int(lerp(80, 84, lit))) if sketch < 0.5 else (90, 70, 50)
        d.ellipse([x - cw, y - cw, x + cw, y + cw], fill=None if sketch > 0.5 else col, outline=ink, width=max(2, int(r * 0.02)))
        for w in range(3):  # winding marks
            d.arc([x - cw * (0.5 + w * 0.2), y - cw * (0.5 + w * 0.2), x + cw * (0.5 + w * 0.2), y + cw * (0.5 + w * 0.2)], 0, 300, fill=ink, width=1)
    rr = r * 0.42
    d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=None if sketch > 0.5 else (70, 66, 62), outline=ink, width=max(2, int(r * 0.03)))
    for k in range(8):  # rotor bars
        a = rotor_ang + k * np.pi / 4
        d.line([(cx + np.cos(a) * rr * 0.3, cy + np.sin(a) * rr * 0.3), (cx + np.cos(a) * rr * 0.92, cy + np.sin(a) * rr * 0.92)],
               fill=ink if sketch > 0.5 else (190, 180, 160), width=max(2, int(r * 0.03)))
    if field_ang is not None and sketch < 0.5:  # the rotating field itself: an amber arc + arrow (not lightning)
        a0 = np.degrees(field_ang)
        d.arc([cx - r * 0.6, cy - r * 0.6, cx + r * 0.6, cy + r * 0.6], a0 - 40, a0 + 40, fill=AMBER, width=int(r * 0.05))
        ax, ay = cx + np.cos(field_ang) * r * 0.62, cy + np.sin(field_ang) * r * 0.62
        d.ellipse([ax - r * 0.05, ay - r * 0.05, ax + r * 0.05, ay + r * 0.05], fill=AMBER)


def base():
    return to_img(zw.DARK).convert("RGBA")


def cam(img, t, seed, amp=0.6, zoom=1.0, cy=900):
    sx, sy, sr = shake(t, amp, 1.5, seed=seed)
    return from_img(cam2d(img.convert("RGB"), zoom, W / 2, cy, sr, sx, sy))


def text_c(d, txt, y, f, col, a=255):
    tw = d.textlength(txt, font=f)
    d.text(((W - tw) / 2, y), txt, font=f, fill=col + (a,), stroke_width=6, stroke_fill=(15, 12, 10, a))


# ---------------------------------------------------------------- scenes
def scene_hook(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    k = ease_out(t / 0.6)
    roadster(d, lerp(-300, W / 2, k), 1150, 1.15, -t * 6 * (1 - k))
    if t > 1.0:
        a = int(255 * smoothstep(1.0, 1.3, t))
        text_c(d, "ELON NAMED IT?", 480, font("anton", 96), AMBER, a)
        if t > 3.0:  # crossed out
            sk = smoothstep(3.0, 3.3, t)
            d.line([(220, 545), (220 + 640 * sk, 545)], fill=RED + (255,), width=12)
    if t > 3.6:
        a = int(255 * smoothstep(3.6, 4.0, t))
        text_c(d, "THE NAME CAME", 640, font("anton", 100), CREAM, a)
        text_c(d, "BEFORE HE JOINED.", 750, font("anton", 100), RED, a)
    return cam(img, t, 1, 0.5, 1.0 + 0.02 * t / 7)


def scene_timeline(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    d.line([(150, 330), (150, 1180)], fill=(150, 140, 125), width=6)
    rows = [(7.3, 400, "2003", "EBERHARD + TARPENNING", ["FOUND TESLA MOTORS", "NAME PROPOSED BY EBERHARD"], 2),
            (11.8, 820, "2004", "MUSK INVESTS", ["MAJOR EARLY INVESTOR", "LATER ALSO RECOGNIZED AS A CO-FOUNDER"], 1)]
    for t0, y, yr, title, notes, nfig in rows:
        if t < t0:
            continue
        k = ease_out((t - t0) / 0.4)
        a = int(255 * k)
        d.ellipse([130, y - 20, 170, y + 20], fill=RED + (a,))
        d.text((200 - (1 - k) * 60, y - 50), yr, font=font("anton", 96), fill=AMBER + (a,))
        d.text((200, y + 60), title, font=font("anton", 64), fill=CREAM + (a,))
        for i, n in enumerate(notes):
            d.text((200, y + 145 + i * 46), n, font=font("oswaldm", 36), fill=(175, 165, 145, a))
        for i in range(nfig):  # stylized figures, no likeness
            ef.man(d, 820 + i * 130, y + 160, 0.45, "cap" if i else "homburg", -1, col=(150, 138, 118) + (a,))
    return cam(img, t, 2, 0.5, 1.0 + 0.02 * (t - 7) / 8)


def workshop_bg(d):
    d.rectangle([0, 1080, W, H], fill=(60, 46, 34))                     # workbench
    d.rectangle([0, 1060, W, 1090], fill=(90, 68, 48))
    for x, h in ((130, 160), (900, 220)):                              # coils/jars on shelf
        d.rectangle([x - 40, 1060 - h, x + 40, 1060], fill=(110, 90, 60), outline=(170, 150, 110), width=3)
        for k in range(8):
            d.line([(x - 40, 1060 - h + 14 + k * (h - 28) / 8), (x + 40, 1060 - h + 20 + k * (h - 28) / 8)], fill=(200, 140, 70), width=4)


def scene_workshop(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    workshop_bg(d)
    tesla_figure(d, 270, 1080, 1.2)
    # sketch on paper turns into the simplified diagram
    tr = smoothstep(19.6, 21.6, t)
    px0, py0, px1, py1 = 470, 420, 1010, 960
    d.rectangle([px0, py0, px1, py1], fill=(int(lerp(225, 30, tr)), int(lerp(214, 28, tr)), int(lerp(188, 32, tr))), outline=(120, 100, 70), width=4)
    motor(d, (px0 + px1) / 2, (py0 + py1) / 2, 210, t, sketch=1 - tr)
    if t > 15.4:
        a = int(255 * smoothstep(15.4, 15.9, t))
        text_c(d, "NIKOLA TESLA", 180, font("anton", 110), CREAM, a)
        sub = "PIONEER OF AC INDUCTION MOTORS"
        f = font("oswaldm", 44)
        tw = d.textlength(sub, font=f)
        d.text(((W - tw) / 2, 315), sub, font=f, fill=AMBER + (a,))
    return cam(img, t, 3, 0.4, 1.0 + 0.03 * (t - 15) / 10)


def field_angle(t):
    return (t - 25.0) * 2 * np.pi * 0.6 * smoothstep(25.0, 26.0, t) - np.pi / 2


def rotor_angle(t):
    # rotor follows the field, lagging slightly (slip), and spins up
    spin = np.clip((t - 26.0) / 2.0, 0, 1)
    return (t - 25.0) * 2 * np.pi * 0.55 * spin


def scene_field(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    if t < 31.2:
        motor(d, W / 2, 820, 360, t, field_angle(t), rotor_angle(t))
        d.text((70, 1210), "SIMPLIFIED", font=font("anton", 54), fill=RED)
        f = font("anton", 64)
        if t > 26.2:
            text_c(d, "ROTATING MAGNETIC FIELD", 260, f, AMBER, int(255 * smoothstep(26.2, 26.6, t)))
        if t > 28.6:
            text_c(d, "ROTOR TURNS", 340, font("anton", 56), CREAM, int(255 * smoothstep(28.6, 29.0, t)))
        return cam(img, t, 4, 0.3)
    # zoom out: motor drives the rear wheels of the original Roadster
    k = ease_in_out((t - 31.2) / 1.4)
    rear = roadster(d, W / 2 - 40, 1120, 1.25, -rotor_angle(t) * 0.3)
    mx, my = lerp(W / 2, rear[0] - 90, k), lerp(820, rear[1] - 150, k)
    mr = lerp(360, 70, k)
    if k < 0.98:
        d.rectangle([0, 0, W, H], fill=(14, 12, 10, int(200 * (1 - k))))
    motor(d, mx, my, mr, t, field_angle(t), rotor_angle(t))
    if k > 0.9:
        d.line([(mx, my), (rear[0], rear[1])], fill=AMBER, width=8)
        a = int(255 * smoothstep(32.6, 33.0, t))
        text_c(d, "ORIGINAL ROADSTER:", 430, font("anton", 72), CREAM, a)
        text_c(d, "AC INDUCTION MOTOR", 520, font("anton", 72), AMBER, a)
        d.text((70, 700), "SIMPLIFIED", font=font("anton", 48), fill=RED + (a,))
    return cam(img, t, 4, 0.3)


def scene_end(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    k = smoothstep(36.6, 39.0, t)
    # 19th-century-style motor illustration -> the Roadster
    if k < 1:
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        ld.rectangle([180, 560, 900, 1120], fill=(225, 214, 188))
        motor(ld, 540, 840, 230, t, sketch=1.0)
        ld.text((210, 1070), "c. 1890s-style illustration", font=font("oldi", 30), fill=(110, 90, 70))
        layer.putalpha(layer.getchannel("A").point(lambda v: int(v * (1 - k))))
        img.alpha_composite(layer)
    if k > 0:
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        roadster(ImageDraw.Draw(layer), W / 2, 1110, 1.25, -(t - 36) * 5)
        layer.putalpha(layer.getchannel("A").point(lambda v: int(v * k)))
        img.alpha_composite(layer)
    d = ImageDraw.Draw(img, "RGBA")
    if 38.0 <= t < 43.5:
        a = int(255 * smoothstep(38.0, 38.4, t))
        text_c(d, "OLD PRINCIPLE.", 300, font("anton", 110), CREAM, a)
        b = int(255 * smoothstep(38.8, 39.2, t))
        text_c(d, "NEW APPLICATION.", 420, font("anton", 110), RED, b)
    if t > 43.6:
        k2 = ease_out_back((t - 43.6) / 0.3, 2.5)
        f = font("anton", int(190 * k2) + 1)
        w = d.textlength("NO WAY.", font=f)
        cy = 330
        d.rectangle([W / 2 - 360, cy - 10, W / 2 + 360, cy + 250], fill=(20, 16, 12, int(235 * min(1, k2))))
        d.text((W / 2 - w / 2, cy + 125 - 125 * k2), "NO WAY.", font=f, fill=(245, 236, 215, 255))
        d.rectangle([W / 2 - 240 * k2, cy + 225, W / 2 + 240 * k2, cy + 238], fill=RED + (255,))
    return cam(img, t, 5, 0.3, 1.0 + 0.02 * (t - 35) / 10)


SCENES = [(0.0, 7.0, scene_hook), (7.0, 15.0, scene_timeline), (15.0, 25.0, scene_workshop),
          (25.0, 35.0, scene_field), (35.0, 45.01, scene_end)]


def overlay(t):
    if 0.05 <= t < 6.9:
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        zw.headline(ImageDraw.Draw(layer), [("WHY TESLA?", CREAM)], 220, t, 0.05, size=150, gap=150)
        return layer
    return None


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
    out = grade(img, idx, t)
    if t > 44.6:
        out = out * (1 - smoothstep(44.6, 45.0, t) * 0.9)
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
