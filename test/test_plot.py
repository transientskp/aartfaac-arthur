import unittest
from arthur import plot


class testPlot(unittest.TestCase):
    def test_calculate_annotations(self):
        plot.calculate_annotations(date)

    def test_plot_image(self):
        plot.plot_image(startdatetime, img_data)

    def test_plot_lag(self):
        plot.plot_lag(lag_data)

    def test_plot_chan_power(self):
        plot.plot_chan_power(chan_data)

    def test_plot_corr_mat(self):
        plot.plot_corr_mat(corr_data, freq, date)

    def test_plot_diff(self):
        plot.plot_diff(diff_data, freq, date)
