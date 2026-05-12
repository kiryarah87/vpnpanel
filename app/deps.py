from typing import Annotated, Callable, Type, TypeVar

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.base import BaseRepository
from app.repositories.client import ClientRepository
from app.repositories.domain import DomainRepository
from app.repositories.inbound import InboundRepository
from app.repositories.subscription import SubscriptionRepository
from app.repositories.user import UserRepository
from app.services.client import ClientService
from app.services.domain import DomainService
from app.services.subscription import SubscriptionService

RepoType = TypeVar("RepoType", bound=BaseRepository)

DbSession = Annotated[AsyncSession, Depends(get_db)]


def make_repo_dep(repo_class: Type[RepoType]) -> Callable[[DbSession], RepoType]:
    """Фабрика зависимостей для репозиториев (DRY)"""

    def _get_repo(session: DbSession) -> RepoType:
        return repo_class(session)

    _get_repo.__name__ = f"get_{repo_class.__name__.lower()}"
    return _get_repo


ClientRepositoryDep = Annotated[
    ClientRepository, Depends(make_repo_dep(ClientRepository))
]
DomainRepositoryDep = Annotated[
    DomainRepository, Depends(make_repo_dep(DomainRepository))
]
InboundRepositoryDep = Annotated[
    InboundRepository, Depends(make_repo_dep(InboundRepository))
]
SubscriptionRepositoryDep = Annotated[
    SubscriptionRepository, Depends(make_repo_dep(SubscriptionRepository))
]
UserRepositoryDep = Annotated[UserRepository, Depends(make_repo_dep(UserRepository))]


def get_client_service(repo: ClientRepositoryDep) -> ClientService:
    return ClientService(repo)


def get_domain_service(repo: DomainRepositoryDep) -> DomainService:
    return DomainService(repo)


def get_subscription_service(
    repo: SubscriptionRepositoryDep,
    inbound_repo: InboundRepositoryDep,
) -> SubscriptionService:
    return SubscriptionService(repo, inbound_repo)


ClientServiceDep = Annotated[ClientService, Depends(get_client_service)]
DomainServiceDep = Annotated[DomainService, Depends(get_domain_service)]
SubscriptionServiceDep = Annotated[
    SubscriptionService, Depends(get_subscription_service)
]
