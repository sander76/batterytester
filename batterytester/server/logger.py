import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(level=logging.INFO, log_folder=None):
    logger = logging.getLogger()
    logger.setLevel(level)

    # create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    if log_folder:
        pt = Path(log_folder)

        rfh = RotatingFileHandler(
            str(pt.joinpath("server.log")), maxBytes=10024, backupCount=50
        )
        rfh.setLevel(level)
        rfh.setFormatter(formatter)
        logger.addHandler(rfh)
