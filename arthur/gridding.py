import numpy as np
from arthur import constants
from functools import lru_cache


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


def grid(U, V, C, duv, size):
    G = np.zeros((size, size), np.complex64)
    G.fill(0)
    for a1 in range(constants.NUM_ANTS):
        for a2 in range(constants.NUM_ANTS):
            p = 1.0
            if a1 == a2:
                p = 0.5

            u = U[a1, a2] / duv + size / 2 - 1
            v = V[a1, a2] / duv + size / 2 - 1

            w = int(np.floor(u))
            e = int(np.ceil(u))
            s = int(np.floor(v))
            n = int(np.ceil(v))

            west_power = p - (u - w)
            east_power = p - (e - u)
            south_power = p - (v - s)
            north_power = p - (n - v)

            south_west_power = south_power * west_power
            north_west_power = north_power * west_power
            south_east_power = south_power * east_power
            north_east_power = north_power * east_power

            G[s, w] += south_west_power * C[a1, a2]
            G[n, w] += north_west_power * C[a1, a2]
            G[s, e] += south_east_power * C[a1, a2]
            G[n, e] += north_east_power * C[a1, a2]
    return G


def image(corr_mat, antposfile, f_hz, size):
    """
    Create an image from the correlation matrix
    """
    U, V = load_antpos(antposfile)
    mDuv = constants.C_MS / f_hz / 2.0
    gridvis = grid(U, V, corr_mat, mDuv, size)
    gridvis = np.fft.fftshift(gridvis)
    gridvis = np.flipud(np.fliplr(gridvis))
    gridvis = np.conjugate(gridvis)
    return np.real(np.fft.fftshift(np.fft.fft2(gridvis)))
