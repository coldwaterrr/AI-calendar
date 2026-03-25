import base64
from pathlib import Path

from cryptography.fernet import Fernet


SECRETS_DIR = Path(__file__).resolve().parent.parent / '.secrets'
KEY_FILE = SECRETS_DIR / 'fernet.key'


def _normalize_key(raw: bytes) -> bytes:
    if len(raw) == 44:
        return raw
    return base64.urlsafe_b64encode(raw[:32].ljust(32, b'0'))


def get_fernet() -> Fernet:
    SECRETS_DIR.mkdir(parents=True, exist_ok=True)
    if not KEY_FILE.exists():
        KEY_FILE.write_bytes(Fernet.generate_key())
    return Fernet(_normalize_key(KEY_FILE.read_bytes().strip()))


def encrypt_value(value: str) -> str:
    return get_fernet().encrypt(value.encode('utf-8')).decode('utf-8')


def decrypt_value(value: str) -> str:
    return get_fernet().decrypt(value.encode('utf-8')).decode('utf-8')


def mask_secret(value: str) -> str:
    if len(value) <= 4:
        return '*' * len(value)
    return f"{'*' * max(len(value) - 4, 4)}{value[-4:]}"
