import os
from casacore.images import image as casa_image
from PIL import Image
import subprocess
import time
import monotonic

FPS = 25

cmd = ["ffmpeg",
       "-f", "alsa", "-ac", "2", "-i", "hw:0,0",

       # stream image
       '-re',
       '-f', 'rawvideo',           # probably required for reading from stdin
       '-s', '1024x1024',          # should match image size
       '-pix_fmt', 'gray',
       '-i', '-',                  # read from stdin

       "-r", str(FPS),             # the framerate
       "-vcodec", "libx264",       # probably required for flv & rtmp

       "-preset", "ultrafast",     # the encoding quality preset
       "-g", "20",
       "-codec:a", "libmp3lame",   # mp3 for audio
       "-ar", "44100",             # 44k audio rate
       "-threads", "6",
       "-bufsize", "512k",
       "-f", "flv",                # required for rtmp
       {}                          # the rtmp stream url
       ]


def setup_stream_pipe(rtmp_url):
    """
    Setup a encoding process where you can pipe images to.

    args:
        rtmp_url (str): a rtmp url, for example rtmp://a.rtmp.youtube.com/live2/{SECRET}

    returns:
        subprocess.Popen: a subprocess pipe. Use pipe.stdin.write for writing images.
    """
    pipe = subprocess.Popen(cmd.format(rtmp_url), stdin=subprocess.PIPE)
    return pipe


def loop_images_in_path(path):
    """
    args:
        path (str): path to folder containing images

    returns:
        generator: yields casacore images
    """
    images = sorted([os.path.join(path, i) for i in os.listdir(path)])
    while True:
        for image_path in images:
            image = casa_image(image_path)
            data = image.getdata().squeeze()
            data -= data.min()
            data *= (255 / data.max())
            arr = data.astype('uint8')
            im = Image.fromarray(arr, 'L')
            return im.tobytes()


def stream(iterator, rtmp_stream):
    """
    stream the images returned by generated to rtmp server

    args:
        iterator (iterator): a image data iterator
        rtmp_stream (str): a rtmp url
    """
    pipe = setup_stream_pipe(rtmp_stream)
    for image_bytes in iterator:
        for i in range(FPS):
            pipe.stdin.write(image_bytes)
        duty_cycle = 1  # seconds
        time.sleep(duty_cycle - monotonic.monotonic() % duty_cycle)
