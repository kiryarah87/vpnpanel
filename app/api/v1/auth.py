from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.deps import AuthServiceDep, CurrentUserDep
from app.schemas.auth import ChangePasswordRequest, TokenRead
from app.schemas.user import UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenRead, status_code=status.HTTP_200_OK)
async def login(
    service: AuthServiceDep,
    form: OAuth2PasswordRequestForm = Depends(),
) -> TokenRead:
    return await service.login(form.username, form.password)


@router.get("/me", response_model=UserRead)
async def get_me(current_user: CurrentUserDep) -> UserRead:
    return current_user


@router.patch("/me", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    data: ChangePasswordRequest,
    service: AuthServiceDep,
    current_user: CurrentUserDep,
) -> None:
    await service.change_password(current_user.username, data)
