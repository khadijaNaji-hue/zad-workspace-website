"""Rebuilds zad-workspace_images.js from the HEIC originals in "ZAD PICS".

Usage:  python build-images.py
Add or swap a photo by editing IMAGES below, then re-run. Keys match the
data-img="..." attributes in zad-workspace-landing.html.
"""
import base64
import io
import os

import pillow_heif
from PIL import Image, ImageOps

pillow_heif.register_heif_opener()

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "ZAD PICS")
OUT = os.path.join(HERE, "zad-workspace_images.js")

# (file stem, longest side in px, webp quality[, x focus 0..1])
# A 4th value crops a landscape photo to a 3:4 portrait around that horizontal
# position, since the services tiles are portrait.
IMAGES = [
    ("20241128_080400680_iOS", 2133, 76),  # hero (full-bleed)
    ("20241128_083017012_iOS", 1600, 74),  # about
    # services tiles
    ("20241128_081204683_iOS", 1200, 74),  # shared space
    ("silent-room", 1200, 74, 0.45),  # silent space (landscape -> portrait crop, x focus)
    ("meeting-room", 1200, 74, 0.50),  # meeting room (landscape -> portrait crop, x focus)
    ("20241128_084314395_iOS", 1200, 74),  # courses room
    # gallery
    ("20241128_084810212_iOS", 1200, 74),  # reception mirror
    ("20241128_081017658_iOS", 1200, 74),  # glass wall, shared area
    ("20241128_080647408_iOS", 1200, 74),  # shared area with clock
    ("20241128_082812288_iOS", 1200, 74),  # reception desk
    ("20241128_082426608_iOS", 1200, 74),  # natural light / curtains
    ("20241128_084400794_iOS", 1200, 74),  # courses room, second angle
]


def open_source(stem):
    for ext in (".heic", ".jpg"):
        path = os.path.join(SRC, stem + ext)
        if os.path.exists(path):
            return Image.open(path)
    raise FileNotFoundError(stem)


def encode(stem, long_side, quality, focus=None):
    im = ImageOps.exif_transpose(open_source(stem)).convert("RGB")
    if focus is not None and im.width > im.height:
        crop_w = round(im.height * 3 / 4)
        left = round(min(max(im.width * focus - crop_w / 2, 0), im.width - crop_w))
        im = im.crop((left, 0, left + crop_w, im.height))
    im.thumbnail((long_side, long_side), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "WEBP", quality=quality, method=6)
    return base64.b64encode(buf.getvalue()).decode("ascii"), buf.tell()


parts = []
total = 0
for stem, long_side, quality, *rest in IMAGES:
    b64, size = encode(stem, long_side, quality, rest[0] if rest else None)
    total += size
    print(f"{stem}: {size // 1024} KB")
    parts.append(f'"{stem}": "data:image/webp;base64,{b64}"')

with open(OUT, "w", encoding="utf-8") as f:
    f.write("window.ZAD_IMAGES = {\n" + ",\n".join(parts) + "\n};\n")
print(f"total webp: {total // 1024} KB -> {OUT}")
