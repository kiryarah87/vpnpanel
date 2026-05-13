from app.core.exception import NotFoundError
from app.repositories.inbound import InboundRepository
from app.schemas.inbound import InboundCreate, InboundRead, InboundUpdate


class InboundService:
    """Сервис для управления инбаундами"""

    def __init__(self, repo: InboundRepository):
        self.repo = repo

    async def get_all(self) -> list[InboundRead]:
        """Получить все инбаунды"""
        inbounds = await self.repo.get_all()
        return [InboundRead.model_validate(i) for i in inbounds]

    async def get_by_id(self, id: int) -> InboundRead:
        """Получить инбаунд по id"""
        inbound = await self.repo.get(id)

        if not inbound:
            raise NotFoundError("Инбаунд не найден")

        return InboundRead.model_validate(inbound)

    async def create(self, data: InboundCreate) -> InboundRead:
        """Создать новый инбаунд"""
        inbound = await self.repo.create_from_dict(data.model_dump())
        return InboundRead.model_validate(inbound)

    async def update(self, id: int, data: InboundUpdate) -> InboundRead:
        """Обновить инбаунд"""
        inbound = await self.repo.get(id)

        if not inbound:
            raise NotFoundError("Инбаунд не найден")

        inbound = await self.repo.update_from_dict(
            inbound, data.model_dump(exclude_unset=True)
        )
        return InboundRead.model_validate(inbound)

    async def delete(self, id: int) -> None:
        """Удалить инбаунд"""
        inbound = await self.repo.get(id)

        if not inbound:
            raise NotFoundError("Инбаунд не найден")

        await self.repo.delete(inbound)
