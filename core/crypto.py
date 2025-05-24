from cryptography.fernet import Fernet
import os

def get_or_create_key():
    if not os.path.exists("vault.key"):
        with open("vault.key", "wb") as f:
            f.write(Fernet.generate_key())
    with open("vault.key", "rb") as f:
        return f.read()

KEY = get_or_create_key()

def encrypt_password(password: str, key: bytes = KEY) -> str:
    f = Fernet(key)
    return f.encrypt(password.encode()).decode()

def decrypt_password(encrypted: str, key: bytes = KEY) -> str:
    f = Fernet(key)
    return f.decrypt(encrypted.encode()).decode()
