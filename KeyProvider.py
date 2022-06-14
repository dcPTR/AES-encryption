import hashlib

from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad


class KeyProvider:
    PRIVATE_KEYS_FILE = "keys/private/private_keys.pem"
    PUBLIC_KEYS_FILE = "keys/public/public_keys.pem"

    def __init__(self, local_key, iv):
        open(KeyProvider.PRIVATE_KEYS_FILE, 'w').close()
        open(KeyProvider.PUBLIC_KEYS_FILE, 'w').close()
        self.cur_key = 0
        self.my_local_key = local_key
        self.iv = iv

    def add_many_key_pairs(self, n):
        for i in range(n):
            self.add_key_pair()

    def add_key_pair(self):
        private_key, public_key = self.generate_keys()
        print(f"Saving keys...")
        with open(KeyProvider.PRIVATE_KEYS_FILE, "ab") as f:
            private_key = self.encrypt_private_key(private_key)
            f.write(private_key + b"\n\n\n")
        with open(KeyProvider.PUBLIC_KEYS_FILE, "ab") as f:
            f.write(public_key + b"\n\n\n")
        print("Keys generated")

    def generate_keys(self):
        print("Generating keys...")
        key = RSA.generate(2048)
        public_key = key.publickey().exportKey('PEM')
        private_key = key.exportKey()
        return private_key, public_key

    def encrypt_private_key(self, private_key):
        # encrypt the private key using aes in cbc mode
        # the key is the SHA1 of the self.local_key
        key_sha = hashlib.sha1(self.my_local_key.encode('utf-8')).digest()
        key_sha = pad(key_sha, AES.block_size)
        local_aes = AES.new(key_sha, AES.MODE_CBC, self.iv)
        return local_aes.encrypt(pad(private_key, AES.block_size))

    def get_key_pair(self):
        f_priv = open(KeyProvider.PRIVATE_KEYS_FILE, "rb")
        priv_keys = f_priv.read().split(b"\n\n\n")

        f_publ = open(KeyProvider.PUBLIC_KEYS_FILE, "rb")
        publ_keys = f_publ.read().split(b"\n\n\n")
        priv_key = priv_keys[self.cur_key].strip()
        publ_key = publ_keys[self.cur_key].strip()
        with open("keys/private/private_key.pem", "wb") as f:
            f.write(priv_key)
        with open("keys/public/public_key.pem", "wb") as f:
            f.write(publ_key)
        print("Returning keys from key provider")
        return priv_key, publ_key

    def next_key_pair(self):
        self.cur_key += 1