from app.core.exception import AlreadyExistsError, NotFoundError
from app.repositories.domain import DomainRepository
from app.schemas.domain import DomainCreate, DomainRead, DomainUpdate


class DomainService:
    """Сервис для управления доменами"""

    def __init__(self, repo: DomainRepository):
        self.repo = repo

    async def get_all(self) -> list[DomainRead]:
        """Получает все домены"""
        domains = await self.repo.get_all()
        return [DomainRead.model_validate(d) for d in domains]

    async def get_by_id(self, id: int) -> DomainRead:
        """Получает домен по ID"""
        domain = await self.repo.get(id)

        if not domain:
            raise NotFoundError("Домен не найден")

        return DomainRead.model_validate(domain)

    async def create(self, data: DomainCreate) -> DomainRead:
        """Создает новый домен"""
        existing = await self.repo.get_by_name(data.name)

        if existing:
            raise AlreadyExistsError("Домен уже существует")

        domain = await self.repo.create_from_dict(data.model_dump())
        return DomainRead.model_validate(domain)

    async def update(self, id: int, data: DomainUpdate) -> DomainRead:
        """Обновляет домен по ID"""
        domain = await self.repo.get(id)

        if not domain:
            raise NotFoundError("Домен не найден")

        domain = await self.repo.update_from_dict(
            domain, data.model_dump(exclude_unset=True)
        )
        return DomainRead.model_validate(domain)

    async def delete(self, id: int) -> None:
        """Удаляет домен по ID"""
        domain = await self.repo.get(id)

        if not domain:
            raise NotFoundError("Домен не найден")

        await self.repo.delete(domain)
