import unittest

from arthur.data import load_antpos
import numpy as np
from arthur import gridding
from arthur import constants

FRQ = 58398437.5  # Central observation frequency in Hz

class testGridding(unittest.TestCase):
    def test_load_antpos(self):
        load_antpos(constants.ANTPOS)

    def test_grid(self):
        U = np.zeros((constants.NUM_ANTS, constants.NUM_ANTS), dtype=np.float64)
        V = np.zeros((constants.NUM_ANTS, constants.NUM_ANTS), dtype=np.float64)
        C = np.zeros((constants.NUM_ANTS, constants.NUM_ANTS), dtype=np.complex64)
        duv = constants.C_MS / FRQ / 2.0
        size = constants.IMAGE_RES
        gridding.grid(U, V, C, duv, size)


