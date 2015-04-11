#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys
import argparse
import json
import os
from collections import defaultdict
import imagearray


def print8(*args):
    print " ".join(unicode(x).encode(u"utf-8") for x in args)

def printerr8(*args):
    print >>sys.stderr, " ".join(unicode(x).encode(u"utf-8") for x in args)


vic_luminance = [0, 15, 4, 11, 5, 9, 1, 14, 6, 2, 10, 3, 8, 13, 7, 12]

def hires_char(image):
    color_counts = defaultdict(int)
    for y in xrange(8):
        for x in xrange(8):
            color_counts[image.get_pixel(x, y)] += 1
    if len(color_counts) > 2:
        return None
    elif len(color_counts) == 1:
        fg = color_counts.keys()[0]
        bg = 0
        if fg == 0:
            fg = 1
            bg = 0
    else:
        bg, fg = sorted(color_counts.keys(), cmp=lambda x,y: cmp(vic_luminance[x], vic_luminance[y]))
    if (bg, fg) == (6, 14):
        (bg, fg) = (fg, bg)
    bytes = list()
    for y in xrange(8):
        byte = 0
        bit = 0x80
        for x in xrange(8):
            if image.get_pixel(x, y) == fg:
                byte |= bit
            bit >>= 1
        bytes.append(byte)
    return (bytes, fg, bg)


def hires_font(image):
    bitmap = list()
    colors = list()
    for y in xrange(0, 32, 8):
        for x in xrange(0, 256, 8):
            char_image = image.copy(x, y, 8, 8)
            try:
                bytes, fg, bg = hires_char(char_image)
            except TypeError:
                return None
            bitmap.extend(bytes)
            colors.append((fg << 4) | bg)
    return (bitmap, colors)


def main(argv):
    p = argparse.ArgumentParser()
    p.add_argument(u"-v", u"--verbose", action=u"store_true",
                   help=u"Verbose output.")
    p.add_argument(u"png")
    p.add_argument(u"font")
    args = p.parse_args([x.decode(u"utf-8") for x in argv[1:]])
    
    image = imagearray.ImageArray.load(args.png)
    bitmap, colors = hires_font(image)
    if bitmap is None:
        printerr8(u"color error in font")
        return 1
    
    with open(args.font, u"wb") as f:
        f.write("".join(chr(x) for x in bitmap))
        f.write("".join(chr(x) for x in colors))
    
    return 0
    

if __name__ == '__main__':
    sys.exit(main(sys.argv))
    
