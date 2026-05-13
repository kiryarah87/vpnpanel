from fastapi import APIRouter, status

from app.core.deps import AuthServiceDep
from app.schemas.auth import LoginForm, TokenRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenRead, status_code=status.HTTP_200_OK)
async def login(form: LoginForm, service: AuthServiceDep) -> TokenRead:
    return await service.login(form.username, form.password)
