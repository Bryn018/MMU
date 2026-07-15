#!/usr/bin/env python3
"""Normalise the 4 hero-carousel photos: consistent 1600x1000 landscape,
gentle brightness lift so the white caption text reads cleanly, NO colour
wash (faithful to the original site's clean photos). Writes img/csN.jpg."""
from PIL import Image, ImageEnhance
import os

SRC = {  # original scraped files
    "cs1": "img/cs1.jpg",
    "cs2": "img/cs2.jpg",
    "cs3": "img/cs3.jpg",
    "cs4": "img/cs4.jpg",
}
W, H = 1600, 1000  # consistent landscape carousel frame

for key, path in SRC.items():
    im = Image.open(path).convert("RGB")
    # cover-crop to target aspect
    iw, ih = im.size
    tw, th = W, H
    scale = max(tw / iw, th / ih)
    im = im.resize((round(iw * scale), round(ih * scale)), Image.LANCZOS)
    left = (im.width - tw) // 2
    top = (im.height - th) // 2
    im = im.crop((left, top, left + tw, top + th))
    # gentle brightness/contrast lift (keeps photos clean, no tint)
    im = ImageEnhance.Brightness(im).enhance(1.08)
    im = ImageEnhance.Contrast(im).enhance(1.05)
    # subtle saturation to make them pop without looking fake
    im = ImageEnhance.Color(im).enhance(1.05)
    out = f"img/{key}.jpg"
    im.save(out, "JPEG", quality=86, optimize=True, progressive=True)
    size = os.path.getsize(out) // 1024
    # quick luminance audit
    small = im.resize((80, 50))
    lum = sum(0.299 * r + 0.587 * g + 0.114 * b for r, g, b in small.getdata()) / (80 * 50)
    print(f"  {out}: 1600x1000 | {size}KB | lum={lum:.0f}/255")
