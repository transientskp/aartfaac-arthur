import unittest
from arthur import imaging
from arthur import constants
import numpy as np


class testImaging(unittest.TestCase):
    def tets_correlation_matrix(self):
        data = np.zeros((constants.NUM_ANTS, constants.NUM_ANTS), dtype=np.complex64)
        antennas = constants.NUM_ANTS
        imaging.correlation_matrix(data, antennas)

    def test_calc_channels(self):
        data = np.zeros((constants.NUM_ANTS, constants.NUM_ANTS),
                        dtype=np.complex64)
        imaging.calc_channels(data)

    def test_make_image(self):
        cm = np.zeros((constants.NUM_ANTS, constants.NUM_ANTS),
                     dtype=np.complex64)
        imaging.make_image(cm)

    def test_historical_channels(self):
        imaging.historical_channels(body, new_row)

    def test_calculate_lag(self):
        imaging.calculate_lag(date)

    def test_historical_lag(self):
        imaging.historical_lag(start_time)

    def test_full_calculation(self):
        body = np.zeros((constants.NUM_ANTS, constants.NUM_ANTS),
                        dtype=np.complex64)
        imaging.full_calculation(body)
