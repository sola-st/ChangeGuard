
import logging
import os
import sys

LOG_DIRECTORY = 'logs'
if not os.path.isdir(LOG_DIRECTORY):
    os.mkdir(LOG_DIRECTORY)


def get_logger(module, name, *, level=logging.INFO):
    logger = logging.getLogger(module)
    logger.setLevel(level)

    formatter = logging.Formatter('%(message)s')

    file_handler = logging.FileHandler(f'{LOG_DIRECTORY}/{name}.log', encoding='UTF-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger
