from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.client import Client
from app.repositories.base import BaseRepository


class ClientRepository(BaseRepository[Client]):
    """Репозиторий для работы с клиентами"""

    def __init__(self, session: AsyncSession):
        super().__init__(Client, session)

    async def get_by_email(self, email: str) -> Client | None:
        """Получить клиента по email"""
        result = await self.session.execute(select(Client).where(Client.email == email))
        return result.scalar_one_or_none()

    async def get_active(self) -> list[Client]:
        """Получить всех активных клиентов"""
        result = await self.session.execute(select(Client).where(Client.is_active))
        return result.scalars().all()

    async def create_from_dict(self, data: dict) -> Client:
        """Создать клиента из схемы"""
        client = Client(**data)
        return await self.create(client)

    async def update_from_dict(self, client: Client, data: dict) -> Client:
        """Обновить клиента из словаря"""
        for key, value in data.items():
            setattr(client, key, value)

        await self.session.flush()
        await self.session.refresh(client)
        return client
