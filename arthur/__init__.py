import datetime
import struct
import time

import ephem
import numpy as np
from matplotlib import pyplot as plt

import arthur.imager as img
from arthur import constants


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

    return img.image(cm, constants.ANTPOS, constants.FRQ, constants.IMAGE_RES)


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


def plot_image(start_time, img_data):

    # initialize ephem, for image annotations
    obs = ephem.Observer()
    obs.pressure = 0  # To prevent refraction corrections.
    obs.lon, obs.lat = '6.869837540', '52.915122495'  # CS002 on LOFAR
    obs_data = {}
    obs_data['Moon'] = ephem.Moon()
    obs_data['Jupiter'] = ephem.Jupiter()
    obs_data['Sun'] = ephem.Sun()
    obs_data['Cas.A'] = ephem.readdb('Cas-A,f|J, 23:23:26.0, 58:48:00,99.00,2000')
    obs_data['Cyg.A'] = ephem.readdb('Cyg-A,f|J, 19:59:28.35, 40:44:02,99.00,2000')
    obs_data['NCP'] = ephem.readdb('NCP,f|J, 0, 90:00:00,99.00,2000')
    obs_data['Gal. Center'] = ephem.readdb('Galactic Center,f|J, 17:45:40.0, -29:00:28.1,99.00, 2000')

    # annotations
    date = datetime.datetime.utcfromtimestamp(start_time)
    obs.date = date

    # Compute local coordinates of all objects to be plotted.
    annotations = {}
    for k, v in obs_data.items():
        v.compute(obs)
        if v.alt > 0:
            l = -(np.cos(v.alt) * np.sin(v.az))
            m = (np.cos(v.alt) * np.cos(v.az))
            annotations[k] = (l, m)

    # fft image
    img_min, img_max = img_data.min(), img_data.max()
    l = np.linspace(-1, 1, constants.IMAGE_RES)
    m = np.linspace(-1, 1, constants.IMAGE_RES)
    mask = np.ones((constants.IMAGE_RES, constants.IMAGE_RES))
    xv, yv = np.meshgrid(l, m)
    mask[np.sqrt(np.array(xv ** 2 + yv ** 2)) > 1] = np.NaN
    plt.imshow(img_data * mask, interpolation='bilinear',
               cmap=plt.get_cmap('jet'), vmin=img_min, vmax=img_max,
               extent=[l[0], l[-1], m[0], m[-1]])
    plt.colorbar(cmap=plt.get_cmap('jet'), norm=plt.Normalize(vmin=img_min,
                                                              vmax=img_max))
    for a in annotations.keys():
        plt.annotate(a, xy=annotations[a],
                     xytext=(annotations[a][0] + 0.1, annotations[a][1] + 0.1),
                     color='white',
                     arrowprops=dict(facecolor='white', width=1, headwidth=4,
                                     headlength=5, shrink=0.15, edgecolor='white'),
                     horizontalalignment='left',
                     verticalalignment='bottom')
    plt.title('XX-%.2f MHz-%s' % (
        constants.FRQ / 1e6, date.strftime("%Y-%m-%d_%H:%M:%S %Z")))
    plt.xlabel(r'$\leftarrow East - West \rightarrow$')
    plt.ylabel(r'$\leftarrow South - North \rightarrow$')
    plt.show()
