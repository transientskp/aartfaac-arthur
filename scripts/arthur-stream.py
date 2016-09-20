#!/usr/bin/env python3

import sys
from arthur.stream import loop_images_in_path, setup_stream_pipe, stream

if len(sys.argv) < 2:
    print("This will stream a folder of casacore images to youtube")
    print()
    print("usage: {} <images> <youtube secret>".format(sys.argv[0]))
    sys.exit(1)
else:
    path = sys.argv[1]
    secret = sys.argv[2]


images = loop_images_in_path(path)
pipe = setup_stream_pipe("rtmp://a.rtmp.youtube.com/live2/" + secret)
stream(images, pipe)
