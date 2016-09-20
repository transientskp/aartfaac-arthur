import datetime

import ephem
import numpy as np
from arthur import constants
from matplotlib import pyplot as plt


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