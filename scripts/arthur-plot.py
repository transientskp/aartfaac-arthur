#!/usr/bin/env python3

import sys
import numpy as np
from arthur.imaging import full_calculation, calculate_lag
from arthur.io import read_full
from arthur.plot import plot_image, plot_lag, plot_chan_power, plot_corr_mat, plot_diff
from arthur.constants import NUM_CHAN
from matplotlib import pyplot

FRQ = 58398437.5  # Central observation frequency in Hz

def main():
    if len(sys.argv) < 2:
        print("Image the first set of visibilites from a visibilities file")
        print()
        print("usage: {} <file>".format(sys.argv[0]))
        sys.exit(1)
    else:
        path = sys.argv[1]

    # define them here so we can access them out of for loop scope
    lags = []
    prev_data = date = img_data = corr_data = diff_data = None
    chan_data = np.zeros((NUM_CHAN, 60), dtype=np.float32)

    for date, body in read_full(path):
        img_data, corr_data, chan_row = full_calculation(body, FRQ)
        lags += [calculate_lag(date).seconds]
        if prev_data is None:
            prev_data = img_data
        chan_data = np.roll(chan_data, 1)
        chan_data[:, 0] = chan_row
        diff_data = img_data - prev_data
        prev_data = img_data

    fig_img = plot_image(date, img_data, FRQ)
    fig_lag = plot_lag(lags)
    fig_chan = plot_chan_power(chan_data)
    fig_cm = plot_corr_mat(corr_data, FRQ, date)
    fig_diff = plot_diff(diff_data, FRQ, date)
    pyplot.show()

if __name__ == '__main__':
    main()
