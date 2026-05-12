from datetime import datetime

from pydantic import BaseModel

from app.models.inbound import PortType, ProtocolType


class InboundCreate(BaseModel):
    protocol: ProtocolType
    port: int | None = None
    port_type: PortType = PortType.RANDOM
    sni: str | None = None
    domain_id: int | None = None


class InboundUpdate(BaseModel):
    protocol: ProtocolType | None = None
    port: int | None = None
    port_type: PortType | None = None
    sni: str | None = None
    domain_id: int | None = None
    is_active: bool | None = None


class InboundRead(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    protocol: ProtocolType
    port: int | None
    port_type: PortType
    sni: str | None
    is_active: bool
    domain_id: int | None
    created_at: datetime
    updated_at: datetime
