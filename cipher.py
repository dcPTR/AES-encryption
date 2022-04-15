from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64

class Cipher:
    def __init__(self):
        self.key = get_random_bytes(16)
        self.mode = "ECB"
        self.cipher = None
        self.iv = None
        self.block_size = None
        self.key_size = None
        self.aes = None
        self.chunk_size = 2**20
        self.set_mode(self.mode)

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

    def encrypt(self):
        # encrypt the file in AED
        # use the encrypt_file function
        # return the ciphertext
        pass

    def encryption_process(self, plaintext):
        if len(plaintext) % 16 != 0:
            plaintext += b' ' * (16 - (len(plaintext) % 16))
        return self.aes.encrypt(plaintext)

    def encrypt_text(self, plaintext):
        # split string plaintext into blocks of 16 bytes
        # if it's not a multiple of 16, pad it
        # then encrypt each block
        # then join the encrypted blocks together
        # make it a string
        # and return the ciphertext in base64

        ciphertext = self.encryption_process(plaintext)
        return base64.b64encode(ciphertext).decode('utf-8')

    def decryption_process(self, ciphertext):
        if len(ciphertext) % 16 != 0:
            ciphertext += b' ' * (16 - (len(ciphertext) % 16))
        return self.aes.decrypt(ciphertext)

    def decrypt_text(self, ciphertext):
        ciphertext = base64.b64decode(ciphertext)
        plaintext = self.decryption_process(ciphertext)
        return plaintext.decode('utf-8').rstrip(' ')

    def encrypt_file(self, source_file, dest_file):
        with open(source_file, 'rb') as f:
            with open(dest_file, 'wb') as f2:
                while True:
                    data = f.read(self.chunk_size)
                    if not data:
                        break
                    f2.write(self.encryption_process(data))
                    # tutaj progress bar

    def decrypt_file(self, source_file, dest_file):
        with open(source_file, 'rb') as f:
            with open(dest_file, 'wb') as f2:
                while True:
                    data = f.read(self.chunk_size)
                    if not data:
                        break
                    f2.write(self.decryption_process(data))
                    # tutaj progress bar
