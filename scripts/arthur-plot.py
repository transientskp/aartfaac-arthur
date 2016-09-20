#!/usr/bin/env python3

import sys
from arthur.imaging import full_calculation
from arthur.io import read_data
from arthur.plot import plot_image

if len(sys.argv) < 2:
    print("Image the first set of visibilites from a visibilities file")
    print()
    print("usage: {} <file>".format(sys.argv[0]))
    sys.exit(1)
else:
    path = sys.argv[1]

start_time, body = read_data(path)
img_data = full_calculation(body)
plot_image(start_time, img_data)
