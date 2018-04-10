import logging
from logging import Logger
from logging.handlers import RotatingFileHandler


def get_logger(logger: Logger, log_file=None,log_file_location=None):
    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)

    logger.addHandler(sh)

    if log_file:
        rfh = RotatingFileHandler()
