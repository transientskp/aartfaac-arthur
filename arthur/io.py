import struct
from datetime import datetime
import numpy as np
from arthur import constants


def parse_header(header):
    """
    parse a AARTFAAC visibilities triangle header.

    args:
        header (bytes): an AARTFAAC header

    returns:
        tuple: start date (datetime.time), body (numpy.array)

    """
    print(len(header))
    magic, _, start, end = struct.unpack("<IIdd", header[0:24])
    assert magic == constants.HDR_MAGIC
    return start, end


def read_data(handler):
    """
    read one data window from a file like object.
    args:
        handler: an object with a file like interface (read)
    returns:
        tuple (date, body)
    """
    raw_header = handler.read(constants.LEN_HDR)
    if len(raw_header) != constants.LEN_HDR:
        raise(IOError('end of file'))
    start_time, end_time = parse_header(raw_header)
    raw_body = np.fromfile(handler, count=(constants.LEN_BDY),
                           dtype=np.complex64)
    indices = create_indices(0, constants.NUM_CHAN, constants.NUM_BSLN,
                             constants.NUM_POLS)
    body = reshape_body(raw_body, indices, constants.NUM_CHAN,
                        constants.NUM_BSLN)
    date = datetime.utcfromtimestamp(start_time)
    return date, body


def read_full(path):
    """
    Open file in path and read until end.

    args:
        path (str): a path to a visibilities file
    returns:
        iterator
    """
    handler = open(path, 'rb')
    while True:
        try:
            yield read_data(handler)
        except IOError:
            raise StopIteration


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