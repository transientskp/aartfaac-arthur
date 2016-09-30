import unittest
from arthur import io


class testIo(unittest.TestCase):
    def test_parse_header(self):
        io.parse_header(raw_header)

    def test_parse_body(self):
        io.parse_body(raw_body)

    def test_reader(self):
        io.reader(producer, bytes_)

    def test_read_data(self):
        io.read_data(handler)

    def test_read_full(self):
        io.read_full(path)

    def test_create_indices(self):
        io.create_indices(pol, channels, baselines, pols)

    def test_reshape_body(self):
        io.reshape_body(raw_body, indices, channels, baselines)

    def test_listen_socket(self):
        io.listen_socket(port=5000, host='localhost')
