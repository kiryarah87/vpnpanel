from app.config_gen.manager import ConfigManager
from app.core.exception import NotFoundError
from app.repositories.client import ClientRepository
from app.repositories.credential import ClientCredentialRepository
from app.repositories.subscription import SubscriptionRepository
from app.schemas.client import ClientCreate, ClientReadDetail, ClientUpdate
from app.schemas.credential import ClientCredentialRead


class ClientService:
    def __init__(
        self,
        repo: ClientRepository,
        credential_repo: ClientCredentialRepository,
        subscription_repo: SubscriptionRepository,
        config_manager: ConfigManager,
    ):
        self.repo = repo
        self.credential_repo = credential_repo
        self.subscription_repo = subscription_repo
        self.config_manager = config_manager

    async def get_all(self) -> list[ClientReadDetail]:
        clients = await self.repo.get_all_with_credentials()
        return [ClientReadDetail.model_validate(c) for c in clients]

    async def get_by_id(self, id: int) -> ClientReadDetail:
        client = await self.repo.get_with_credential(id)

        if not client:
            raise NotFoundError("Клиент не найден")
        return ClientReadDetail.model_validate(client)

    async def get_credentials(self, id: int) -> ClientCredentialRead:
        client = await self.repo.get_with_credential(id)

        if not client:
            raise NotFoundError("Клиент не найден")

        if not client.credential:
            raise NotFoundError("Credentials не найдены")

        return ClientCredentialRead.model_validate(client.credential)

    async def create(self, data: ClientCreate) -> ClientReadDetail:
        client = await self.repo.create_from_dict(data.model_dump())

        await self.credential_repo.create_for_client(
            client_id=client.id,
            naiveproxy_username=data.name,
        )

        client = await self.repo.get_with_credential(client.id)
        await self.config_manager.regenerate_all()
        return ClientReadDetail.model_validate(client)

    async def update(self, id: int, data: ClientUpdate) -> ClientReadDetail:
        client = await self.repo.get_with_credential(id)

        if not client:
            raise NotFoundError("Клиент не найден")

        update_data = data.model_dump(exclude_unset=True)

        if "is_active" in update_data:
            if update_data["is_active"]:
                await self.subscription_repo.activate_by_client(id)
            else:
                await self.subscription_repo.deactivate_by_client(id)

        client = await self.repo.update_from_dict(client, update_data)
        await self.config_manager.regenerate_all()
        return ClientReadDetail.model_validate(client)

    async def delete(self, id: int) -> None:
        client = await self.repo.get(id)

        if not client:
            raise NotFoundError("Клиент не найден")

        await self.repo.delete(client)
        await self.config_manager.regenerate_all()
