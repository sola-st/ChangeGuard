
import logging
import os
import sys

LOG_DIRECTORY = '../logs'

skip_logger = logging.getLogger()
skip_logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(message)s')
if not os.path.isdir(LOG_DIRECTORY):
    os.mkdir(LOG_DIRECTORY)
file_handler = logging.FileHandler(f'{LOG_DIRECTORY}/skips.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
# stream_handler = logging.StreamHandler(sys.stdout)
# stream_handler.setLevel(logging.WARNING)
# stream_handler.setFormatter(formatter)

skip_logger.addHandler(file_handler)
# skip_logger.addHandler(stream_handler)
