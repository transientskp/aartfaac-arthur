import unittest
from arthur import stream


class testStream(unittest.TestCase):
    def test_setup_stream_pipe(self):
        stream.setup_stream_pipe(rtmp_url)

    def test_loop_images_in_path(self):
        stream.loop_images_in_path(path)

    def test_stream(self):
        stream.stream(iterator, rtmp_stream)
