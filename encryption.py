# backend/encryption.py
import hashlib
import os
import random
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.decrepit.ciphers.algorithms import Blowfish
from cryptography.hazmat.primitives.ciphers import Cipher, modes
from cryptography.hazmat.backends import default_backend
from Crypto.Cipher import DES3
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad

def encryptor(edata):

    #splitting
    def div_str(edata):
        data1 = edata[::2]
        data2 = edata[1::2]
        return data1, data2
    data1, data2 = div_str(edata)

    # blowfish algorithm
    def blowfish_encrypt(plaintextb, keyb):
        cipher = Cipher(Blowfish(keyb), modes.CBC(b'\00' * 8), backend=default_backend())
        encryptor = cipher.encryptor()
        padder = padding.PKCS7(64).padder()
        padded_datab = padder.update(plaintextb.encode()) + padder.finalize()
        ciphertextb = encryptor.update(padded_datab) + encryptor.finalize()
        return ciphertextb
    keyb = os.urandom(16)
    plaintextb = data1
    ciphertextb = blowfish_encrypt(plaintextb, keyb)
    keyb1 = keyb.hex()
    ciphertextb1 = ciphertextb.hex()

    
    #TRI-DES encryption
    def trides_key():
        key = get_random_bytes(24)
        return key

    def encrypt_3des(plaintextd, keyd):
        cipher = DES3.new(keyd, DES3.MODE_ECB)
        padded_plaintextd = pad(plaintextd.encode(), DES3.block_size)
        ciphertextd = cipher.encrypt(padded_plaintextd)
        return ciphertextd
    keyd = trides_key()
    plaintextd = data2
    ciphertextd = encrypt_3des(plaintextd, keyd)
    keyd1 = keyd.hex()
    ciphertextd1 = ciphertextd.hex()

    # combine ciphertexts
    len_hex_ciphertextb1 = format(len(ciphertextb1),'04x')
    c = ciphertextb1 + ciphertextd1
    combined_str = len_hex_ciphertextb1 + c

    # combine keys
    bhex_key = keyb1
    dhex_key = keyd1
    combined_key = bhex_key + dhex_key

    #AES KEY
    aes_key = combined_key[:64]

    #AES_ENCRYPTION
    def encrypt(plaintexta, key_bytesa):
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key_bytesa), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(plaintexta.encode()) + padder.finalize()
        ct = encryptor.update(padded_data) + encryptor.finalize()
        return iv + ct
    plaintexta = combined_str
    key_bytesa = bytes.fromhex(aes_key)
    ciphertexta = encrypt(plaintexta, key_bytesa)
    dataaes = ciphertexta.hex()
    return dataaes, combined_key

