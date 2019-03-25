import logging


class LaconicFormatter(logging.Formatter):
    _FMT = '%(message)s'

    def __init__(self):
        super(LaconicFormatter, self).__init__(fmt=self._FMT)


class LaconicStreamHandler(logging.StreamHandler):
    def __init__(self, stream=None):
        super(LaconicStreamHandler, self).__init__(stream)
        self.formatter = LaconicFormatter()
