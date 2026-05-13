from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.config_gen.base import BaseConfigGenerator
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

        if not naive_inbounds:
            self.write("# No active NaiveProxy inbounds\n")
            return

        active_clients = [c for c in clients if c.credential and c.is_active]

        lines = []

        for inbound in naive_inbounds:
            domain = inbound.domain.name if inbound.domain else "localhost"

            # Формируем список пользователей
            users = " ".join(
                f"{c.credential.naiveproxy_username}:{c.credential.naiveproxy_password}"
                for c in active_clients
            )

            lines.append(f":{inbound.port}, {domain}:{inbound.port} {{")
            lines.append("  tls /etc/caddy/server.crt /etc/caddy/server.key")
            lines.append("  route {")
            lines.append("    forward_proxy {")
            lines.append(f"      basic_auth {users}")
            lines.append("      hide_ip")
            lines.append("      hide_via")
            lines.append("    }")
            lines.append("  }")
            lines.append("}")
            lines.append("")

        self.write("\n".join(lines))
