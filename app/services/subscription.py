from fastapi import HTTPException

from app.core.config import settings
from app.repositories.inbound import InboundRepository
from app.repositories.subscription import SubscriptionRepository
from app.schemas.subscription import (
    SubscriptionCreate,
    SubscriptionRead,
    SubscriptionReadDetail,
    SubscriptionUpdate,
)


class SubscriptionService:
    """Сервис для управления подписками"""

    def __init__(self, repo: SubscriptionRepository, inbound_repo: InboundRepository):
        self.repo = repo
        self.inbound_repo = inbound_repo

    async def get_all(self) -> list[SubscriptionRead]:
        """Получить все подписки"""
        subs = await self.repo.get_all()
        return [SubscriptionRead.model_validate(s) for s in subs]

    async def get_by_id(self, id: int) -> SubscriptionReadDetail | None:
        """Получить подписку по id"""
        sub = await self.repo.get_with_inbounds(id)
        return SubscriptionReadDetail.model_validate(sub) if sub else None

    async def get_by_token(self, token: str) -> SubscriptionReadDetail | None:
        """Получить подписку по токену"""
        sub = await self.repo.get_by_token(token)
        return SubscriptionReadDetail.model_validate(sub) if sub else None

    async def create(self, data: SubscriptionCreate) -> SubscriptionReadDetail:
        """Создать новую подписку"""
        self._validate_inbounds_limit(data.inbound_ids)

        subscription = await self.repo.create_from_dict(
            data.model_dump(exclude={"inbound_ids"})
        )

        for inbound_id in data.inbound_ids:
            await self._ensure_inbound_exists(inbound_id)
            await self.repo.add_inbound(subscription.id, inbound_id)

        sub = await self.repo.get_with_inbounds(subscription.id)
        return SubscriptionReadDetail.model_validate(sub)

    async def update(
        self, id: int, data: SubscriptionUpdate
    ) -> SubscriptionReadDetail | None:
        """Обновить подписку"""
        subscription = await self.repo.get_with_inbounds(id)

        if not subscription:
            return None

        await self.repo.update_from_dict(
            subscription, data.model_dump(exclude_unset=True, exclude={"inbound_ids"})
        )

        if data.inbound_ids is not None:
            self._validate_inbounds_limit(data.inbound_ids)
            await self.repo.remove_all_inbounds(subscription)

            for inbound_id in data.inbound_ids:
                await self._ensure_inbound_exists(inbound_id)
                await self.repo.add_inbound(subscription.id, inbound_id)

        sub = await self.repo.get_with_inbounds(id)
        return SubscriptionReadDetail.model_validate(sub)

    async def delete(self, id: int) -> bool:
        """Удалить подписку"""
        subscription = await self.repo.get(id)

        if not subscription:
            return False

        await self.repo.delete(subscription)
        return True

    def get_subscription_url(self, token: str) -> str:
        """Получить URL для подписки по токену"""
        return f"{settings.SUBSCRIPTION_BASE_URL}/sub/{token}"

    def _validate_inbounds_limit(self, inbound_ids: list[int]) -> None:
        '''Проверить, что количество инбаундов не превышает лимит'''
        if len(inbound_ids) > settings.MAX_INBOUNDS_PER_SUBSCRIPTION:
            raise HTTPException(
                status_code=400,
                detail=f"Максимум {settings.MAX_INBOUNDS_PER_SUBSCRIPTION} инбаундов",
            )

    async def _ensure_inbound_exists(self, inbound_id: int) -> None:
        '''Проверить, что инбаунд существует'''
        inbound = await self.inbound_repo.get(inbound_id)
        if not inbound:
            raise HTTPException(
                status_code=404, detail=f"Инбаунд {inbound_id} не найден"
            )
