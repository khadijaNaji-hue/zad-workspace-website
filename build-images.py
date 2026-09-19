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

# (file stem, longest side in px, webp quality)
IMAGES = [
    ("20241128_080400680_iOS", 2133, 76),  # hero (full-bleed)
    ("20241128_083017012_iOS", 1600, 74),  # about
    # services tiles
    ("20241128_081204683_iOS", 1200, 74),  # shared space
    ("20241128_080149597_iOS", 1200, 74),  # silent space (interim)
    ("20241128_082320554_iOS", 1200, 74),  # meeting room (interim)
    ("20241128_084314395_iOS", 1200, 74),  # courses room
    # gallery
    ("20241128_084810212_iOS", 1200, 74),  # reception mirror
    ("20241128_081017658_iOS", 1200, 74),  # glass wall, shared area
    ("20241128_080647408_iOS", 1200, 74),  # shared area with clock
    ("20241128_082812288_iOS", 1200, 74),  # reception desk
    ("20241128_082426608_iOS", 1200, 74),  # natural light / curtains
    ("20241128_084400794_iOS", 1200, 74),  # courses room, second angle
]


def encode(stem, long_side, quality):
    im = Image.open(os.path.join(SRC, stem + ".heic"))
    im = ImageOps.exif_transpose(im).convert("RGB")
    im.thumbnail((long_side, long_side), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "WEBP", quality=quality, method=6)
    return base64.b64encode(buf.getvalue()).decode("ascii"), buf.tell()


parts = []
total = 0
for stem, long_side, quality in IMAGES:
    b64, size = encode(stem, long_side, quality)
    total += size
    print(f"{stem}: {size // 1024} KB")
    parts.append(f'"{stem}": "data:image/webp;base64,{b64}"')

with open(OUT, "w", encoding="utf-8") as f:
    f.write("window.ZAD_IMAGES = {\n" + ",\n".join(parts) + "\n};\n")
print(f"total webp: {total // 1024} KB -> {OUT}")
