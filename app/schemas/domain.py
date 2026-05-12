from datetime import datetime

from pydantic import BaseModel


class DomainCreate(BaseModel):
    name: str


class DomainUpdate(BaseModel):
    name: str | None = None
    is_active: bool | None = None


class DomainRead(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
