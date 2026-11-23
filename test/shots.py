"""Decode test/shots/*.raw (bar /api/screen: base64 BGR 72x16) into exact
72x16 PNGs (test/shots/png/) and an x5 contact sheet (test/shots/sheet.png)."""
import base64, glob, json, os
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "shots")
os.makedirs(os.path.join(SHOTS, "png"), exist_ok=True)
ims = []
for f in sorted(glob.glob(os.path.join(SHOTS, "*.raw"))):
    raw = open(f, "rb").read()
    raw = base64.b64decode(json.loads(raw)["data"] if raw[:1] == b"{" else raw)
    im = Image.new("RGB", (72, 16))
    im.putdata([(raw[i + 2], raw[i + 1], raw[i]) for i in range(0, 72 * 16 * 3, 3)])
    name = os.path.basename(f)[:-4]
    im.save(os.path.join(SHOTS, "png", name + ".png"))
    ims.append((name, im))
S = 5
sheet = Image.new("RGB", (72 * S + 140, (16 * S + 6) * len(ims)), (60, 60, 60))
d = ImageDraw.Draw(sheet)
for i, (name, im) in enumerate(ims):
    y = i * (16 * S + 6)
    sheet.paste(im.resize((72 * S, 16 * S), Image.NEAREST), (0, y))
    d.text((72 * S + 6, y + 34), name, fill=(255, 255, 255))
sheet.save(os.path.join(SHOTS, "sheet.png"))
print(len(ims), "shots ->", os.path.join(SHOTS, "sheet.png"))
