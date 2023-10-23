
import logging
import os
import sys

LOG_DIRECTORY = '../logs'
if not os.path.isdir(LOG_DIRECTORY):
    os.mkdir(LOG_DIRECTORY)


def get_logger(module, prefix, *, level=logging.INFO, debug=False):
    logger = logging.getLogger(module)
    logger.setLevel(level)

    formatter = logging.Formatter('%(message)s')

    file_handler = logging.FileHandler(f'{LOG_DIRECTORY}/{prefix}_skips.log', encoding='UTF-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    if debug:
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(logging.DEBUG)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
    return logger
