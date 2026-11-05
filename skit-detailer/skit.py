"""NO WAY. skit — The Detailer's Worst Nightmare (30s, 1080x1920, 30 fps).
Illustrated animation drawn in code: shop, SUV interior, detailer (lip-synced to his voice track), carpet close-ups,
phone-call UI, word-synced captions and the NO WAY. outro. Reuses fonts/camera helpers from molasses-flood."""
import os
import subprocess
import sys
from multiprocessing import Pool

import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "molasses-flood"))
from common import W, H, font, to_img, from_img, cam2d, shake, lerp, smoothstep, ease_in_out, ease_out, ease_out_back, VIGNETTE, GRAIN  # noqa: E402

FPS = 30
DURATION = 30.0
NFR = int(FPS * DURATION)
AMBER = (255, 184, 64)
FRIEND_COL = (150, 215, 255)
VOICE_DIR = os.environ.get("SKIT_VOICES", os.path.join(HERE, "voices"))

# (id, speaker, start time, caption groups)
LINES = [
    ("f1", "F", 0.7, [["YO,", "YOU", "ALMOST", "DONE?"], ["WE", "STILL", "GOING", "OUT?"]]),
    ("d1", "D", 3.2, [["NAH,", "BRO."], ["I'M", "COOKED."]]),
    ("f2", "F", 6.1, [["WHAT", "HAPPENED?"]]),
    ("d2", "D", 7.1, [["GOT", "THE", "OLD"], ["DOG", "HAIR,"], ["BEACH", "SAND", "COMBO."]]),
    ("f3", "F", 11.3, [["DAMN."], ["BOTH?"]]),
    ("d3", "D", 12.6, [["BOTH,", "BRO."]]),
    ("f4", "F", 15.0, [["SO", "WHEN", "YOU"], ["GETTING", "OUT?"]]),
    ("d4", "D", 16.4, [["I", "BEEN", "VACUUMING"], ["THE", "SAME"], ["SQUARE", "FOOT"], ["FOR", "45", "MINUTES."]]),
    ("d5", "D", 21.6, [["I", "THINK", "THIS", "DOG"], ["LIVED", "AT", "THE", "BEACH."]]),
    ("f5", "F", 24.4, [["SO…", "TOMORROW?"]]),
    ("d6", "D", 27.0, [["I'LL", "CALL", "YOU"], ["NEXT", "WEEK."]]),
]
SPOKEN = {"45": "forty five"}
KEYWORDS = {"COOKED.", "DOG", "HAIR,", "BEACH", "SAND", "COMBO.", "BOTH?", "BOTH,", "SAME", "45", "MINUTES.",
            "BEACH.", "NEXT", "WEEK."}
OUTRO_T = 28.6


def _dur(lid):
    return sf.info(os.path.join(VOICE_DIR, f"{lid}.wav")).duration


def build_chunks():
    out = []
    for lid, spk, t0, groups in LINES:
        words = [w for g in groups for w in g]
        wts = [len(SPOKEN.get(w, w)) + 2 for w in words]
        d = _dur(lid) - 0.15
        t = t0 + 0.05
        times = []
        for wt in wts:
            dt = d * wt / sum(wts)
            times.append((t, t + dt))
            t += dt
        i = 0
        for g in groups:
            out.append((spk, [(w, *times[i + k]) for k, w in enumerate(g)]))
            i += len(g)
    res = []
    for k, (spk, ws) in enumerate(out):
        end = ws[-1][2] + 0.35
        if k + 1 < len(out):
            end = min(end, out[k + 1][1][0][1] - 0.04)
        res.append((ws[0][1] - 0.04, min(end, OUTRO_T), spk, ws))
    return res


def envelope(speaker):
    """Per-frame mouth/talk amplitude for one speaker (drives lip-sync and the phone waveform)."""
    env = np.zeros(NFR)
    for lid, spk, t0, _ in LINES:
        if spk != speaker:
            continue
        a, sr = sf.read(os.path.join(VOICE_DIR, f"{lid}.wav"))
        hop = sr // FPS
        for i in range(len(a) // hop):
            fi = int(t0 * FPS) + i
            if fi < NFR:
                env[fi] = np.sqrt(np.mean(a[i * hop:(i + 1) * hop] ** 2))
    env = env / (env.max() + 1e-9)
    return np.clip(env * 1.8, 0, 1)


CHUNKS = MOUTH = FRIEND = None
SHOP = SHOP_BLUR = CARPET = None


# ---------------------------------------------------------------- environment art
def build_shop():
    img = Image.new("RGB", (W, H), (62, 70, 80))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 380], fill=(48, 54, 62))                                        # ceiling
    for x in range(-100, W, 330):                                                         # LED panels
        d.rectangle([x, 120, x + 230, 160], fill=(245, 248, 255))
    d.rectangle([0, 380, W, 1500], fill=(70, 78, 90))                                     # wall
    for y in (620, 820, 1020):                                                            # shelves + bottles
        d.rectangle([40, y, W - 40, y + 14], fill=(40, 44, 50))
        x = 60
        k = 0
        while x < W - 80:
            col = [(220, 60, 50), (60, 140, 220), (240, 200, 60), (70, 190, 110), (230, 230, 235), (150, 90, 200)][k % 6]
            hgt = 90 + (k * 37) % 50
            d.rounded_rectangle([x, y - hgt, x + 46, y], 8, fill=col)
            d.rectangle([x + 14, y - hgt - 22, x + 32, y - hgt], fill=(30, 30, 34))
            d.rectangle([x + 6, y - hgt * 0.6, x + 40, y - hgt * 0.35], fill=(245, 245, 245))
            x += 64 + (k * 13) % 20
            k += 1
    d.rectangle([0, 1500, W, H], fill=(110, 116, 124))                                     # epoxy floor
    for x in range(-100, W, 330):
        d.rectangle([x + 20, 1560, x + 210, 1600], fill=(160, 166, 175))                   # light reflections
    d.rounded_rectangle([780, 1250, 1000, 1520], 20, fill=(200, 40, 40))                   # extractor machine
    d.rectangle([800, 1290, 980, 1320], fill=(40, 40, 44))
    d.text((812, 1340), "EXTRACTOR", font=font("oswaldm", 34), fill=(255, 235, 235))
    return img


def build_carpet():
    """Big carpet texture with embedded dog hair and beach sand (1.6x for crash zooms)."""
    CW, CH = int(W * 1.6), int(H * 1.6)
    rng = np.random.default_rng(3)
    base = rng.normal(0, 1, (CH // 3, CW // 3)).astype(np.float32)
    base = np.asarray(Image.fromarray(base).resize((CW, CH), Image.BILINEAR))
    v = 0.22 + 0.05 * base
    img = Image.fromarray(np.clip(np.stack([v, v, v * 1.05], -1) * 255, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    for _ in range(26000):                                                                 # carpet loops
        x, y = rng.integers(0, CW), rng.integers(0, CH)
        c = int(40 + rng.integers(0, 30))
        d.ellipse([x, y, x + 5, y + 5], fill=(c, c, c + 4))
    for _ in range(1800):                                                                  # dog hair
        x, y = rng.uniform(0, CW), rng.uniform(0, CH)
        L, a = rng.uniform(25, 70), rng.uniform(0, 6.28)
        pts = [(x + np.cos(a + s * 0.6) * L * s, y + np.sin(a + s * 0.6) * L * s) for s in np.linspace(0, 1, 6)]
        col = [(225, 205, 170), (240, 235, 225), (190, 150, 105)][rng.integers(0, 3)]
        d.line(pts, fill=col, width=2)
    for _ in range(9000):                                                                  # sand grains
        x, y = rng.integers(0, CW), rng.integers(0, CH)
        r = rng.uniform(1.2, 3.2)
        c = (int(rng.uniform(200, 235)), int(rng.uniform(175, 200)), int(rng.uniform(120, 150)))
        d.ellipse([x - r, y - r, x + r, y + r], fill=c)
    return img


SAND_RNG = np.random.default_rng(8)
EXTRA_SAND = [(SAND_RNG.uniform(200, 880), SAND_RNG.uniform(700, 1250), SAND_RNG.uniform(2, 5)) for _ in range(1500)]


# ---------------------------------------------------------------- the detailer
SKIN, SKIN_D, HAIR, SHIRT = (196, 146, 110), (160, 112, 82), (38, 28, 22), (24, 24, 26)


def face(d, cx, cy, s, mouth, blink, mood=0.0, look=0.0, beard=True):
    """Front-facing close-up. mouth 0..1, blink 0..1, mood 0 tired .. 1 defeated, look -1..1 (eyes down = +)."""
    # shoulders + black work shirt
    d.polygon([(cx - 420 * s, cy + 900 * s), (cx - 380 * s, cy + 520 * s), (cx - 120 * s, cy + 400 * s),
               (cx + 120 * s, cy + 400 * s), (cx + 380 * s, cy + 520 * s), (cx + 420 * s, cy + 900 * s)], fill=SHIRT)
    d.polygon([(cx - 120 * s, cy + 400 * s), (cx, cy + 520 * s), (cx + 120 * s, cy + 400 * s)], fill=(40, 40, 44))  # collar
    d.rectangle([cx - 90 * s, cy + 300 * s, cx + 90 * s, cy + 420 * s], fill=SKIN_D)                              # neck
    d.text((cx + 150 * s, cy + 600 * s), "DETAIL", font=font("oswald", int(46 * s)), fill=(150, 150, 155))
    # head
    d.ellipse([cx - 230 * s, cy - 300 * s, cx + 230 * s, cy + 340 * s], fill=SKIN)
    for sx in (-1, 1):  # ears
        d.ellipse([cx + sx * 215 * s - 40 * s, cy - 40 * s, cx + sx * 215 * s + 40 * s, cy + 90 * s], fill=SKIN)
    d.ellipse([cx + 200 * s, cy + 10 * s, cx + 236 * s, cy + 46 * s], fill=(245, 245, 245))                        # earbud
    # stubble / beard shadow
    if beard:
        d.chord([cx - 215 * s, cy - 40 * s, cx + 215 * s, cy + 340 * s], 0, 180, fill=(150, 108, 80))
        d.ellipse([cx - 150 * s, cy + 40 * s, cx + 150 * s, cy + 240 * s], fill=SKIN)
    # hair (short fade)
    d.chord([cx - 235 * s, cy - 320 * s, cx + 235 * s, cy + 40 * s], 180, 360, fill=HAIR)
    d.rectangle([cx - 236 * s, cy - 150 * s, cx - 205 * s, cy - 20 * s], fill=HAIR)
    d.rectangle([cx + 205 * s, cy - 150 * s, cx + 236 * s, cy - 20 * s], fill=HAIR)
    # eyes: heavy lids, bags
    lid = 0.45 + 0.25 * mood + (1 - 0.45 - 0.25 * mood) * blink
    for sx in (-1, 1):
        ex, ey = cx + sx * 95 * s, cy - 10 * s
        d.ellipse([ex - 52 * s, ey - 30 * s, ex + 52 * s, ey + 30 * s], fill=(245, 240, 232))
        px = ex + 0
        py = ey + look * 12 * s + 4 * s
        d.ellipse([px - 20 * s, py - 20 * s, px + 20 * s, py + 20 * s], fill=(70, 45, 30))
        d.ellipse([px - 9 * s, py - 9 * s, px + 9 * s, py + 9 * s], fill=(15, 10, 8))
        d.rectangle([ex - 56 * s, ey - 34 * s, ex + 56 * s, ey - 34 * s + 64 * s * lid], fill=SKIN_D)          # eyelid
        d.line([(ex - 52 * s, ey - 34 * s + 64 * s * lid), (ex + 52 * s, ey - 34 * s + 64 * s * lid)], fill=(90, 60, 45), width=max(2, int(5 * s)))
        d.arc([ex - 50 * s, ey + 10 * s, ex + 50 * s, ey + 60 * s], 20, 160, fill=(130, 90, 95), width=max(2, int(6 * s)))  # bags
        # brows: flat & low when tired, inner ends raised when defeated
        inner = -60 * s - 18 * s * mood
        outer = -52 * s + 8 * s * mood
        d.line([(ex - sx * 55 * s, ey + inner), (ex + sx * 60 * s, ey + outer)], fill=HAIR, width=max(3, int(16 * s)))
    # nose
    d.line([(cx, cy - 10 * s), (cx - 18 * s, cy + 90 * s), (cx + 10 * s, cy + 100 * s)], fill=(150, 105, 78), width=max(2, int(6 * s)))
    # mouth
    my = cy + 170 * s
    mw = 70 * s
    if mouth > 0.08:
        mh = 10 * s + 60 * s * mouth
        d.ellipse([cx - mw, my - mh / 2, cx + mw, my + mh / 2], fill=(70, 25, 25))
        d.rectangle([cx - mw * 0.7, my - mh / 2, cx + mw * 0.7, my - mh / 2 + 10 * s], fill=(235, 230, 220))
    else:
        d.arc([cx - mw, my - 10 * s - 14 * s * mood, cx + mw, my + 30 * s], 200, 340, fill=(110, 60, 50), width=max(2, int(7 * s)))


def detailer_side(d, t, wand_x, sit=False, mouth=0.0):
    """Side view of the detailer leaning into the SUV with the vacuum wand (or slumped on the door sill)."""
    if not sit:
        hx, hy = 330, 780
        d.polygon([(250, 870), (390, 860), (440, 1150), (330, 1420), (170, 1420), (190, 1150)], fill=SHIRT)       # torso
        d.polygon([(170, 1420), (330, 1420), (350, 1900), (150, 1900)], fill=(40, 42, 48))                     # pants
        hand = (wand_x - 120, 1060)
        d.line([(360, 900), (hand[0] - 40, 1000), hand], fill=SHIRT, width=70)                                  # arm
        d.ellipse([hand[0] - 34, hand[1] - 34, hand[0] + 34, hand[1] + 34], fill=SKIN)
        # wand + nozzle on the carpet + hose
        d.line([(hand[0] - 40, hand[1] - 50), (wand_x + 60, 1290)], fill=(170, 175, 182), width=26)
        d.polygon([(wand_x + 20, 1280), (wand_x + 160, 1290), (wand_x + 160, 1310), (wand_x + 20, 1305)], fill=(60, 62, 68))
        d.line([(hand[0] - 40, hand[1] - 50), (hand[0] - 160, 1150), (60, 1500), (-40, 1700)], fill=(110, 115, 120), width=46, joint="curve")
    else:
        hx, hy = 300, 980
        d.polygon([(220, 1060), (370, 1060), (400, 1330), (190, 1340)], fill=SHIRT)                             # slumped torso
        d.polygon([(190, 1330), (420, 1320), (560, 1360), (560, 1440), (200, 1440)], fill=(40, 42, 48))       # thighs
        d.rectangle([500, 1360, 560, 1700], fill=(40, 42, 48))                                                  # shins
        d.line([(360, 1100), (470, 1300)], fill=SHIRT, width=60)                                                # arm on knee
        d.line([(600, 1700), (900, 1560)], fill=(170, 175, 182), width=22)                                     # dropped wand
    # head in profile, facing right
    d.ellipse([hx - 90, hy - 110, hx + 90, hy + 110], fill=SKIN)
    d.chord([hx - 95, hy - 120, hx + 95, hy + 30], 180, 360, fill=HAIR)
    d.ellipse([hx - 40, hy - 20, hx, hy + 30], fill=SKIN_D)                                                     # ear
    d.ellipse([hx - 30, hy - 8, hx - 10, hy + 12], fill=(245, 245, 245))                                        # earbud
    d.polygon([(hx + 85, hy - 10), (hx + 115, hy + 30), (hx + 85, hy + 40)], fill=SKIN)                         # nose
    d.chord([hx - 60, hy + 20, hx + 95, hy + 120], 0, 180, fill=(150, 108, 80))                                # stubble
    d.line([(hx + 40, hy - 25), (hx + 75, hy - 22)], fill=(60, 40, 30), width=6)                                 # tired eye
    if mouth > 0.1:
        d.ellipse([hx + 55, hy + 55, hx + 85, hy + 55 + 30 * mouth], fill=(70, 25, 25))
    else:
        d.line([(hx + 55, hy + 65), (hx + 85, hy + 62)], fill=(110, 60, 50), width=5)


def suv_interior(d, debris_k=1.0):
    """Open rear door of an SUV seen from the side: door frame, seat, carpet with hair + sand."""
    d.rounded_rectangle([40, 470, W - 40, 1400], 60, fill=(28, 28, 32))                    # body/frame
    d.rounded_rectangle([90, 520, W - 90, 1350], 40, fill=(52, 54, 60))                    # cabin
    d.rounded_rectangle([600, 560, 880, 1150], 30, fill=(120, 122, 128))                   # seat back
    d.rounded_rectangle([440, 1050, 980, 1200], 30, fill=(132, 134, 140))                  # seat cushion
    d.rectangle([100, 1200, W - 100, 1345], fill=(40, 40, 44))                             # carpet
    rng = np.random.default_rng(5)
    for _ in range(int(500 * debris_k)):
        x, y = rng.uniform(110, W - 110), rng.uniform(1205, 1340)
        if rng.random() < 0.5:
            d.line([(x, y), (x + rng.uniform(-14, 14), y + rng.uniform(-5, 5))], fill=(225, 205, 170), width=2)
        else:
            d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(220, 190, 140))
    for _ in range(int(220 * debris_k)):                                                   # hair on the seats too
        x, y = rng.uniform(450, 960), rng.uniform(580, 1190)
        d.line([(x, y), (x + rng.uniform(-14, 14), y + rng.uniform(-6, 6))], fill=(225, 205, 170), width=2)
    d.rectangle([40, 1350, W - 40, 1400], fill=(20, 20, 22))                               # sill


# ---------------------------------------------------------------- shots
def blink_at(t):
    ph = (t * 0.31) % 1.0
    return 1.0 if ph < 0.025 else 0.0


def shot_vacuum(t, t0):
    img = SHOP.copy()
    d = ImageDraw.Draw(img)
    suv_interior(d)
    wand_x = 520 + 160 * np.sin((t - t0) * 9.5)  # aggressive back-and-forth
    detailer_side(d, t, wand_x, mouth=MOUTH[min(NFR - 1, int(t * FPS))])
    # debris being sucked into the nozzle
    rng = np.random.default_rng(int(t * FPS))
    for _ in range(40):
        a = rng.random()
        x = wand_x + 90 + rng.uniform(-90, 90) * (1 - a)
        y = 1300 - a * 60
        d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(225, 200, 150))
    return img


def shot_face(t, mood=0.0, look=0.0):
    img = SHOP_BLUR.copy()
    d = ImageDraw.Draw(img)
    face(d, W / 2, 820, 1.0, MOUTH[min(NFR - 1, int(t * FPS))], blink_at(t), mood, look)
    return img


def shot_carpet(t, t0, brush=False):
    img = CARPET.copy() if not brush else CARPET.copy()
    d = ImageDraw.Draw(img)
    if brush:
        a = t - t0
        n = int(min(1, a / 1.4) * len(EXTRA_SAND))
        for x, y, r in EXTRA_SAND[:n]:  # more sand keeps surfacing
            X, Y = x * 1.6, y * 1.6
            d.ellipse([X - r * 1.6, Y - r * 1.6, X + r * 1.6, Y + r * 1.6], fill=(226, 196, 140))
        bx = W * 0.8 + np.sin(a * 14) * 260
        by = H * 0.8
        d.rounded_rectangle([bx - 250, by - 60, bx + 250, by + 60], 30, fill=(150, 95, 50))                  # brush block
        for k in range(28):
            x = bx - 230 + k * 17
            d.line([(x, by + 60), (x + np.sin(a * 14 + k) * 6, by + 140)], fill=(240, 230, 210), width=7)  # bristles
        d.rounded_rectangle([bx - 60, by - 220, bx + 60, by - 60], 20, fill=(120, 75, 40))                 # handle
    return img


def frame_image(t):
    """Returns (PIL image, camera zoom, cam centre, shake amp)."""
    if t < 3.1:   # hook: aggressive vacuuming, crash-zoom in at the start
        z = lerp(1.35, 1.0, ease_out(t / 0.5))
        return shot_vacuum(t, 0), z, (W / 2, 1150), 4
    if t < 6.0:   # "Nah, bro. I'm cooked." — punch-in close-up
        z = 1.0 + 0.25 * ease_out_back((t - 3.1) / 0.25, 2) if t < 4.3 else 1.25 + 0.1 * ease_in_out((t - 4.3) / 0.6)
        return shot_face(t), z, (W / 2, 860), 1.5
    if t < 9.9:   # "What happened?" / "Dog hair, beach sand combo."
        return shot_face(t, look=0.6), 1.05 + 0.04 * (t - 6.0) / 3.9, (W / 2, 860), 1.2
    if t < 11.2:  # dramatic carpet close-up: crash zoom
        z = lerp(0.65, 1.15, ease_out((t - 9.9) / 0.35)) + 0.05 * (t - 9.9)
        return shot_carpet(t, 9.9), z, (W * 0.8, H * 0.8), 8 * np.exp(-(t - 9.9) * 4) + 1
    if t < 14.4:  # "Damn. Both?" / "Both, bro." — exaggerated zoom on "Both, bro."
        z = 1.0 if t < 12.6 else 1.0 + 0.45 * ease_out_back((t - 12.6) / 0.3, 2)
        return shot_face(t, mood=0.3), z, (W / 2, 820), 1.5
    if t < 19.8:  # back to the same square foot
        return shot_vacuum(t, 14.4), 1.0 + 0.04 * (t - 14.4) / 5.4, (W / 2, 1150), 3
    if t < 21.5:  # brushing brings up even more sand
        return shot_carpet(t, 19.8, brush=True), 1.0 + 0.06 * (t - 19.8), (W * 0.8, H * 0.8), 2
    if t < 24.0:  # "I think this dog lived at the beach."
        return shot_face(t, mood=0.5, look=0.5), 1.1, (W / 2, 860), 1.2
    if t < 26.8:  # defeated stare, slow zoom toward his face
        img = SHOP.copy()
        d = ImageDraw.Draw(img)
        suv_interior(d)
        detailer_side(d, t, 0, sit=True, mouth=MOUTH[min(NFR - 1, int(t * FPS))])
        z = lerp(1.0, 1.8, ease_in_out((t - 24.0) / 2.8))
        return img, z, (lerp(W / 2, 300, ease_in_out((t - 24.0) / 2.8)), lerp(1150, 980, ease_in_out((t - 24.0) / 2.8))), 0.8
    # "I'll call you next week."
    return shot_face(t, mood=1.0, look=0.8), 1.15 + 0.06 * (t - 26.8) / 1.8, (W / 2, 840), 0.8


# ---------------------------------------------------------------- overlays
def phone_ui(t):
    if t < 0.15 or t >= OUTRO_T:
        return None
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    ringing = t < 0.7
    jx = np.sin(t * 90) * 6 if ringing else 0
    k = ease_out_back((t - 0.15) / 0.25, 2)
    x0, y0 = 150 + jx, 150 - (1 - k) * 200
    d.rounded_rectangle([x0, y0, x0 + 780, y0 + 150], 40, fill=(20, 22, 26, 225))
    d.ellipse([x0 + 26, y0 + 26, x0 + 124, y0 + 124], fill=(70, 190, 110))
    d.text((x0 + 56, y0 + 36), "B", font=font("anton", 64), fill=(255, 255, 255))
    d.text((x0 + 150, y0 + 22), "BRO", font=font("anton", 64), fill=(255, 255, 255))
    if ringing:
        d.text((x0 + 150, y0 + 98), "incoming call…", font=font("oswaldm", 34), fill=(180, 185, 195))
    else:
        s = int(t - 0.7)
        d.text((x0 + 150, y0 + 98), f"{s // 60}:{s % 60:02d}", font=font("oswaldm", 34), fill=(120, 220, 140))
        amp = FRIEND[min(NFR - 1, int(t * FPS))]
        for i in range(7):
            hh = 8 + amp * (30 + 22 * np.sin(t * 25 + i * 1.3))
            bx = x0 + 560 + i * 26
            d.rounded_rectangle([bx, y0 + 75 - hh, bx + 14, y0 + 75 + hh], 6, fill=(150, 215, 255))
    return layer


def caption_layer(t):
    for start, end, spk, ws in CHUNKS:
        if start <= t < end:
            break
    else:
        return None
    f = font("anton", 112)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    widths = [d.textlength(w, font=f) for w, _, _ in ws]
    space = 26
    lines = [list(range(len(ws)))]
    if sum(widths) + space * (len(ws) - 1) > W - 160:
        mid = (len(ws) + 1) // 2
        lines = [list(range(mid)), list(range(mid, len(ws)))]
    pop = ease_out_back((t - start) / 0.14, 2.2)
    y0 = 1330 - (len(lines) - 1) * 70
    base = FRIEND_COL if spk == "F" else (255, 255, 255)
    for li, idxs in enumerate(lines):
        lw = sum(widths[i] for i in idxs) + space * (len(idxs) - 1)
        x = (W - lw) / 2
        for i in idxs:
            w, a0, a1 = ws[i]
            col = AMBER if (w in KEYWORDS or a0 <= t < a1 + 0.05) else base
            d.text((x, y0 + li * 140), w, font=f, fill=col + (255,), stroke_width=10, stroke_fill=(0, 0, 0, 255))
            x += widths[i] + space
    sc = 0.75 + 0.25 * pop
    if abs(sc - 1) > 1e-3:
        layer = cam2d(layer, sc, W / 2, 1360, 0, 0, 1360 - H / 2, fill=(0, 0, 0, 0))
    return layer


def outro(t, idx):
    a = t - OUTRO_T
    img = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(img)
    k = ease_out_back(a / 0.25, 2.5)
    f = font("anton", int(230 * min(1.2, k)) + 1)
    w = d.textlength("NO WAY.", font=f)
    d.text(((W - w) / 2, 790), "NO WAY.", font=f, fill=(245, 240, 230))
    bw = 520 * ease_out(a / 0.4)
    d.rectangle([W / 2 - bw / 2, 1100, W / 2 + bw / 2, 1114], fill=AMBER)
    arr = np.asarray(img, np.float32) / 255.0
    g = max(0.0, 1 - a / 0.3)
    if g > 0:  # quick RGB-split glitch on the hit
        off = int(22 * g)
        arr = np.stack([np.roll(arr[..., 0], off, 1), arr[..., 1], np.roll(arr[..., 2], -off, 1)], -1)
        rng = np.random.default_rng(idx)
        for _ in range(8):
            y = rng.integers(700, 1200)
            arr[y:y + 20] = np.roll(arr[y:y + 20], int(rng.normal(0, 80 * g)), 1)
    return np.clip(arr, 0, 1)


def frame(idx):
    t = idx / FPS
    if t >= OUTRO_T:
        out = outro(t, idx)
    else:
        img, z, (cx, cy), amp = frame_image(t)
        sx, sy, sr = shake(t, amp, 6, seed=2)
        out = from_img(cam2d(img, z, cx, cy, sr, sx, sy))
        # light modern grade: slight contrast, vignette, fine grain
        out = np.clip((out - 0.5) * 1.06 + 0.5, 0, 1) * (0.55 + 0.45 * VIGNETTE)
        out = np.clip(out + GRAIN[idx % len(GRAIN)][..., None] * 0.018, 0, 1)
    pil = to_img(out).convert("RGBA")
    for lay in (phone_ui(t), caption_layer(t) if t < OUTRO_T else None):
        if lay is not None:
            pil = Image.alpha_composite(pil, lay)
    return np.asarray(pil.convert("RGB")).tobytes()


def _init():
    global CHUNKS, MOUTH, FRIEND, SHOP, SHOP_BLUR, CARPET
    CHUNKS = build_chunks()
    MOUTH = envelope("D")
    FRIEND = envelope("F")
    SHOP = build_shop()
    SHOP_BLUR = SHOP.filter(ImageFilter.GaussianBlur(16))
    CARPET = build_carpet()


if __name__ == "__main__":
    out = sys.argv[1]
    if len(sys.argv) > 2:
        _init()
        for fi in map(int, sys.argv[2:]):
            Image.frombytes("RGB", (W, H), frame(fi)).save(f"{out}_{fi:03d}.png")
        sys.exit()
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "17",
                           "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    with Pool(int(os.environ.get("JOBS", 4)), initializer=_init) as pool:
        for fb in pool.imap(frame, range(NFR), chunksize=4):
            ff.stdin.write(fb)
    ff.stdin.close()
    ff.wait()
