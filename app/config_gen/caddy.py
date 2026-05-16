from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.config_gen.base import BaseConfigGenerator
from app.core.config import settings
from app.models.enum import ProtocolType
from app.repositories.client import ClientRepository
from app.repositories.inbound import InboundRepository


class CaddyConfigGenerator(BaseConfigGenerator):
    """Генератор Caddyfile для NaiveProxy"""

    def __init__(self, config_path: Path, session: AsyncSession):
        super().__init__(config_path)
        self.inbound_repo = InboundRepository(session)
        self.client_repo = ClientRepository(session)

    async def generate(self) -> None:
        inbounds = await self.inbound_repo.get_active()
        clients = await self.client_repo.get_all_with_credentials()

        naive_inbounds = [i for i in inbounds if i.protocol == ProtocolType.NAIVEPROXY]
        active_clients = [c for c in clients if c.credential and c.is_active]

        is_local = settings.DOMAIN in ("localhost", "127.0.0.1")
        lines = []

        if is_local:
            # Локально — всё на HTTP
            lines.append(":80 {")
            lines.append("    root * /srv/frontend")
            lines.append("")
            lines.append("    handle /api/* {")
            lines.append("        reverse_proxy localhost:8000")
            lines.append("    }")
            lines.append("")
            lines.append("    handle /sub/* {")
            lines.append("        reverse_proxy localhost:8000")
            lines.append("    }")
            lines.append("")
            lines.append("    handle {")
            lines.append("        try_files {path} /index.html")
            lines.append("        file_server")
            lines.append("    }")
            lines.append("}")
        else:
            # На VPS:
            # 1. Публичный домен — заглушка + подписки
            lines.append(f"{settings.DOMAIN} {{")
            lines.append("    handle /sub/* {")
            lines.append("        reverse_proxy localhost:8000")
            lines.append("    }")
            lines.append("")
            lines.append("    handle {")
            lines.append("        root * /srv/decoy")
            lines.append("        file_server")
            lines.append("    }")
            lines.append("}")
            lines.append("")

            # 2. Панель — только localhost (SSH tunnel)
            lines.append(f"http://localhost:{settings.PORT} {{")
            lines.append("    root * /srv/frontend")
            lines.append("")
            lines.append("    handle /api/* {")
            lines.append("        reverse_proxy localhost:8000")
            lines.append("    }")
            lines.append("")
            lines.append("    handle /sub/* {")
            lines.append("        reverse_proxy localhost:8000")
            lines.append("    }")
            lines.append("")
            lines.append("    handle {")
            lines.append("        try_files {path} /index.html")
            lines.append("        file_server")
            lines.append("    }")
            lines.append("}")
            lines.append("")

            # 3. NaiveProxy инбаунды
            for inbound in naive_inbounds:
                users = " ".join(
                    f"{c.credential.naiveproxy_username}:{c.credential.naiveproxy_password}"
                    for c in active_clients
                )
                lines.append(f"{settings.DOMAIN}:{inbound.port} {{")
                lines.append("    route {")
                lines.append("        forward_proxy {")
                if users:
                    lines.append(f"            basic_auth {users}")
                lines.append("            hide_ip")
                lines.append("            hide_via")
                lines.append("        }")
                lines.append("    }")
                lines.append("}")
                lines.append("")

        self.write("\n".join(lines))
