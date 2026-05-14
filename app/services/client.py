from app.config_gen.manager import ConfigManager
from app.core.exception import NotFoundError
from app.repositories.client import ClientRepository
from app.repositories.credential import ClientCredentialRepository
from app.schemas.client import ClientCreate, ClientReadDetail, ClientUpdate


class ClientService:
    def __init__(
        self,
        repo: ClientRepository,
        credential_repo: ClientCredentialRepository,
        config_manager: ConfigManager,
    ):
        self.repo = repo
        self.credential_repo = credential_repo
        self.config_manager = config_manager

    async def get_all(self) -> list[ClientReadDetail]:
        clients = await self.repo.get_all_with_credentials()
        return [ClientReadDetail.model_validate(c) for c in clients]

    async def get_by_id(self, id: int) -> ClientReadDetail:
        client = await self.repo.get_with_credential(id)

        if not client:
            raise NotFoundError("Клиент не найден")
        return ClientReadDetail.model_validate(client)

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

        client = await self.repo.update_from_dict(
            client, data.model_dump(exclude_unset=True)
        )

        await self.config_manager.regenerate_all()
        return ClientReadDetail.model_validate(client)

    async def delete(self, id: int) -> None:
        client = await self.repo.get(id)

        if not client:
            raise NotFoundError("Клиент не найден")

        await self.repo.delete(client)
        await self.config_manager.regenerate_all()
