import hashlib
import os
import struct

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from Crypto.Util.Padding import pad, unpad
from KeyProvider import KeyProvider


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
        self.chunk_size = 2 ** 20
        self.set_mode(self.mode)
        self.encryped_key = None
        self.public_rec_key = None
        self.provider = None
        with open("local.key") as f:
            self.my_local_key = f.read()
        self.initialize_key_provider()

    def initialize_key_provider(self):
        self.provider = KeyProvider(self.my_local_key, self.iv)
        self.provider.add_many_key_pairs(2)


    def encrypt_key(self):
        # encrypt the key using the public key
        try:
            print("Encrypting key...")
            with open('keys/public/public_key_rec.pem', 'rb') as f:
                public_key = RSA.importKey(f.read())
                cipher = PKCS1_OAEP.new(public_key)
                self.encryped_key = cipher.encrypt(self.key)
                print(f"Key encrypted. Length of the key: {len(self.encryped_key)}")
        except:
            print("Error: public key of the receiver not found")

    def set_decrypted_key(self, encryped_key):
        # decrypt key using the private key
        priv, _ = self.provider.get_key_pair()
        print("Set decrypted key...")
        key_decrypted = self.decrypt_private_key(priv)
        print("Importing private key...")
        private_key = RSA.importKey(key_decrypted)
        self.key = PKCS1_OAEP.new(private_key).decrypt(encryped_key)
        print(f"Key imported. Length of the key: {len(self.key)}")

    def set_key(self, key):
        self.key = key

    def set_mode(self, mode, gui=None):
        self.mode = mode
        if self.mode == "CBC":
            self.aes = AES.new(self.key, AES.MODE_CBC, self.iv)
            if gui is not None:
                gui.cipherModeCBC.click()
        else:
            self.aes = AES.new(self.key, AES.MODE_ECB)
            if gui is not None:
                gui.cipherModeECB.click()

    def set_cipher(self, cipher):
        self.cipher = cipher

    def set_iv(self, iv):
        self.iv = iv
        self.set_mode(self.mode)

    def encryption_process(self, plaintext):
        if len(plaintext) % 16 != 0:
            plaintext += b' ' * (16 - (len(plaintext) % 16))
        return self.aes.encrypt(plaintext)

    def encrypt_text(self, plaintext):
        # self.provider.next_key_pair()
        try:
            self.encrypt_key()
        except:
            print("Error: public key of the receiver not found")
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

    def encrypt_file(self, source_file, dest_file, gui):
        # self.provider.next_key_pair()
        try:
            self.encrypt_key()
        except:
            print("Error: public key of the receiver not found")

        print("Encrypting file...")
        filesize = os.path.getsize(source_file)
        with open(source_file, 'rb') as f:
            with open(dest_file, 'wb') as f2:
                # write the key in the file
                f2.write(struct.pack('<Q', filesize))
                if not gui.connectButton.isEnabled():
                    f2.write(self.encryped_key)
                f2.write(self.iv)
                f2.write(self.mode.encode('utf-8'))
                while True:
                    data = f.read(self.chunk_size)
                    if not data:
                        break
                    f2.write(self.encryption_process(data))
                    gui.progressBar.setValue(int(f.tell() / filesize * 100))

    def decrypt_file(self, source_file, dest_file, gui):
        filesize = os.path.getsize(source_file)
        with open(source_file, 'rb') as f:
            with open(dest_file, 'wb') as f2:
                print("Reading parametres from file...")
                originalsize = struct.unpack('<Q', f.read(struct.calcsize('Q')))[0]
                if not gui.connectButton.isEnabled():
                    self.set_decrypted_key(f.read(256))
                self.set_iv(f.read(16))
                self.set_mode(f.read(3).decode('utf-8'), gui=gui)
                print("Decrypting file...")
                while True:
                    data = f.read(self.chunk_size)
                    if not data:
                        break
                    f2.write(self.decryption_process(data))
                    gui.update_progress(f.tell(), filesize)
                f2.truncate(originalsize)

    def decrypt_private_key(self, private_key):
        # decrypt the private key using aes in cbc mode
        # the key is the SHA1 of the self.local_key
        print("Decrypting private key...")
        key_sha = hashlib.sha1(self.my_local_key.encode('utf-8')).digest()
        key_sha = pad(key_sha, AES.block_size)
        local_aes = AES.new(key_sha, AES.MODE_CBC, self.iv)
        return unpad(local_aes.decrypt(private_key), AES.block_size)
