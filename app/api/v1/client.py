from fastapi import APIRouter, Depends, status

from app.core.deps import ClientServiceDep, get_current_user
from app.schemas.client import ClientCreate, ClientReadDetail, ClientUpdate
from app.schemas.credential import ClientCredentialRead

router = APIRouter(
    prefix="/clients",
    tags=["clients"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/", response_model=list[ClientReadDetail])
async def get_clients(service: ClientServiceDep) -> list[ClientReadDetail]:
    return await service.get_all()


@router.get("/{id}", response_model=ClientReadDetail)
async def get_client(id: int, service: ClientServiceDep) -> ClientReadDetail:
    return await service.get_by_id(id)


@router.post("/", response_model=ClientReadDetail, status_code=status.HTTP_201_CREATED)
async def create_client(
    data: ClientCreate, service: ClientServiceDep
) -> ClientReadDetail:
    return await service.create(data)


@router.patch("/{id}", response_model=ClientReadDetail)
async def update_client(
    id: int, data: ClientUpdate, service: ClientServiceDep
) -> ClientReadDetail:
    return await service.update(id, data)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(id: int, service: ClientServiceDep) -> None:
    await service.delete(id)


@router.get("/{id}/credentials", response_model=ClientCredentialRead)
async def get_client_credentials(id: int, service: ClientServiceDep) -> ClientCredentialRead:
    return await service.get_credentials(id)
