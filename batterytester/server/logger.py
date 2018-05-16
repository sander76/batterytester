import logging
from logging import Logger
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(logger: Logger, log_folder=None):
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    ch.setFormatter(formatter)

    logger.addHandler(ch)

    if log_folder:
        pt = Path(log_folder)

        rfh = RotatingFileHandler(str(pt.joinpath('server.log')),
                                  maxBytes=10024, backupCount=10)
        rfh.setLevel(logging.INFO)
        rfh.setFormatter(formatter)
        logger.addHandler(rfh)
