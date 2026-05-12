from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inbound import Inbound, ProtocolType
from app.repositories.base import BaseRepository


class InboundRepository(BaseRepository[Inbound]):
    def __init__(self, session: AsyncSession):
        super().__init__(Inbound, session)

    async def get_by_protocol(self, protocol: ProtocolType) -> list[Inbound]:
        result = await self.session.execute(
            select(Inbound).where(Inbound.protocol == protocol)
        )
        return result.scalars().all()

    async def get_by_domain(self, domain_id: int) -> list[Inbound]:
        result = await self.session.execute(
            select(Inbound).where(Inbound.domain_id == domain_id)
        )
        return result.scalars().all()

    async def get_active(self) -> list[Inbound]:
        result = await self.session.execute(select(Inbound).where(Inbound.is_active))
        return result.scalars().all()
