import socket
import json
import random
from pathlib import Path

import cipher
import logger
import users_storage
import filemanager
import ftpserver


MIN_PORT = 1024
MAX_PORT = 65535


class SecureServer:

    @classmethod
    def load_certs(cls, filename):
        with open(filename) as file:
            return json.load(file)

    @classmethod
    def load_key(cls, filename):
        return Path(filename).read_text()

    def __init__(self, public_key_filename, certs_filename, port=8080):
        self._port = port
        self._public_key = self.load_key(public_key_filename)
        self._certs = self.load_certs(certs_filename)
        self._socket = socket.socket()
        self._socket.bind(('', self._port))
        self._socket.listen()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    @property
    def certs(self):
        return self._certs

    def accept(self):
        conn, addr = self._socket.accept()
        SecureServerHandler(conn, addr, self).handle()

    def close(self):
        self._socket.close()


class SecureServerHandler:

    def __init__(self, conn, addr, server):
        self._socket = conn
        self._ip = addr[0]
        self._port = addr[1]
        self._server = server
        self._encryptor = None
        self._protected_port = None
        self._protected_socket = None

    @property
    def socket(self):
        return self._socket

    @property
    def ip(self):
        return self._ip

    @property
    def port(self):
        return self._port

    @property
    def server(self):
        return self._server

    def handle(self):
        client_public_key = self.recv_text()
        print(f'Публичный ключ {client_public_key} клиента получен')
        if client_public_key in self._server.certs:
            print('Публичный ключ клиент сертифицирован')
            private_key = self._server.certs[client_public_key]
            print(f'Приватный ключ клиента {private_key} извлечен')
            self._encryptor = cipher.Vigenere(private_key)
            sock, port = listen_random_port()
            self._protected_socket = sock
            print(f'Отправка порта {port} клиенту')
            self.send_text(str(port))
            self.on_success()
        else:
            print('Публичный ключ клиент не сертифицирован')


    def on_success(self):
        print('Запуск FTP сервера')
        users = users_storage.JSONUsersStorage('users.json')
        txt_logger = logger.TXTLogger('logs.txt')
        with ftpserver.FTPServer(port=self._protected_port,
                                     file_manager=filemanager.FileManager,
                                     users=users,
                                     logger=txt_logger,
                                     sock=self._protected_socket,
                                     encryptor=self._encryptor,
                                     location='storage') as server:
            server.accept()

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


def listen_random_port():
    sock = socket.socket()
    while True:
        port = random.randint(MIN_PORT, MAX_PORT)
        try:
            sock.bind(('', port))
        except socket.error:
            pass
        else:
            return sock, port


with SecureServer('server_keys/public.txt',
                  'server_keys/certs.json') as server:
    server.accept()