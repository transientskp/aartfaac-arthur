from setuptools import setup, find_packages
from Cython.Build import cythonize

__version__ = "0.2dev"


install_requires = (
    'pillow',
    'python-casacore',
    'astropy',
    'ephem',
    'matplotlib',
    'scipy',
    'monotonic',
    'Cython',
)


scripts = [
    'scripts/arthur-plot.py',
    'scripts/arthur-stream.py',
]

setup(
    name="aartfaac-arthur",
    version=__version__,
    packages=find_packages(),
    scripts=scripts,
    install_requires=install_requires,
    package_data={
        '': ['*.txt', '*.rst'],
        'arthur': ['lba_outer.dat'],
    },
    author="Gijs Molenaar",
    author_email="gijs@pythonic.nl",
    description="AARTFAAC visualisation utilities",
    license="GPL3",
    keywords="science astronomy aartfaac",
    url="https://github.com/transientskp/aartfaac-arthur",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.5",
        "Topic :: Scientific/Engineering",
        ],
    ext_modules=cythonize("arthur/gridding_fast.pyx"),
)
