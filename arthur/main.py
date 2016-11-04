import logging
from arthur.writer import make_imaging_closure
from arthur.imaging import full_calculation
from arthur.stream import setup_stream_pipe, stream
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Manager


logger = logging.getLogger(__name__)


def image_queue_pusher(date, body, frequency, queue):
    """
    Do calculations and put results in a queue. Run this in a thread or
    multiprocess.
    """
    result = full_calculation(body, frequency)
    queue.put([date] + list(result))


def queue_repeater(in_queue, out_queues):
    """
    Listen for incoming objects on a queue, replay on out queues.

    args:
        in_queue (Queue): in coming
        out_queues (list):
    """
    logger.debug("repeater starting")
    while True:
        result = in_queue.get()
        logger.debug("Going to repeat something on repeat queue ({})".format(in_queue.qsize()))
        for queue in out_queues:
            queue.put(result)
        logger.debug("Done repeating")


def write_scheduler(queue, frequency, media_root):
    """
    Queue listener that will make images and write them to disk. Run in thread
    or multiprocess.
    """
    imager_writer = make_imaging_closure(media_root, frequency)
    while True:
        result = queue.get()
        logger.debug("recieved on writer queue ({})".format(queue.qsize()))
        imager_writer(*result)
        logger.debug("done writing")


def stream_scheduler(queue, youtube_url):
    """
    Queue listener that will stream images to youtube. Run in thread
    or multiprocess.
    """
    pipe = setup_stream_pipe(youtube_url)
    while True:
        _, img_data, _, _ = queue.get()
        logger.debug("Got something from stream queue ({})".format(queue.qsize()))
        stream(img_data, pipe)
        logger.debug("done streaming")


def big_fat_loop_that_does_everything(generator, frequency,
                                      media_root, youtube_url):
        manager = Manager()
        repeat_queue = manager.Queue()
        writer_queue = manager.Queue()
        stream_queue = manager.Queue()

        with ProcessPoolExecutor() as executor:
            executor.submit(queue_repeater, repeat_queue,
                            [writer_queue, stream_queue])
            executor.submit(write_scheduler, writer_queue,
                            frequency, media_root)
            executor.submit(stream_scheduler, stream_queue, youtube_url)
            for date, body in generator:
                logging.info("processing image timestamped {}".format(date))
                executor.submit(image_queue_pusher, date, body,
                                frequency, repeat_queue)
            print("done! now what")

