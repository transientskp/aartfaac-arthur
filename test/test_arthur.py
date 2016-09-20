import arthur
import unittest
from os import path


HERE = path.dirname(__file__)
VIS_PATH = path.join(HERE, 'data/2aartfaac.vis')


class TestArthur(unittest.TestCase):
    def test_arthur(self):
        start_time, img_data = arthur.full_calculation(VIS_PATH)
        arthur.plot_image(start_time, img_data)