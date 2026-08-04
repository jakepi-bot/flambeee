#!/usr/bin/env python3
"""Render Flambeee logo SVGs to PNG at multiple sizes."""
import cairosvg
import os

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo")
os.makedirs(BASE, exist_ok=True)

# (source svg, output name, target width px, target height px)
jobs = [
    # Square icon -> sizes (favicon through high-res avatar)
    ("flambeee-logo-icon.svg", "flambeee-512.png", 512, 512),
    ("flambeee-logo-icon.svg", "flambeee-256.png", 256, 256),
    ("flambeee-logo-icon.svg", "flambeee-128.png", 128, 128),
    ("flambeee-logo-icon.svg", "flambeee-64.png", 64, 64),
    ("flambeee-logo-icon.svg", "flambeee-32.png", 32, 32),
    ("flambeee-logo-icon.svg", "flambeee-16.png", 16, 16),
    # Bluesky avatar is 400x400
    ("flambeee-logo-icon.svg", "flambeee-avatar-400.png", 400, 400),
    # Banner for social header
    ("flambeee-banner.svg", "flambeee-banner-1500.png", 1500, 500),
    ("flambeee-banner.svg", "flambeee-banner-1200.png", 1200, 400),
]

for src, out, w, h in jobs:
    src_path = os.path.join(BASE, src)
    out_path = os.path.join(BASE, out)
    cairosvg.svg2png(url=src_path, write_to=out_path, output_width=w, output_height=h)
    print(f"  {out}  {w}x{h}  ({os.path.getsize(out_path)} bytes)")

print("\nDone.")
