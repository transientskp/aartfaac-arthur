#!/usr/bin/env python3

import logging
from arthur.io import listen_socket


def main():
    logging.basicConfig(level=logging.INFO)
    for date, mat in listen_socket():
        print(date)

if __name__ == '__main__':
    main()
