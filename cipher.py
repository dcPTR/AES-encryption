import os
import struct

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5

class Cipher:
    def __init__(self):
        self.key = get_random_bytes(16)
        self.mode = "ECB"
        self.cipher = None
        self.iv = get_random_bytes(16)
        self.block_size = None
        self.key_size = None
        self.aes = None
        # chunk_size equal to to 1 MB (2**20) as a power of 2
        self.chunk_size = 2**20
        self.set_mode(self.mode)
        self.generate_keys()

    def set_key(self, key):
        self.key = key

    def set_mode(self, mode):
        self.mode = mode
        if self.mode == "CBC":
            self.aes = AES.new(self.key, AES.MODE_CBC, self.iv)
        else:
            self.aes = AES.new(self.key, AES.MODE_ECB)

    def set_cipher(self, cipher):
        self.cipher = cipher

    def set_iv(self, iv):
        self.iv = iv
        self.set_mode(self.mode)

    def encrypt(self):
        # encrypt the file in AES
        # use the encrypt_file function
        # return the ciphertext
        pass

    def encryption_process(self, plaintext):
        if len(plaintext) % 16 != 0:
            plaintext += b' ' * (16 - (len(plaintext) % 16))
        return self.aes.encrypt(plaintext)

    def encrypt_text(self, plaintext):
        ciphertext = self.encryption_process(plaintext.encode('utf-8'))
        return base64.b64encode(ciphertext).decode('utf-8')

    def decryption_process(self, ciphertext):
        if len(ciphertext) % 16 != 0:
            ciphertext = ciphertext[:-(len(ciphertext) % 16)]
        return self.aes.decrypt(ciphertext)

    def decrypt_text(self, ciphertext):
        # to prevent TypeError in CBC mode: decrypt() cannot be called after encrypt()
        # we recreate the cipher object (self.aes) using self.set_mode(self.mode)
        self.set_mode(self.mode)
        ciphertext = base64.b64decode(ciphertext)
        plaintext = self.decryption_process(ciphertext)
        return plaintext.decode('utf-8').rstrip(' ')

    def encrypt_file(self, source_file, dest_file, obj):
        filesize = os.path.getsize(source_file)
        with open(source_file, 'rb') as f:
            with open(dest_file, 'wb') as f2:
                f2.write(struct.pack('<Q', filesize))
                f2.write(self.iv)
                while True:
                    data = f.read(self.chunk_size)
                    if not data:
                        break
                    f2.write(self.encryption_process(data))
                    obj.progressBar.setValue(int(f.tell()/filesize*100))

    def decrypt_file(self, source_file, dest_file, obj):
        filesize = os.path.getsize(source_file)
        with open(source_file, 'rb') as f:
            with open(dest_file, 'wb') as f2:
                originalsize = struct.unpack('<Q', f.read(struct.calcsize('Q')))[0]
                self.set_iv(f.read(16))
                while True:
                    data = f.read(self.chunk_size)
                    if not data:
                        break
                    f2.write(self.decryption_process(data))
                    obj.update_progress(f.tell(), filesize)
                f2.truncate(originalsize)

    def generate_keys(self):
        key = RSA.generate(2048)
        public_key = key.publickey()
        private_key = key.exportKey()
        # save the public key in a file
        with open('keys/public_key.pem', 'wb') as f:
            f.write(public_key.exportKey('PEM'))
        # save the private key in a file
        with open('keys/private_key.pem', 'wb') as f:
            f.write(private_key)

