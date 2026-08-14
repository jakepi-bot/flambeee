#!/usr/bin/env python3
"""Palette — v0.7.0 release graphics (Mobile Touch Quality Pass).

Renders an on-brand teaser: a phone mockup showing the Wordfire board with
the new color legend (the marquee feature of this release), sized for the
blog header and the Bluesky card. Uses brand colors and the brand flame.
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


def draw_phone(draw, img, cx, y_top, w, h):
    """Phone bezel with screen; returns screen rect (x0, y0, x1, y1)."""
    x0 = cx - w // 2
    rounded_rect(draw, [x0, y_top, x0 + w, y_top + h], 36, (42, 42, 66))  # lighter bezel
    # screen
    sx0, sy0, sx1, sy1 = x0 + 14, y_top + 14, x0 + w - 14, y_top + h - 14
    rounded_rect(draw, [sx0, sy0, sx1, sy1], 24, NAVY)
    # screen border so the screen reads against the background
    draw.rounded_rectangle([sx0, sy0, sx1, sy1], radius=24, outline=(58, 58, 74), width=2)
    # notch pill
    nw, nh = 70, 8
    rounded_rect(draw, [cx - nw // 2, sy0 + 10, cx + nw // 2, sy0 + 10 + nh], nh // 2, (58, 58, 74))
    return (sx0, sy0, sx1, sy1)


def render_wordfire_screen(draw, img, screen, title_size=26):
    sx0, sy0, sx1, sy1 = screen
    W = sx1 - sx0
    # mini title
    ft = ImageFont.truetype(FONT_BOLD, title_size)
    t = "Wordfire"
    tw = draw.textlength(t, font=ft)
    x = sx0 + (W - tw) / 2
    draw.text((x, sy0 + 26), t, font=ft, fill=TEXT)
    flame = flame_png(24)
    img.paste(flame, (int(x + tw + 10), int(sy0 + 32)), flame)

    # solved rows: A P P L E solved, plus one partial row
    rows = [
        [("S", "gray"), ("T", "gray"), ("A", "yellow"), ("R", "yellow"), ("E", "gray")],
        [("A", "gray"), ("L", "gray"), ("L", "gray"), ("O", "yellow"), ("Y", "yellow")],
        [("A", "green"), ("P", "green"), ("P", "green"), ("L", "green"), ("E", "green")],
    ]
    colors = {"gray": GRAY, "yellow": YELLOW, "green": GREEN}
    tile = 44
    gap = 8
    board_w = 5 * tile + 4 * gap
    bx = sx0 + (W - board_w) / 2
    by = sy0 + 74
    font_tile = ImageFont.truetype(FONT_BOLD, 26)
    for r, row in enumerate(rows):
        for c, (letter, col) in enumerate(row):
            x = bx + c * (tile + gap)
            y = by + r * (tile + gap)
            rounded_rect(draw, [x, y, x + tile, y + tile], 8, colors[col])
            lw = draw.textlength(letter, font=font_tile)
            draw.text((x + (tile - lw) / 2, y + 8), letter, font=font_tile, fill=TEXT)

    # legend chips (the marquee feature)
    ly = by + 3 * (tile + gap) + 18
    items = [("green", "Right spot"), ("yellow", "In word"), ("gray", "Not in")]
    chip_f = ImageFont.truetype(FONT, 14)
    widths = []
    for col, label in items:
        tw = draw.textlength(label, font=chip_f)
        widths.append(14 + 5 + tw + 12)
    total_w = sum(widths) + 8 * (len(items) - 1)
    lx = sx0 + (W - total_w) / 2
    for (col, label), cw in zip(items, widths):
        rounded_rect(draw, [lx, ly, lx + cw, ly + 28], 14, SURFACE)
        rounded_rect(draw, [lx + 6, ly + 6, lx + 20, ly + 20], 5, colors[col])
        draw.text((lx + 26, ly + 6), label, font=chip_f, fill=TEXT)
        lx += cw + 8

    # bottom nav hint
    nf = ImageFont.truetype(FONT, 14)
    n = "touch-action: manipulation"
    nw = draw.textlength(n, font=nf)
    draw.text((sx0 + (W - nw) / 2, sy1 - 34), n, font=nf, fill=MUTED)


def title_block(draw, img, W, title, subtitle, y_title, y_sub, size_title, size_sub, flame_size, cx):
    ft = ImageFont.truetype(FONT_BOLD, size_title)
    tw = draw.textlength(title, font=ft)
    x = cx - (tw + flame_size + 16) / 2
    draw.text((x, y_title), title, font=ft, fill=TEXT)
    flame = flame_png(flame_size)
    img.paste(flame, (int(x + tw + 16), int(y_title + size_title * 0.62 - flame_size / 2)), flame)
    fs = ImageFont.truetype(FONT, size_sub)
    sw = draw.textlength(subtitle, font=fs)
    draw.text(((W - sw) / 2, y_sub), subtitle, font=fs, fill=MUTED)


def footer(draw, W, H, text="Flambeee · flambeee.com"):
    ff = ImageFont.truetype(FONT, 22)
    fw = draw.textlength(text, font=ff)
    draw.text(((W - fw) / 2, H - 40), text, font=ff, fill=MUTED)


def render_1200():
    W, H = 1200, 675
    img = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(img)
    for y in range(0, 210):
        t = y / 210
        col = tuple(int(SURFACE[i] + (NAVY[i] - SURFACE[i]) * t) for i in range(3))
        draw.line([(0, y), (W, y)], fill=col)

    title_block(draw, img, W, "Mobile Touch Quality", "v0.7.0 - no more zoom, no more scroll-jump",
                38, 132, 76, 26, 40, W // 2)
    screen = draw_phone(draw, img, W // 2, 196, 320, 420)
    render_wordfire_screen(draw, img, screen)
    footer(draw, W, H)

    out = os.path.join(BASE, "touch-release-1200.png")
    img.save(out, "PNG")
    print("  " + out, os.path.getsize(out), "bytes")


def render_800():
    W, H = 800, 800
    img = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(img)
    for y in range(0, 200):
        t = y / 200
        col = tuple(int(SURFACE[i] + (NAVY[i] - SURFACE[i]) * t) for i in range(3))
        draw.line([(0, y), (W, y)], fill=col)

    title_block(draw, img, W, "Mobile Touch Quality", "v0.7.0", 40, 150, 64, 28, 36, W // 2)
    screen = draw_phone(draw, img, W // 2, 220, 360, 470)
    render_wordfire_screen(draw, img, screen)
    footer(draw, W, H)

    out = os.path.join(BASE, "touch-bsky-card-800.png")
    img.save(out, "PNG")
    print("  " + out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    render_1200()
    render_800()
