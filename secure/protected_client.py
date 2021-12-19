import socket
from pathlib import Path


import cipher
import ftpclient


EXIT = 'exit'


class SecureClient:

    @classmethod
    def load_key(cls, filename):
        return Path(filename).read_text()

    def __init__(self, public_key_filename, private_key_filename,
                 host='localhost', port=8080):
        self._public_key = self.load_key(public_key_filename)
        self._private_key = self.load_key(private_key_filename)
        self._encryptor = None
        self._host = host
        self._port = port
        self._socket = socket.socket()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def connect(self):
        self._socket.connect((self._host, self._port))
        self.send_text(self._public_key)
        self._encryptor = cipher.Vigenere(self._private_key)
        port = self.recv_text()
        if port:
            print('Ваш публичный ключ сертифицирован')
            print(f'Подключаемся на FTP сервер по порту {port}')
            with ftpclient.FTPClient(port=int(port),
                                         encryptor=self._encryptor) as client:
                client.connect()
        else:
            print('Ваш публичный ключ не сертифицирован')

    def recv_text(self, bufsize=1024, encoding='utf-8'):
        text = self._socket.recv(bufsize).decode(encoding)
        if self._encryptor:
            decrypted = self._encryptor.decrypt(text)
            print('Получено:', text)
            print('Расшифровано:', decrypted)
            return decrypted
        return text

    def send_text(self, text, encoding='utf-8'):
        if self._encryptor:
            text = self._encryptor.encrypt(text)
        self._socket.send(text.encode(encoding))

    def close(self):
        self._socket.close()

print(Path('../client_keys/public.txt').resolve())
with SecureClient('../client_keys/public.txt',
                  '../client_keys/private.txt') as client:
    client.connect()