from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.client import Client
from app.repositories.base import BaseRepository


class ClientRepository(BaseRepository[Client]):
    """Репозиторий для работы с клиентами"""

    def __init__(self, session: AsyncSession):
        super().__init__(Client, session)

    async def get_by_email(self, email: str) -> Client | None:
        result = await self.session.execute(select(Client).where(Client.email == email))
        return result.scalar_one_or_none()

    async def get_active(self) -> list[Client]:
        result = await self.session.execute(select(Client).where(Client.is_active))
        return result.scalars().all()

    async def create_from_dict(self, data: dict) -> Client:
        client = Client(**data)
        return await self.create(client)

    async def update_from_dict(self, client: Client, data: dict) -> Client:
        for key, value in data.items():
            setattr(client, key, value)
        await self.session.flush()
        await self.session.refresh(client)
        return client

    async def get_with_credential(self, id: int) -> Client | None:
        result = await self.session.execute(
            select(Client)
            .where(Client.id == id)
            .options(selectinload(Client.credential))
        )
        return result.scalar_one_or_none()

    async def get_all_with_credentials(self) -> list[Client]:
        result = await self.session.execute(
            select(Client).options(selectinload(Client.credential))
        )
        return list(result.scalars().all())
