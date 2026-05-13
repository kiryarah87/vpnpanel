import secrets
import subprocess


def generate_reality_keys() -> tuple[str, str]:
    """
    Генерировать пару ключей для Reality через xray x25519.
    Возвращает (private_key, public_key).
    """
    try:
        result = subprocess.run(
            ["xray", "x25519"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        lines = result.stdout.strip().splitlines()
        private_key = lines[0].split(": ")[1].strip()
        public_key = lines[1].split(": ")[1].strip()
        return private_key, public_key
    except Exception:
        return "PLACEHOLDER_PRIVATE_KEY", "PLACEHOLDER_PUBLIC_KEY"


def generate_short_id() -> str:
    """Генерировать shortId для Reality (8 байт hex)"""
    return secrets.token_hex(8)
