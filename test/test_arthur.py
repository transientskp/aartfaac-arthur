import arthur
import unittest
from os import path

import arthur.imaging
import arthur.plot

HERE = path.dirname(__file__)
VIS_PATH = path.join(HERE, 'data/2aartfaac.vis')


class TestArthur(unittest.TestCase):
    def test_arthur(self):
        start_time, img_data = arthur.imaging.full_calculation(VIS_PATH)
        arthur.plot.plot_image(start_time, img_data)