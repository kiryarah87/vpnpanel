import logging
from pathlib import Path

from docker.errors import DockerException
from sqlalchemy.ext.asyncio import AsyncSession

import docker
from app.config_gen.caddy import CaddyConfigGenerator
from app.config_gen.hysteria2 import Hysteria2ConfigGenerator
from app.config_gen.xray import XrayConfigGenerator

logger = logging.getLogger(__name__)

CONFIGS_DIR = Path("configs")


class ConfigManager:
    """Оркестратор генерации конфигов и перезагрузки сервисов"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.xray = XrayConfigGenerator(CONFIGS_DIR / "xray" / "config.json", session)
        self.hysteria2 = Hysteria2ConfigGenerator(
            CONFIGS_DIR / "hysteria2" / "config.yaml", session
        )
        self.caddy = CaddyConfigGenerator(CONFIGS_DIR / "caddy" / "Caddyfile", session)

    async def regenerate_all(self) -> None:
        """Пересгенерировать все конфиги и перезагрузить сервисы"""
        await self.xray.generate()
        await self.hysteria2.generate()
        await self.caddy.generate()

        await self._reload_container("xray")
        await self._reload_container("hysteria2")
        await self._reload_caddy()

    async def regenerate_xray(self) -> None:
        await self.xray.generate()
        await self._reload_container("xray")

    async def regenerate_hysteria2(self) -> None:
        await self.hysteria2.generate()
        await self._reload_container("hysteria2")

    async def regenerate_caddy(self) -> None:
        await self.caddy.generate()
        await self._reload_caddy()

    async def _reload_container(self, name: str) -> None:
        """Отправить SIGHUP контейнеру"""
        try:
            client = docker.from_env()
            container = client.containers.get(name)
            container.kill(signal="SIGHUP")
            logger.info(f"Sent SIGHUP to container '{name}'")
        except DockerException as e:
            logger.warning(f"Failed to reload container '{name}': {e}")

    async def _reload_caddy(self) -> None:
        """Caddy перезагружается через caddy reload"""
        try:
            client = docker.from_env()
            container = client.containers.get("caddy")
            container.exec_run("caddy reload --config /etc/caddy/Caddyfile")
            logger.info("Caddy reloaded")
        except DockerException as e:
            logger.warning(f"Failed to reload Caddy: {e}")
