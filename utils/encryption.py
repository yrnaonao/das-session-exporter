import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def get_encryption_key():
    """
    从环境变量获取加密密钥，如果没有则生成一个
    """
    password = os.getenv("ENCRYPTION_PASSWORD", "default_password_for_encryption")
    salt = b'salt_32bytes_length_for_pbkdf2'  # 在生产环境中应该从环境变量获取
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key


def encrypt_string(plaintext: str) -> str:
    """
    加密字符串
    """
    f = Fernet(get_encryption_key())
    encrypted_bytes = f.encrypt(plaintext.encode())
    return base64.urlsafe_b64encode(encrypted_bytes).decode()


def decrypt_string(encrypted_text: str) -> str:
    """
    解密字符串
    """
    f = Fernet(get_encryption_key())
    encrypted_bytes = base64.urlsafe_b64decode(encrypted_text.encode())
    decrypted_bytes = f.decrypt(encrypted_bytes)
    return decrypted_bytes.decode()