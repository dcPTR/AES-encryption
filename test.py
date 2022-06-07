import unittest
from unittest.mock import Mock
import filecmp
from KeyProvider import KeyProvider
from cipher import Cipher
from tcp_handler import TCPHandler


class TestStringMethods(unittest.TestCase):

    def test_encryption(self):
        cipher = Cipher()
        msg = "foobar"
        ciphered = cipher.encrypt_text(msg)
        deciphered = cipher.decrypt_text(ciphered)
        self.assertEqual(deciphered, msg)

    def test_encryption_CBC(self):
        cipher = Cipher()
        cipher.set_mode("CBC")
        msg = "foobar"
        ciphered = cipher.encrypt_text(msg)
        deciphered = cipher.decrypt_text(ciphered)
        self.assertEqual(deciphered, msg)

    def test_encrypt_file(self):
        cipher = Cipher()
        mock = Mock()
        cipher.encrypt_file("testFiles/1.txt", "testFiles/1cipher.txt", mock)
        cipher.decrypt_file("testFiles/1cipher.txt", "testFiles/1decipher.txt", mock)
        self.assertTrue(filecmp.cmp("testFiles/1.txt", "testFiles/1decipher.txt"))

    def test_encrypt_file_CBC(self):
        cipher = Cipher()
        cipher.set_mode("CBC")
        mock = Mock()
        cipher.encrypt_file("testFiles/1.txt", "testFiles/1cipher.txt", mock)
        cipher.decrypt_file("testFiles/1cipher.txt", "testFiles/1decipher.txt", mock)
        self.assertTrue(filecmp.cmp("testFiles/1.txt", "testFiles/1decipher.txt"))

    def test_encrypt_big_file(self):
        cipher = Cipher()
        mock = Mock()
        cipher.encrypt_file("testFiles/500.txt", "testFiles/500cipher.txt", mock)
        cipher.decrypt_file("testFiles/500cipher.txt", "testFiles/500decipher.txt", mock)
        self.assertTrue(filecmp.cmp("testFiles/500.txt", "testFiles/500decipher.txt"))

    def test_encrypt_big_file_CBC(self):
        cipher = Cipher()
        cipher.set_mode("CBC")
        mock = Mock()
        cipher.encrypt_file("testFiles/500.txt", "testFiles/500cipher.txt", mock)
        cipher.decrypt_file("testFiles/500cipher.txt", "testFiles/500decipher.txt", mock)
        self.assertTrue(filecmp.cmp("testFiles/500.txt", "testFiles/500decipher.txt"))

    def test_message_parts(self):
        tcp = TCPHandler(5000, 5001)
        msg = "foobar"*(int(tcp.MAX_BUF/4))
        parts = tcp.get_message_parts(msg)
        merged = "".join(parts)
        tcp.disconnect()
        self.assertEqual(merged, msg)

    def test_generating_keys(self):
        n = 5
        key_provider = KeyProvider()
        key_provider.add_many_key_pairs(n)
        keys_not_empty = True
        for i in range(n):
            priv, publ = key_provider.get_key_pair()
            key_provider.next_key_pair()
            if len(priv) == 0 or len(publ) == 0:
                keys_not_empty = False
                break

        self.assertTrue(keys_not_empty and key_provider.cur_key == n)


if __name__ == '__main__':
    unittest.main()
