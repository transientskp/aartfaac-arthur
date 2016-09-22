#!/usr/bin/env python3

import sys
from arthur.imaging import full_calculation, calculate_lag
from arthur.io import read_full
from arthur.plot import plot_image, plot_lag, plot_chan_power, plot_corr_mat, plot_diff
from arthur.constants import FRQ
from matplotlib import pyplot


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
    prev_data = date = img_data = chan_data = corr_data = diff_data = None

    for date, body in read_full(path):
        img_data, chan_data, corr_data = full_calculation(body)
        lags += [calculate_lag(date).seconds]
        if prev_data is None:
            prev_data = img_data
        diff_data = img_data - prev_data
        prev_data = img_data

    fig1 = plot_image(date, img_data)
    fig2 = plot_lag(lags)
    fig3 = plot_chan_power(chan_data)
    fig4 = plot_corr_mat(corr_data, FRQ, date)
    fig5 = plot_diff(diff_data, FRQ, date)
    pyplot.show()

if __name__ == '__main__':
    main()