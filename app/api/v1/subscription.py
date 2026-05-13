from fastapi import APIRouter, Depends, status

from app.core.deps import CurrentUser, SubscriptionServiceDep
from app.schemas.subscription import (
    SubscriptionCreate,
    SubscriptionRead,
    SubscriptionReadDetail,
    SubscriptionUpdate,
)

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])
protected = APIRouter(dependencies=[Depends(CurrentUser)])


@protected.get("/", response_model=list[SubscriptionRead])
async def get_subscriptions(service: SubscriptionServiceDep) -> list[SubscriptionRead]:
    return await service.get_all()


@protected.get("/{id}", response_model=SubscriptionReadDetail)
async def get_subscription(
    id: int, service: SubscriptionServiceDep
) -> SubscriptionReadDetail:
    return await service.get_by_id(id)


@protected.post(
    "/", response_model=SubscriptionReadDetail, status_code=status.HTTP_201_CREATED
)
async def create_subscription(
    data: SubscriptionCreate,
    service: SubscriptionServiceDep,
) -> SubscriptionReadDetail:
    return await service.create(data)


@protected.patch("/{id}", response_model=SubscriptionReadDetail)
async def update_subscription(
    id: int,
    data: SubscriptionUpdate,
    service: SubscriptionServiceDep,
) -> SubscriptionReadDetail:
    return await service.update(id, data)


@protected.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subscription(id: int, service: SubscriptionServiceDep) -> None:
    await service.delete(id)


@router.get(
    "/sub/{token}", response_model=SubscriptionReadDetail, include_in_schema=False
)
async def get_subscription_by_token(
    token: str,
    service: SubscriptionServiceDep,
) -> SubscriptionReadDetail:
    return await service.get_by_token(token)


router.include_router(protected)
