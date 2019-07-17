import logging


class dlog:
    _name: str = ""
    _log_file: str = ""
    _formatter = logging.Formatter('%(message)s')
    _logger = None

    def __init__(self):
        pass

    @staticmethod
    def setup_logger(name=None, log_file=None, level=logging.INFO):
        """Function setup as many loggers as you want"""

        if name is None:
            name = dlog._name
        if log_file is None:
            log_file = dlog._log_file

        handler = logging.FileHandler(log_file, 'w')
        handler.setFormatter(dlog._formatter)

        dlog._name = name
        dlog._log_file = log_file

        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.addHandler(handler)

        dlog._logger = logger
        dlog.debug("logger initialized")

    @staticmethod
    def name():
        return dlog._name

    @staticmethod
    def logger():
        return dlog.logger()

    @staticmethod
    def log_file():
        return dlog._log_file

    @staticmethod
    def debug(msg):
        return dlog._logger.debug(msg)
