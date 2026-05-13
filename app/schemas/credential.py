from datetime import datetime

from pydantic import BaseModel


class ClientCredentialRead(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    xray_uuid: str
    hysteria2_password: str
    naiveproxy_username: str
    naiveproxy_password: str
    created_at: datetime
    updated_at: datetime
