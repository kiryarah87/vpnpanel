import secrets

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.subscription import Subscription
from app.models.subscription_inbound import SubscriptionInbound
from app.repositories.base import BaseRepository


class SubscriptionRepository(BaseRepository[Subscription]):
    """Репозиторий для управления подписками"""

    def __init__(self, session: AsyncSession):
        super().__init__(Subscription, session)

    async def get_by_token(self, token: str) -> Subscription | None:
        """Получить подписку по токену"""
        result = await self.session.execute(
            select(Subscription).where(Subscription.token == token)
        )
        return result.scalar_one_or_none()

    async def get_by_client(self, client_id: int) -> list[Subscription]:
        """Получить подписки по id клиента"""
        result = await self.session.execute(
            select(Subscription).where(Subscription.client_id == client_id)
        )
        return result.scalars().all()

    async def get_with_inbounds(self, id: int) -> Subscription | None:
        """Получить подписку с инбаундами по id"""
        result = await self.session.execute(
            select(Subscription)
            .where(Subscription.id == id)
            .options(
                selectinload(Subscription.subscription_inbounds).selectinload(
                    SubscriptionInbound.inbound
                )
            )
        )
        return result.scalar_one_or_none()

    async def create_from_dict(self, data: dict) -> Subscription:
        """Создать подписку из словаря"""
        subscription = Subscription(
            **data,
            token=secrets.token_urlsafe(32),
        )
        return await self.create(subscription)

    async def update_from_dict(
        self, subscription: Subscription, data: dict
    ) -> Subscription:
        """Обновить подписку из словаря"""
        for key, value in data.items():
            setattr(subscription, key, value)

        await self.session.flush()
        await self.session.refresh(subscription)
        return subscription

    async def add_inbound(self, subscription_id: int, inbound_id: int) -> None:
        """Добавить инбаунд к подписке"""
        link = SubscriptionInbound(
            subscription_id=subscription_id,
            inbound_id=inbound_id,
        )
        self.session.add(link)
        await self.session.flush()

    async def remove_all_inbounds(self, subscription: Subscription) -> None:
        """Удалить все инбаунды из подписки"""
        for si in subscription.subscription_inbounds:
            await self.session.delete(si)
        await self.session.flush()

    async def remove_inbound(self, subscription_id: int, inbound_id: int) -> None:
        """Удалить конкретный инбаунд из подписки"""
        result = await self.session.execute(
            select(SubscriptionInbound).where(
                SubscriptionInbound.subscription_id == subscription_id,
                SubscriptionInbound.inbound_id == inbound_id,
            )
        )
        link = result.scalar_one_or_none()
        if link:
            await self.session.delete(link)
            await self.session.flush()
