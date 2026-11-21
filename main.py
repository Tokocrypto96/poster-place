#!/usr/bin/env python3
"""VELMARIS — travel poster for a place that isn't there.

A classic flat travel poster, drawn entirely with the Python standard
library. Writes one PNG to /output/entry.png (1024x1024, <= 1 MiB).

The place: Velmaris, a fictional island city where the tide keeps the
light — a spiral nautilus lighthouse on a rock islet, a coral sun over
a teal lagoon, warm sand below. Slogan: WHERE THE TIDE KEEPS THE LIGHT.
"""

import math
import os
import struct
import zlib

W = 1024
H = 1024

# --- palette (purposeful, limited) -------------------------------------
CREAM = (247, 232, 200)   # sky top / lighthouse walls
PEACH = (246, 217, 168)   # sky mid
APRICOT = (242, 184, 128) # sky low / horizon glow
CORAL = (232, 99, 44)     # sun / lighthouse bands
NAVY = (18, 50, 74)       # title / cliffs / islet
TEAL_D = (14, 94, 107)    # deep sea
TEAL_M = (18, 112, 127)   # mid sea
TEAL_L = (42, 140, 150)   # light sea
TEAL_H = (127, 196, 196)  # wave highlights
SAND = (232, 192, 122)    # foreground sand
SAND_D = (217, 167, 94)   # sand shadow
CLOUD = (255, 246, 227)   # clouds
BEAM = (255, 226, 150)    # lighthouse beam

canvas = bytearray(W * H * 3)


def px(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        canvas[i], canvas[i + 1], canvas[i + 2] = color


def fill_rect(x0, y0, x1, y1, color):
    x0 = max(0, x0); y0 = max(0, y0)
    x1 = min(W, x1); y1 = min(H, y1)
    for y in range(y0, y1):
        base = (y * W + x0) * 3
        for x in range(x0, x1):
            i = base + (x - x0) * 3
            canvas[i], canvas[i + 1], canvas[i + 2] = color


def hline(x0, x1, y, color, thick=1):
    for t in range(thick):
        fill_rect(x0, y + t, x1, y + t + 1, color)


def disc(cx, cy, r, color):
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                px(x, y, color)


def ellipse(cx, cy, rx, ry, color):
    for y in range(cy - ry, cy + ry + 1):
        for x in range(cx - rx, cx + rx + 1):
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0:
                px(x, y, color)


def polygon(points, color):
    """Scanline fill for a simple polygon [(x, y), ...]."""
    ys = [p[1] for p in points]
    for y in range(max(0, min(ys)), min(H, max(ys) + 1)):
        xs = []
        n = len(points)
        for i in range(n):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % n]
            if (y0 <= y < y1) or (y1 <= y < y0):
                t = (y - y0) / (y1 - y0)
                xs.append(x0 + t * (x1 - x0))
        xs.sort()
        for j in range(0, len(xs) - 1, 2):
            fill_rect(int(xs[j]), y, int(xs[j + 1]) + 1, y + 1, color)


# --- 5x7 bitmap font ----------------------------------------------------
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
}


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def draw_text(x, y, text, scale, color):
    cx = x
    for ch in text:
        glyph = FONT.get(ch, FONT[" "])
        for r, row in enumerate(glyph):
            for c, bit in enumerate(row):
                if bit == "1":
                    fill_rect(cx + c * scale, y + r * scale,
                              cx + (c + 1) * scale, y + (r + 1) * scale,
                              color)
        cx += 6 * scale


def draw_text_centered(y, text, scale, color):
    draw_text((W - text_width(text, scale)) // 2, y, text, scale, color)


# --- scene ---------------------------------------------------------------
def draw_scene():
    # Sky: warm flat bands, cream to apricot.
    fill_rect(0, 0, W, 190, CREAM)
    fill_rect(0, 190, W, 330, PEACH)
    fill_rect(0, 330, W, 470, APRICOT)

    # Coral sun, upper right, below the title so the name stays legible.
    disc(820, 288, 100, CORAL)
    ellipse(690, 348, 150, 32, CLOUD)
    ellipse(800, 366, 120, 26, CLOUD)
    ellipse(180, 250, 110, 26, CLOUD)
    ellipse(260, 268, 90, 22, CLOUD)

    # Sea: teal bands.
    fill_rect(0, 470, W, 590, TEAL_L)
    fill_rect(0, 590, W, 730, TEAL_M)
    fill_rect(0, 730, W, 906, TEAL_D)  # runs under the sand edge: no gap

    # Sun path shimmering on the water, under the sun.
    for i, (y0, wdt) in enumerate([(500, 300), (540, 380), (585, 460),
                                   (630, 540), (680, 620), (740, 700)]):
        x0 = 770 - wdt // 2
        hline(x0, x0 + wdt, y0, TEAL_H, 5)
        hline(x0 + 40, x0 + wdt - 40, y0 + 14, BEAM, 3)

    # Wave strokes.
    for y, x0, x1 in [(520, 60, 300), (560, 700, 960), (620, 90, 330),
                      (700, 640, 950), (780, 70, 320), (830, 660, 980)]:
        hline(x0, x1, y, TEAL_H, 4)

    # Distant headland, left horizon.
    polygon([(0, 470), (0, 430), (90, 448), (210, 432), (300, 470)], NAVY)

    # Islet rock, centre.
    polygon([(380, 880), (410, 800), (470, 770), (590, 770),
             (650, 800), (680, 880)], NAVY)

    # Nautilus lighthouse: tapered tower, cream with clean coral bands.
    base_y, top_y = 800, 500
    base_w, top_w = 96, 54
    cx = 530
    polygon([(cx - base_w / 2, base_y), (cx + base_w / 2, base_y),
             (cx + top_w / 2, top_y), (cx - top_w / 2, top_y)], CREAM)
    bands = 5
    for s in range(bands):
        if s % 2 == 0:
            continue
        y0 = base_y - (s + 1) * (base_y - top_y) // bands
        y1 = base_y - s * (base_y - top_y) // bands
        t0 = (base_y - y1) / (base_y - top_y)
        t1 = (base_y - y0) / (base_y - top_y)
        w0 = base_w + (top_w - base_w) * t0
        w1 = base_w + (top_w - base_w) * t1
        polygon([(cx - w0 / 2, y1), (cx + w0 / 2, y1),
                 (cx + w1 / 2, y0), (cx - w1 / 2, y0)], CORAL)
    # Light room + dome.
    fill_rect(cx - 34, 462, cx + 34, 500, NAVY)
    fill_rect(cx - 22, 470, cx + 22, 492, BEAM)
    disc(cx, 462, 30, CORAL)
    disc(cx, 466, 12, BEAM)
    # Light beams fanning out, symmetric wedges.
    polygon([(cx - 18, 474), (cx + 18, 474), (90, 396), (40, 432)], BEAM)
    polygon([(cx - 18, 474), (cx + 18, 474), (934, 396), (984, 432)], BEAM)

    # Sailboat on the lagoon, right side.
    polygon([(800, 742), (880, 742), (868, 762), (812, 762)], NAVY)
    polygon([(838, 742), (838, 668), (892, 742)], CREAM)
    polygon([(832, 742), (832, 682), (788, 742)], CORAL)

    # Birds.
    for bx, by in [(180, 330), (240, 300), (300, 340), (880, 330)]:
        polygon([(bx, by), (bx + 12, by - 8), (bx + 24, by)], NAVY)

    # Foreground sand with a gentle curved dune edge.
    edge = [(x, 890 + int(7 * math.sin(x / 130.0))) for x in range(0, W + 1, 32)]
    polygon([(0, H), (W, H)] + list(reversed(edge)), SAND)

    # Title: place name, big and deliberate, top of the poster.
    draw_text_centered(64, "VELMARIS", 16, NAVY)
    # One rule under the title, spanning the name, to anchor it.
    hline(136, 888, 198, NAVY, 4)

    # Slogan, one line, on the sand.
    draw_text_centered(946, "WHERE THE TIDE KEEPS THE LIGHT", 5, NAVY)


def write_png(path):
    raw = bytearray()
    for y in range(H):
        raw.append(0)  # filter: none
        start = y * W * 3
        raw += canvas[start:start + W * 3]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    draw_scene()
    out = "/output/entry.png"
    size = write_png(out)
    print(f"Wrote {out}: {W}x{H}, {size} bytes")


if __name__ == "__main__":
    main()
