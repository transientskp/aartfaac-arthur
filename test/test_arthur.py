import arthur
import unittest
from os import path

import arthur.imaging
import arthur.plot
import arthur.io

HERE = path.dirname(__file__)
VIS_PATH = path.join(HERE, 'data/2aartfaac.vis')


class TestArthur(unittest.TestCase):
    def test_arthur(self):
        start_time, body = arthur.io.read_data(VIS_PATH)
        img_data = arthur.imaging.full_calculation(body)
        arthur.plot.plot_image(start_time, img_data)