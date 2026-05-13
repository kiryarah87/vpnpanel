from app.core.exception import NotFoundError
from app.repositories.client import ClientRepository
from app.schemas.client import ClientCreate, ClientRead, ClientUpdate


class ClientService:
    """Сервис для управления клиентами"""

    def __init__(self, repo: ClientRepository):
        self.repo = repo

    async def get_all(self) -> list[ClientRead]:
        """Получает всех клиентов"""
        clients = await self.repo.get_all()
        return [ClientRead.model_validate(c) for c in clients]

    async def get_by_id(self, id: int) -> ClientRead:
        """Получает клиента по ID"""
        client = await self.repo.get(id)

        if not client:
            raise NotFoundError("Клиент не найден")

        return ClientRead.model_validate(client)

    async def create(self, data: ClientCreate) -> ClientRead:
        """Создает нового клиента"""
        client = await self.repo.create_from_dict(data.model_dump())
        return ClientRead.model_validate(client)

    async def update(self, id: int, data: ClientUpdate) -> ClientRead:
        """Обновляет клиента по ID"""
        client = await self.repo.get(id)

        if not client:
            raise NotFoundError("Клиент не найден")

        client = await self.repo.update_from_dict(
            client, data.model_dump(exclude_unset=True)
        )
        return ClientRead.model_validate(client)

    async def delete(self, id: int) -> None:
        """Удаляет клиента по ID"""
        client = await self.repo.get(id)

        if not client:
            raise NotFoundError("Клиент не найден")

        await self.repo.delete(client)
