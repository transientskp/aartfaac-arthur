import struct

import numpy as np
from arthur import constants


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


def read_data(visabilities_file):
    h = open(visabilities_file, 'rb')
    raw_header = h.read(constants.LEN_HDR)
    start_time, end_time = parse_header(raw_header)
    raw_body = np.fromfile(h, count=(constants.LEN_BDY), dtype=np.complex64)
    indices = create_indices(0, constants.NUM_CHAN, constants.NUM_BSLN, constants.NUM_POLS)
    body = reshape_body(raw_body, indices, constants.NUM_CHAN, constants.NUM_BSLN)
    return start_time, body


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