#!/usr/bin/env python3
"""Palette — v0.8.0 release graphics (Wordfire Share + Per-Difficulty Stats).

Renders an on-brand teaser: a phone mockup showing the Wordfire win overlay
with the new Share button and the share summary grid (the marquee feature of
this release), sized for the blog header and the Bluesky card. Uses brand
colors and the brand flame.
"""
import os
from io import BytesIO
import cairosvg
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "brand", "release")
os.makedirs(BASE, exist_ok=True)

NAVY = (26, 26, 46)        # --bg #1a1a2e
SURFACE = (22, 33, 62)     # --surface #16213e
ACCENT = (233, 69, 96)     # --accent #e94560
ACCENT_HI = (255, 90, 117) # --accent-hover #ff5a75
GRAY = (58, 58, 74)        # --gray #3a3a4a
YELLOW = (245, 166, 35)    # --yellow #f5a623
GREEN = (76, 175, 125)     # --green #4caf7d
TEXT = (238, 238, 238)
MUTED = (136, 136, 136)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

FLAME_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024">'
    '<defs><linearGradient id="g" x1="0" y1="1" x2="0" y2="0">'
    '<stop offset="0%" stop-color="#c2185b"/>'
    '<stop offset="35%" stop-color="#e94560"/>'
    '<stop offset="70%" stop-color="#ff5a75"/>'
    '<stop offset="100%" stop-color="#ffb74d"/>'
    '</linearGradient></defs>'
    '<path d="M512 200 C 560 300, 620 360, 640 470 C 660 580, 620 700, 512 720 '
    'C 404 700, 364 580, 384 470 C 404 360, 464 300, 512 200 Z" fill="url(#g)"/>'
    '</svg>'
)


def flame_png(size):
    png = cairosvg.svg2png(bytestring=FLAME_SVG.encode(), output_width=size, output_height=size)
    return Image.open(BytesIO(png)).convert("RGBA")


def rounded_rect(draw, xy, radius, fill):
    draw.rounded_rectangle(xy, radius=radius, fill=fill)


def render_phone(canvas_w, canvas_h, scale=1.0):
    """Render the phone mockup with Wordfire win overlay + share summary."""
    img = Image.new("RGB", (canvas_w, canvas_h), NAVY)
    draw = ImageDraw.Draw(img)

    # Subtle radial glow behind phone
    glow = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    cx, cy = canvas_w // 2, int(canvas_h * 0.42)
    for r in range(220, 0, -4):
        alpha = int(14 * (1 - r / 220))
        gd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(233, 69, 96, alpha))
    img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Phone frame
    pw, ph = int(300 * scale), int(560 * scale)
    px, py = (canvas_w - pw) // 2, (canvas_h - ph) // 2
    rounded_rect(draw, [px, py, px + pw, py + ph], int(28 * scale), (10, 12, 24))
    # Screen
    sx, sy, sw, sh = px + int(10 * scale), py + int(10 * scale), pw - int(20 * scale), ph - int(20 * scale)
    rounded_rect(draw, [sx, sy, sx + sw, sy + sh], int(18 * scale), SURFACE)

    # Screen content: title
    f_title = ImageFont.truetype(FONT_BOLD, int(26 * scale))
    f_body = ImageFont.truetype(FONT, int(15 * scale))
    f_small = ImageFont.truetype(FONT, int(12 * scale))
    f_btn = ImageFont.truetype(FONT_BOLD, int(14 * scale))

    title = "Splendid!"
    tw = draw.textlength(title, font=f_title)
    draw.text((sx + (sw - tw) / 2, sy + int(22 * scale)), title, font=f_title, fill=GREEN)

    # Answer word
    ans = "MAYOR"
    aw = draw.textlength(ans, font=f_body)
    draw.text((sx + (sw - aw) / 2, sy + int(62 * scale)), ans, font=f_body, fill=ACCENT)

    # Share summary card
    card_x, card_y = sx + int(24 * scale), sy + int(100 * scale)
    card_w, card_h = sw - int(48 * scale), int(240 * scale)
    rounded_rect(draw, [card_x, card_y, card_x + card_w, card_y + card_h], int(12 * scale), NAVY)

    # Header line: Wordfire 3/6 · streak 5
    header = "Wordfire 3/6  ·  streak 5"
    hw = draw.textlength(header, font=f_small)
    draw.text((card_x + (card_w - hw) / 2, card_y + int(14 * scale)), header, font=f_small, fill=TEXT)

    # Grid: 6 rows x 5 tiles
    tile = int(26 * scale)
    gap = int(5 * scale)
    grid_w = tile * 5 + gap * 4
    gx = card_x + (card_w - grid_w) // 2
    gy = card_y + int(40 * scale)
    rows = [
        [GRAY, YELLOW, GRAY, GREEN, GRAY],
        [YELLOW, GREEN, GRAY, GREEN, GRAY],
        [GREEN, GREEN, GREEN, GREEN, GREEN],
        [GRAY, GRAY, GRAY, GRAY, GRAY],
        [GRAY, GRAY, GRAY, GRAY, GRAY],
        [GRAY, GRAY, GRAY, GRAY, GRAY],
    ]
    for r, row in enumerate(rows):
        for c, col in enumerate(row):
            x = gx + c * (tile + gap)
            y = gy + r * (tile + gap)
            rounded_rect(draw, [x, y, x + tile, y + tile], int(5 * scale), col)

    # Share button
    btn_w, btn_h = int(120 * scale), int(34 * scale)
    bx, by = sx + (sw - btn_w) // 2, card_y + card_h + int(18 * scale)
    rounded_rect(draw, [bx, by, bx + btn_w, by + btn_h], int(8 * scale), GREEN)
    bt = "Share"
    btw = draw.textlength(bt, font=f_btn)
    draw.text((bx + (btn_w - btw) / 2, by + int(8 * scale)), bt, font=f_btn, fill=(255, 255, 255))

    # Copied message
    cm = "Copied!"
    cmw = draw.textlength(cm, font=f_small)
    draw.text((sx + (sw - cmw) / 2, by + btn_h + int(10 * scale)), cm, font=f_small, fill=GREEN)

    # Flame mark top-right of screen
    flame = flame_png(int(34 * scale))
    img.paste(flame, (sx + sw - int(44 * scale), sy + int(14 * scale)), flame)

    return img


def main():
    # Blog header 1200x630
    img = render_phone(1200, 630, scale=1.0)
    img.save(os.path.join(BASE, "share-release-1200.png"))
    print("wrote share-release-1200.png")

    # Bluesky card 800x420
    img2 = render_phone(800, 420, scale=0.66)
    img2.save(os.path.join(BASE, "share-bsky-card-800.png"))
    print("wrote share-bsky-card-800.png")


if __name__ == "__main__":
    main()
