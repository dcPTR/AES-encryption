from Crypto.PublicKey import RSA


class KeyProvider:
    PRIVATE_KEYS_FILE = "keys/private/private_keys.pem"
    PUBLIC_KEYS_FILE = "keys/public/public_keys.pem"

    def __init__(self):
        open(KeyProvider.PRIVATE_KEYS_FILE, 'w').close()
        open(KeyProvider.PUBLIC_KEYS_FILE, 'w').close()
        self.cur_key = 0

    def add_many_key_pairs(self, n):
        for i in range(n):
            self.add_key_pair()

    def add_key_pair(self):
        private_key, public_key = self.generate_keys()
        print(f"Saving keys...")
        with open(KeyProvider.PRIVATE_KEYS_FILE, "ab") as f:
            f.write(private_key + b"\n\n\n")
        with open(KeyProvider.PUBLIC_KEYS_FILE, "ab") as f:
            f.write(public_key + b"\n\n\n")
        print("Keys generated")

    def generate_keys(self):
        print("Generating keys...")
        key = RSA.generate(2048)
        public_key = key.publickey().exportKey('PEM')
        private_key = key.exportKey()
        return (private_key, public_key)

    def get_key_pair(self):
        f_priv = open(KeyProvider.PRIVATE_KEYS_FILE)
        priv_keys = f_priv.read().split("\n\n\n")

        f_publ = open(KeyProvider.PUBLIC_KEYS_FILE)
        publ_keys = f_publ.read().split("\n\n\n")

        return priv_keys[self.cur_key], publ_keys[self.cur_key]

    def next_key_pair(self):
        self.cur_key += 1
