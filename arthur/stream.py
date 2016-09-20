import os
from casacore.images import image as casa_image
from PIL import Image
import subprocess
import time
import monotonic
import sys

images_path = '/scratch/aartfaac_with_subbands/S298'
images = sorted([os.path.join(images_path, i) for i in os.listdir(images_path)])

if len(sys.argv) < 2:
    print("usage: {} YOUTUBE_SECRET".format(sys.argv[0]))
    sys.exit(1)
else:
    SECRET = sys.argv[1]

FPS = 25

cmd = ["ffmpeg",
       "-f", "alsa", "-ac", "2", "-i", "hw:0,0",
       #'-i', 'gijs.mp3',
       #'-i', 'playlist.txt',

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
       "rtmp://a.rtmp.youtube.com/live2/" + SECRET    # the youtube stream url
       ]


pipe = subprocess.Popen(cmd, stdin=subprocess.PIPE)


while True:
    for image_path in images:
        print(image_path)
        i = casa_image(image_path)
        data = i.getdata().squeeze()
        data -= data.min()
        data *= (255/data.max())
        arr = data.astype('uint8')
        im = Image.fromarray(arr, 'L')
        for i in range(FPS):
            pipe.stdin.write(im.tobytes())
        duty_cycle = 1  # seconds
        time.sleep(duty_cycle - monotonic.monotonic() % duty_cycle)
