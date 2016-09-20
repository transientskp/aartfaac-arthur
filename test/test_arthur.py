import arthur
import unittest

VIS_PATH = '/scratch/vis/S295-160818140952.vis'


class TestArthur(unittest.TestCase):
    def test_arthur(self):
        start_time, img_data = arthur.full_calculation(VIS_PATH)
        arthur.plot_image(start_time, img_data)