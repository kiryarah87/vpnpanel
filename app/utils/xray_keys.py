import base64
import secrets

from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey


def generate_reality_keys() -> tuple[str, str]:
    """Генерирует пару ключей X25519 для Reality"""
    private_key = X25519PrivateKey.generate()
    public_key = private_key.public_key()

    private_bytes = private_key.private_bytes_raw()
    public_bytes = public_key.public_bytes_raw()

    private_b64 = base64.urlsafe_b64encode(private_bytes).decode().rstrip("=")
    public_b64 = base64.urlsafe_b64encode(public_bytes).decode().rstrip("=")

    return private_b64, public_b64


def generate_short_id() -> str:
    """Генерирует случайный short_id для Reality"""
    return secrets.token_hex(8)
