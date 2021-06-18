import argparse
import base64
import os
import re

from Crypto.Cipher import AES


class Encryptor(object):
    AES_KEY_SIZE = 32

    def __init__(self, aes_key):
        self.aes_key = aes_key
        if not aes_key or len(aes_key) != self.AES_KEY_SIZE:
            raise Exception("aes_key should be 256 bits long: got %r" % aes_key)

    def encrypt_binary(self, plaintext):
        cipher = AES.new(self.aes_key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(plaintext)
        data = [cipher.nonce, ciphertext, tag]
        return ":".join([base64.b64encode(i).decode() for i in data])

    def decrypt_binary(self, ciphertext):
        nonce, ciphertext, tag = [base64.b64decode(
            i) for i in ciphertext.split(":")]
        cipher = AES.new(self.aes_key, AES.MODE_GCM, nonce=nonce)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        return plaintext

    def encrypt_string(self, plaintext, encoding="utf-8"):
        return self.encrypt_binary(plaintext.encode(encoding))

    def decrypt_string(self, ciphertext, encoding="utf-8"):
        return self.decrypt_binary(ciphertext).decode(encoding)


def _decrypt_secret(env, key, project_folder):
    secret_file_path = os.path.join(project_folder, 'secret', 'decrypt', f'{env}_values.yml')
    with open(secret_file_path, 'rb+') as f:
        print(f'decrypt {secret_file_path}')
        encryptor = Encryptor(key.encode())
        result = encryptor.decrypt_binary(f.read().decode())
        f.seek(0)
        f.write(result)
        f.truncate()


def _decrypt_case_secret(env, key, case_folder):
    for dir_path, _dir_names, files in os.walk(case_folder):
        for file in files:
            if re.compile(f'{env}_(.*?).yml').match(file):
                matched_file_path = os.path.join(dir_path, file)
                with open(matched_file_path, 'rb+') as f:
                    print(f'decrypt {matched_file_path}')
                    encryptor = Encryptor(key.encode())
                    result = encryptor.decrypt_binary(f.read().decode())
                    f.seek(0)
                    f.write(result)
                    f.truncate()


def main():
    parser = argparse.ArgumentParser(prog='crypto')
    parser.add_argument('-e', '--env', help='The env to test', type=str, required=True)
    parser.add_argument('-k', '--key', help='The key of AES for encrypt/decrypt', type=str, required=True)
    parser.add_argument('-p', '--test-data-path', dest="path", help='The path of test data', type=str)
    args = parser.parse_args()

    env = args.env
    key = args.key
    path = '.' if args.path is None else args.path

    _decrypt_secret(env, key, f'{path}')
    _decrypt_case_secret(env, key, f'{path}/cases')


if __name__ == "__main__":
    main()