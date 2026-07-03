import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

# AES-256 requires exactly 32 bytes. Key stored as 64-char hex string.
_AES_KEY_HEX = os.getenv("AES_KEY", "0" * 64)
try:
    AES_KEY = bytes.fromhex(_AES_KEY_HEX)
    assert len(AES_KEY) == 32
except (ValueError, AssertionError):
    AES_KEY = _AES_KEY_HEX.encode()[:32].ljust(32, b"\x00")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def encrypt_field(plaintext: str) -> str:
    """Encrypt a string using AES-256-GCM. Returns base64(nonce + ciphertext)."""
    aesgcm = AESGCM(AES_KEY)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    return base64.b64encode(nonce + ct).decode("utf-8")


def decrypt_field(encrypted: str) -> str:
    """Decrypt a field encrypted by encrypt_field(). Plaintext legacy values pass through."""
    if "@" in encrypted:
        return encrypted
    try:
        data = base64.b64decode(encrypted.encode("utf-8"), validate=True)
        if len(data) < 13:
            raise ValueError("ciphertext too short")
        nonce, ct = data[:12], data[12:]
        aesgcm = AESGCM(AES_KEY)
        return aesgcm.decrypt(nonce, ct, None).decode("utf-8")
    except Exception as exc:
        raise ValueError("Failed to decrypt field") from exc


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload.update({"exp": expire})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
