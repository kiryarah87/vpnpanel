from app.core.exception import NotFoundError
from app.repositories.client import ClientRepository
from app.repositories.credential import ClientCredentialRepository
from app.schemas.client import ClientCreate, ClientReadDetail, ClientUpdate


class ClientService:
    """Сервис для управления клиентами"""

    def __init__(
        self,
        repo: ClientRepository,
        credential_repo: ClientCredentialRepository,
    ):
        self.repo = repo
        self.credential_repo = credential_repo

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
            naiveproxy_username=data.name.lower().replace(" ", "_"),
        )
        client = await self.repo.get_with_credential(client.id)
        return ClientReadDetail.model_validate(client)

    async def update(self, id: int, data: ClientUpdate) -> ClientReadDetail:
        client = await self.repo.get(id)

        if not client:
            raise NotFoundError("Клиент не найден")

        await self.repo.update_from_dict(client, data.model_dump(exclude_unset=True))

        client = await self.repo.get_with_credential(id)
        return ClientReadDetail.model_validate(client)

    async def delete(self, id: int) -> None:
        client = await self.repo.get(id)

        if not client:
            raise NotFoundError("Клиент не найден")
        await self.repo.delete(client)
