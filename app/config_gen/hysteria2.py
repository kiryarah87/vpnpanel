from pathlib import Path

import yaml
from sqlalchemy.ext.asyncio import AsyncSession

from app.config_gen.base import BaseConfigGenerator
from app.core.config import settings
from app.models.enum import ProtocolType
from app.repositories.client import ClientRepository
from app.repositories.inbound import InboundRepository


class Hysteria2ConfigGenerator(BaseConfigGenerator):
    """Генератор конфига Hysteria2"""

    def __init__(self, config_path: Path, session: AsyncSession):
        super().__init__(config_path)
        self.inbound_repo = InboundRepository(session)
        self.client_repo = ClientRepository(session)

    async def generate(self) -> None:
        inbounds = await self.inbound_repo.get_active()
        clients = await self.client_repo.get_all_with_credentials()

        hysteria_inbounds = [
            i for i in inbounds if i.protocol == ProtocolType.HYSTERIA2
        ]

        if not hysteria_inbounds:
            self.write("# No active Hysteria2 inbounds\n")
            return

        inbound = hysteria_inbounds[0]

        auth_users = {
            c.name: c.credential.hysteria2_password
            for c in clients
            if c.credential and c.is_active
        }

        config = {
            "listen": f":{inbound.port}",
            "tls": {
                "cert": f"/caddy-data/caddy/certificates/acme-v02.api.letsencrypt.org-directory/{settings.DOMAIN}/{settings.DOMAIN}.crt",
                "key": f"/caddy-data/caddy/certificates/acme-v02.api.letsencrypt.org-directory/{settings.DOMAIN}/{settings.DOMAIN}.key",
            },
            "auth": {
                "type": "userpass",
                "userpass": auth_users,
            },
            "masquerade": {
                "type": "proxy",
                "proxy": {
                    "url": f"https://{settings.DOMAIN}",
                    "rewriteHost": True,
                },
            },
            "bandwidth": {
                "up": "1 gbps",
                "down": "1 gbps",
            },
        }

        self.write(yaml.dump(config, allow_unicode=True, sort_keys=False))
