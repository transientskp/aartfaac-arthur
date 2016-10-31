from os import path

IMAGE_RES = 256
C_MS = 299792458.0
NUM_ANTS = 288
NUM_BSLN = int((NUM_ANTS ** 2 + NUM_ANTS) / 2)
NUM_CHAN = 63
NUM_POLS = 2
LEN_HDR = 512
LEN_BDY = NUM_BSLN * NUM_POLS * NUM_CHAN * 8  # complex64 (8 bytes)

HDR_MAGIC = 0x3B98F002
HERE = path.dirname(__file__)
ANTPOS = path.join(HERE, 'lba_outer.dat')
