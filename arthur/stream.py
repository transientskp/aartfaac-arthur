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
       ]


def setup_stream_pipe(rtmp_url):
    """
    Setup a encoding process where you can pipe images to.

    args:
        rtmp_url (str): a rtmp url, for example rtmp://a.rtmp.youtube.com/live2/{SECRET}

    returns:
        subprocess.Popen: a subprocess pipe. Use pipe.stdin.write for writing images.
    """
    pipe = subprocess.Popen(cmd + [rtmp_url], stdin=subprocess.PIPE)
    return pipe


def serialize_array(array):
    """
    serialize a numpy array into a binary stream which can be streamed

    args:
        array (numpy.array)

    returns:
        bytes
    """
    data = array.squeeze()
    data -= data.min()
    data *= (255 / data.max())
    arr = data.astype('uint8')
    im = Image.fromarray(arr, 'L')
    return im.tobytes()


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
            return serialize_array(casa_image(image_path).getdata())


def stream(iterator, pipe):
    """
    stream the images returned by generated to rtmp server.

    args:
        iterator (iterator): a image data iterator
        pipe (subprocess.Popen): a pipe created with setup_stream_pipe()
    """
    for image_bytes in iterator:
        for i in range(FPS):
            pipe.stdin.write(serialize_array(image_bytes))
        duty_cycle = 1  # seconds
        time.sleep(duty_cycle - monotonic.monotonic() % duty_cycle)
