# VPN Panel

Панель управления VPN сервисами с поддержкой нескольких протоколов.

## Возможности

- 🔐 **Протоколы**: VLESS TCP Reality, VLESS xHTTP Reality, Hysteria2, NaiveProxy
- 👥 **Клиенты**: управление пользователями и их credentials
- 📋 **Подписки**: гибкое назначение инбаундов клиентам
- 🌐 **Домены**: управление доменами для NaiveProxy
- ⚙️ **Авто-конфигурация**: автоматическая генерация конфигов Xray, Hysteria2, Caddy
- 🐳 **Docker**: все сервисы запускаются в контейнерах

## Стек

- **Backend**: FastAPI, SQLAlchemy, Pydantic
- **Database**: SQLite (aiosqlite)
- **Auth**: JWT (python-jose)
- **VPN**: Xray, Hysteria2, Caddy (NaiveProxy)

## Быстрый старт

### Локально

```bash
cp .env.example .env
uv sync
alembic upgrade head
uv run uvicorn main:app --reload
```

### Docker

```bash
docker compose -f docker/docker-compose.yml up -d --build
```

API документация доступна по адресу: `http://localhost:8000/docs`

## Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `SECRET_KEY` | Секретный ключ JWT | — |
| `JWT_EXPIRE_MINUTES` | Время жизни токена (мин) | `1440` |
| `ADMIN_USERNAME` | Логин администратора | `admin` |
| `ADMIN_PASSWORD` | Пароль администратора | `admin` |
| `DATABASE_URL` | URL базы данных | `sqlite+aiosqlite:///./vpnpanel.db` |
| `SUBSCRIPTION_BASE_URL` | Базовый URL для подписок | `http://localhost:8000` |
