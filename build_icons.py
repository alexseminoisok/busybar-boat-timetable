"""Regenerates the Apps-menu icons (river boat on waves)."""
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "community.boat_timetable", "appmeta")
AMBER = (255, 140, 0, 255)
DARK = (60, 60, 60, 255)
WATER = (30, 140, 200, 255)

FRONT = [            # 8x8, colour: # hull/cabin, w window, ~ water
    "........",
    "..####..",
    "..#ww#..",
    ".######.",
    "########",
    ".######.",
    "~~.~~.~~",
    ".~~.~~.~",
]
BACK = [             # 11x11, greyscale: # on, . off
    "...........",
    "....####...",
    "....#..#...",
    "..#######..",
    "###########",
    ".#########.",
    "..#######..",
    "...........",
    "##.##.##.##",
    ".##.##.##.#",
    "...........",
]

def build(rows, mode, colours, name):
    h, w = len(rows), len(rows[0])
    im = Image.new(mode, (w, h), 0)
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in colours:
                im.putpixel((x, y), colours[ch])
    im.save(os.path.join(OUT, name))

build(FRONT, "RGBA", {"#": AMBER, "w": DARK, "~": WATER}, "icon_front_8x8.png")
build(BACK, "L", {"#": 255}, "icon_back_11x11.png")
