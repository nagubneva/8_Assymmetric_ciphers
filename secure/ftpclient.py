import socket

from ftpserver import STATUS_SUCCESS, STATUS_EMPTY_RESPONSE

IP = 'localhost'
PORT = 8080
EXIT = 'exit'


class FTPClient:

    def __init__(self, ip=IP, port=PORT, encryptor=None):
        self._ip = ip
        self._port = port
        self._encryptor = encryptor
        self._socket = socket.socket()
        self.username = ''

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def connect(self):
        self._socket.connect((self._ip, self._port))
        self.auth()

    def auth(self):
        username = input('Введите имя: ')
        password = input('Введите пароль: ')
        self._username = username
        self.send_text((username + ' ' + password))
        response = self.recv_text()
        if response == STATUS_SUCCESS:
            self.on_success()
        else:
            self.on_fail()

    def on_success(self):
        while True:
            pwd = self.recv_text()
            command = input(self.get_invite(pwd))
            if command == EXIT:
                break
            self.send_text(command)
            response = self.recv_text()
            if response != STATUS_EMPTY_RESPONSE:
                print(response)

    def on_fail(self):
        print('Ошибка: неверный пароль')

    def get_invite(self, pwd):
        return f'{self._username}:{pwd}$ '

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
