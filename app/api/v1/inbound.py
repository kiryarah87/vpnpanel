from fastapi import APIRouter, Depends, status

from app.core.deps import InboundServiceDep, get_current_user
from app.schemas.inbound import InboundCreate, InboundRead, InboundUpdate

router = APIRouter(
    prefix="/inbounds",
    tags=["inbounds"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/", response_model=list[InboundRead])
async def get_inbounds(service: InboundServiceDep) -> list[InboundRead]:
    return await service.get_all()


@router.get("/{id}", response_model=InboundRead)
async def get_inbound(id: int, service: InboundServiceDep) -> InboundRead:
    return await service.get_by_id(id)


@router.post("/", response_model=InboundRead, status_code=status.HTTP_201_CREATED)
async def create_inbound(
    data: InboundCreate, service: InboundServiceDep
) -> InboundRead:
    return await service.create(data)


@router.patch("/{id}", response_model=InboundRead)
async def update_inbound(
    id: int, data: InboundUpdate, service: InboundServiceDep
) -> InboundRead:
    return await service.update(id, data)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inbound(id: int, service: InboundServiceDep) -> None:
    await service.delete(id)
