import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


# def setup_logging(log_folder=None):
#     ch = logging.StreamHandler()
#     ch.setLevel(logging.DEBUG)
#
#     # create formatter
#     formatter = logging.Formatter(
#         '%(asctime)s - %(name)s - %(levelname)s - %(message)s\n')
#
#     ch.setFormatter(formatter)
#
#     logger.addHandler(ch)
#
#     if log_folder:
#         pt = Path(log_folder)
#
#         rfh = RotatingFileHandler(str(pt.joinpath('server.log')),
#                                   maxBytes=10024, backupCount=10)
#         rfh.setLevel(logging.INFO)
#         rfh.setFormatter(formatter)
#         logger.addHandler(rfh)


def setup_logging(level=logging.INFO, log_folder=None):
    logger = logging.getLogger()
    logger.setLevel(level)
    #ch = logging.StreamHandler()
    #ch.setLevel(logging.INFO)

    # create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    #ch.setFormatter(formatter)

    #logger.addHandler(ch)

    if log_folder:
        pt = Path(log_folder)

        rfh = RotatingFileHandler(str(pt.joinpath('server.log')),
                                  maxBytes=10024, backupCount=50)
        rfh.setLevel(level)
        rfh.setFormatter(formatter)
        logger.addHandler(rfh)
