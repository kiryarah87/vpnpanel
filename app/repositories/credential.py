import secrets
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.credential import ClientCredential
from app.repositories.base import BaseRepository


class ClientCredentialRepository(BaseRepository[ClientCredential]):
    def __init__(self, session: AsyncSession):
        super().__init__(ClientCredential, session)

    async def get_by_client(self, client_id: int) -> ClientCredential | None:
        result = await self.session.execute(
            select(ClientCredential).where(ClientCredential.client_id == client_id)
        )
        return result.scalar_one_or_none()

    async def create_for_client(
        self, client_id: int, naiveproxy_username: str
    ) -> ClientCredential:
        """Создать все credentials для нового клиента"""
        credential = ClientCredential(
            client_id=client_id,
            xray_uuid=str(uuid.uuid4()),
            hysteria2_password=secrets.token_urlsafe(16),
            naiveproxy_username=naiveproxy_username,
            naiveproxy_password=secrets.token_urlsafe(16),
        )
        self.session.add(credential)
        await self.session.flush()
        await self.session.refresh(credential)
        return credential
