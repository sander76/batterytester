import logging

lgr = logging.getLogger(__name__)

lgr.debug("message 1")

class Test:
    def __init__(self):
        lgr.debug("yet another test message")
