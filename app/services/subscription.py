from app.config_gen.links import LinkGenerator
from app.core.config import settings
from app.core.exception import ForbiddenError, NotFoundError, ValidationError
from app.repositories.credential import ClientCredentialRepository
from app.repositories.inbound import InboundRepository
from app.repositories.subscription import SubscriptionRepository
from app.schemas.subscription import (
    SubscriptionCreate,
    SubscriptionReadDetail,
    SubscriptionUpdate,
)


class SubscriptionService:
    def __init__(
        self,
        repo: SubscriptionRepository,
        inbound_repo: InboundRepository,
        credential_repo: ClientCredentialRepository,
    ):
        self.repo = repo
        self.inbound_repo = inbound_repo
        self.credential_repo = credential_repo

    def _validate_inbounds_limit(self, inbound_ids: list[int]) -> None:
        """Проверить, что количество инбаундов не превышает лимит"""
        if len(inbound_ids) > settings.MAX_INBOUNDS_PER_SUBSCRIPTION:
            raise ValidationError(
                f"Максимум {settings.MAX_INBOUNDS_PER_SUBSCRIPTION} инбаундов"
            )

    async def _ensure_inbound_exists(self, inbound_id: int) -> None:
        """Проверить, что инбаунд с данным id существует"""
        inbound = await self.inbound_repo.get(inbound_id)
        if not inbound:
            raise NotFoundError(f"Инбаунд {inbound_id} не найден")

    async def get_all(self) -> list[SubscriptionReadDetail]:
        """Получить все подписки"""
        subs = await self.repo.get_all_with_inbounds()
        return [SubscriptionReadDetail.model_validate(s) for s in subs]

    async def get_by_id(self, id: int) -> SubscriptionReadDetail:
        """Получить подписку по id"""
        sub = await self.repo.get_with_inbounds(id)

        if not sub:
            raise NotFoundError("Подписка не найдена")

        return SubscriptionReadDetail.model_validate(sub)

    async def get_by_token(self, token: str) -> SubscriptionReadDetail:
        """Получить подписку по токену"""
        sub = await self.repo.get_by_token(token)

        if not sub:
            raise NotFoundError("Подписка не найдена")

        if not sub.is_active:
            raise ForbiddenError("Подписка деактивирована")
        return SubscriptionReadDetail.model_validate(sub)

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

    async def update(self, id: int, data: SubscriptionUpdate) -> SubscriptionReadDetail:
        """Обновить существующую подписку"""
        subscription = await self.repo.get_with_inbounds(id)

        if not subscription:
            raise NotFoundError("Подписка не найдена")

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

    async def delete(self, id: int) -> None:
        """Удалить подписку"""
        subscription = await self.repo.get(id)

        if not subscription:
            raise NotFoundError("Подписка не найдена")

        await self.repo.delete(subscription)

    def get_subscription_url(self, token: str) -> str:
        """Получить URL для подписки по токену"""
        return f"{settings.SUBSCRIPTION_BASE_URL}/sub/{token}"

    async def get_links(self, token: str, host: str) -> str:
        sub = await self.repo.get_by_token(token)

        if not sub:
            raise NotFoundError("Подписка не найдена")

        if not sub.is_active:
            raise ForbiddenError("Подписка деактивирована")

        credential = await self.credential_repo.get_by_client(sub.client_id)

        if not credential:
            raise NotFoundError("Credentials не найдены")

        inbounds = [si.inbound for si in sub.subscription_inbounds]
        generator = LinkGenerator()
        return generator.generate(inbounds, credential, host)
