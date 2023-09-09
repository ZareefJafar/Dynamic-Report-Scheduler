
from Crypto.Cipher import AES
import json
import binascii
from Crypto.Cipher import AES
from Crypto import Random
import base64
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import binascii, os
import hashlib




HASH_NAME = "SHA512"
IV_LENGTH = 12
ITERATION_COUNT = 65535
KEY_LENGTH = 32
SALT_LENGTH = 16
TAG_LENGTH = 16

def decrypt(password, cipher_message):
    decoded_cipher_byte = base64.b64decode(cipher_message)

    salt = decoded_cipher_byte[:SALT_LENGTH]
    iv = decoded_cipher_byte[SALT_LENGTH : (SALT_LENGTH + IV_LENGTH)]
    encrypted_message_byte = decoded_cipher_byte[
        (IV_LENGTH + SALT_LENGTH) : -TAG_LENGTH
    ]
    tag = decoded_cipher_byte[-TAG_LENGTH:]
    secret = get_secret_key(password, salt)
    cipher = AES.new(secret, AES.MODE_GCM, iv)

    decrypted_message_byte = cipher.decrypt_and_verify(encrypted_message_byte, tag)
    print(decrypted_message_byte.decode("utf-8"))
    return decrypted_message_byte.decode("utf-8")


def get_secret_key(password, salt):
    return hashlib.pbkdf2_hmac(
        HASH_NAME, password.encode(), salt, ITERATION_COUNT, KEY_LENGTH
    )


outputFormat = "{:<25}:{}"
secret_key = input("Enter key: ") 
encrypted_text = input("Enter decrypted text: ")

decrypted_text = decrypt(secret_key, encrypted_text)

print("\n------ AES-GCM Decryption ------")
print(outputFormat.format("decryption input", encrypted_text))
print(outputFormat.format("decryption output", decrypted_text))
