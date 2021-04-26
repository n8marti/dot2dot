#!/usr/bin/env python3

'''
Convert an image into a dot-to-dot drawing.
'''

import sys

from pathlib import Path
from PIL import Image, ImageFilter

infile = Path('./images/unicorn-03.jpg').resolve()
if len(sys.argv) > 1:
    infile = Path(sys.argv[1]).resolve()

out_name = infile.stem
in_ext = infile.suffix
out_raster = Path.home() / f"{out_name}{in_ext}"
out_scalar = Path.home() / f"{out_name}.svg"

# Using grayscale conversion.
image = Image.open(infile)
mask = image.convert('L')
th = 150
th = 225
mask = mask.point(lambda i: i < th and 255)
#mask.save(out_raster)

# Using ImageFilter.
#image = image.filter(ImageFilter.EDGE_ENHANCE)
filters = [ImageFilter.CONTOUR, ImageFilter.FIND_EDGES]
out_image = image.filter(filters[0])
out_image.save(out_raster)


# Convert to SVG
import cv2
import svgwrite

img = cv2.imread(str(out_raster), cv2.IMREAD_UNCHANGED)
ret, mask = cv2.threshold(img[:, :, 2], 0, 255, cv2.THRESH_BINARY)

def add_pixel_fillers(img, cnt):
    n_points = len(cnt)
    for idx in range(n_points):
        prev_pt = cnt[(idx+n_points+1) % n_points]
        next_pt = cnt[(idx+1) % n_points]
        if abs(cnt[idx][0]-next_pt[0])==1 and abs(cnt[idx][1]-next_pt[1])==1:
            temp_x, temp_y = max(cnt[idx][0], next_pt[0]), min(cnt[idx][1], next_pt[1])
            if img[temp_y, temp_x] == 255:
                cnt[idx][0] = temp_x
                cnt[idx][1] = temp_y
            else:
                temp_x, temp_y = min(cnt[idx][0], next_pt[0]), max(cnt[idx][1], next_pt[1])
                if img[temp_y, temp_x] == 255:
                    cnt[idx][0] = temp_x
                    cnt[idx][1] = temp_y
    return cnt

contours, hierarchy = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

h, w = width=img.shape[0], img.shape[1]
dwg = svgwrite.Drawing(out_scalar, height=h, width=w, viewBox=(f'-10 -10 {h} {w}'))
for cnt in contours:
    cnt = add_pixel_fillers(mask, cnt.squeeze().tolist())
    dwg.add(dwg.polygon(
        points=cnt,
        stroke_linecap='round',
        stroke='black',
        fill='none',
        stroke_linejoin='miter'
        ))
dwg.save()
