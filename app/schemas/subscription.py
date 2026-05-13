from datetime import datetime

from pydantic import BaseModel, model_validator

from app.schemas.inbound import InboundRead


class SubscriptionCreate(BaseModel):
    name: str
    client_id: int
    inbound_ids: list[int] = []


class SubscriptionUpdate(BaseModel):
    name: str | None = None
    is_active: bool | None = None
    inbound_ids: list[int] | None = None


class SubscriptionRead(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    token: str
    is_active: bool
    client_id: int
    created_at: datetime
    updated_at: datetime


class SubscriptionReadDetail(SubscriptionRead):
    model_config = {"from_attributes": True}

    inbounds: list[InboundRead] = []

    @model_validator(mode="before")
    @classmethod
    def extract_inbounds(cls, value):
        if hasattr(value, "subscription_inbounds"):
            value.__dict__["inbounds"] = [
                si.inbound for si in value.subscription_inbounds
            ]
        return value
