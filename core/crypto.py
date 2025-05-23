from cryptography.fernet import Fernet
import base64
import os

def get_key():
    return base64.urlsafe_b64encode(os.urandom(32))

def encrypt_password(password: str, key: bytes) -> str:
    f = Fernet(key)
    return f.encrypt(password.encode()).decode()

def decrypt_password(encrypted: str, key: bytes) -> str:
    f = Fernet(key)
    return f.decrypt(encrypted.encode()).decode()
