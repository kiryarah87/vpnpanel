from fastapi import APIRouter, Depends, status

from app.core.deps import DomainServiceDep, get_current_user
from app.schemas.domain import DomainCreate, DomainRead, DomainUpdate

router = APIRouter(
    prefix="/domains",
    tags=["domains"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/", response_model=list[DomainRead])
async def get_domains(service: DomainServiceDep) -> list[DomainRead]:
    return await service.get_all()


@router.get("/{id}", response_model=DomainRead)
async def get_domain(id: int, service: DomainServiceDep) -> DomainRead:
    return await service.get_by_id(id)


@router.post("/", response_model=DomainRead, status_code=status.HTTP_201_CREATED)
async def create_domain(data: DomainCreate, service: DomainServiceDep) -> DomainRead:
    return await service.create(data)


@router.patch("/{id}", response_model=DomainRead)
async def update_domain(
    id: int, data: DomainUpdate, service: DomainServiceDep
) -> DomainRead:
    return await service.update(id, data)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_domain(id: int, service: DomainServiceDep) -> None:
    await service.delete(id)
