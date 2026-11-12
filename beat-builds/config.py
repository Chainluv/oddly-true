"""THE BEAT BUILDS ITSELF — timing, palette, layout and camera settings (shared by music.py and beat.py)."""

# ---------------------------------------------------------------- tempo map
DURATION = 45.0
FPS = 30
SR = 48000
BPM = 86
BEAT = 60.0 / BPM
STEP = BEAT / 4               # 16th note
BAR = BEAT * 4
T0 = 4.0                      # first downbeat (drums enter)


def bar(n):
    """Start time of bar n (bar 0 starts at T0)."""
    return T0 + n * BAR


# section entrances, all on downbeats
KICK_IN = bar(0)              # 4.00  turntable starts the kick
SNARE_IN = bar(1)             # 6.79  pencil
HAT_IN = bar(2)               # 9.58  window droplets
BASS_IN = bar(3)              # 12.37 amp light turns on
CHORDS_IN = bar(5)            # 17.95 keyboard
MELODY_IN = bar(8)            # 26.33 synth
PAYOFF = bar(11)              # 34.70 full groove
RESET = bar(13)               # 40.28 instruments drop out in sequence
FINAL_CHORD = bar(14)         # 43.07 last chord rings out
RECORD_LAND = 3.65
RECORD_LIFT = 42.6

# ---------------------------------------------------------------- harmony (D minor)
CHORDS = [  # one chord per bar, cycling
    ("Dm9", [146.83, 174.61, 220.00, 261.63, 329.63], 73.42),
    ("Bbmaj9", [116.54, 146.83, 174.61, 220.00, 261.63], 58.27),
    ("Gm9", [98.00, 116.54, 146.83, 174.61, 220.00], 49.00),
    ("A7b9", [110.00, 138.59, 196.00, 233.08, 277.18], 55.00),
]
# 2-bar motif, (step offset within 2 bars, length in steps, frequency)
MOTIF = [(0, 2, 440.00), (3, 1, 523.25), (4, 3, 587.33), (8, 2, 698.46), (10, 2, 659.25),
         (16, 2, 587.33), (19, 1, 523.25), (20, 4, 440.00), (26, 4, 392.00)]

# ---------------------------------------------------------------- palette
NAVY = (14, 18, 38)
NAVY2 = (22, 28, 56)
WOOD = (58, 40, 30)
WOOD_HI = (92, 64, 44)
AMBER = (255, 176, 84)
VIOLET = (150, 100, 255)
TEAL = (90, 210, 220)
CREAM = (238, 226, 206)
BLACK = (10, 10, 14)

# ---------------------------------------------------------------- layout (world px; full frame = 1080x1920)
WINDOW = (70, 230, 520, 860)
SILL_Y = 890
DESK_Y = 1240                 # desk surface line
TURNTABLE = (270, 1150)       # platter centre
PLATTER_R = 150
AMP = (870, 1080)             # amp centre (with indicator light)
MONITORS = [(690, 560), (930, 560)]
CUP = (690, 1205)
PENCIL = (520, 1225)          # tip position on the desk
KEYBOARD = (250, 1290, 760, 1390)
SYNTH = (800, 1290, 1030, 1390)
MIXER = (430, 1150, 640, 1215)
CHAIR = (540, 1700)
LAMP = (120, 560)

# camera keyframes: (time, zoom, centre x, centre y)
CAMERA = [
    (0.0, 1.9, 280, 1040), (3.8, 1.9, 280, 1080),
    (6.6, 1.75, 330, 1100), (9.2, 1.35, 380, 1000),
    (11.0, 1.35, 600, 1100), (12.2, 1.6, 800, 1120),
    (17.6, 1.6, 760, 1150), (18.6, 1.7, 500, 1330), (25.0, 1.2, 540, 1120),
    (26.0, 1.5, 820, 1300), (30.5, 1.3, 640, 1350),
    (33.8, 1.3, 600, 1250), (35.2, 1.0, 540, 960), (40.0, 1.0, 540, 960),
    (44.4, 1.9, 280, 1040), (45.0, 1.9, 280, 1040),
]
