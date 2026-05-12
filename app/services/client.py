from app.repositories.client import ClientRepository
from app.schemas.client import ClientCreate, ClientRead, ClientUpdate


class ClientService:
    """Сервис для управления клиентами"""

    def __init__(self, repo: ClientRepository):
        self.repo = repo

    async def get_all(self) -> list[ClientRead]:
        """Получить всех клиентов"""
        clients = await self.repo.get_all()
        return [ClientRead.model_validate(c) for c in clients]

    async def get_by_id(self, id: int) -> ClientRead | None:
        """Получить клиента по id"""
        client = await self.repo.get(id)
        return ClientRead.model_validate(client) if client else None

    async def create(self, data: ClientCreate) -> ClientRead:
        """Создать нового клиента"""
        client = await self.repo.create_from_dict(data.model_dump())
        return ClientRead.model_validate(client)

    async def update(self, id: int, data: ClientUpdate) -> ClientRead | None:
        """Обновить клиента"""
        client = await self.repo.get(id)

        if not client:
            return

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(client, key, value)

        await self.repo.session.flush()
        await self.repo.session.refresh(client)
        return ClientRead.model_validate(client)

    async def delete(self, id: int) -> bool:
        """Удалить клиента"""
        client = await self.repo.get(id)

        if not client:
            return False

        await self.repo.delete(client)
        return True
