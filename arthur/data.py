from functools import lru_cache

from arthur import constants
import numpy as np


@lru_cache()
def load_antpos(path):
    """
    Load antenna positions and compute U,V coordinates

    args:
        path (str): path to antenna pos file

    returns:
        tuple: (numpy.array, numpy.array)
    """
    A = np.loadtxt(path)
    R = np.array([[-0.1195950000, -0.7919540000, 0.5987530000],
                  [0.9928230000, -0.0954190000, 0.0720990000],
                  [0.0000330000, 0.6030780000, 0.7976820000]])
    L = A.dot(R)

    U = np.zeros((constants.NUM_ANTS, constants.NUM_ANTS), dtype=np.float64)
    V = np.zeros((constants.NUM_ANTS, constants.NUM_ANTS), dtype=np.float64)

    for a1 in range(constants.NUM_ANTS):
        for a2 in range(constants.NUM_ANTS):
            U[a1, a2] = L[a1, 0] - L[a2, 0]
            V[a1, a2] = L[a1, 1] - L[a2, 1]
    return U, V