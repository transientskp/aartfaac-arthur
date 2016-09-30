#!/usr/bin/env python3

import logging
from arthur.io import listen_socket


def main():
    logging.basicConfig(level=logging.INFO)
    for bla in listen_socket():
        print(bla)

if __name__ == '__main__':
    main()
