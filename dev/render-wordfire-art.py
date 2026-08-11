#!/usr/bin/env python3
"""Palette — Wordfire release graphics (v0.6.0).

Renders an on-brand teaser: the Wordfire wordmark + a sample solved board
using brand tile colors, sized for blog header and Bluesky card.
The flame accent is the actual brand flame path from flambeee-logo-icon.svg.
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


def render_board(draw, origin, tile, gap, rows, font_tile, th):
    """rows: list of list of (letter, color-name)"""
    colors = {"gray": GRAY, "yellow": YELLOW, "green": GREEN}
    x0, y0 = origin
    for r, row in enumerate(rows):
        for c, (letter, col) in enumerate(row):
            x = x0 + c * (tile + gap)
            y = y0 + r * (tile + gap)
            rounded_rect(draw, [x, y, x + tile, y + tile], 10, colors[col])
            lw = draw.textlength(letter, font=font_tile)
            draw.text((x + (tile - lw) / 2, y + (tile - th) / 2), letter,
                      font=font_tile, fill=TEXT)


def title_block(draw, img, W, title, subtitle, y_title, y_sub, size_title, size_sub, flame_size):
    ft = ImageFont.truetype(FONT_BOLD, size_title)
    tw = draw.textlength(title, font=ft)
    x = (W - tw) / 2
    draw.text((x, y_title), title, font=ft, fill=TEXT)
    flame = flame_png(flame_size)
    img.paste(flame, (int(x + tw + 16), int(y_title + size_title * 0.62 - flame_size / 2)), flame)
    fs = ImageFont.truetype(FONT, size_sub)
    sw = draw.textlength(subtitle, font=fs)
    draw.text(((W - sw) / 2, y_sub), subtitle, font=fs, fill=MUTED)


ROWS = [
    [("S", "gray"), ("T", "gray"), ("A", "yellow"), ("R", "yellow"), ("E", "gray")],
    [("B", "gray"), ("L", "gray"), ("A", "gray"), ("N", "gray"), ("K", "gray")],
    [("C", "gray"), ("A", "gray"), ("R", "yellow"), ("R", "green"), ("Y", "gray")],
    [("M", "green"), ("A", "green"), ("R", "green"), ("R", "green"), ("Y", "green")],
]
LABEL = "4-day streak · best 9"
FOOT = "Flambeee · flambeee.com"


def streak_chip(draw, W, y, w=300, h=50):
    x = (W - w) / 2
    rounded_rect(draw, [x, y, x + w, y + h], 25, SURFACE)
    fc = ImageFont.truetype(FONT_BOLD, 26)
    lw = draw.textlength(LABEL, font=fc)
    draw.text((x + (w - lw) / 2, y + 9), LABEL, font=fc, fill=ACCENT_HI)


def footer(draw, W, H):
    ff = ImageFont.truetype(FONT, 22)
    fw = draw.textlength(FOOT, font=ff)
    draw.text(((W - fw) / 2, H - 40), FOOT, font=ff, fill=MUTED)


def render_1200():
    W, H = 1200, 675
    img = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(img)
    for y in range(0, 210):
        t = y / 210
        col = tuple(int(SURFACE[i] + (NAVY[i] - SURFACE[i]) * t) for i in range(3))
        draw.line([(0, y), (W, y)], fill=col)

    title_block(draw, img, W, "Wordfire", "One word a day. Light it up.",
                42, 148, 88, 30, 44)

    tile, gap = 76, 12
    board_w = 5 * tile + 4 * gap
    x0 = (W - board_w) / 2
    y0 = 216
    font_tile = ImageFont.truetype(FONT_BOLD, 42)
    render_board(draw, (x0, y0), tile, gap, ROWS, font_tile, 42)
    board_h = 4 * tile + 3 * gap
    streak_chip(draw, W, y0 + board_h + 26)
    footer(draw, W, H)

    out_blog = os.path.join(BASE, "wordfire-release-1200.png")
    img.save(out_blog, "PNG")
    print("  " + out_blog, os.path.getsize(out_blog), "bytes")


def render_800():
    W, H = 800, 800
    img = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(img)
    for y in range(0, 200):
        t = y / 200
        col = tuple(int(SURFACE[i] + (NAVY[i] - SURFACE[i]) * t) for i in range(3))
        draw.line([(0, y), (W, y)], fill=col)

    title_block(draw, img, W, "Wordfire", "One word a day. Light it up.",
                38, 130, 72, 26, 38)

    tile, gap = 104, 16
    board_w = 5 * tile + 4 * gap
    bx = (W - board_w) / 2
    by = 208
    font_tile = ImageFont.truetype(FONT_BOLD, 56)
    render_board(draw, (bx, by), tile, gap, ROWS, font_tile, 56)
    board_h = 4 * tile + 3 * gap
    streak_chip(draw, W, by + board_h + 28)
    footer(draw, W, H)

    out_bsky = os.path.join(BASE, "wordfire-bsky-card-800.png")
    img.save(out_bsky, "PNG")
    print("  " + out_bsky, os.path.getsize(out_bsky), "bytes")


if __name__ == "__main__":
    render_1200()
    render_800()
