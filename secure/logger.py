import os
from datetime import datetime
from abc import ABC, abstractmethod
from pathlib import Path


class Logger(ABC):

    @abstractmethod
    def log(self, message):
        pass

    @abstractmethod
    def show(self):
        pass

    @abstractmethod
    def clear(self):
        pass


class TXTLogger(Logger):

    def __init__(self, filename):
        self._filename = Path(filename).resolve()
        if filename is not None and not os.path.isfile(filename):
            self.clear()
        self._filename = Path(filename).resolve()

    @property
    def filename(self):
        return self._filename

    def log(self, message):
        log_message = f'[{datetime.now()}] {message}'
        if self._filename is None:
            print(log_message)
        else:
            with open(self._filename, 'a') as file:
                print(log_message, file=file)

    def show(self):
        with open(self._filename) as file:
            print(file.read())

    def clear(self):
        open(self._filename, 'w').close()
