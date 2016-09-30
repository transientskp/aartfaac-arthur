import struct
from datetime import datetime
import numpy as np
from arthur import constants
import socket
import logging
from functools import lru_cache
from io import BytesIO

logger = logging.getLogger(__name__)


def parse_header(raw_header):
    """
    parse a AARTFAAC visibilities triangle header.

    args:
        header (bytes): an AARTFAAC header

    returns:
        tuple: start date (datetime.time), body (numpy.array)

    """
    magic, _, start, end = struct.unpack("<IIdd", raw_header[0:24])
    assert magic == constants.HDR_MAGIC
    return start, end


def parse_body(raw_body):
    serial_body = np.fromstring(raw_body,  dtype=np.complex64)
    indices = create_indices(0, constants.NUM_CHAN, constants.NUM_BSLN,
                             constants.NUM_POLS)
    body = reshape_body(serial_body, indices, constants.NUM_CHAN,
                        constants.NUM_BSLN)
    return body


def reader(producer, bytes_):
    """Read an amount of bytes from a socket or file"""
    if type(producer) == socket.socket:
        result = BytesIO()
        count = bytes_
        while count > 0:
            recv = producer.recv(count)
            if len(recv) == 0:
                logger.info("client closed connection")
                raise StopIteration("client closed connection")
            count -= len(recv)
            result.write(recv)
        return result.getvalue()
    else:
        # assuming file like interface
        data = producer.read(bytes_)
        if len(data) != bytes_:
            logger.info("end of file")
            raise StopIteration("end of file")
        return data


def read_data(handler):
    """
    read one data window from a file or socket like object.
    args:
        handler: an object with a file like interface (read)
    returns:
        tuple (date, body)
    """
    raw_header = reader(handler, constants.LEN_HDR)
    start_time, end_time = parse_header(raw_header)
    raw_body = reader(handler, constants.LEN_BDY)
    body = parse_body(raw_body)
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
        yield read_data(handler)


@lru_cache()
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


def listen_socket(port=5000, host='localhost'):
    logger.info("waiting for connection...")
    sid = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sid.bind((host, port))
    sid.listen(1)

    while True:
        handler, address = sid.accept()
        logger.info("connection from {}".format(address))
        while True:
            yield read_data(handler)
