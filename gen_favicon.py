#!/usr/bin/env python3
"""Regenerate favicon + OG assets from the original high-res SACCO logo.

- Favicon/apple/icons: tight-cropped emblem on a brand-cream disc -> reads
  cleanly at 16px, perfectly uniform with the on-site logo.
- OG image: a composed 1200x630 social card (gradient + emblem + wordmark +
  tagline) instead of a floating logo on empty space.
"""
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SRC = "img/MMU_Sacco_LOGO.png"
CREAM = (251, 248, 238, 255)    # #FBF8EE
GREEN = (90, 146, 46, 255)      # #5A922E (deep green for text contrast)
GREEN_L = (124, 179, 66, 255)   # #7CB342
GOLD = (200, 160, 44, 255)      # #C8A02C
INK = (31, 42, 36, 255)         # #1F2A24

logo = Image.open(SRC).convert("RGBA")


def tight_box(im):
    """Bounding box of opaque pixels."""
    alpha = im.split()[-1]
    bg = Image.new("L", im.size, 0)
    bg.paste(alpha, mask=alpha)
    return bg.getbbox()


def emblem(size, pad_frac=0.03, circle=True):
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    if circle:
        d = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        dp = d.load()
        cx = cy = size / 2
        r = size / 2 - 1
        for y in range(size):
            for x in range(size):
                if ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5 <= r:
                    dp[x, y] = CREAM
        canvas = d
    # tight-crop the logo so the ring text is never clipped
    bb = tight_box(logo)
    em = logo.crop(bb)
    inner = int(size * (1 - 2 * pad_frac))
    lw, lh = em.size
    scale = inner / max(lw, lh)
    em = em.resize((int(lw * scale), int(lh * scale)), Image.LANCZOS)
    canvas.alpha_composite(em, ((size - em.width) // 2, (size - em.height) // 2))
    return canvas


def save_ico(path, sizes=(16, 24, 32, 48, 64, 128, 192, 256)):
    import struct as _st, io as _io
    pngs = []
    for s in sizes:
        b = _io.BytesIO()
        emblem(s).save(b, format="PNG")
        pngs.append(b.getvalue())
    out = _io.BytesIO()
    out.write(_st.pack("<HHH", 0, 1, len(pngs)))
    offset = 6 + 16 * len(pngs)
    for s, png in zip(sizes, pngs):
        wb = 0 if s >= 256 else s
        hb = 0 if s >= 256 else s
        out.write(_st.pack("<BBBBHHII", wb, hb, 0, 0, 1, 32, len(png), offset))
        offset += len(png)
    for png in pngs:
        out.write(png)
    open(path, "wb").write(out.getvalue())
    print("wrote", path, "sizes", sizes)


save_ico("favicon/favicon.ico")
for s in (180, 192, 512):
    emblem(s).save(f"favicon/favicon-{s}.png", format="PNG")
    print("wrote", f"favicon/favicon-{s}.png")


# ---------- OG social card (1200x630) ----------
def og_card():
    W, H = 1200, 630
    # diagonal cream -> soft green gradient
    base = Image.new("RGB", (W, H), CREAM[:3])
    px = base.load()
    for y in range(H):
        for x in range(W):
            t = (x + y) / (W + H)
            r = int(CREAM[0] * (1 - t) + GREEN_L[0] * t * 0.10)
            g = int(CREAM[1] * (1 - t) + GREEN_L[1] * t * 0.10)
            b = int(CREAM[2] * (1 - t) + GREEN_L[2] * t * 0.10)
            px[x, y] = (r, g, b)
    card = base.convert("RGBA")

    # emblem, enlarged
    em = emblem(300).resize((300, 300), Image.LANCZOS)
    card.alpha_composite(em, ((W - 300) // 2, 70))

    draw = ImageDraw.Draw(card)
    # wordmark
    try:
        fbig = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 54)
        ftag = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 26)
    except Exception:
        fbig = ImageFont.load_default()
        ftag = ImageFont.load_default()
    title = "MAASAI MARA SACCO SOCIETY LTD"
    tb = draw.textbbox((0, 0), title, font=fbig)
    tw = tb[2] - tb[0]
    draw.text(((W - tw) / 2 - tb[0], 400), title, font=fbig, fill=INK[:3])
    tag = "Jijenge Tujijenge  ·  Your trusted, member-owned financial partner"
    tb2 = draw.textbbox((0, 0), tag, font=ftag)
    draw.text(((W - (tb2[2] - tb2[0])) / 2 - tb2[0], 470), tag, font=ftag, fill=(91, 107, 97))
    # thin gold rule
    draw.line([(W/2-120, 520), (W/2+120, 520)], fill=GOLD[:3], width=3)
    card.convert("RGB").save("favicon/og-logo.png", format="PNG", optimize=True)
    print("wrote favicon/og-logo.png")


og_card()
