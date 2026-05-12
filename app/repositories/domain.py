from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.domain import Domain
from app.repositories.base import BaseRepository


class DomainRepository(BaseRepository[Domain]):
    """Репозиторий для работы с доменами"""

    def __init__(self, session: AsyncSession):
        super().__init__(Domain, session)

    async def get_by_name(self, name: str) -> Domain | None:
        """Получить домен по имени"""
        result = await self.session.execute(select(Domain).where(Domain.name == name))
        return result.scalar_one_or_none()

    async def get_active(self) -> list[Domain]:
        """Получить все активные домены"""
        result = await self.session.execute(select(Domain).where(Domain.is_active))
        return result.scalars().all()

    async def get_with_inbounds(self, id: int) -> Domain | None:
        """Получить домен с инбаундами по id"""
        result = await self.session.execute(
            select(Domain).where(Domain.id == id).options(selectinload(Domain.inbounds))
        )
        return result.scalar_one_or_none()

    async def create_from_dict(self, data: dict) -> Domain:
        """Создать домен из схемы"""
        domain = Domain(**data)
        return await self.create(domain)

    async def update_from_dict(self, domain: Domain, data: dict) -> Domain:
        """Обновить домен из словаря"""
        for key, value in data.items():
            setattr(domain, key, value)

        await self.session.flush()
        await self.session.refresh(domain)
        return domain
