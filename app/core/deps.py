from typing import Annotated, Callable, Type, TypeVar

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.exception import UnauthorizedError
from app.repositories.base import BaseRepository
from app.repositories.client import ClientRepository
from app.repositories.domain import DomainRepository
from app.repositories.inbound import InboundRepository
from app.repositories.subscription import SubscriptionRepository
from app.repositories.user import UserRepository
from app.schemas.user import UserRead
from app.services.auth import AuthService
from app.services.client import ClientService
from app.services.domain import DomainService
from app.services.inbound import InboundService
from app.services.subscription import SubscriptionService

RepoType = TypeVar("RepoType", bound=BaseRepository)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

DbSession = Annotated[AsyncSession, Depends(get_session)]


def make_repo_dep(repo_class: Type[RepoType]) -> Callable[[DbSession], RepoType]:
    """Фабрика зависимостей для репозиториев"""

    def _get_repo(session: DbSession) -> RepoType:
        return repo_class(session)

    _get_repo.__name__ = f"get_{repo_class.__name__.lower()}"
    return _get_repo


UserRepositoryDep = Annotated[UserRepository, Depends(make_repo_dep(UserRepository))]
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


def get_auth_service(repo: UserRepositoryDep) -> AuthService:
    return AuthService(repo)


def get_client_service(repo: ClientRepositoryDep) -> ClientService:
    return ClientService(repo)


def get_domain_service(repo: DomainRepositoryDep) -> DomainService:
    return DomainService(repo)


def get_inbound_service(repo: InboundRepositoryDep) -> InboundService:
    return InboundService(repo)


def get_subscription_service(
    repo: SubscriptionRepositoryDep,
    inbound_repo: InboundRepositoryDep,
) -> SubscriptionService:
    return SubscriptionService(repo, inbound_repo)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
ClientServiceDep = Annotated[ClientService, Depends(get_client_service)]
DomainServiceDep = Annotated[DomainService, Depends(get_domain_service)]
InboundServiceDep = Annotated[InboundService, Depends(get_inbound_service)]
SubscriptionServiceDep = Annotated[
    SubscriptionService, Depends(get_subscription_service)
]


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: AuthServiceDep,
) -> UserRead:
    user = await auth_service.get_current_user_by_token(token)
    if not user or not user.is_active:
        raise UnauthorizedError()
    return user


CurrentUser = Annotated[UserRead, Depends(get_current_user)]
