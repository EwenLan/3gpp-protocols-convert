import logging
import os
import time


class Log:
    log: logging.Logger

    def __init__(self, logger: str) -> None:
        self.log = logging.getLogger(logger)
        self.log.setLevel(logging.DEBUG)
        os.makedirs("log", exist_ok=True)
        formatter = logging.Formatter(
            fmt="[[%(levelname)-s][%(asctime)-s][%(filename)s:%(lineno)s]%(message)s]")
        fileLog = logging.FileHandler(time.strftime(
            "log/%Y-%m-%d.log"), mode="w", encoding="utf-8")
        stdOutLog = logging.StreamHandler()
        stdOutLog.setFormatter(formatter)
        fileLog.setFormatter(formatter)
        self.log.addHandler(fileLog)
        self.log.addHandler(stdOutLog)

    def getLogger(self) -> logging.Logger:
        return self.log
