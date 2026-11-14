"""NO WAY. — London Was Flooded With Beer. Eight People Died. (London Beer Flood, 17 Oct 1814). 50s.
Reuses molasses-flood (3D street + wave engine, grade, captions), zanzibar-war (headline, backgrounds, caption
timing), bonus-army (caption grouping) and rap-grammy (stamp). All scenes are stylized reconstructions."""
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
import street as stt  # 3D street + wave

# 1814 London: no trolley rails, no shop signs, no elevated railway in view
stt.RAILS[:] = []
stt.SEG_SIGN[:] = -1

DURATION = 50.0
NFR = int(DURATION * FPS)
AMBER, RED, CREAM = mf.AMBER, (205, 55, 40), (236, 226, 205)
PORTER = (62, 34, 18)
VOICES = os.path.join(HERE, "voices")

NARR = {"n01": 0.15, "n02": 2.25, "n03": 4.9, "n04": 10.3, "n05": 14.7, "n06": 20.6, "n07": 26.2, "n08": 29.0,
        "n09": 32.6, "n10": 35.6, "n11": 40.6, "n12": 45.1, "n13": 48.4}
TEXT = {"n01": "LONDON ONCE DROWNED IN BEER.",
        "n02": "LITERALLY. PART OF IT.",
        "n03": "ON OCTOBER 17TH, 1814, A 22-FOOT WOODEN VAT BURST AT THE HORSE SHOE BREWERY.",
        "n04": "THE ESCAPING PORTER DAMAGED OTHER CONTAINERS, UNLEASHING EVEN MORE BEER.",
        "n05": "SOME ESTIMATES PUT THE TOTAL AT UP TO 323,000 IMPERIAL GALLONS.",
        "n06": "A WAVE REPORTEDLY 15 FEET HIGH SMASHED INTO THE CROWDED NEIGHBORHOOD OF ST GILES.",
        "n07": "THIS WASN'T BEER TRICKLING DOWN A PUB FLOOR.",
        "n08": "BUILDINGS WERE DAMAGED. HOMES FLOODED.",
        "n09": "EIGHT PEOPLE DIED.",
        "n10": "WHAT SOUNDS LIKE A RIDICULOUS DRINKING STORY WAS ACTUALLY AN INDUSTRIAL DISASTER.",
        "n11": "A GIANT STORAGE VAT. A CHAIN REACTION. A NEIGHBORHOOD CAUGHT IN THE PATH.",
        "n12": "LONDON'S BEER FLOOD WAS REAL.",
        "n13": "NO WAY."}
zw.LINES = [(k, ba.groups(TEXT[k])) for k in NARR]
zw.NARR = NARR
zw.DUR = {k: sf.info(os.path.join(VOICES, f"{k}.wav")).duration for k in NARR}
zw.SPOKEN = {"17TH,": "seventeenth", "1814,": "eighteen fourteen", "22-FOOT": "twenty two foot",
             "323,000": "three hundred twenty three thousand", "15": "fifteen", "ST": "saint"}
mf.CHUNKS = zw.build_chunks()
mf.KEYWORDS = {"BEER.", "PART", "1814,", "22-FOOT", "VAT", "BURST", "PORTER", "MORE", "UP", "TO", "323,000",
               "15", "FEET", "GILES.", "DAMAGED.", "FLOODED.", "EIGHT", "DIED.", "INDUSTRIAL", "DISASTER.",
               "CHAIN", "REACTION.", "REAL.", "WAY."}

T_BURST = 9.3
T_DIED = 32.6


# ---------------------------------------------------------------- helpers
def base():
    return to_img(zw.DARK).convert("RGBA")


def cam(img, t, seed, amp=0.6, zoom=1.0, cy=900, cx=W / 2):
    sx, sy, sr = shake(t, amp, 1.5, seed=seed)
    return from_img(cam2d(img.convert("RGB"), zoom, cx, cy, sr, sx, sy))


def text_c(d, txt, y, f, col, a=255, stroke=6):
    tw = d.textlength(txt, font=f)
    d.text(((W - tw) / 2, y), txt, font=f, fill=col + (a,), stroke_width=stroke, stroke_fill=(15, 12, 10, a))


def street_shot(t, wave_z, cam_z, wave_h, ch=4.5, yh=1300, f=1000, shake_amp=8, spray=True):
    st = stt.Street(f=f, yh=yh, ch=ch, camX=-3, camZ=cam_z, time=t, wave_z=wave_z, wave_h=wave_h, el_c=900.0, fog=330)
    img = st.render()
    if spray:
        img = stt.draw_spray(img, st, n=90)
    sx, sy, sr = shake(t, shake_amp, 11, seed=2)
    return from_img(cam2d(to_img(img), 1.04, W / 2, H / 2, sr, sx, sy))


def houses(d, x0, by, n, w=180, h=360, damage=0.0, seed=1):
    """Row of plain Georgian brick houses (side elevation)."""
    rng = np.random.default_rng(seed)
    for i in range(n):
        x = x0 + i * w
        hh = h + rng.integers(-30, 40)
        d.rectangle([x, by - hh, x + w - 6, by], fill=(118, 92, 72), outline=(70, 54, 42), width=3)
        d.rectangle([x - 4, by - hh - 14, x + w - 2, by - hh], fill=(70, 60, 54))
        d.rectangle([x + w * 0.6, by - hh - 60, x + w * 0.75, by - hh - 14], fill=(80, 66, 56))  # chimney
        for fl in range(3):
            for c in range(2):
                wx, wy = x + 28 + c * (w / 2 - 6), by - hh + 30 + fl * (hh / 3.2)
                broken = damage > 0 and rng.random() < damage
                d.rectangle([wx, wy, wx + 46, wy + 64], fill=(36, 32, 30) if not broken else (24, 20, 18), outline=(200, 190, 170), width=3)
                if broken:
                    d.line([(wx + 4, wy + 6), (wx + 40, wy + 58)], fill=(150, 140, 120), width=2)
                    d.line([(wx + 40, wy + 8), (wx + 10, wy + 40)], fill=(150, 140, 120), width=2)
        if damage > 0 and rng.random() < damage * 1.2:  # structural crack
            pts = [(x + w * 0.5, by - hh + 10)]
            for k in range(6):
                pts.append((pts[-1][0] + rng.integers(-18, 18), pts[-1][1] + hh / 7))
            d.line(pts, fill=(40, 30, 24), width=4)


def porter_band(d, x0, x1, y_top, by, t, a=255):
    """Dark brown porter surface: no foam, a thin darker crest and faint amber sheen."""
    pts = [(x, y_top + 10 * np.sin(x * 0.02 + t * 3) + 6 * np.sin(x * 0.05 - t * 5)) for x in range(int(x0), int(x1) + 20, 20)]
    d.polygon(pts + [(x1, by), (x0, by)], fill=PORTER + (a,))
    d.line(pts, fill=(40, 20, 10, a), width=6)
    for k in range(6):
        y = y_top + 40 + k * 50
        if y < by - 10:
            d.line([(x0 + 40 + k * 70, y), (x0 + 200 + k * 70, y + 4)], fill=(150, 90, 40, int(a * 0.35)), width=3)


def vat(d, cx, by, h, w, crack=0.0, t=0.0):
    """Huge wooden vat with iron hoops."""
    x0, x1 = cx - w / 2, cx + w / 2
    d.rectangle([x0, by - h, x1, by], fill=(122, 86, 56))
    for k in range(1, 9):
        x = x0 + k * w / 9
        d.line([(x, by - h), (x, by)], fill=(96, 66, 42), width=3)
    for k in range(7):
        y = by - h + 30 + k * (h - 40) / 6
        snapped = crack > 0 and k == 1
        if snapped:  # the snapped hoop flies off
            a = min(1.0, crack * 2)
            d.arc([x1 - 30 + a * 80, y - 60 - a * 140, x1 + 90 + a * 80, y + 60 - a * 140], 200, 340, fill=(60, 60, 64), width=10)
        else:
            d.line([(x0 - 6, y), (x1 + 6, y)], fill=(60, 60, 64), width=12)
    d.ellipse([x0, by - h - 30, x1, by - h + 30], fill=(100, 70, 46), outline=(60, 60, 64), width=8)
    if crack > 0:  # split staves and porter bursting out
        k = min(1.0, crack)
        d.polygon([(x1 - 40, by - h * 0.7), (x1 + 4, by - h * 0.72), (x1 + 4, by - h * 0.1), (x1 - 30, by - h * 0.15)], fill=(40, 22, 12))
        reach = 600 * k
        d.polygon([(x1, by - h * 0.7), (x1 + reach, by - h * 0.25 - 60 * np.sin(t * 6)), (x1 + reach + 80, by), (x1, by)], fill=PORTER + (255,))
        d.line([(x1, by - h * 0.7), (x1 + reach, by - h * 0.25 - 60 * np.sin(t * 6))], fill=(150, 90, 40, 140), width=4)


# ---------------------------------------------------------------- scenes
def scene_hook(t):
    if t < 3.1:  # porter surging between London houses
        wz = 95 * (1 - (t / 3.3) ** 1.3) + 6
        return street_shot(t, wz, -t * 3, 18, ch=4.2, yh=1250, shake_amp=3 + 8 * smoothstep(1.5, 3.0, t))
    # pull back: a neighbourhood, not the whole city
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    k = ease_out((t - 3.1) / 1.5)
    p = to_img(zw.paper_bg(4, (0.84, 0.78, 0.64))).crop((0, 0, W, 1140))
    img.paste(p, (0, 140))
    d = ImageDraw.Draw(img, "RGBA")
    thames = [(0, 1040), (200, 1000), (420, 1060), (640, 990), (860, 1050), (1080, 1000)]
    d.line(thames, fill=(120, 140, 150), width=46, joint="curve")
    for i in range(40):  # street grid suggestion
        x = 40 + (i % 8) * 130
        y = 260 + (i // 8) * 140
        d.rectangle([x, y, x + 100, y + 100], outline=(150, 135, 110), width=2)
    zx, zy = 430, 520
    r = 70
    d.ellipse([zx - r, zy - r, zx + r, zy + r], fill=PORTER + (220,), outline=RED, width=6)
    d.text((zx + 90, zy - 30), "ST GILES", font=font("anton", 64), fill=RED)
    d.text((60, 1220), "LONDON (STYLIZED MAP)", font=font("oldb", 34), fill=(90, 75, 60))
    d.text((660, 980), "THAMES", font=font("oldi", 36), fill=(70, 85, 95))
    return cam(img, t, 1, 0.3, lerp(2.4, 1.0, k), lerp(zy, 760, k) if True else 760, lerp(zx, W / 2, k))


def scene_failure(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    if t < 6.8:  # the brewery exterior
        d.rectangle([0, 1180, W, H], fill=(46, 40, 34))
        d.rectangle([160, 520, 920, 1180], fill=(104, 78, 60), outline=(60, 46, 36), width=5)
        d.rectangle([780, 300, 860, 520], fill=(80, 62, 50))                      # chimney
        for c in range(5):
            for fl in range(3):
                d.rectangle([210 + c * 140, 600 + fl * 170, 270 + c * 140, 690 + fl * 170], fill=(32, 28, 26), outline=(190, 180, 160), width=3)
        d.rectangle([240, 540, 840, 590], fill=(36, 30, 26))
        tw = d.textlength("HORSE SHOE BREWERY", font=font("oldb", 40))
        d.text(((W - tw) / 2, 545), "HORSE SHOE BREWERY", font=font("oldb", 40), fill=CREAM)
        d.text((330, 1110), "MEUX & CO.  ·  reconstruction", font=font("oldi", 30), fill=(200, 190, 170))
        return cam(img, t, 2, 0.4, 1.0 + 0.04 * (t - 4.8) / 2)
    # inside: the vat, the 22-ft marker, the rupture and chain reaction
    d.rectangle([0, 1180, W, H], fill=(52, 44, 36))
    crack = smoothstep(T_BURST, T_BURST + 1.2, t)
    chain = smoothstep(10.8, 13.6, t)
    for i, (x, h) in enumerate(((800, 380), (960, 320))):  # neighbouring containers
        hit = chain > (0.3 + 0.4 * i)
        vat(d, x, 1180, h, 150, crack=1.0 if hit else 0.0, t=t + i)
    vat(d, 400, 1180, 760, 420, crack=crack, t=t)
    # height marker
    d.line([(130, 420), (130, 1180)], fill=CREAM, width=5)
    for y in (420, 1180):
        d.line([(110, y), (150, y)], fill=CREAM, width=5)
    d.text((40, 760), "22", font=font("anton", 72), fill=CREAM)
    d.text((40, 840), "FEET", font=font("anton", 40), fill=CREAM)
    if crack > 0:
        fl = max(0.0, 1 - (t - T_BURST) / 0.25)
        if fl > 0:
            d.rectangle([0, 0, W, H], fill=(255, 245, 220, int(110 * fl)))
    amp = 0.4 + (16 * np.exp(-(t - T_BURST) * 5) if t >= T_BURST else 0) + 4 * chain * (t < 14)
    return cam(img, t, 3, amp, 1.0 + 0.03 * (t - 6.8) / 7)


def scene_scale(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    grow = ease_out((t - 14.5) / 2.5)
    yl = lerp(1320, 380, grow)
    porter_band(d, -20, W + 20, yl, H, t)
    a = int(255 * smoothstep(15.6, 16.1, t))
    text_c(d, "UP TO", 560, font("anton", 90), CREAM, a)
    text_c(d, "323,000", 660, font("anton", 230), AMBER, a, 9)
    text_c(d, "GALLONS", 900, font("anton", 120), CREAM, a)
    text_c(d, "IMPERIAL • UPPER ESTIMATE", 1050, font("anton", 56), (230, 210, 180), a)
    return cam(img, t, 4, 0.4, 1.0 + 0.02 * (t - 14.5) / 6)


def scene_wave(t):
    if t < 24.4:  # the wave heading into St Giles
        a = t - 20.4
        wz = 70 - a * 17 - a * a * 1.2 + 4
        return street_shot(t, wz, -a * 2, 15, ch=4.5, yh=1280, shake_amp=3 + 5 * smoothstep(22, 24.3, t))
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    by = 1180
    d.rectangle([0, by, W, H], fill=(46, 40, 34))
    houses(d, 80, by, 5, 190, 470)
    # comparison: a person-height scale and the reported 15-ft crest
    px = 60
    d.line([(px, by), (px, by - 95)], fill=CREAM, width=6)                               # 6 ft ~ 95 px here
    d.ellipse([px - 12, by - 120, px + 12, by - 96], fill=CREAM)
    k = ease_out((t - 24.4) / 0.9)
    crest = by - 240 * k                                                                  # 15 ft ~ 240 px
    porter_band(d, -20, W + 20, crest, by + 40, t, 235)
    d.line([(990, by), (990, by - 240)], fill=RED, width=6)
    for y in (by, by - 240):
        d.line([(970, y), (1010, y)], fill=RED, width=6)
    d.text((820, by - 300), "15 FT", font=font("anton", 56), fill=RED)
    d.text((60, 560), "ILLUSTRATION", font=font("anton", 48), fill=(200, 185, 160))
    return cam(img, t, 5, 0.5 + 3 * np.exp(-(t - 24.4) * 3), 1.0)


def scene_cost(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    by = 900
    d.rectangle([0, by, W, H], fill=(40, 34, 30))
    houses(d, 40, by, 5, 200, 420, damage=0.45, seed=7)
    # cross-section: flooded basement rooms below street level (no people shown)
    for i in range(5):
        x = 40 + i * 200
        d.rectangle([x + 6, by + 20, x + 194, by + 230], fill=(60, 52, 46), outline=(30, 26, 22), width=4)
        d.rectangle([x + 70, by + 120, x + 120, by + 230], fill=(30, 26, 22))           # doorway
        lvl = smoothstep(29.2 + i * 0.25, 31.0 + i * 0.25, t)
        d.rectangle([x + 10, by + 226 - 190 * lvl, x + 190, by + 226], fill=PORTER + (240,))
    d.line([(0, by), (W, by)], fill=(110, 95, 80), width=6)
    d.text((40, by + 250), "STREET LEVEL / BASEMENTS · ILLUSTRATION", font=font("oswaldm", 34), fill=(170, 155, 135))
    dim = 1 - 0.2 * smoothstep(T_DIED - 0.3, T_DIED + 0.4, t)
    out = cam(img, t, 6, 0.25, 1.0 + 0.03 * (t - 29) / 6.4, cy=900)
    return out * dim


def arrow_down(d, cx, y0, y1, col):
    d.line([(cx, y0), (cx, y1 - 18)], fill=col, width=8)
    d.polygon([(cx - 22, y1 - 26), (cx + 22, y1 - 26), (cx, y1)], fill=col)


def scene_chain(t):
    img = base()
    d = ImageDraw.Draw(img, "RGBA")
    if t < 44.8:
        steps = [("VAT FAILURE", 36.2), ("CHAIN REACTION", 37.6), ("FLOODED HOMES", 39.0)]
        for i, (txt, t0) in enumerate(steps):
            if t < t0:
                continue
            k = ease_out((t - t0) / 0.35)
            a = int(255 * k)
            y = 360 + i * 300
            f = font("anton", 96)
            tw = d.textlength(txt, font=f)
            d.rounded_rectangle([W / 2 - tw / 2 - 36, y - 10, W / 2 + tw / 2 + 36, y + 128], 20, fill=(24, 20, 16, int(230 * k)), outline=(RED if i == 2 else CREAM) + (a,), width=5)
            d.text((W / 2 - tw / 2, y), txt, font=f, fill=(RED if i == 2 else CREAM) + (a,))
            if i < 2 and t > t0 + 0.5:
                arrow_down(d, W / 2, y + 140, y + 290, AMBER + (int(255 * smoothstep(t0 + 0.5, t0 + 0.9, t)),))
        return cam(img, t, 7, 0.3)
    # brewery silhouette, the date, the title, the wordmark
    d.rectangle([0, 1180, W, H], fill=(30, 26, 22))
    d.rectangle([180, 760, 900, 1180], fill=(58, 46, 38))
    d.rectangle([780, 560, 860, 760], fill=(58, 46, 38))
    a = int(255 * smoothstep(44.9, 45.4, t))
    text_c(d, "THE LONDON", 830, font("anton", 120), CREAM, a)
    text_c(d, "BEER FLOOD", 960, font("anton", 120), RED, a)
    text_c(d, "OCTOBER 17, 1814  ·  ST GILES", 1110, font("oswaldm", 44), (210, 195, 170), a)
    if t > 48.4:
        k2 = ease_out_back((t - 48.4) / 0.3, 2.5)
        f = font("anton", int(190 * k2) + 1)
        w = d.textlength("NO WAY.", font=f)
        cy = 300
        d.rectangle([W / 2 - 360, cy - 10, W / 2 + 360, cy + 250], fill=(20, 16, 12, int(235 * min(1, k2))))
        d.text((W / 2 - w / 2, cy + 125 - 125 * k2), "NO WAY.", font=f, fill=(245, 236, 215, 255))
        d.rectangle([W / 2 - 240 * k2, cy + 225, W / 2 + 240 * k2, cy + 238], fill=RED + (255,))
    return cam(img, t, 8, 0.2, 1.0 + 0.02 * (t - 44.8) / 5)


SCENES = [(0.0, 4.8, scene_hook), (4.8, 14.5, scene_failure), (14.5, 20.4, scene_scale), (20.4, 29.0, scene_wave),
          (29.0, 35.4, scene_cost), (35.4, 50.01, scene_chain)]

HEADS = [(0.05, 3.05, [("LONDON FLOODED", CREAM), ("WITH BEER.", AMBER)]),
         (4.9, 8.4, [("OCTOBER 17,", CREAM), ("1814.", RED)]),
         (24.5, 28.9, [("15-FOOT WAVE", CREAM), ("REPORTED HEIGHT", (215, 200, 175))]),
         (T_DIED, 35.3, [("8 PEOPLE", CREAM), ("DIED.", RED)])]


def overlay(t):
    for t0, t1, lines in HEADS:
        if t0 <= t < t1:
            layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            big = 140 if lines[0][0].startswith("LONDON") else 130
            if lines[1][0] == "REPORTED HEIGHT":  # the qualifier is smaller but readable
                zw.headline(ImageDraw.Draw(layer), lines[:1], 180, t, t0 + 0.02, size=130, gap=140)
                ld = ImageDraw.Draw(layer)
                a = int(255 * smoothstep(t0 + 0.3, t0 + 0.6, t))
                text_c(ld, "REPORTED HEIGHT", 335, font("anton", 62), (230, 212, 182), a)
                return layer
            zw.headline(ImageDraw.Draw(layer), lines, 180, t, t0 + 0.02, size=big, gap=big + 12)
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
    if t > 49.6:
        out = out * (1 - smoothstep(49.6, 50.0, t) * 0.9)
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
