#!/usr/bin/env python3
"""Produce a tight-cropped SQUARE emblem from the scraped logo for on-site use.
The source canvas (393x261) has heavy internal padding and is wider than tall,
so a square <img> box letterboxes it. Cropping to the opaque bounding box and
fitting into a square makes the emblem fill the frame cleanly and uniformly
with the favicon (same source, same crop logic)."""
from PIL import Image

SRC = "img/MMU_Sacco_LOGO.png"
OUT = "img/logo.png"
SIZE = 512

logo = Image.open(SRC).convert("RGBA")
alpha = logo.split()[-1]
bbox = alpha.getbbox()                      # (l, t, r, b) of opaque pixels
em = logo.crop(bbox)

# fit into a centered square with a little breathing room
pad = 0.04
inner = int(SIZE * (1 - 2 * pad))
ew, eh = em.size
scale = inner / max(ew, eh)
em = em.resize((int(ew * scale), int(eh * scale)), Image.LANCZOS)

canvas = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
canvas.alpha_composite(em, ((SIZE - em.width) // 2, (SIZE - em.height) // 2))
canvas.save(OUT, format="PNG", optimize=True)
print("wrote", OUT, canvas.size, "opaque-bbox was", bbox)
