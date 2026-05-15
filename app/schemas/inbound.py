from datetime import datetime

from pydantic import BaseModel, model_validator

from app.models.enum import PortType, ProtocolType

REALITY_PROTOCOLS = {ProtocolType.VLESS_TCP_REALITY, ProtocolType.VLESS_XHTTP_REALITY}


class InboundCreate(BaseModel):
    protocol: ProtocolType
    port: int | None = None
    port_type: PortType = PortType.RANDOM
    sni: str | None = None
    domain_id: int | None = None

    @model_validator(mode="after")
    def validate_fields(self):
        if self.port_type == PortType.FIXED and self.port is None:
            raise ValueError("port обязателен при port_type=FIXED")

        if self.protocol in REALITY_PROTOCOLS and not self.sni:
            raise ValueError("sni обязателен для VLESS протоколов")
        return self


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
    tag: str | None
    protocol: ProtocolType
    port: int | None
    port_type: PortType
    sni: str | None
    is_active: bool
    domain_id: int | None
    reality_public_key: str | None
    reality_short_id: str | None
    created_at: datetime
    updated_at: datetime
