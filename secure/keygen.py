from random import randint
import json
from pathlib import Path

SERVER_PUBLIC_FILE = Path('server_keys/public.txt')
SERVER_PRIVATE_FILE = Path('server_keys/certs.json')
CLIENT_PUBLIC_FILE = Path('client_keys/public.txt')
CLIENT_PRIVATE_FILE = Path('client_keys/private.txt')

def get_public_key(secrete_number, g, p):
    return g ** secrete_number % p


def get_private_key(public_key, secrete_number, p):
    return public_key ** secrete_number % p


def gen_client_keys(count, g, p, server_public_key):
    for i in range(count + 1):
        b = randint(2, p - 1)
        client_public_key = get_public_key(b, g, p)
        private_key = get_private_key(server_public_key, b, p)

        if i == 0:
            CLIENT_PUBLIC_FILE.write_text(str(client_public_key))
            CLIENT_PRIVATE_FILE.write_text(str(private_key))

        with open(SERVER_PRIVATE_FILE) as file:
            certs = json.load(file)

        certs[client_public_key] = str(private_key)

        with open(SERVER_PRIVATE_FILE, 'w') as file:
            json.dump(certs, file)


def main():
    count = 10
    print('Генерация ключей...')
    p = 365021
    g = randint(2, 10)
    a = randint(2, p - 1)
    server_public_key = get_public_key(a, g, p)
    SERVER_PUBLIC_FILE.write_text(str(server_public_key))

    with open(SERVER_PRIVATE_FILE, 'w') as file:
        json.dump({}, file)

    gen_client_keys(10, g, p, server_public_key)
    print(f'Успешно сгенерированы {count} ключей')


if __name__ == '__main__':
    main()
