from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.user import User
from app.repositories.user import UserRepository


async def create_admin_if_not_exists(session: AsyncSession) -> None:
    """Создать администратора при первом запуске"""
    from app.core.config import settings

    repo = UserRepository(session)
    existing = await repo.get_by_username(settings.ADMIN_USERNAME)

    if not existing:
        admin = User(
            username=settings.ADMIN_USERNAME,
            hashed_password=hash_password(settings.ADMIN_PASSWORD),
            is_active=True,
            is_superuser=True,
        )
        session.add(admin)
        await session.flush()
