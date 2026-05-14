from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import hash_password
from app.models.user import User
from app.repositories.user import UserRepository

CONFIGS_DIR = Path("app/config_gen/configs")

DEFAULT_XRAY_CONFIG = """{
  "log": {"loglevel": "warning"},
  "inbounds": [],
  "outbounds": [
    {"protocol": "freedom", "tag": "direct"},
    {"protocol": "blackhole", "tag": "block"}
  ]
}
"""

DEFAULT_HYSTERIA2_CONFIG = "# No active Hysteria2 inbounds\n"

DEFAULT_CADDYFILE = "# No active NaiveProxy inbounds\n"


def create_default_configs() -> None:
    """Создать дефолтные конфиги если не существуют"""
    xray_config = CONFIGS_DIR / "xray" / "config.json"
    hysteria2_config = CONFIGS_DIR / "hysteria2" / "config.yaml"
    caddy_config = CONFIGS_DIR / "caddy" / "Caddyfile"

    xray_config.parent.mkdir(parents=True, exist_ok=True)
    hysteria2_config.parent.mkdir(parents=True, exist_ok=True)
    caddy_config.parent.mkdir(parents=True, exist_ok=True)

    if not xray_config.exists():
        xray_config.write_text(DEFAULT_XRAY_CONFIG, encoding="utf-8")

    if not hysteria2_config.exists():
        hysteria2_config.write_text(DEFAULT_HYSTERIA2_CONFIG, encoding="utf-8")

    if not caddy_config.exists():
        caddy_config.write_text(DEFAULT_CADDYFILE, encoding="utf-8")


async def create_admin_if_not_exists(session: AsyncSession) -> None:
    """Создать администратора при первом запуске"""
    repo = UserRepository(session)
    existing = await repo.get_by_username(settings.ADMIN_USERNAME)

    if not existing:
        admin = User(
            username=settings.ADMIN_USERNAME,
            hashed_password=hash_password(settings.ADMIN_PASSWORD),
            is_active=True,
            is_superuser=True,
        )
        session.add(admin)
        await session.flush()
