from datetime import datetime

from pydantic import BaseModel

from app.schemas.inbound import InboundRead


class SubscriptionCreate(BaseModel):
    name: str
    client_id: int
    inbound_ids: list[int] = []


class SubscriptionUpdate(BaseModel):
    name: str | None = None
    inbound_ids: list[int] | None = None


class SubscriptionRead(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    token: str
    client_id: int
    created_at: datetime
    updated_at: datetime


class SubscriptionReadDetail(SubscriptionRead):
    inbounds: list[InboundRead] = []
