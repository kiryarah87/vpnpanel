import random

from app.config_gen.manager import ConfigManager
from app.core.exception import NotFoundError
from app.models.enum import PortType, ProtocolType
from app.repositories.inbound import InboundRepository
from app.schemas.inbound import InboundCreate, InboundRead, InboundUpdate
from app.utils.xray_keys import generate_reality_keys, generate_short_id

PORT_RANGE = (10000, 60000)
REALITY_PROTOCOLS = {ProtocolType.VLESS_TCP_REALITY, ProtocolType.VLESS_XHTTP_REALITY}


class InboundService:
    def __init__(self, repo: InboundRepository, config_manager: ConfigManager):
        self.repo = repo
        self.config_manager = config_manager

    async def get_all(self) -> list[InboundRead]:
        inbounds = await self.repo.get_all()
        return [InboundRead.model_validate(i) for i in inbounds]

    async def get_by_id(self, id: int) -> InboundRead:
        inbound = await self.repo.get(id)

        if not inbound:
            raise NotFoundError("Инбаунд не найден")
        return InboundRead.model_validate(inbound)

    async def create(self, data: InboundCreate) -> InboundRead:
        payload = data.model_dump()

        if data.port_type == PortType.RANDOM or data.port is None:
            payload["port"] = random.randint(*PORT_RANGE)
            payload["port_type"] = PortType.RANDOM

        if data.protocol in REALITY_PROTOCOLS:
            private_key, public_key = generate_reality_keys()
            payload["reality_private_key"] = private_key
            payload["reality_public_key"] = public_key
            payload["reality_short_id"] = generate_short_id()

        inbound = await self.repo.create_from_dict(payload)
        await self.config_manager.regenerate_xray()
        return InboundRead.model_validate(inbound)

    async def update(self, id: int, data: InboundUpdate) -> InboundRead:
        inbound = await self.repo.get(id)

        if not inbound:
            raise NotFoundError("Инбаунд не найден")

        inbound = await self.repo.update_from_dict(
            inbound, data.model_dump(exclude_unset=True)
        )

        await self.config_manager.regenerate_xray()
        return InboundRead.model_validate(inbound)

    async def delete(self, id: int) -> None:
        inbound = await self.repo.get(id)

        if not inbound:
            raise NotFoundError("Инбаунд не найден")

        await self.repo.delete(inbound)
        await self.config_manager.regenerate_xray()
