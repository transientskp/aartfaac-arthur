import unittest
import numpy as np
from arthur import gridding
from arthur import constants


class testGridding(unittest.TestCase):
    def test_load_antpos(self):
        gridding.load_antpos(constants.ANTPOS)

    def test_grid(self):
        U = np.zeros((constants.NUM_ANTS, constants.NUM_ANTS), dtype=np.float64)
        V = np.zeros((constants.NUM_ANTS, constants.NUM_ANTS), dtype=np.float64)
        C = np.zeros((constants.NUM_ANTS, constants.NUM_ANTS), dtype=np.complex64)
        duv = constants.C_MS / constants.FRQ / 2.0
        size = constants.IMAGE_RES
        gridding.grid(U, V, C, duv, size)

    def test_image(self):
        corr_mat = np.zeros((constants.NUM_ANTS, constants.NUM_ANTS),
                     dtype=np.complex64)
        antposfile = constants.ANTPOS
        f_hz = constants.FRQ
        size = constants.IMAGE_RES
        gridding.image(corr_mat, antposfile, f_hz, size)
