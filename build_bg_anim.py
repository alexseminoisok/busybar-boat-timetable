#!/usr/bin/env python3
"""Pre-render Boat Timetable's animated background as a native .anim file.

The river at night, in the style of BBC News' "aurora" background: three
soft glows (Thames blue, teal, indigo) drifting slowly on Lissajous paths over
deep navy, a gentle ripple texture riding on them, and a faint moonlight
glint gliding along the water once per loop. The firmware plays .anim files
itself at the file's fps, so the app sends no per-frame draws for it. Every
motion completes a whole number of cycles per loop, so it repeats seamlessly.

A soft limiter keeps the lit water mid-dark (each channel tops out below
CEIL) so cyan, green, amber, pink and red text all keep their contrast.

Output: community.boat_timetable/anims/bg_water.anim ("bicycle1", encoded with
the firmware's scripts/seq2anim.py — set BSB_FW if the checkout isn't at
../busybar-fw-jerryscript).

  python build_bg_anim.py [--preview DIR] [--no-anim]   # DIR gets an x10 sheet
"""
import json, math, os, sys, tempfile
from pathlib import Path
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "community.boat_timetable", "anims", "bg_water.anim")

W, H = 72, 16
FPS = 25
LOOP_S = 8
BASE = (3, 6, 14)                 # = BG_COLOR in main.js (#03060E), deep navy
GAIN = 1.0                        # overall glow strength

# colour, x centre, x swing, x cycles/loop, y centre, y swing, y cycles,
# phase, radius x, radius y, strength
GLOWS = [
    ((10, 52, 150), 36, 34, 1, 8, 5, 2, 0.0, 15, 9, 0.66),    # Thames blue
    ((0, 92, 112),  36, 30, -1, 9, 6, 1, 2.1, 13, 8, 0.58),   # teal
    ((40, 26, 140), 36, 36, 1, 7, 4, -2, 4.2, 12, 7, 0.50),   # indigo
]

# Ripples: brightness modulation of the glow (not of the navy), so dark areas
# stay calm and the lit water shimmers.
# (x wavelength px, y wavelength px or 0, cycles per loop, weight, phase)
RIPPLES = [
    (18, 0,  -2, 0.55, 0.0),      # swell drifting left
    (11, 20, -3, 0.30, 1.7),      # diagonal ripple
    (7, -14,  2, 0.15, 4.1),      # fine counter-ripple
]
RIPPLE_DEPTH = 0.35               # 0 = flat glow, 1 = ripples fully on/off

CEIL = 130                        # soft ceiling for glow light per channel

GLINT_AT = 0.30                   # moonlight glint: start (loop fraction)
GLINT_LEN = 0.40                  # duration (loop fraction)
GLINT_RGB = (40, 70, 95)          # peak added light (cool white-blue)


def glow(x, y, t):
    r = g = b = 0.0
    for (cr, cg, cb), xc, xs, xn, yc, ys, yn, ph, rx, ry, k in GLOWS:
        gx = xc + xs * math.sin(2 * math.pi * xn * t + ph)
        gy = yc + ys * math.sin(2 * math.pi * yn * t + ph * 0.7)
        d = ((x - gx) / rx) ** 2 + ((y - gy) / ry) ** 2
        f = k * math.exp(-d) * GAIN
        r += cr * f
        g += cg * f
        b += cb * f
    return r, g, b


def ripple(x, y, t):
    v = 0.0
    for lx, ly, cyc, w, ph in RIPPLES:
        a = x / lx + (y / ly if ly else 0.0) + cyc * t
        v += w * math.sin(2 * math.pi * a + ph)
    return 1.0 + RIPPLE_DEPTH * v          # ~0.65..1.35


def glint(x, y, t):
    """A soft horizontal streak of light gliding left to right along the water."""
    p = (t - GLINT_AT) / GLINT_LEN
    if not 0 <= p <= 1:
        return 0.0
    ease = p * p * (3 - 2 * p)
    pos = -16 + ease * (W + 32)
    d = (x - pos) / 9.0
    # broken into shimmering dashes along the streak, like light on ripples
    dash = 0.7 + 0.3 * math.sin(2 * math.pi * (x / 11.0 + y / 9.0 - 4 * t))
    band = math.exp(-d * d) * math.exp(-((y - 10.5) / 4.5) ** 2)
    return band * dash * math.sin(math.pi * p)


def limit(v):
    """Soft knee: ~linear while dim, approaches CEIL where glows pile up."""
    return CEIL * (1 - math.exp(-v / CEIL))


def frame(t):
    im = Image.new("RGB", (W, H))
    px = im.load()
    for y in range(H):
        for x in range(W):
            r, g, b = glow(x, y, t)
            m = ripple(x, y, t)
            s = glint(x, y, t)
            px[x, y] = tuple(max(0, min(255, round(c + limit(v * m) + gc * s))) for c, v, gc in zip(
                BASE, (r, g, b), GLINT_RGB))
    return im


def frames():
    n = FPS * LOOP_S
    return [frame(i / n) for i in range(n)]


def load_converter():
    fw = os.environ.get("BSB_FW", os.path.join(HERE, "..", "busybar-fw-jerryscript"))
    sys.path.insert(0, os.path.join(fw, "scripts"))
    from seq2anim import BSBAnimConverter
    return BSBAnimConverter


def write_anim(ims, path):
    conv = load_converter()
    with tempfile.TemporaryDirectory(prefix="bt-bg-") as tmp:
        for i, im in enumerate(ims):
            # No R/B pre-swap: a plain RGB anim shows the same colours as the
            # draw API (verified on fw api 27.9.0).
            im.save(os.path.join(tmp, f"frame_{i}.png"))
        with open(os.path.join(tmp, "meta.json"), "w") as f:
            json.dump({"fps": FPS, "color_mode": "rgb888", "sections": []}, f)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        info = conv().convert_dir(Path(tmp), Path(path))
    print(f"Wrote {os.path.relpath(path, HERE)}: {info.frame_cnt} frames @ {FPS} fps, "
          f"{os.path.getsize(path)} bytes")


if __name__ == "__main__":
    ims = frames()
    if "--preview" in sys.argv:
        d = sys.argv[sys.argv.index("--preview") + 1]
        os.makedirs(d, exist_ok=True)
        step = max(1, len(ims) // 8)
        picks = ims[::step][:8]
        sheet = Image.new("RGB", (W * 10, (H * 10 + 6) * len(picks)))
        for i, im in enumerate(picks):
            sheet.paste(im.resize((W * 10, H * 10), Image.NEAREST), (0, i * (H * 10 + 6)))
        sheet.save(os.path.join(d, "bg_sheet.png"))
        print(f"preview -> {d}/bg_sheet.png")
    if "--no-anim" not in sys.argv:
        write_anim(ims, OUT)
