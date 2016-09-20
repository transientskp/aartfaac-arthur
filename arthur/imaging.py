import struct
import time

import numpy as np
from arthur import constants
from arthur.gridding import image


def create_indices(pol, channels, baselines, pols):
    """
    Creates the indices to obtain an upper triangle of visibilities for a
    certain polarization from a data block as constructed via the GPU
    correlator.

    args:
        pol (int): probably polarisation
        channels (int): number of channels
        baselines (int): number of baselines
        pols (int): number of polarisations
    """
    I = np.empty((channels, baselines), dtype=np.uint32)
    for b in range(baselines):
        for c in range(channels):
            I[c, b] = pol + c * pols + b * pols * channels
    return I.reshape(I.size, 1)


def parse_header(header):
    """
    parse a AARTFAAC visibilities triangle header.

    args:
        header (bytes): an AARTFAAC header

    returns:
        tuple: start, end

    """
    magic, _, start, end = struct.unpack("<IIdd", header[0:24])
    assert magic == constants.HDR_MAGIC
    return start, end


def reshape_body(raw_body, indices, channels, baselines):
    """
    Restructure the data into CHANNELS x BASELINES matrix for a certain
    polarization.

    args:
        raw_body (numpy.array): a flat numpy array
        channels (int): number of channels
        baselines (int): number of baselines

    return:
        numpy.array
    """
    result = np.zeros((channels, baselines), dtype=np.complex64)
    np.copyto(result.reshape(result.size, 1), np.take(raw_body, indices))
    return result


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


def full_calculation(visabilities_file):
    h = open(visabilities_file, 'rb')
    raw_header = h.read(constants.LEN_HDR)
    start_time, end_time = parse_header(raw_header)
    raw_body = np.fromfile(h, count=(constants.NUM_BSLN * constants.NUM_CHAN * constants.NUM_POLS), dtype=np.complex64)
    indices = create_indices(0, constants.NUM_CHAN, constants.NUM_BSLN, constants.NUM_POLS)
    body = reshape_body(raw_body, indices, constants.NUM_CHAN, constants.NUM_BSLN)
    lag_data = np.zeros(60, dtype=np.float32)

    chan_data = np.zeros((constants.NUM_CHAN, 60), dtype=np.float32)

    # channels
    chan_data = np.roll(chan_data, 1)
    chan_data[:, 0] = calc_channels(body)

    # correlation matrix
    cm = correlation_matrix(body, constants.NUM_ANTS)
    corr_data = np.abs(cm)
    corr_data[np.diag_indices(constants.NUM_ANTS)] = np.min(corr_data)

    # lag
    lag_data = np.roll(lag_data, 1)
    lag_data[0] = (time.time() - start_time) - 1.0

    # imager
    img_data = make_image(cm)
    return start_time, img_data