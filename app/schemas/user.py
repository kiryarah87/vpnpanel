from pydantic import BaseModel


class UserRead(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    username: str
    is_active: bool
