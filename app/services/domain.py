from fastapi import HTTPException

from app.repositories.domain import DomainRepository
from app.schemas.domain import DomainCreate, DomainRead, DomainUpdate


class DomainService:
    """Сервис для управления доменами"""

    def __init__(self, repo: DomainRepository):
        self.repo = repo

    async def get_all(self) -> list[DomainRead]:
        """Получить все домены"""
        domains = await self.repo.get_all()
        return [DomainRead.model_validate(d) for d in domains]

    async def get_by_id(self, id: int) -> DomainRead | None:
        """Получить домен по id"""
        domain = await self.repo.get(id)
        return DomainRead.model_validate(domain) if domain else None

    async def create(self, data: DomainCreate) -> DomainRead:
        """Создать новый домен"""
        existing = await self.repo.get_by_name(data.name)

        if existing:
            raise HTTPException(status_code=400, detail="Домен уже существует")

        domain = await self.repo.create_from_dict(data.model_dump())
        return DomainRead.model_validate(domain)

    async def update(self, id: int, data: DomainUpdate) -> DomainRead | None:
        """Обновить домен"""
        domain = await self.repo.get(id)

        if not domain:
            return None

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(domain, key, value)

        await self.repo.session.flush()
        await self.repo.session.refresh(domain)
        return DomainRead.model_validate(domain)

    async def delete(self, id: int) -> bool:
        """Удалить домен"""
        domain = await self.repo.get(id)

        if not domain:
            return False

        await self.repo.delete(domain)
        return True
