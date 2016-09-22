import ephem
import numpy as np
from arthur import constants
from matplotlib import pyplot as plt


def calculate_annotations(date):
    """
    Calculates the positions of a list of bodies in the sky, as seen from
    CS002 on LOFAR and based on the datetime.

    args:
        date (datetime.datetime): For what moment to calculate positions

    returns:
        dict: name of object name, value a tuple for position.
    """
    obs = ephem.Observer()
    obs.pressure = 0  # To prevent refraction corrections.
    obs.lon, obs.lat = '6.869837540', '52.915122495'  # CS002 on LOFAR
    objects = [
        ephem.Moon(),
        ephem.Jupiter(),
        ephem.Sun(),
        ephem.readdb('Cas-A,f|J, 23:23:26.0, 58:48:00,99.00,2000'),
        ephem.readdb('Cyg-A,f|J, 19:59:28.35, 40:44:02,99.00,2000'),
        ephem.readdb('NCP,f|J, 0, 90:00:00,99.00,2000'),
        ephem.readdb('Galactic Center,f|J, 17:45:40.0, -29:00:28.1,99.00, 2000'),
    ]

    # annotations
    obs.date = date

    # Compute local coordinates of all objects to be plotted.
    annotations = {}
    for o in objects:
        o.compute(obs)
        if o.alt > 0:
            l = -(np.cos(o.alt) * np.sin(o.az))
            m = (np.cos(o.alt) * np.cos(o.az))
            annotations[o.name] = (l, m)

    return annotations


def plot_image(startdatetime, img_data):
    """
    Plot a sky image with object overlay.

    args:
        date (datetime.time): start datetime of observation
        img_data (numpy.array): a numpy array with image data

    returns:
        matplotlib.figure.Figure
    """
    annotations = calculate_annotations(startdatetime)

    # fft image
    img_min = img_data.min()
    img_max = img_data.max()
    l = np.linspace(-1, 1, constants.IMAGE_RES)
    m = np.linspace(-1, 1, constants.IMAGE_RES)
    mask = np.ones((constants.IMAGE_RES, constants.IMAGE_RES))
    xv, yv = np.meshgrid(l, m)
    mask[np.sqrt(np.array(xv ** 2 + yv ** 2)) > 1] = np.NaN

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    img = ax.imshow(img_data * mask, interpolation='bilinear',
               cmap=plt.get_cmap('jet'), vmin=img_min, vmax=img_max,
               extent=[l[0], l[-1], m[0], m[-1]])
    fig.colorbar(img, cmap=plt.get_cmap('jet'), norm=plt.Normalize(vmin=img_min,
                                                              vmax=img_max))

    arrowprops = {'facecolor': 'white', 'width': 1, 'headwidth': 4,
                  'headlength': 5, 'shrink': 0.15, 'edgecolor': 'white'}
    for source, pos in annotations.items():
        ax.annotate(source, xy=pos, xytext=(pos[0] + 0.1, pos[1] + 0.1),
                     color='white', arrowprops=arrowprops,
                     horizontalalignment='left', verticalalignment='bottom')
    moment = startdatetime.strftime("%Y-%m-%d_%H:%M:%S %Z")
    ax.set_title('XX-%.2f MHz-%s' % (constants.FRQ / 1e6, moment))
    ax.set_xlabel(r'$\leftarrow East - West \rightarrow$')
    ax.set_ylabel(r'$\leftarrow South - North \rightarrow$')
    return fig


def plot_lag(lag_data):
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(lag_data)
    ax.set_title('Lag')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Lag (s)')
    return fig


def plot_chan_power(chan_data):
    # Check if the chan_data has non-zero values. If the stations are turned
    # off, correlator still runs, but generates visibilities with value 0. The
    # dataselection below then generates a ValueError.
    if (np.any(chan_data)):
        chan_min, chan_max = chan_data[chan_data != 0].min(), chan_data[
            chan_data != 0].max()
    else:
        chan_min = 0
        chan_max = 0

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    img = ax.imshow(chan_data, interpolation='nearest',
                    cmap=plt.get_cmap('afmhot'), vmin=chan_min, vmax=chan_max)
    fig.colorbar(img, cmap=plt.get_cmap('afmhot'),
                 norm=plt.Normalize(vmin=chan_min, vmax=chan_max))
    ax.set_title('Channel Power (dB)')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Channels')
    return fig


def plot_corr_mat(corr_data, freq, date):
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    img = ax.imshow(corr_data, interpolation='nearest',
               cmap=plt.get_cmap('jet'), vmin=corr_data.min(),
               vmax=corr_data.max(), extent=[288, 0, 288, 0])
    ax.set_title('Dipole Covariance XX-%.2f MHz-%s' % (
    freq / 1e6, date.strftime("%Y-%m-%d_%H:%M:%S %Z")))
    ax.set_xticks([])
    ax.set_yticks([])
    return fig


def plot_diff(diff_data, freq, date):
    annotations = calculate_annotations(date)
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    diff_min, diff_max = diff_data.min(), diff_data.max()
    img = ax.imshow(diff_data, interpolation='bilinear',
                    cmap=plt.get_cmap('coolwarm'), vmin=diff_min, vmax=diff_max)
    fig.colorbar(img, cmap=plt.get_cmap('coolwarm'),
                 norm=plt.Normalize(vmin=diff_min, vmax=diff_max))

    arrowprops = {'facecolor': 'white', 'width': 1, 'headwidth': 4,
                  'headlength': 5, 'shrink': 0.15, 'edgecolor': 'white'}

    for source, pos in annotations.items():
        ax.annotate(source, xy=pos, xytext=(pos[0] + 0.1, pos[1] + 0.1),
                     color='white', arrowprops=arrowprops,
                     horizontalalignment='left', verticalalignment='bottom')
    moment = date.strftime("%Y-%m-%d_%H:%M:%S %Z")
    plt.title('XX-%.2f MHz Difference-%s' % (freq/1e6, moment))
    plt.xlabel(r'$\leftarrow East - West \rightarrow$')
    plt.ylabel(r'$\leftarrow South - North \rightarrow$')
    plt.xticks([])
    plt.yticks([])
