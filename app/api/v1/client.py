from fastapi import APIRouter, Depends, status

from app.core.deps import ClientServiceDep, CurrentUser
from app.schemas.client import ClientCreate, ClientRead, ClientUpdate

router = APIRouter(
    prefix="/clients",
    tags=["clients"],
    dependencies=[Depends(CurrentUser)],
)


@router.get("/", response_model=list[ClientRead])
async def get_clients(service: ClientServiceDep) -> list[ClientRead]:
    return await service.get_all()


@router.get("/{id}", response_model=ClientRead)
async def get_client(id: int, service: ClientServiceDep) -> ClientRead:
    return await service.get_by_id(id)


@router.post("/", response_model=ClientRead, status_code=status.HTTP_201_CREATED)
async def create_client(data: ClientCreate, service: ClientServiceDep) -> ClientRead:
    return await service.create(data)


@router.patch("/{id}", response_model=ClientRead)
async def update_client(
    id: int, data: ClientUpdate, service: ClientServiceDep
) -> ClientRead:
    return await service.update(id, data)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(id: int, service: ClientServiceDep) -> None:
    await service.delete(id)
