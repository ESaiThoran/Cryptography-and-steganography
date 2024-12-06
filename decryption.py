import hashlib
import os
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.decrepit.ciphers.algorithms import Blowfish
from cryptography.hazmat.primitives.ciphers import Cipher, modes
from Crypto.Util.Padding import unpad
from Crypto.Cipher import DES3

def decryptor(ddata, tot_key):

                    
                    #splitting key for aes
                    AES_key = tot_key[:64]
                    
                    #splitting key for blowfish and tri-des
                    keyB = tot_key[:32]  
                    keyD = tot_key[32:]  

                    #AES decryption
                    def decrypt(ciphertextA, key_bytesA):
                        iv = ciphertextA[:16]
                        ct = ciphertextA[16:]
                        cipher = Cipher(algorithms.AES(key_bytesA), modes.CBC(iv), backend=default_backend())
                        decryptor = cipher.decryptor()
                        pt = decryptor.update(ct) + decryptor.finalize()
                        unpadder = padding.PKCS7(128).unpadder()
                        unpadded_data = unpadder.update(pt) + unpadder.finalize()
                        return unpadded_data.decode()
                    ciphertextA_hex = ''.join(filter(lambda c: c in '0123456789abcdefABCDEF', ddata))
                    ciphertextA = bytes.fromhex(ciphertextA_hex)
                    key_bytesA = bytes.fromhex(AES_key)
                    decryptedtextA = decrypt(ciphertextA, key_bytesA)

                    #splitting data for blowfish and tri-des
                    # Extract the first 4 characters and convert to decimal
                    n_c = int(decryptedtextA[:4], 16)
                    r_str = decryptedtextA[4:]
                    ciphertextB1 = r_str[:n_c]
                    ciphertextD1 = r_str[n_c:]

                    #blowfish decryption
                    def blowfish_decrypt(ciphertextB, keyB):
                        cipher = Cipher(Blowfish(keyB), modes.CBC(b'\00' * 8), backend=default_backend())
                        decryptor = cipher.decryptor()
                        padded_dataB = decryptor.update(ciphertextB) + decryptor.finalize()
                        unpadder = padding.PKCS7(64).unpadder()
                        plaintextB = unpadder.update(padded_dataB) + unpadder.finalize()
                        return plaintextB.decode()
                    ciphertextB = ciphertextB1
                    ciphertextB_bytes = bytes.fromhex(ciphertextB)
                    keyB_bytes = bytes.fromhex(keyB)
                    decryptedtextB = blowfish_decrypt(ciphertextB_bytes, keyB_bytes)

                    #TRI-DES Encryption
                    def decrypt_3des(ciphertextD, keyD):
                        decipher = DES3.new(keyD, DES3.MODE_ECB)
                        padded_plaintextD = decipher.decrypt(ciphertextD)
                        plaintextD = unpad(padded_plaintextD, DES3.block_size)
                        return plaintextD.decode()
                    ciphertextD = ciphertextD1 
                    ciphertextD_bytes = bytes.fromhex(ciphertextD)
                    keyD_bytes = bytes.fromhex(keyD)
                    decryptedtextD = decrypt_3des(ciphertextD_bytes, keyD_bytes)
    
                    def combined_str(decryptedtextB, decryptedtextD):
                        combined = []
                        for i in range(max(len(decryptedtextB), len(decryptedtextD))):
                            if i < len(decryptedtextB):
                                combined.append(decryptedtextB[i])
                            if i < len(decryptedtextD):
                                combined.append(decryptedtextD[i])
                        return ''.join(combined)
                    COMBINED_STR = combined_str(decryptedtextB, decryptedtextD)

                    return COMBINED_STR
