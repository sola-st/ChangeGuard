import logging
import os
import sys

LOG_DIRECTORY = 'logs'
if not os.path.isdir(LOG_DIRECTORY):
    os.mkdir(LOG_DIRECTORY)


def get_logger(module, to_stream=True, to_file=False, *, level=logging.INFO):
    logger = logging.getLogger(module)
    logger.setLevel(level)
    formatter = logging.Formatter('"%(name)s" : %(message)s')
    if to_stream:
        stream_handler = logging.StreamHandler(sys.stderr)
        stream_handler.setLevel(logging.DEBUG)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
    if to_file:
        file_handler = logging.FileHandler(f'{LOG_DIRECTORY}/{module}.log', encoding='UTF-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    return logger
