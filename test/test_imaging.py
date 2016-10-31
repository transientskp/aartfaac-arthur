import unittest
from arthur import imaging
from arthur import constants
import numpy as np


FRQ = 58398437.5  # Central observation frequency in Hz


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
        imaging.make_image(cm, FRQ)
