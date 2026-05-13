from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.deps import AuthServiceDep
from app.schemas.auth import TokenRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenRead, status_code=status.HTTP_200_OK)
async def login(
    service: AuthServiceDep,
    form: OAuth2PasswordRequestForm = Depends(),
) -> TokenRead:
    return await service.login(form.username, form.password)
