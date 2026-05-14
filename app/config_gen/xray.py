import json
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.config_gen.base import BaseConfigGenerator
from app.models.enum import ProtocolType
from app.repositories.client import ClientRepository
from app.repositories.inbound import InboundRepository


class XrayConfigGenerator(BaseConfigGenerator):
    """Генератор конфига Xray для VLESS протоколов"""

    def __init__(self, config_path: Path, session: AsyncSession):
        super().__init__(config_path)
        self.inbound_repo = InboundRepository(session)
        self.client_repo = ClientRepository(session)

    async def generate(self) -> None:
        inbounds = await self.inbound_repo.get_active()
        clients = await self.client_repo.get_all_with_credentials()

        xray_inbounds = []

        for inbound in inbounds:
            if inbound.protocol == ProtocolType.VLESS_TCP_REALITY:
                xray_inbounds.append(self._build_vless_tcp_reality(inbound, clients))
            elif inbound.protocol == ProtocolType.VLESS_XHTTP_REALITY:
                xray_inbounds.append(self._build_vless_xhttp_reality(inbound, clients))

        config = {
            "log": {"loglevel": "warning"},
            "inbounds": xray_inbounds,
            "outbounds": [
                {"protocol": "freedom", "tag": "direct"},
                {"protocol": "blackhole", "tag": "block"},
            ],
            "routing": {
                "rules": [
                    {"type": "field", "ip": ["geoip:private"], "outboundTag": "block"}
                ]
            },
        }

        self.write(json.dumps(config, indent=2, ensure_ascii=False))

    def _build_clients(self, clients: list) -> list[dict]:
        return [
            {
                "id": c.credential.xray_uuid,
                "flow": "xtls-rprx-vision",
            }
            for c in clients
            if c.credential and c.is_active
        ]

    def _build_vless_tcp_reality(self, inbound, clients: list) -> dict:
        return {
            "tag": f"vless-tcp-reality-{inbound.id}",
            "listen": "0.0.0.0",
            "port": inbound.port,
            "protocol": "vless",
            "settings": {
                "clients": self._build_clients(clients),
                "decryption": "none",
            },
            "streamSettings": {
                "network": "tcp",
                "security": "reality",
                "realitySettings": {
                    "show": False,
                    "dest": f"{inbound.sni}:443",
                    "xver": 0,
                    "serverNames": [inbound.sni],
                    "privateKey": "",  # TODO: генерировать при создании инбаунда
                    "shortIds": [""],
                },
            },
        }

    def _build_vless_xhttp_reality(self, inbound, clients: list) -> dict:
        return {
            "tag": f"vless-xhttp-reality-{inbound.id}",
            "listen": "0.0.0.0",
            "port": inbound.port,
            "protocol": "vless",
            "settings": {
                "clients": self._build_clients(clients),
                "decryption": "none",
            },
            "streamSettings": {
                "network": "xhttp",
                "security": "reality",
                "realitySettings": {
                    "show": False,
                    "dest": f"{inbound.sni}:443",
                    "xver": 0,
                    "serverNames": [inbound.sni],
                    "privateKey": "",  # TODO: генерировать при создании инбаунда
                    "shortIds": [""],
                },
                "xhttpSettings": {
                    "path": "/",
                    "mode": "auto",
                },
            },
        }
