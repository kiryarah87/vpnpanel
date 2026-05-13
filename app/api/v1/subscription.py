from fastapi import APIRouter, Depends, status

from app.core.deps import SubscriptionServiceDep, get_current_user
from app.schemas.subscription import (
    SubscriptionCreate,
    SubscriptionRead,
    SubscriptionReadDetail,
    SubscriptionUpdate,
)

router = APIRouter(
    prefix="/subscriptions",
    tags=["subscriptions"],
    dependencies=[Depends(get_current_user)],
)

public_router = APIRouter(tags=["subscriptions"])


@router.get("/", response_model=list[SubscriptionRead])
async def get_subscriptions(service: SubscriptionServiceDep) -> list[SubscriptionRead]:
    return await service.get_all()


@router.get("/{id}", response_model=SubscriptionReadDetail)
async def get_subscription(
    id: int, service: SubscriptionServiceDep
) -> SubscriptionReadDetail:
    return await service.get_by_id(id)


@router.post(
    "/", response_model=SubscriptionReadDetail, status_code=status.HTTP_201_CREATED
)
async def create_subscription(
    data: SubscriptionCreate,
    service: SubscriptionServiceDep,
) -> SubscriptionReadDetail:
    return await service.create(data)


@router.patch("/{id}", response_model=SubscriptionReadDetail)
async def update_subscription(
    id: int,
    data: SubscriptionUpdate,
    service: SubscriptionServiceDep,
) -> SubscriptionReadDetail:
    return await service.update(id, data)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subscription(id: int, service: SubscriptionServiceDep) -> None:
    await service.delete(id)


@public_router.get(
    "/sub/{token}", response_model=SubscriptionReadDetail, include_in_schema=False
)
async def get_subscription_by_token(
    token: str,
    service: SubscriptionServiceDep,
) -> SubscriptionReadDetail:
    return await service.get_by_token(token)
