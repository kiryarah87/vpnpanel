from app.core.exception import UnauthorizedError
from app.core.security import create_access_token, decode_access_token, verify_password
from app.repositories.user import UserRepository
from app.schemas.auth import TokenRead
from app.schemas.user import UserRead


class AuthService:
    """Сервис для аутентификации пользователей"""

    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def login(self, username: str, password: str) -> TokenRead:
        """Проверяет логин и пароль, возвращает токен доступа"""
        user = await self.repo.get_by_username(username)

        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedError("Неверный логин или пароль")

        token = create_access_token({"sub": user.username})
        return TokenRead(access_token=token)

    async def get_current_user_by_token(self, token: str) -> UserRead | None:
        """Получает текущего пользователя по токену доступа"""
        payload = decode_access_token(token)

        if not payload:
            return None

        username = payload.get("sub")

        if not username:
            return None

        user = await self.repo.get_by_username(username)
        return UserRead.model_validate(user) if user else None
