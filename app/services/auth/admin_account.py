import os
import hashlib
import binascii
import hmac
from dotenv import load_dotenv


load_dotenv()

def _hash_password(password: str, salt: str, iterations: int = 100_000) -> str:
    if password is None:
        password = ""
    if salt is None:
        salt = ""
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations)
    return binascii.hexlify(dk).decode()

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin")
_ADMIN_PASSWORD_RAW = os.getenv("ADMIN_PASSWORD", "a")
ADMIN_SALT = os.getenv("ADMIN_SALT", ADMIN_EMAIL)
ADMIN_NAME = os.getenv("ADMIN_NAME", "Admin")


_STORED_PASSWORD_HASH = _hash_password(_ADMIN_PASSWORD_RAW, ADMIN_SALT)

def validate_admin_credentials(email: str, password: str):
    if not email or not password:
        return None
    if email != ADMIN_EMAIL:
        return None
    provided_hash = _hash_password(password, ADMIN_SALT)
    if hmac.compare_digest(provided_hash, _STORED_PASSWORD_HASH):
        return {"email": ADMIN_EMAIL, "name": ADMIN_NAME}
    return None