import logging
from os import path, symlink, unlink
import numpy as np
import time
from arthur.imaging import  calculate_lag
from arthur.plot import plot_image, plot_lag, plot_chan_power, plot_corr_mat, plot_diff
from arthur.constants import NUM_CHAN
from matplotlib import pyplot as plt

filename_template = "S{band}_R01-63_{timestamp}_{figure}.png"

logger = logging.getLogger(__name__)


def write_images_to_disk(date, img_data, corr_data, lags, prev_data,
                         chan_data, chan_row, frequency, prefix):
    """
    Calculate and write various images to disk.

    Note that this function has side affects to keep track of history.

    args:
        date (datetime.datetime)
        img_data (numpy.array): the image data
        corr_data (numpy.array): the correlation data
        lags (numpy.array): history of difference between header timestamp and
                            arrival
        prev_data (numpy.array): the previous image, used for calculate diff
        chan_data (numpy.array): the historical chan data, will be
                                 updated using chan_row
        chan_row (numpy.array): the new chan array
        frequency (float): the frequency of the observation
        prefix (str): where to write the images to
    """
    lags += [calculate_lag(date).seconds]
    if prev_data is None:
        prev_data = img_data

        # update historical data
    chan_data = np.roll(chan_data, 1)
    chan_data[:, 0] = chan_row
    diff_data = img_data - prev_data
    prev_data = img_data

    figures = (
        ('image', plot_image(date, img_data, frequency)),
        ('lag', plot_lag(lags)),
        ('chan', plot_chan_power(chan_data)),
        ('corr', plot_corr_mat(corr_data, frequency, date)),
        ('diff', plot_diff(diff_data, frequency, date)),
    )

    timestamp = date.strftime("T%d-%m-%Y-%H-%M-%S%Z")
    some_constant = 195312.5  # not sure what this is, ask Folkert
    for name, figure in figures:
        args = {'band': int(frequency / some_constant),
                'timestamp': timestamp,
                'figure': name}
        filename = filename_template.format(**args)
        full_filename = path.join(prefix, filename)
        logger.info('writing {}'.format(filename))
        figure.savefig(full_filename)  # pad_inches=0, bbox_inches='tight')
        plt.close(figure)  # required to free up memory

        # symlink to latest version
        link_target = path.join(prefix, name + '.png')
        if path.islink(link_target):
            unlink(link_target)
        symlink(filename, link_target)


def make_imaging_closure(prefix, frequency):
    """
    iterate over iterable containing visibilities, makes images and writes them
    into prefix:

    args:
        iterable (iterable): an iterable of generators generating visibilites
        prefix (str): a filesystem prefix where to write the images to
        frequency (float): the central frequency

    return:

    """
    # initialise historical structures
    lags = []
    prev_data = None
    chan_data = np.zeros((NUM_CHAN, 60), dtype=np.float32)

    # we create a closure here so we can store state (
    def closure(date, img_data, corr_data, chan_row):
        """
        args:
            date:
            img_data:
            corr_data:
            chan_row:

        """
        nonlocal prev_data
        write_images_to_disk(date, img_data, corr_data, lags, prev_data,
                             chan_data, chan_row, frequency, prefix)
        prev_data = img_data
    return closure
