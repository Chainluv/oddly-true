"""NO WAY. skit — Mirror Check (25s, 1080x1920, 30 fps).
A guy at the bathroom mirror, slowly suspecting his hair is thinning. Reuses the detailer skit's face rig,
lip-sync envelopes, captions and fonts (skit-detailer/skit.py)."""
import os
import subprocess
import sys
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "skit-detailer"))
sys.path.insert(0, os.path.join(HERE, "..", "molasses-flood"))
from common import W, H, font, to_img, from_img, cam2d, shake, lerp, smoothstep, ease_in_out, ease_out, ease_out_back, VIGNETTE, GRAIN  # noqa: E402
import skit as sk  # noqa: E402  face rig, captions, lip-sync

FPS = 30
DURATION = 25.0
NFR = int(FPS * DURATION)
CUT_T = 24.45

sk.NFR = NFR
sk.OUTRO_T = CUT_T
sk.VOICE_DIR = os.environ.get("SKIT_VOICES", os.path.join(HERE, "voices"))
# speaker "D" = the guy (white captions, lip-synced); "F" = the barber on the phone (blue captions)
sk.LINES = [
    ("g1", "D", 1.6, [["YEAH…"], ["IT'S", "GETTIN'", "REAL"], ["LIGHT,", "MY", "BOY."]]),
    ("g2", "D", 5.3, [["EITHER", "A", "BAD"], ["HAIRCUT,", "OR…"]]),
    ("g3", "D", 10.3, [["NAH."], ["THAT'S", "DEFINITELY"], ["THE", "LIGHTING."]]),
    ("g4", "D", 13.0, [["…LIGHTING", "KINDA"], ["GOT", "A", "POINT,"], ["THOUGH."]]),
    ("g5", "D", 15.9, [["BE", "HONEST."], ["WHEN", "YOU", "SAID"], ["“TAKE", "A", "LITTLE"], ["OFF", "THE", "TOP”…"],
                       ["WAS", "THAT", "YOU"], ["OR", "GOD?"]]),
    ("b1", "F", 20.6, [["SEND", "ME", "A", "PICTURE."]]),
    ("g6", "D", 22.7, [["WE", "CAN", "DISCUSS"], ["IT", "VERBALLY."]]),
]
sk.SPOKEN = {}
sk.KEYWORDS = {"LIGHT,", "HAIRCUT,", "OR…", "DEFINITELY", "LIGHTING.", "POINT,", "GOD?", "PICTURE.", "VERBALLY."}

LIGHT_OFF, LIGHT_ON = 10.15, 12.85
RING_T, ANSWER_T = 15.0, 15.7
RAISE_T, LOWER_T = 21.75, 22.55
BG = None


# ---------------------------------------------------------------- art
def bathroom():
    img = Image.new("RGB", (W, H), (196, 204, 208))
    d = ImageDraw.Draw(img)
    for y in range(0, H, 120):                                    # wall tiles
        for x in range(-60 * ((y // 120) % 2), W, 120):
            d.rectangle([x + 3, y + 3, x + 117, y + 117], fill=(206, 214, 218))
    d.rectangle([0, 0, W, 170], fill=(225, 228, 230))             # ceiling
    d.ellipse([W / 2 - 170, 70, W / 2 + 170, 150], fill=(255, 252, 240))  # overhead light (reflected)
    d.rectangle([60, 1500, 300, 1520], fill=(160, 165, 170))      # towel bar + towel
    d.rectangle([90, 1520, 260, 1780], fill=(120, 150, 170))
    d.rectangle([800, 1580, 1000, 1600], fill=(180, 180, 185))    # shelf + bottles
    for k, col in enumerate([(230, 230, 235), (80, 140, 200), (40, 40, 44)]):
        d.rounded_rectangle([815 + k * 60, 1480 - k * 20, 860 + k * 60, 1580], 10, fill=col)
    return img.filter(ImageFilter.GaussianBlur(10))


TEE, TEE_D = (150, 152, 158), (120, 122, 128)


def guy(t, rub=0.0, squint=0.0, look_x=0.0, defeat=0.0, phone=0.0):
    """Mirror reflection of the guy. Built on the detailer face rig, then restyled: grey tee, no earbud,
    subtly thinning crown, rubbing hand, optional phone at the ear."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    cx, cy, s = W / 2, 820, 1.0
    mouth = sk.MOUTH[min(NFR - 1, int(t * FPS))]
    sk.face(d, cx, cy, s, mouth, sk.blink_at(t), mood=min(1.0, 0.15 + 0.5 * squint + defeat), look=0.0)
    # grey crew-neck tee over the work shirt
    d.polygon([(cx - 420, cy + 900), (cx - 380, cy + 520), (cx - 120, cy + 400), (cx + 120, cy + 400),
               (cx + 380, cy + 520), (cx + 420, cy + 900)], fill=TEE)
    d.chord([cx - 110, cy + 340, cx + 110, cy + 470], 0, 180, fill=sk.SKIN_D)
    d.arc([cx - 115, cy + 335, cx + 115, cy + 475], 0, 180, fill=TEE_D, width=12)
    d.ellipse([cx + 196, cy + 6, cx + 240, cy + 50], fill=sk.SKIN)                          # no earbud
    # squint: lower lids push up
    if squint > 0:
        for sx in (-1, 1):
            ex, ey = cx + sx * 95, cy - 10
            d.rectangle([ex - 56, ey + 34 - 40 * squint, ex + 56, ey + 36], fill=sk.SKIN)
    # pupils drift toward the side he's checking
    if abs(look_x) > 0.01:
        for sx in (-1, 1):
            ex, ey = cx + sx * 95, cy - 6
            d.ellipse([ex - 22, ey - 4, ex + 22, ey + 18], fill=(245, 240, 232))
            px = ex + look_x * 26
            d.ellipse([px - 18, ey - 2, px + 18, ey + 30 - 16], fill=(70, 45, 30))
    # subtly thinning crown: a little scalp shows through, a few strands remain
    d.ellipse([cx - 80, cy - 292, cx + 80, cy - 240], fill=(150, 108, 82))
    rng = np.random.default_rng(4)
    for _ in range(110):
        x = cx + rng.uniform(-80, 80)
        y = cy - 290 + rng.uniform(0, 45)
        d.line([(x, y), (x + rng.uniform(-6, 6), y + rng.uniform(8, 16))], fill=sk.HAIR, width=3)
    # hand rubbing the top of the head
    if rub > 0:
        hx = cx + 40 * np.sin(t * 9) * rub
        hy = cy - 300
        d.line([(cx + 380, cy + 700), (cx + 300, cy - 50), (hx + 60, hy + 30)], fill=TEE, width=110, joint="curve")
        d.line([(cx + 300, cy - 50), (hx + 60, hy + 30)], fill=sk.SKIN, width=80)
        d.ellipse([hx - 95, hy - 55, hx + 105, hy + 75], fill=sk.SKIN)
        for k in range(4):
            d.line([(hx - 70 + k * 40, hy - 50), (hx - 60 + k * 40, hy + 50)], fill=sk.SKIN_D, width=6)
    if phone > 0:  # phone at the ear (his left in the mirror)
        px, py = cx - 250, cy + 40
        d.line([(cx - 380, cy + 700), (px - 60, py + 220), (px, py + 120)], fill=TEE, width=110, joint="curve")
        d.ellipse([px - 70, py + 40, px + 60, py + 190], fill=sk.SKIN)
        d.rounded_rectangle([px - 45, py - 120, px + 35, py + 130], 18, fill=(28, 28, 32))
    return lay


def head_pose(t):
    """(rotation deg, x shift, lean zoom) for the reflection layer."""
    rot = 0.0
    if 5.0 <= t < 7.6:                                 # checks another angle
        rot = 14 * ease_in_out((t - 5.0) / 0.6) * (1 - ease_in_out((t - 7.0) / 0.6))
    lean = 0.08 * ease_in_out(t / 1.4) if t < 15 else 0.0
    return rot, lean


def light_level(t):
    if LIGHT_OFF <= t < LIGHT_ON:
        return 0.32
    return 1.0


def phone_cam(t):
    """What his phone's front camera shows when he raises it: the top of his own head."""
    img = Image.new("RGB", (W, H), (12, 12, 14))
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 170, 260, W - 170, 1240
    d.rounded_rectangle([x0 - 24, y0 - 24, x1 + 24, y1 + 24], 70, fill=(30, 30, 34))
    d.rounded_rectangle([x0, y0, x1, y1], 54, fill=(200, 206, 210))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 + 60
    d.ellipse([cx - 300, cy - 330, cx + 300, cy + 330], fill=sk.HAIR)                     # head from above
    d.ellipse([cx - 120, cy - 150, cx + 140, cy + 110], fill=(178, 134, 104))              # the crown
    rng = np.random.default_rng(6)
    for _ in range(160):
        x, y = cx + rng.uniform(-120, 130), cy + rng.uniform(-140, 100)
        d.line([(x, y), (x + rng.uniform(-8, 8), y + rng.uniform(8, 18))], fill=sk.HAIR, width=3)
    d.ellipse([cx - 40, cy - 70, cx + 70, cy + 10], fill=(225, 190, 160))                  # overhead-light shine
    d.rounded_rectangle([cx - 110, y0 + 30, cx + 110, y0 + 70], 20, fill=(20, 20, 22))     # front camera notch
    d.ellipse([cx - 55, y1 - 120, cx + 55, y1 - 10], outline=(255, 255, 255), width=8)    # shutter
    return img


def frame_image(t):
    if RAISE_T + 0.15 <= t < LOWER_T:      # phone POV
        k = ease_out((t - RAISE_T - 0.15) / 0.25)
        return phone_cam(t), lerp(1.15, 1.0, k), (W / 2, H / 2), 1.0, 1.0
    img = BG.copy().convert("RGBA")
    rub = 1.0 if t < 7.2 else 0.0
    squint = smoothstep(0.8, 1.6, t) * (1 - smoothstep(4.4, 5.0, t)) + smoothstep(13.0, 13.6, t) * 0.4
    look_x = 0.7 * smoothstep(5.2, 5.6, t) * (1 - smoothstep(6.9, 7.3, t))
    defeat = 0.5 * smoothstep(7.4, 8.4, t) * (1 - smoothstep(10.0, 10.3, t)) + 0.6 * smoothstep(13.0, 13.4, t)
    phone = 1.0 if ANSWER_T <= t < RAISE_T else 0.0
    lay = guy(t, rub, squint, look_x, defeat, phone)
    rot, lean = head_pose(t)
    if abs(rot) > 0.05:
        lay = lay.rotate(rot, center=(W / 2, 1500), resample=Image.BICUBIC)
    img.alpha_composite(lay)
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, 0, W, H], outline=(150, 150, 150, 255), width=26)                     # mirror edge
    # slow push toward the mirror, with a held extra push on the long stare
    z = 1.0 + lean + 0.012 * t + 0.12 * ease_in_out((t - 7.4) / 2.4) * (t < 10.2)
    if t >= LOWER_T:
        z = 1.25 + 0.02 * (t - LOWER_T)
    return img.convert("RGB"), z, (W / 2, 760), 0.8, light_level(t)


def phone_ui(t):
    if not (RING_T <= t < RAISE_T):
        return None
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    ringing = t < ANSWER_T
    jx = np.sin(t * 90) * 6 if ringing else 0
    k = ease_out_back((t - RING_T) / 0.25, 2)
    x0, y0 = 150 + jx, 150 - (1 - k) * 200
    d.rounded_rectangle([x0, y0, x0 + 780, y0 + 150], 40, fill=(20, 22, 26, 225))
    d.ellipse([x0 + 26, y0 + 26, x0 + 124, y0 + 124], fill=(200, 60, 50))
    d.text((x0 + 58, y0 + 36), "B", font=font("anton", 64), fill=(255, 255, 255))
    d.text((x0 + 150, y0 + 22), "BARBER", font=font("anton", 64), fill=(255, 255, 255))
    sub = "incoming call…" if ringing else f"0:{int(t - ANSWER_T):02d}"
    d.text((x0 + 150, y0 + 98), sub, font=font("oswaldm", 34), fill=(180, 185, 195) if ringing else (120, 220, 140))
    if not ringing:
        amp = sk.FRIEND[min(NFR - 1, int(t * FPS))]
        for i in range(7):
            hh = 8 + amp * (30 + 22 * np.sin(t * 25 + i * 1.3))
            bx = x0 + 560 + i * 26
            d.rounded_rectangle([bx, y0 + 75 - hh, bx + 14, y0 + 75 + hh], 6, fill=(150, 215, 255))
    return layer


def logo(t):
    img = Image.new("RGB", (W, H), (0, 0, 0))
    a = t - CUT_T - 0.12
    if a > 0:
        d = ImageDraw.Draw(img)
        k = ease_out(a / 0.2)
        f = font("anton", 110)
        w = d.textlength("NO WAY.", font=f)
        col = tuple(int(c * k) for c in (245, 240, 230))
        d.text(((W - w) / 2, 880), "NO WAY.", font=f, fill=col)
        d.rectangle([W / 2 - 150 * k, 1030, W / 2 + 150 * k, 1038], fill=tuple(int(c * k) for c in sk.AMBER))
    return np.asarray(img, np.float32) / 255.0


def frame(idx):
    t = idx / FPS
    if t >= CUT_T:
        out = logo(t)
    else:
        img, z, (cx, cy), amp, light = frame_image(t)
        sx, sy, sr = shake(t, amp, 2, seed=7)
        out = from_img(cam2d(img, z, cx, cy, sr, sx, sy))
        out = np.clip((out - 0.5) * 1.05 + 0.5, 0, 1) * (0.6 + 0.4 * VIGNETTE)
        if light < 1:  # overhead light off: dim, cool, a bit noisier
            out = out * light * np.array([0.85, 0.92, 1.1], np.float32)
        out = np.clip(out + GRAIN[idx % len(GRAIN)][..., None] * (0.018 if light == 1 else 0.035), 0, 1)
    pil = to_img(out).convert("RGBA")
    if t < CUT_T:
        for lay in (phone_ui(t), sk.caption_layer(t)):
            if lay is not None:
                pil = Image.alpha_composite(pil, lay)
    return np.asarray(pil.convert("RGB")).tobytes()


def _init():
    global BG
    sk.CHUNKS = sk.build_chunks()
    sk.MOUTH = sk.envelope("D")
    sk.FRIEND = sk.envelope("F")
    BG = bathroom()


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
