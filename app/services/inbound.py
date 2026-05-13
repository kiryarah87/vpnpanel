import random

from app.core.exception import NotFoundError
from app.models.enum import PortType
from app.repositories.inbound import InboundRepository
from app.schemas.inbound import InboundCreate, InboundRead, InboundUpdate

PORT_RANGE = (10000, 60000)


class InboundService:
    """Сервис для управления инбаундами"""

    def __init__(self, repo: InboundRepository):
        self.repo = repo

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

        inbound = await self.repo.create_from_dict(payload)
        return InboundRead.model_validate(inbound)

    async def update(self, id: int, data: InboundUpdate) -> InboundRead:
        inbound = await self.repo.get(id)

        if not inbound:
            raise NotFoundError("Инбаунд не найден")

        inbound = await self.repo.update_from_dict(
            inbound, data.model_dump(exclude_unset=True)
        )
        return InboundRead.model_validate(inbound)

    async def delete(self, id: int) -> None:
        inbound = await self.repo.get(id)

        if not inbound:
            raise NotFoundError("Инбаунд не найден")
        await self.repo.delete(inbound)
