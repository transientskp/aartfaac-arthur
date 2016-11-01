#!/usr/bin/env python3

import sys
from arthur.io import read_full
import numpy as np
from arthur import constants
from arthur.data import load_antpos
from arthur.imaging import correlation_matrix

from arthur.gridding_fast import grid as grid_fast
from arthur.gridding import grid
import time

FRQ = 58398437.5  # Central observation frequency in Hz


def main():
    if len(sys.argv) < 2:
        print("Image the first set of visibilites from a visibilities file")
        print()
        print("usage: {} <file>".format(sys.argv[0]))
        sys.exit(1)
    else:
        path = sys.argv[1]

    _, body = next(read_full(path))
    cm = correlation_matrix(body, constants.NUM_ANTS)
    corr_data = np.abs(cm)
    corr_data[np.diag_indices(constants.NUM_ANTS)] = np.min(corr_data)
    gains = np.ones((1, constants.NUM_ANTS), dtype=np.complex64)
    cal_mat = gains.conj().transpose() * gains
    cm = cal_mat * cm
    U, V = load_antpos(constants.ANTPOS)
    mDuv = constants.C_MS / FRQ / 2.0

    normal = []
    for i in range(5):
        start = time.time()
        grid(U, V, cm, mDuv, constants.IMAGE_RES)
        end = time.time()
        normal.append(end-start)
    print("normal: {}".format(np.average(normal)))

    fast = []
    for i in range(5):
        start = time.time()
        grid_fast(U, V, cm, mDuv, constants.IMAGE_RES)
        end = time.time()
        fast.append(end-start)
    print("fast: {}".format(np.average(fast)))

if __name__ == '__main__':
    main()
