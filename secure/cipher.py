import hashlib
from abc import ABC, abstractmethod
from collections import Counter


class Cipher(ABC):

    MIN_ORD = 0
    MAX_ORD = 65536

    @staticmethod
    def chars(ords):
        return ''.join(Cipher._get_sequence(chr, ords))

    @staticmethod
    def ords(chars):
        return Cipher._get_sequence(ord, chars)

    @staticmethod
    def _get_sequence(function, sequence):
        return tuple(map(function, sequence))

    def __init__(self, key):
        self._key = key

    @abstractmethod
    def encrypt(self, text):
        pass

    @abstractmethod
    def decrypt(self, text):
        pass


class Caesar(Cipher):

    @classmethod
    def hack(cls, text):
        key = ord(Counter(text).most_common()[0][0]) - ord(' ')
        return cls(key).decrypt(text)

    def encrypt(self, text):
        return self.chars(
            [(x + self._key) % self.MAX_ORD for x in self.ords(text)]
        )

    def decrypt(self, text):
        self._invert_key()
        result = self.encrypt(text)
        self._invert_key()
        return result

    def _invert_key(self):
        self._key = -self._key


class Vigenere(Cipher):

    def __init__(self, key):
        super().__init__(hashlib.sha256(key.encode()).hexdigest())

    def encrypt(self, text):
        return self.chars(
            [
                (x ^ y) % self.MAX_ORD for x, y in
                zip(self.ords(text), self.ords(self._get_shift_key(text)))
            ]
        )

    def decrypt(self, text):
        return self.encrypt(text)

    def _get_shift_key(self, text):
        return self._key * (len(text) // len(self._key)) \
               + self._key[:len(text) % len(self._key)]
