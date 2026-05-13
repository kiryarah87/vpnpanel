from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.schemas.credential import ClientCredentialRead


class ClientCreate(BaseModel):
    name: str
    email: EmailStr | None = None
    traffic_limit_bytes: int | None = None


class ClientUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    is_active: bool | None = None
    traffic_limit_bytes: int | None = None


class ClientRead(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    email: EmailStr | None
    is_active: bool
    traffic_limit_bytes: int | None
    used_traffic_bytes: int
    created_at: datetime
    updated_at: datetime


class ClientReadDetail(ClientRead):
    credential: ClientCredentialRead | None = None
