import arthur
import unittest
from os import path

import arthur.imaging
import arthur.plot
import arthur.io

HERE = path.dirname(__file__)
VIS_PATH = path.join(HERE, 'data/2aartfaac.vis')
FRQ = 58398437.5  # Central observation frequency in Hz


class TestArthur(unittest.TestCase):
    def test_arthur(self):
        start_time, body = arthur.io.read_data(open(VIS_PATH, 'rb'))
        image, corr_data, chan_row = arthur.imaging.full_calculation(body, FRQ)
        arthur.plot.plot_image(start_time, image, FRQ)
