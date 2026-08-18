#!/usr/bin/env python3
"""Palette — v0.9.0 release graphics (Wordfire Guess Distribution + Site Screenshots).

Renders an on-brand teaser: a phone mockup showing the Wordfire game with the
new "Your record" guess-distribution panel (the marquee feature of this
release), sized for the blog header and the Bluesky card. Uses brand colors
and the brand flame.
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
KEYBG = (42, 42, 62)       # --key-bg #2a2a3e
BORDER = (58, 58, 74)      # --border #3a3a4a

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
    """Phone mockup: Wordfire board + guess distribution panel."""
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
    sx, sy, sw, sh = px + int(10 * scale), py + int(10 * scale), pw - int(20 * scale), ph - int(20 * scale)
    rounded_rect(draw, [sx, sy, sx + sw, sy + sh], int(18 * scale), SURFACE)

    f_title = ImageFont.truetype(FONT_BOLD, int(24 * scale))
    f_body = ImageFont.truetype(FONT, int(14 * scale))
    f_small = ImageFont.truetype(FONT, int(12 * scale))
    f_btn = ImageFont.truetype(FONT_BOLD, int(14 * scale))

    # Title
    title = "Wordfire"
    tw = draw.textlength(title, font=f_title)
    draw.text((sx + (sw - tw) / 2, sy + int(18 * scale)), title, font=f_title, fill=TEXT)

    # Streak bar (flame icon + text)
    flame_small = flame_png(int(14 * scale))
    img.paste(flame_small, (int(sx + (sw - 120 * scale) / 2), sy + int(50 * scale)), flame_small)
    streak = "4-day streak · best 6"
    stw = draw.textlength(streak, font=f_small)
    draw.text((int(sx + (sw - stw) / 2 + 10 * scale), sy + int(52 * scale)), streak, font=f_small, fill=ACCENT)

    # Distribution panel
    panel_x, panel_y = sx + int(22 * scale), sy + int(76 * scale)
    panel_w, panel_h = sw - int(44 * scale), int(190 * scale)
    rounded_rect(draw, [panel_x, panel_y, panel_x + panel_w, panel_y + panel_h], int(10 * scale), NAVY)

    p_title = "YOUR RECORD"
    ptw = draw.textlength(p_title, font=f_small)
    draw.text((panel_x + int(14 * scale), panel_y + int(10 * scale)), p_title, font=f_small, fill=TEXT)

    p_sub = "10 played · 7 won · 70%"
    psw = draw.textlength(p_sub, font=f_small)
    draw.text((panel_x + int(14 * scale), panel_y + int(28 * scale)), p_sub, font=f_small, fill=MUTED)

    # Bars: 6 rows, values
    counts = [0, 2, 1, 0, 1, 0]
    max_c = max(counts)
    bar_y = panel_y + int(52 * scale)
    bar_h = int(13 * scale)
    row_gap = int(18 * scale)
    label_w = int(12 * scale)
    count_w = int(14 * scale)
    track_w = panel_w - int(28 * scale) - label_w - count_w
    for i, n in enumerate(counts):
        y = bar_y + i * row_gap
        draw.text((panel_x + int(14 * scale), y - int(2 * scale)), str(i + 1), font=f_small, fill=MUTED)
        track_x = panel_x + int(14 * scale) + label_w + int(6 * scale)
        rounded_rect(draw, [track_x, y, track_x + track_w, y + bar_h], int(4 * scale), KEYBG)
        if n > 0:
            w = max(int(4 * scale), int(track_w * n / max_c))
            rounded_rect(draw, [track_x, y, track_x + w, y + bar_h], int(4 * scale), GREEN)
        draw.text((track_x + track_w + int(6 * scale), y - int(2 * scale)), str(n), font=f_small, fill=TEXT)

    # Board: 2 committed rows + 4 empty
    tile = int(30 * scale)
    gap = int(5 * scale)
    board_w = tile * 5 + gap * 4
    bx = sx + (sw - board_w) // 2
    by = panel_y + panel_h + int(22 * scale)
    row_colors = [
        [GRAY, YELLOW, GRAY, GREEN, GRAY],
        [GREEN, GREEN, GREEN, GREEN, GREEN],
    ]
    for r in range(6):
        for c in range(5):
            x = bx + c * (tile + gap)
            y = by + r * (tile + gap)
            col = NAVY
            if r < 2:
                col = row_colors[r][c]
            rounded_rect(draw, [x, y, x + tile, y + tile], int(5 * scale), col)

    # Keyboard hint row (3 keys)
    key_w, key_h = int(26 * scale), int(26 * scale)
    kx = bx
    ky = by + 6 * (tile + gap) + int(10 * scale)
    for i in range(3):
        rounded_rect(draw, [kx + i * (key_w + int(5 * scale)), ky, kx + i * (key_w + int(5 * scale)) + key_w, ky + key_h],
                     int(5 * scale), KEYBG)

    # Flame mark top-right
    flame = flame_png(int(30 * scale))
    img.paste(flame, (sx + sw - int(40 * scale), sy + int(12 * scale)), flame)

    return img


def main():
    img = render_phone(1200, 630, scale=1.0)
    img.save(os.path.join(BASE, "dist-release-1200.png"))
    print("wrote dist-release-1200.png")

    img2 = render_phone(800, 420, scale=0.66)
    img2.save(os.path.join(BASE, "dist-bsky-card-800.png"))
    print("wrote dist-bsky-card-800.png")


if __name__ == "__main__":
    main()
