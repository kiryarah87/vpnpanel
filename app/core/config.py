from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App
    APP_NAME: str
    APP_VERSION: str = "0.1.0"
    DEBUG: bool

    # Server
    HOST: str
    PORT: int

    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Admin (первичный пользователь)
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str

    # Docker
    DOCKER_SOCKET: str
    VPN_NETWORK: str

    # Subscription
    SUBSCRIPTION_BASE_URL: str
    MAX_INBOUNDS_PER_SUBSCRIPTION: int


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
