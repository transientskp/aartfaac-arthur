import time
from datetime import datetime
import numpy as np
from arthur import constants
from arthur.gridding import image


def correlation_matrix(data, antennas):
    """
    Construct the mean correlation matrix from the CHANNELS x BASELINES data
    matrix.

    args:
        antennas (int): number of antennas

    return:
        numpy.array
    """
    tril_index = np.tril_indices(constants.NUM_ANTS)
    triangle = data.mean(axis=0)
    cm = np.zeros((antennas, antennas), dtype=np.complex64)
    cm[tril_index] = np.conjugate(triangle)
    cm = cm.transpose()
    cm[tril_index] = triangle
    return cm


def calc_channels(data):
    """
    Construct the mean normalized absolute value per channel in dB scale
    """
    pol = np.abs(data.mean(axis=1))
    # prevent div by zero
    if np.sum(pol) > 0:
        pol = 10.0 * np.log10(pol)
    return pol


def make_image(cm):
    # No calibration vector applied
    gains = np.ones((1, constants.NUM_ANTS), dtype=np.complex64)
    cal_mat = gains.conj().transpose() * gains

    # Apply supplied calibration vector
    cm = cal_mat * cm

    return image(cm, constants.ANTPOS, constants.FRQ, constants.IMAGE_RES)


def historical_channels(body):
    """
    Make a matrix of historical channel data

    TODO: add history

    args:
        body (numpy.array): a sky image
    returns:
        numpy.array: a matrix containing historical channel data

    """
    chan_data = np.zeros((constants.NUM_CHAN, 60), dtype=np.float32)
    chan_data = np.roll(chan_data, 1)
    chan_data[:, 0] = calc_channels(body)
    return chan_data


def calculate_lag(date):
    return datetime.now() - date


def historical_lag(start_time):
    # lag
    lag_data = np.zeros(60, dtype=np.float32)
    lag_data = np.roll(lag_data, 1)
    lag_data[0] = (time.time() - start_time) - 1.0


def full_calculation(body):
    # correlation matrix
    cm = correlation_matrix(body, constants.NUM_ANTS)
    corr_data = np.abs(cm)
    corr_data[np.diag_indices(constants.NUM_ANTS)] = np.min(corr_data)

    image = make_image(cm)
    chan_data = historical_channels(body)

    return image, chan_data, corr_data